from flask import Flask, render_template, request, send_file
import os, zipfile, tempfile, json

app = Flask(__name__)

# HOME - SYSTEM DASHBOARD
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/marketwatch')
def marketwatch():
    return render_template('marketwatch_demo.html')

# TOOL 01: APK BUILDER
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

    # save lead
    os.makedirs("data", exist_ok=True)
    with open("data/leads.txt","a", encoding="utf-8") as f:
        f.write(f"{app_name} | {url} | {phone}\n")

    base_apk = os.path.join(os.getcwd(), "base.apk")
    if not os.path.exists(base_apk):
        return "System error: base.apk missing in repo root.", 500

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
