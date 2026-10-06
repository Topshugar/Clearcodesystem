from flask import Flask, render_template, request, send_file, jsonify
import os, zipfile, tempfile, json, subprocess, io, base64

app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except:
        return "<h2>ClearCode System LIVE</h2><a href='/tools/apk-builder'>APK</a> | <a href='/tools/ruler-terminal'>Ruler</a> | <a href='/tools/wa-qr'>QR</a> | <a href='/tools/invoice'>Invoice</a> | <a href='/tools/bg-remover'>BG</a>"

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
        return "base.apk missing - upload it to root", 500
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
    return send_file(final_path, as_attachment=True, download_name=f"{app_name}.apk")

# === TOOL 02 ===
@app.route('/tools/ruler-terminal')
def ruler_terminal():
    return render_template('ruler_terminal.html')

@app.route('/api/ruler-terminal', methods=['POST'])
def ruler_api():
    cmd = request.get_json().get('cmd','').strip()
    if cmd == 'clear': return jsonify(output="__CLEAR__")
    if cmd in ['help','?']: return jsonify(output="ls, pwd, echo, date, clear")
    if any(x in cmd for x in ["rm -rf","sudo",":()"]): return jsonify(output="Blocked")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        return jsonify(output=(r.stdout+r.stderr)[:4000] or "(no output)")
    except Exception as e:
        return jsonify(output=str(e))

# === TOOL 03 ===
@app.route('/tools/wa-qr')
def wa_qr_tool():
    return render_template('wa_qr.html')

@app.route('/api/qr', methods=['POST'])
def api_qr():
    import qrcode
    text = request.get_json().get('text','').strip()
    if not text: return jsonify(qr="")
    img = qrcode.make(text)
    buf = io.BytesIO(); img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify(qr=f"data:image/png;base64,{b64}")

# === TOOL 04 ===
@app.route('/tools/invoice')
def invoice_tool():
    return render_template('invoice.html')

# === TOOL 05 - FIXED, WON'T CRASH ===
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
            return jsonify(error="No image uploaded"), 400
        input_img = Image.open(file.stream)
        output_img = remove(input_img)
        buf = io.BytesIO()
        output_img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify(result=f"data:image/png;base64,{b64}")
    except ImportError as e:
        return jsonify(error="Server still installing AI model. Wait 2 mins and try again. Or remove rembg from requirements to use lite mode."), 500
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
