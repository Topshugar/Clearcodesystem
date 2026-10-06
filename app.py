from flask import Flask, render_template, request, send_file
import os, zipfile, tempfile

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/builder')
def builder():
    return render_template('builder.html')

@app.route('/marketwatch')
def marketwatch():
    return render_template('marketwatch_demo.html')

@app.route('/generate', methods=['POST'])
def generate():
    app_name = request.form.get('app_name', 'MyApp')
    url = request.form.get('url', 'https://example.com')
    
    # Lead saving
    with open("leads.txt","a") as f:
        f.write(f"{app_name},{url},{request.remote_addr}\n")
    
    # Create APK zip logic here (simplified for deploy)
    tmp = tempfile.mkdtemp()
    zip_path = os.path.join(tmp, f"{app_name}.zip")
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.writestr("README.txt", f"App: {app_name}\nURL: {url}\nBuilt by ClearCode System")
    
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
