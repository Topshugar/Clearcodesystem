from flask import Flask, request, send_file, jsonify
import os, zipfile, tempfile, json, subprocess, io, base64

app = Flask(__name__)

# Fallback HTML if templates missing
FALLBACK_HOME = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:#000;color:#fff;font-family:Arial;padding:20px}
a{display:block;background:#0f0f0f;border:1px solid #222;padding:15px;margin:10px 0;border-radius:12px;color:#00ff88;text-decoration:none}
</style></head><body>
<h2>ClearCode System LIVE ✅</h2>
<a href="/tools/apk-builder">Tool 01 APK Builder</a>
<a href="/tools/ruler-terminal">Tool 02 Ruler</a>
<a href="/tools/wa-qr">Tool 03 WA QR</a>
<a href="/tools/invoice">Tool 04 Invoice</a>
<a href="/tools/bg-remover">Tool 05 BG Remover</a>
<a href="/debug">/debug</a>
</body></html>
"""

def safe_render(template_name, fallback_html):
    try:
        from flask import render_template
        return render_template(template_name)
    except Exception as e:
        return f"<div style='color:red;padding:10px'>Missing {template_name}: {e}</div>" + fallback_html, 200

@app.route('/')
def home():
    return safe_render('index.html', FALLBACK_HOME)

@app.route('/debug')
def debug():
    files = []
    for root, dirs, filenames in os.walk("."):
        if ".git" in root:
            continue
        for f in filenames:
            files.append(os.path.join(root, f))
    return "<br>".join(files[:300])

# === TOOL 01 APK ===
@app.route('/tools/apk-builder')
@app.route('/builder')
def apk_builder():
    return safe_render('builder.html', "<h2>builder.html missing - upload it</h2>")

@app.route('/generate', methods=['POST'])
def generate():
    try:
        app_name = request.form.get('app_name','MyApp')[:20] or "MyApp"
        url = request.form.get('url','').strip()
        phone = request.form.get('phone','')
        if not url.startswith('http'):
            return "URL must start with http", 400
        os.makedirs("data", exist_ok=True)
        with open("data/leads.txt","a", encoding="utf-8") as f:
            f.write(f"{app_name} | {url} | {phone}\n")
        base_apk = os.path.join(os.getcwd(), "base.apk")
        if not os.path.exists(base_apk):
            return "base.apk not found in root - upload it", 500
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
    except Exception as e:
        return f"Error in generate: {e}", 500

# === TOOL 02 RULER ===
@app.route('/tools/ruler-terminal')
def ruler_terminal():
    return safe_render('ruler_terminal.html', "<h2>ruler_terminal.html missing</h2>")

@app.route('/api/ruler-terminal', methods=['POST'])
def ruler_api():
    cmd = request.get_json().get('cmd','').strip()
    if cmd == 'clear':
        return jsonify(output="__CLEAR__")
    if cmd in ['help','?']:
        return jsonify(output="Commands: ls, pwd, echo, date, clear")
    if any(x in cmd for x in ["rm -rf","sudo",":()"]):
        return jsonify(output="Blocked")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        return jsonify(output=(r.stdout+r.stderr)[:4000] or "(no output)")
    except Exception as e:
        return jsonify(output=str(e))

# === TOOL 03 WA QR ===
@app.route('/tools/wa-qr')
def wa_qr_tool():
    return safe_render('wa_qr.html', "<h2>wa_qr.html missing</h2>")

@app.route('/api/qr', methods=['POST'])
def api_qr():
    try:
        import qrcode
        text = request.get_json().get('text','').strip()
        if not text:
            return jsonify(qr="")
        img = qrcode.make(text)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify(qr=f"data:image/png;base64,{b64}")
    except Exception as e:
        return jsonify(error=str(e)), 500

# === TOOL 04 INVOICE ===
@app.route('/tools/invoice')
def invoice_tool():
    return safe_render('invoice.html', "<h2>invoice.html missing - upload the file I gave you</h2>")

# === TOOL 05 BG REMOVER - LITE, NO REMBG NEEDED ===
@app.route('/tools/bg-remover')
def bg_remover_tool():
    return safe_render('bg_remover.html', "<h2>bg_remover.html missing</h2>")

@app.route('/api/remove-bg', methods=['POST'])
def api_remove_bg():
    try:
        from PIL import Image
        file = request.files.get('image')
        if not file:
            return jsonify(error="No image uploaded"), 400

        img = Image.open(file.stream).convert("RGBA")
        datas = img.getdata()
        new_data = []
        for item in datas:
            # Remove near-white background (for product photos)
            if item[0] > 210 and item[1] > 210 and item[2] > 210:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify(result=f"data:image/png;base64,{b64}")
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port) 
