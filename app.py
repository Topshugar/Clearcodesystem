from flask import Flask, render_template, request, send_file, jsonify
import os, zipfile, tempfile, json, subprocess, io, base64

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/marketwatch')
def marketwatch():
    return render_template('marketwatch_demo.html')

# === TOOL 01 APK ===
@app.route('/tools/apk-builder')
@app.route('/builder')
def apk_builder():
    return render_template('builder.html')

@app.route('/generate', methods=['POST'])
def generate():
    app_name = request.form.get('app_name','MyApp').strip()[:20] or "MyApp"
    url = request.form.get('url','').strip()
    phone = request.form.get('phone','')
    if not url.startswith('http'):
        return "URL must start with https://", 400
    os.makedirs("data", exist_ok=True)
    with open("data/leads.txt","a", encoding="utf-8") as f:
        f.write(f"{app_name} | {url} | {phone}\n")
    base_apk = os.path.join(os.getcwd(), "base.apk")
    if not os.path.exists(base_apk):
        return "base.apk missing", 500
    tmpdir = tempfile.mkdtemp()
    final_path = os.path.join(tmpdir, f"{app_name.replace(' ','_')}.apk")
    config_data = json.dumps({"url": url, "app_name": app_name})
    with zipfile.ZipFile(base_apk, 'r') as zin, zipfile.ZipFile(final_path, 'w') as zout:
        for item in zin.infolist():
            if item.filename == "assets/config.json":
                zout.writestr(item, config_data)
            elif item.filename.startswith("META-INF/"):
                continue
            else:
                zout.writestr(item, zin.read(item.filename))
        if "assets/config.json" not in zin.namelist():
            zout.writestr("assets/config.json", config_data)
    return send_file(final_path, as_attachment=True, download_name=f"{app_name}.apk", mimetype="application/vnd.android.package-archive")

# === TOOL 02 RULER TERMINAL ===
@app.route('/tools/ruler-terminal')
def ruler_terminal():
    return render_template('ruler_terminal.html')

@app.route('/api/ruler-terminal', methods=['POST'])
def ruler_api():
    data = request.get_json()
    cmd = data.get('cmd','').strip()
    if not cmd:
        return jsonify(output="")
    if cmd in ['help','?']:
        return jsonify(output="Commands: ls, pwd, echo, date, clear, ls templates, cat [file]")
    if cmd == 'clear':
        return jsonify(output="__CLEAR__")
    if any(x in cmd for x in ["rm -rf","sudo",":(){","shutdown","mkfs"]):
        return jsonify(output="Blocked")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3, cwd=os.getcwd())
        out = (result.stdout + result.stderr)[:4000]
        return jsonify(output=out or "(no output)")
    except Exception as e:
        return jsonify(output=str(e))

# === TOOL 03 WA QR ===
@app.route('/tools/wa-qr')
def wa_qr_tool():
    return render_template('wa_qr.html')

@app.route('/api/qr', methods=['POST'])
def api_qr():
    import qrcode
    text = request.get_json().get('text','').strip()
    if not text:
        return jsonify(qr="")
    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify(qr=f"data:image/png;base64,{b64}")

# === TOOL 04 INVOICE ===
@app.route('/tools/invoice')
def invoice_tool():
    return render_template('invoice.html') 
    # === TOOL 05 BG REMOVER ===
@app.route('/tools/bg-remover')
def bg_remover_tool():
    return render_template('bg_remover.html')

@app.route('/api/remove-bg', methods=['POST'])
def api_remove_bg():
    try:
        from rembg import remove
        from PIL import Image
        file = request.files.get('image')
        if not file:
            return jsonify(error="No image"), 400
        input_img = Image.open(file.stream)
        output_img = remove(input_img)
        buf = io.BytesIO()
        output_img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify(result=f"data:image/png;base64,{b64}")
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
