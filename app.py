from flask import Flask, render_template, request, jsonify, Response
import qrcode, os, io, base64, requests
from datetime import datetime
import paramiko
from PIL import Image

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

# --- GEO IP STRICT - 55 TOOLS - NG 23 + QA 6 + SA 6 + US 7 + AE 7 + KW 6 ---
COUNTRY_TOOLS = {
 'NG': ['nepa_calculator','cac_checker','fuel_calculator','rent_splitter','land_converter','paye_calculator','jamb_calculator','waec_calculator','nin_validator','pos_charges','wa_qr','whatsapp_broadcast','invoice','bg_remover','tip_calculator','delivery_fee','fake_text','debt_book','price_tag','profit_calc','ruler_terminal','clear_shell','market_ledger'],
 'US': ['paycheck','background_check','tip_calculator','invoice','bg_remover','fake_text','usa_notify'],
 'SA': ['iqama_expiry','hijri_converter','gosi_calculator','zatca_qr','gpa_calculator','salary_sa'],
 'QA': ['qid_check','qatar_traffic_fines','qatar_gratuity','qatar_rent_splitter','qatar_gold_price','qatar_overtime'],
 'AE': ['emirates_id_check','uae_traffic_fines','uae_gratuity','uae_gold_price','uae_rent_splitter','uae_overtime','uae_salary'],
 'KW': ['kuwait_civil_id','kuwait_traffic_fines','kuwait_gratuity','kuwait_gold_price','kuwait_rent','kuwait_overtime'],
}

COUNTRY_NAME = {
'NG':'🇳🇬 Nigeria','US':'🇺🇸 USA','SA':'🇸🇦 Saudi','QA':'🇶🇦 Qatar','AE':'🇦🇪 UAE','KW':'🇰🇼 Kuwait',
'GH':'🇳🇬 Nigeria','KE':'🇳🇬 Nigeria','CA':'🇺🇸 USA','GB':'🇺🇸 USA','BH':'🇸🇦 Saudi','OM':'🇸🇦 Saudi','EG':'🇸🇦 Saudi'
}

def get_country():
    try:
        cf = request.headers.get('CF-IPCountry')
        if cf and len(cf)==2 and cf.upper()!='XX':
            return cf.upper()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()
        if ip in ['127.0.0.1','::1','']:
            return 'NG'
        r = requests.get(f'https://ipapi.co/{ip}/country/', timeout=2.5)
        code = r.text.strip().upper()
        return code if len(code)==2 else 'NG'
    except:
        return 'NG'

def map_to_group(code):
    code = code.upper()
    if code in COUNTRY_TOOLS:
        return code
    if code in ['GH','KE','ZA','NG']:
        return 'NG'
    if code in ['US','CA','GB','AU']:
        return 'US'
    if code in ['SA','BH','OM','EG']:
        return 'SA'
    if code in ['QA']:
        return 'QA'
    if code in ['AE']:
        return 'AE'
    if code in ['KW']:
        return 'KW'
    return 'NG'

@app.route('/')
def home():
    raw_country = get_country()
    country = map_to_group(raw_country)
    allowed = COUNTRY_TOOLS.get(country, COUNTRY_TOOLS['NG'])
    display_name = COUNTRY_NAME.get(raw_country, COUNTRY_NAME.get(country, f'🌍 {country}'))
    return render_template('index.html', country=country, raw_country=raw_country, country_name=display_name, allowed=allowed, all_groups=COUNTRY_TOOLS)

@app.route('/unlock')
def unlock(): return render_template('unlock.html')
@app.route('/tool/builder')
@app.route('/tool/store-builder')
def builder(): return render_template('builder.html')
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
@app.route('/tool/market-ledger')
def market_ledger(): return render_template('market_ledger.html')
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
def whatsapp_broadcast(): return render_template('whatsapp_broadcast.html')
@app.route('/tool/background-check')
@app.route('/tool/usa-background-check')
@app.route('/tool/background_check')
def background_check(): return render_template('usa_background_check.html')
# SAUDI
@app.route('/tool/iqama-expiry')
def iqama_expiry(): return render_template('iqama_expiry.html')
@app.route('/tool/hijri-converter')
def hijri_converter(): return render_template('hijri_converter.html')
@app.route('/tool/gosi-calculator')
def gosi_calculator(): return render_template('gosi_calculator.html')
@app.route('/tool/zatca-qr')
def zatca_qr(): return render_template('zatca_qr.html')
@app.route('/tool/gpa-calculator')
def gpa_calculator(): return render_template('gpa_calculator.html')
@app.route('/tool/salary-sa')
def salary_sa(): return render_template('salary_sa.html')
# NG 9
@app.route('/tool/nepa-calculator')
def nepa_calculator(): return render_template('nepa_calculator.html')
@app.route('/tool/cac-checker')
def cac_checker(): return render_template('cac_checker.html')
@app.route('/tool/fuel-calculator')
def fuel_calculator(): return render_template('fuel_calculator.html')
@app.route('/tool/rent-splitter')
def rent_splitter(): return render_template('rent_splitter.html')
@app.route('/tool/land-converter')
def land_converter(): return render_template('land_converter.html')
@app.route('/tool/paye-calculator')
def paye_calculator(): return render_template('paye_calculator.html')
@app.route('/tool/jamb-calculator')
def jamb_calculator(): return render_template('jamb_calculator.html')
@app.route('/tool/waec-calculator')
def waec_calculator(): return render_template('waec_calculator.html')
@app.route('/tool/nin-validator')
def nin_validator(): return render_template('nin_validator.html')
# QATAR 6
@app.route('/tool/qid-check')
def qid_check(): return render_template('qid_check.html')
@app.route('/tool/qatar-traffic-fines')
def qatar_traffic_fines(): return render_template('qatar_traffic_fines.html')
@app.route('/tool/qatar-gratuity')
def qatar_gratuity(): return render_template('qatar_gratuity.html')
@app.route('/tool/qatar-rent-splitter')
def qatar_rent_splitter(): return render_template('qatar_rent_splitter.html')
@app.route('/tool/qatar-gold-price')
def qatar_gold_price(): return render_template('qatar_gold_price.html')
@app.route('/tool/qatar-overtime')
def qatar_overtime(): return render_template('qatar_overtime.html')
# UAE 7
@app.route('/tool/emirates-id-check')
def emirates_id_check(): return render_template('emirates_id_check.html')
@app.route('/tool/uae-traffic-fines')
def uae_traffic_fines(): return render_template('uae_traffic_fines.html')
@app.route('/tool/uae-gratuity')
def uae_gratuity(): return render_template('uae_gratuity.html')
@app.route('/tool/uae-gold-price')
def uae_gold_price(): return render_template('uae_gold_price.html')
@app.route('/tool/uae-rent-splitter')
def uae_rent_splitter(): return render_template('uae_rent_splitter.html')
@app.route('/tool/uae-overtime')
def uae_overtime(): return render_template('uae_overtime.html')
@app.route('/tool/uae-salary')
def uae_salary(): return render_template('uae_salary.html')
# KUWAIT 6
@app.route('/tool/kuwait-civil-id')
def kuwait_civil_id(): return render_template('kuwait_civil_id.html')
@app.route('/tool/kuwait-traffic-fines')
def kuwait_traffic_fines(): return render_template('kuwait_traffic_fines.html')
@app.route('/tool/kuwait-gratuity')
def kuwait_gratuity(): return render_template('kuwait_gratuity.html')
@app.route('/tool/kuwait-gold-price')
def kuwait_gold_price(): return render_template('kuwait_gold_price.html')
@app.route('/tool/kuwait-rent')
def kuwait_rent(): return render_template('kuwait_rent.html')
@app.route('/tool/kuwait-overtime')
def kuwait_overtime(): return render_template('kuwait_overtime.html')

@app.route('/sitemap.xml')
def sitemap():
    tools = ['nepa-calculator','cac-checker','fuel-calculator','rent-splitter','land-converter','paye-calculator','jamb-calculator','waec-calculator','nin-validator','qid-check','qatar-traffic-fines','qatar-gratuity','qatar-rent-splitter','qatar-gold-price','qatar-overtime','emirates-id-check','uae-traffic-fines','uae-gratuity','uae-gold-price','uae-rent-splitter','uae-overtime','uae-salary','kuwait-civil-id','kuwait-traffic-fines','kuwait-gratuity','kuwait-gold-price','kuwait-rent','kuwait-overtime','builder','wa-qr','invoice','bg-remover','pos-charges','delivery-fee','price-tag','profit-calc','debt-book','ruler-terminal','clear-shell','market-ledger','usa-notify','gamer-tag','sensitivity','clan-logo','tournament','paycheck','fake-text','tip-calculator','whatsapp-broadcast','background-check','iqama-expiry','hijri-converter','gosi-calculator','zatca-qr','gpa-calculator','salary-sa']
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += '<url><loc>https://clearcodesystem.onrender.com/</loc><priority>1.0</priority></url>'
    for t in tools:
        xml += f'<url><loc>https://clearcodesystem.onrender.com/tool/{t}</loc><priority>0.8</priority></url>'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    txt = "User-agent: *\nAllow: /\nDisallow: /unlock\nDisallow: /api/\nSitemap: https://clearcodesystem.onrender.com/sitemap.xml"
    return Response(txt, mimetype='text/plain')

@app.route('/api/qr', methods=['POST'])
def gen_qr():
    try:
        data = request.json.get('text','').strip()
        if not data: return jsonify({'error': 'Empty text'}), 400
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
        if not file: return jsonify({'error': 'No image uploaded'}), 400
        mode = request.form.get('mode', 'human')
        if not get_session(mode): return jsonify({'error': 'AI loading, try again in 10s'}), 503
        from rembg import remove
        input_img = Image.open(file.stream).convert('RGBA')
        if mode == 'human' and human_session and human_session!= True:
            output = remove(input_img, session=human_session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10)
        elif cloth_session and cloth_session!= True:
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
    outs = {'help':'help, clear, ls, pwd, date, echo, whoami, neofetch, hack, matrix, banner, vendors, free, df, uptime','ls':'qid_check.html qatar_gratuity.html uae_gratuity.html emirates_id_check.html kuwait_civil_id.html','pwd':'/home/clearcode/vendors','whoami':'clearcode-vendor','date':datetime.now().strftime('%a %b %d %H:%M:%S WAT %Y'),'clear':'__CLEAR__'}
    if cmd.startswith('echo '): return jsonify({'output': cmd[5:]})
    if cmd == '': return jsonify({'output': ''})
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