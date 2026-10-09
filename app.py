from flask import Flask, render_template, request, jsonify, Response
import qrcode, os, io, base64
from datetime import datetime
import paramiko
from PIL import Image

# --- FIX FOR 512Mi - LAZY LOAD (no crash at boot) ---
REMBG_AVAILABLE = False
human_session = None
cloth_session = None

def get_session(mode='human'):
    global human_session, cloth_session, REMBG_AVAILABLE
    try:
        from rembg import remove, new_session
        REMBG_AVAILABLE = True
        if mode == 'human' and human_session is None:
            try:
                human_session = new_session("u2net_human_seg")
            except:
                human_session = True
        elif cloth_session is None:
            try:
                cloth_session = new_session("isnet-general-use")
            except:
                cloth_session = True
        return True
    except Exception as e:
        print(f"rembg init error: {e}")
        return False

app = Flask(__name__)

# --- HOME + ALL 21 TOOLS ---
@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/unlock')
def unlock():
    return render_template('unlock.html')

@app.route('/tool/builder')
@app.route('/tool/store-builder')
def builder(): 
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

@app.route('/tool/whatsapp-broadcast')
@app.route('/tool/whatsapp_broadcast')
@app.route('/template/whatsapp_broadcast.html')
def whatsapp_broadcast(): 
    return render_template('whatsapp_broadcast.html')

@app.route('/tool/background-check')
@app.route('/tool/usa-background-check')
@app.route('/tool/background_check')
def background_check(): 
    return render_template('usa_background_check.html')

# --- SEO: SITEMAP + ROBOTS ---
@app.route('/sitemap.xml')
def sitemap():
    tools = ['builder','wa-qr','invoice','bg-remover','pos-charges','delivery-fee','price-tag','profit-calc','debt-book','ruler-terminal','clear-shell','usa-notify','gamer-tag','sensitivity','clan-logo','tournament','paycheck','fake-text','tip-calculator','whatsapp-broadcast','background-check']
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += '<url><loc>https://clearcode.quest/</loc><priority>1.0</priority></url>'
    for t in tools:
        xml += f'<url><loc>https://clearcode.quest/tool/{t}</loc><priority>0.8</priority></url>'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    txt = "User-agent: *\nAllow: /\nDisallow: /unlock\nDisallow: /api/\nSitemap: https://clearcode.quest/sitemap.xml"
    return Response(txt, mimetype='text/plain')

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

@app.route('/api/bg-remove', methods=['POST'])
def api_bg_remove():
    try:
        file = request.files.get('image')
        if not file:
            return jsonify({'error': 'No image uploaded'}), 400
        mode = request.form.get('mode', 'human')
        if not get_session(mode):
            return jsonify({'error': 'AI loading, try again in 10s'}), 503
        from rembg import remove
        input_img = Image.open(file.stream).convert('RGBA')
        if mode == 'human' and human_session and human_session != True:
            output = remove(input_img, session=human_session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10)
        elif cloth_session and cloth_session != True:
            output = remove(input_img, session=cloth_session, alpha_matting=True)
        else:
            output = remove(input_img)
        buf = io.BytesIO()
        output.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify({'result': f'data:image/png;base64,{b64}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ruler-terminal', methods=['POST'])
def ruler_api():
    cmd = request.json.get('cmd','').strip().lower()
    outs = {
        'help': 'help, clear, ls, pwd, date, echo, whoami, neofetch, hack, matrix, banner, vendors, free, df, uptime',
        'ls': 'builder.html wa_qr.html invoice.html bg_remover.html usa_notify.html pos_charges.html delivery_fee.html price_tag.html profit_calculator.html debt_book.html clear_shell.html ruler_terminal.html gamer_tag.html sensitivity.html clan_logo.html tournament.html paycheck.html fake_text.html tip_calculator.html whatsapp_broadcast.html usa_background_check.html unlock.html',
        'pwd': '/home/clearcode/vendors',
        'whoami': 'clearcode-vendor',
        'date': datetime.now().strftime('%a %b %d %H:%M:%S WAT %Y'),
        'clear': '__CLEAR__',
        'free': 'Mem: 3.8Gi total, 1.2Gi used, 2.2Gi free',
        'df': 'Filesystem 50G Used 12G Avail 36G Use% 25% /',
        'uptime': 'up 12 days - ClearCode VPS',
        'vendors': '5,231+ vendors using ClearCode',
        'neofetch': 'root@clearcode-vps\nOS: Ubuntu 22.04 LTS\nUptime: 12 days\nMemory: 1.2GiB / 3.8GiB',
        'hack': '[ACCESS GRANTED] ClearCode premium',
        'matrix': '010101 MATRIX MODE',
    }
    if cmd.startswith('echo '):
        return jsonify({'output': cmd[5:]})
    if cmd == '':
        return jsonify({'output': ''})
    return jsonify({'output': outs.get(cmd, f'Command not found: {cmd}')})

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
        return jsonify({'output': out or '(No output)'})
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)