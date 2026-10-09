from flask import Flask, render_template, request, jsonify
import qrcode, os, io, base64
from datetime import datetime
import paramiko

app = Flask(__name__)

# --- HOME + ALL 19 TOOLS ---
@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/tool/builder')
@app.route('/tool/store-builder')  # <--- FIX for your new homepage
def builder(): 
    # your file is builder.html not store_builder.html
    return render_template('builder.html')

@app.route('/tool/wa-qr')
def wa_qr(): return render_template('wa_qr.html')

@app.route('/tool/invoice')
def invoice(): return render_template('invoice.html')

@app.route('/tool/bg-remover')
def bg_remover(): return render_template('bg_remover.html')

@app.route('/tool/pos-charges')
def pos_charges(): return render_template('pos_charges.html')

@app.route('/tool/delivery-fee')
def delivery_fee(): return render_template('delivery_fee.html')

@app.route('/tool/price-tag')
def price_tag(): return render_template('price_tag.html')

@app.route('/tool/profit-calc')
def profit_calc(): return render_template('profit_calculator.html')

@app.route('/tool/debt-book')
def debt_book(): return render_template('debt_book.html')

@app.route('/tool/ruler-terminal')
def ruler_terminal(): return render_template('ruler_terminal.html')

@app.route('/tool/clear-shell')
def clear_shell(): return render_template('clear_shell.html')

@app.route('/tool/usa-notify')
def usa_notify(): return render_template('usa_notify.html')

@app.route('/tool/gamer-tag')
def gamer_tag(): return render_template('gamer_tag.html')

@app.route('/tool/sensitivity')
def sensitivity(): return render_template('sensitivity.html')

@app.route('/tool/clan-logo')
def clan_logo(): return render_template('clan_logo.html')

@app.route('/tool/tournament')
def tournament(): return render_template('tournament.html')

@app.route('/tool/paycheck')
def paycheck(): return render_template('paycheck.html')

@app.route('/tool/fake-text')
def fake_text(): return render_template('fake_text.html')

@app.route('/tool/tip-calculator')
def tip_calculator(): return render_template('tip_calculator.html')

# --- API: QR GENERATOR ---
@app.route('/api/qr', methods=['POST'])
def gen_qr():
    try:
        data = request.json.get('text','').strip()
        if not data:
            return jsonify({'error': 'Empty text'}), 400
        img = qrcode.make(data)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify({'qr': f'data:image/png;base64,{b64}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- API: RULER TERMINAL (V2 + MORE COMMANDS FOR RETENTION) ---
@app.route('/api/ruler-terminal', methods=['POST'])
def ruler_api():
    cmd = request.json.get('cmd','').strip().lower()
    
    # Premium outputs to keep user typing = more Monetag views
    outs = {
        'help': 'Available: help, clear, ls, pwd, date, echo, whoami, neofetch, hack, matrix, banner, vendors, free, df, uptime, monetag',
        'ls': 'builder.html  wa_qr.html  invoice.html  bg_remover.html  pos_charges.html  delivery_fee.html  price_tag.html  profit_calculator.html  debt_book.html  clear_shell.html  ruler_terminal.html  gamer_tag.html  sensitivity.html  clan_logo.html  tournament.html  paycheck.html  fake_text.html  tip_calculator.html  usa_notify.html',
        'pwd': '/home/clearcode/vendors',
        'whoami': 'clearcode-vendor',
        'date': datetime.now().strftime('%a %b %d %H:%M:%S WAT %Y'),
        'clear': '__CLEAR__',
        'free': 'Mem: 3.8Gi total, 1.2Gi used, 2.2Gi free - ClearCode VPS',
        'df': 'Filesystem 50G Used 12G Avail 36G Use% 25% Mounted on /',
        'uptime': 'up 12 days, 4:23, 1 user, load average: 0.08 - ClearCode VPS',
        'vendors': '5,231+ vendors using ClearCode tools - 19 tools premium 4K',
        'banner': ' ██████╗██╗     ███████╗ █████╗ ██████╗  ██████╗ ██████╗ ██████╗ ███████╗\n██╔════╝██║     ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝\n██║     ██║     █████╗  ███████║██████╔╝██║     ██║   ██║██║  ██║█████╗\n██║     ██║     ██╔══╝  ██╔══██║██╔══██╗██║     ██║   ██║██║  ██║██╔══╝\n╚██████╗███████╗███████╗██║  ██║██║  ██║╚██████╗╚██████╔╝██████╔╝███████╗',
        'neofetch': 'root@clearcode-vps\nOS: Ubuntu 22.04 LTS\nHost: ClearCode VPS\nUptime: 12 days\nMemory: 1.2GiB / 3.8GiB\nDisk: 12G / 50G',
        'hack': '[ACCESS GRANTED] - ClearCode premium terminal - fake hacker mode for TikTok',
        'matrix': '010101010101 - MATRIX MODE - Record this for content',
        'monetag': 'Monetag Active - Zone 11970643 + Vignette 11988352 - Keep typing to trigger',
    }
    if cmd.startswith('echo '):
        return jsonify({'output': cmd[5:]})
    if cmd == '':
        return jsonify({'output': ''})
    return jsonify({'output': outs.get(cmd, f'Command not found: {cmd} - type help')})

# --- API: CLEAR-SHELL REAL VPS (your current exec method - works without upgrade) ---
@app.route('/api/clear-shell', methods=['POST'])
def shell_api():
    d = request.json
    try:
        host = d.get('host','').strip()
        user = d.get('user','root').strip()
        pwd = d.get('pass','')
        cmd = d.get('cmd','').strip()
        if not host or not pwd or not cmd:
            return jsonify({'output': 'Error: host, password and command required'})
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=pwd, timeout=8, banner_timeout=8, auth_timeout=8)
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        out = stdout.read().decode(errors='ignore') + stderr.read().decode(errors='ignore')
        client.close()
        return jsonify({'output': out or '(No output - command executed)'})
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)} - Check IP/user/password'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)