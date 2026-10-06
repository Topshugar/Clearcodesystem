from flask import Flask, request, send_file, jsonify
import os, zipfile, tempfile, json, subprocess, io, base64

app = Flask(__name__)

# Inline HTML fallback if templates folder missing
FALLBACK_HOME = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:#000;color:#fff;font-family:Arial;padding:20px}
a{display:block;background:#0f0f0f;border:1px solid #222;padding:15px;margin:10px 0;border-radius:12px;color:#00ff88;text-decoration:none}
</style></head><body>
<h2>ClearCode System LIVE ✅</h2>
<p>Templates folder is missing, but app is running. Re-upload your html files.</p>
<a href="/tools/apk-builder">Tool 01 APK Builder</a>
<a href="/tools/ruler-terminal">Tool 02 Ruler</a>
<a href="/tools/wa-qr">Tool 03 WA QR</a>
<a href="/tools/invoice">Tool 04 Invoice</a>
<a href="/tools/bg-remover">Tool 05 BG Remover</a>
<a href="/debug">/debug - Check files</a>
</body></html>
"""

def safe_render(template_name, fallback_html):
    try:
        from flask import render_template
        return render_template(template_name)
    except Exception as e:
        return f"<h3 style='color:red'>Missing {template_name}: {e}</h3>" + fallback_html, 200

@app.route('/')
def home():
    return safe_render('index.html', FALLBACK_HOME)

@app.route('/debug')
def debug():
    files = []
    for root, dirs, filenames in os.walk("."):
        if ".git" in root: continue
        for f in filenames:
            files.append(os.path.join(root, f))
    return "<br>".join(files[:200])

# === TOOLS ===
@app.route('/tools/apk-builder')
@app.route('/builder')
def apk_builder():
    return safe_render('builder.html', "<h2>builder.html missing - upload it</h2>")

@app.route('/tools/ruler-terminal')
def ruler_terminal():
    return safe_render('ruler_terminal.html', "<h2>ruler_terminal.html missing</h2>")

@app.route('/tools/wa-qr')
def wa_qr_tool():
    return safe_render('wa_qr.html', "<h2>wa_qr.html missing</h2>")

@app.route('/tools/invoice')
def invoice_tool():
    return safe_render('invoice.html', "<h2>invoice.html missing</h2>")

@app.route('/tools/bg-remover')
def bg_remover_tool():
    return safe_render('bg_remover.html', "<h2>bg_remover.html missing</h2>")

@app.route('/generate', methods=['POST'])
def generate():
    try:
        app_name = request.form.get('app_name','MyApp')[:20] or "MyApp"
        url = request.form.get('url','').strip()
        if not url.startswith('http'): return "URL must start with http", 400
        base_apk = os.path.join(os.getcwd(), "base.apk")
        if not os.path.exists(base_apk): return "base.apk not in root", 500
        tmpdir = tempfile.mkdtemp()
        final_path = os.path.join(tmpdir, f"{app_name}.apk")
        config_data = json.dumps({"url": url, "app_name": app_name})
        with zipfile.ZipFile(base_apk, 'r') as zin, zipfile.ZipFile(final_path, 'w') as zout:
            for item in zin.infolist():
                if item.filename == "assets/config.json":
                    zout.writestr(item, config_data)
                elif item.filename.startswith("META-INF/"): continue
                else:
                    zout.writestr(item, zin.read(item.filename))
            if "assets/config.json" not in zin.namelist():
                zout.writestr("assets/config.json", config_data)
        return send_file(final_path, as_attachment=True, download_name=f"{app_name}.apk")
    except Exception as e:
        return f"Error in generate: {e}", 500

@app.route('/api/ruler-terminal', methods=['POST'])
def ruler_api():
    cmd = request.get_json().get('cmd','').strip()
    if cmd == 'clear': return jsonify(output="__CLEAR__")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        return jsonify(output=(r.stdout+r.stderr)[:4000] or "(no output)")
    except Exception as e:
        return jsonify(output=str(e))

@app.route('/api/qr', methods=['POST'])
def api_qr():
    try:
        import qrcode
        text = request.get_json().get('text','').strip()
        img = qrcode.make(text)
        buf = io.BytesIO(); img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify(qr=f"data:image/png;base64,{b64}")
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/remove-bg', methods=['POST'])
def api_remove_bg():
    try:
        from rembg import remove
        from PIL import Image
        file = request.files.get('image')
        if not file: return jsonify(error="No image"), 400
        input_img = Image.open(file.stream)
        output_img = remove(input_img)
        buf = io.BytesIO(); output_img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify(result=f"data:image/png;base64,{b64}")
    except Exception as e:
        return jsonify(error=f"BG Remover not ready: {e}. Remove rembg from requirements.txt for lite mode."), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
