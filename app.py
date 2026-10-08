from flask import Flask, render_template, request, jsonify
import qrcode, io, base64, os, requests, paramiko
from PIL import Image
from rembg import remove
from datetime import datetime

app = Flask(__name__)

# --- VISITOR TRACKER ---
@app.before_request
def track_visit():
    if request.path.startswith('/api/') or request.path.startswith('/admin/'):
        return
    if request.path.startswith('/tools') or request.path == '/' or request.path == '/unlock':
        try:
            with open('visits.txt','a', encoding='utf-8') as f:
                f.write(f"{datetime.now()} | {request.remote_addr} | {request.path} | {request.headers.get('User-Agent','')[:80]}\n")
        except:
            pass

@app.route('/admin/visits')
def admin_visits():
    if not os.path.exists('visits.txt'):
        return "<h2>No visits yet</h2>"
    try:
        with open('visits.txt','r', encoding='utf-8') as f:
            lines = f.read().splitlines()[-300:][::-1]
        html = "<h2>ClearCode - Last 300 Visits</h2><hr><pre style='background:#111;color:#0f0;padding:15px'>"
        for l in lines:
            html += l + "\n"
        html += "</pre><br><a href='/'>Back Home</a>"
        return html
    except Exception as e:
        return str(e)

# --- PAGES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tools/apk-builder')
def apk_builder():
    return render_template('builder.html')

@app.route('/tools/ruler-terminal')
def ruler_terminal():
    return render_template('ruler_terminal.html')

@app.route('/tools/wa-qr')
def wa_qr():
    return render_template('wa_qr.html')

@app.route('/tools/invoice')
def invoice():
    return render_template('invoice.html')

@app.route('/tools/bg-remover')
def bg_remover():
    return render_template('bg_remover.html')

@app.route('/tools/fake-alert')
def fake_alert():
    return render_template('fake_alert.html')

@app.route('/tools/pos-charges')
def pos_charges():
    return render_template('pos_charges.html')

@app.route('/tools/delivery-fee')
def delivery_fee():
    return render_template('delivery_fee.html')

@app.route('/tools/price-tag')
def price_tag():
    return render_template('price_tag.html')

@app.route('/tools/profit-calculator')
def profit_calculator():
    return render_template('profit_calculator.html')

@app.route('/tools/debt-book')
def debt_book():
    return render_template('debt_book.html')

@app.route('/tools/clear-shell')
def clear_shell():
    return render_template('clear_shell.html')

@app.route('/unlock')
def unlock_page():
    return render_template('unlock.html')

# --- APIS ---
@app.route('/generate', methods=['POST'])
def generate():
    app_name = request.form.get('app_name','MyApp')
    url = request.form.get('url')
    phone = request.form.get('phone')
    with open('leads.txt','a', encoding='utf-8') as f:
        f.write(f"{datetime.now()} | {app_name} | {url} | {phone}\n")
    return f"<h2>{app_name} APK Generated!</h2><p>{url}</p><p>We will contact {phone}</p><a href='/'>Back</a>"

@app.route('/api/qr', methods=['POST'])
def api_qr():
    data = request.get_json()
    text = data.get('text','')
    qr = qrcode.make(text)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify({'qr': f'data:image/png;base64,{b64}'})

@app.route('/api/ruler-terminal', methods=['POST'])
def api_ruler():
    data = request.get_json()
    cmd = data.get('cmd','').strip()
    if cmd == 'help':
        out = "Commands: help, clear, ls, pwd, date, echo [text], whoami"
    elif cmd == 'clear':
        out = '__CLEAR__'
    elif cmd.startswith('echo '):
        out = cmd[5:]
    elif cmd == 'ls':
        out = "builder.html ruler_terminal.html wa_qr.html invoice.html bg_remover.html fake_alert.html pos_charges.html delivery_fee.html price_tag.html profit_calculator.html debt_book.html clear_shell.html"
    elif cmd == 'pwd':
        out = "/home/clearcode/system"
    elif cmd == 'date':
        out = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif cmd == 'whoami':
        out = "clearcode-vendor"
    else:
        out = f"Command not found: {cmd} - type 'help'"
    return jsonify({'output': out})

@app.route('/api/remove-bg', methods=['POST'])
def api_remove_bg():
    try:
        file = request.files.get('image')
        if not file:
            return jsonify({'error':'No image'}), 400
        img = Image.open(file.stream)
        output = remove(img)
        buf = io.BytesIO()
        output.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify({'result': f'data:image/png;base64,{b64}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-image')
def api_ai_image():
    prompt = request.args.get('prompt','white puma shoe product photo white background studio')
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&nologo=true&model=turbo"
    try:
        r = requests.get(url, timeout=30)
        b64 = base64.b64encode(r.content).decode()
        return jsonify({'image': f'data:image/jpeg;base64,{b64}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-shell', methods=['POST'])
def api_clear_shell():
    data = request.get_json()
    host = data.get('host','').strip()
    user = data.get('user','root').strip()
    pwd = data.get('pass','')
    cmd = data.get('cmd','ls').strip()
    if not host or not pwd:
        return jsonify({'output': 'Add IP and Password'})
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=pwd, timeout=8, look_for_keys=False)
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        out = stdout.read().decode(errors='ignore') + stderr.read().decode(errors='ignore')
        client.close()
        with open('visits.txt','a', encoding='utf-8') as f:
            f.write(f"{datetime.now()} | ClearShell | {host} | {cmd}\n")
        return jsonify({'output': out or 'Command done - no output'})
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)