from flask import Flask, render_template, request, jsonify
import qrcode, io, base64, os
from PIL import Image
from rembg import remove

app = Flask(__name__)

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

@app.route('/unlock')
def unlock_page():
    return render_template('unlock.html')

@app.route('/generate', methods=['POST'])
def generate():
    app_name = request.form.get('app_name','MyApp')
    url = request.form.get('url')
    phone = request.form.get('phone')
    with open('leads.txt','a') as f:
        f.write(f"{app_name} | {url} | {phone}\n")
    return f"<h2>{app_name} APK Generated!</h2><p>{url}</p><p>We will contact {phone} - 08165043865</p><a href='/'>Back</a>"

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
        out = "builder.html ruler_terminal.html wa_qr.html invoice.html bg_remover.html fake_alert.html pos_charges.html delivery_fee.html price_tag.html"
    elif cmd == 'pwd':
        out = "/home/clearcode/system"
    elif cmd == 'date':
        out = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
