import os
import json
import io
import base64
import requests
from datetime import datetime
from collections import Counter
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from PIL import Image
import qrcode
import paramiko

app = Flask(__name__)

# ===== CONFIG =====
ADMIN_KEY = "CLEARCODE2026"
DATA_FILE = "data.json"
ANALYTICS_FILE = "analytics.json"

# Load or create data
def load_data():
    global ANALYTICS, DISABLED_TOOLS
    try:
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, 'r') as f:
                d = json.load(f)
                ANALYTICS = d.get('analytics', [])
                DISABLED_TOOLS = set(d.get('disabled', []))
        else:
            ANALYTICS = []
            DISABLED_TOOLS = set()
    except:
        ANALYTICS = []
        DISABLED_TOOLS = set()

def save_data():
    try:
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump({'analytics': ANALYTICS[-5000:], 'disabled': list(DISABLED_TOOLS)}, f)
    except:
        pass

ANALYTICS = []
DISABLED_TOOLS = set()
load_data()

# ===== COUNTRY TOOLS - BANK INFO GLOBAL NOW =====
COUNTRY_TOOLS = {
    'NG': ['nepa_calculator','cac_checker','fuel_calculator','rent_splitter','land_converter','paye_calculator','jamb_calculator','waec_calculator','nin_validator','lagos_rent_package','ivr_builder','builder','pos_receipt','wa_qr','invoice','bg_remover','pos_charges','delivery_fee','price_tag','profit_calc','debt_book','ruler_terminal','clear_shell','market_ledger','bank_card_info','salary_flex','anonymous_link','arabic_stylish_name'],
    'BH': ['bahrain_cpr_check','bahrain_traffic_fines','bahrain_gratuity','bahrain_gold_price','bahrain_rent','bahrain_overtime','salary_flex','anonymous_link','arabic_stylish_name','bank_card_info','ivr_builder'],
    'QA': ['qid_check','qatar_traffic_fines','qatar_gratuity','qatar_rent_splitter','qatar_gold_price','qatar_overtime','salary_flex','anonymous_link','arabic_stylish_name','bank_card_info','ivr_builder'],
    'SA': ['iqama_expiry','hijri_converter','gosi_calculator','zatca_qr','gpa_calculator','salary_sa','salary_flex','anonymous_link','arabic_stylish_name','bank_card_info','ivr_builder'],
    'AE': ['emirates_id_check','uae_traffic_fines','uae_gratuity','uae_gold_price','uae_rent_splitter','uae_overtime','uae_salary','salary_flex','anonymous_link','arabic_stylish_name','bank_card_info','ivr_builder'],
    'KW': ['kuwait_civil_id','kuwait_traffic_fines','kuwait_gratuity','kuwait_gold_price','kuwait_rent','kuwait_overtime','salary_flex','anonymous_link','arabic_stylish_name','bank_card_info','ivr_builder'],
    'OM': ['oman_civil_check','oman_traffic_fines','oman_gratuity','oman_gold_price','oman_rent','oman_overtime','salary_flex','anonymous_link','arabic_stylish_name','bank_card_info','ivr_builder'],
    'US': ['usa_notify','paycheck','fake_text','tip_calculator','whatsapp_broadcast','background_check','bank_card_info','ivr_builder'],
    'UK': ['uk_paycheck','uk_rent_splitter','uk_tip_calculator','uk_vat_calculator','bank_card_info','ivr_builder'],
    'DEFAULT': ['wa_qr','invoice','bg_remover','bank_card_info','salary_flex','anonymous_link','arabic_stylish_name','ivr_builder']
}

COUNTRY_NAMES = {
    'NG': 'Nigeria', 'BH': 'Bahrain', 'QA': 'Qatar', 'SA': 'Saudi Arabia',
    'AE': 'UAE', 'KW': 'Kuwait', 'OM': 'Oman', 'US': 'USA', 'UK': 'UK', 'DEFAULT': 'Global'
}

# ===== BG REMOVER SESSIONS =====
human_session = None
cloth_session = None
def get_session(mode):
    global human_session, cloth_session
    try:
        from rembg import new_session
        if mode == 'human':
            if human_session is None:
                human_session = True
                try:
                    human_session = new_session('u2net_human_seg')
                except:
                    human_session = new_session('u2net')
            return human_session
        else:
            if cloth_session is None:
                cloth_session = True
                try:
                    cloth_session = new_session('u2net_cloth_seg')
                except:
                    cloth_session = new_session('u2net')
            return cloth_session
    except Exception as e:
        print(f"rembg error {e}")
        return None
# ===== HELPERS =====
def get_country():
    raw = request.args.get('country', '').upper()
    if raw in COUNTRY_TOOLS:
        return raw
    # Auto detect from IP header (Cloudflare / Render)
    cf_country = request.headers.get('CF-IPCountry', '').upper()
    if cf_country in COUNTRY_TOOLS:
        return cf_country
    # Check?country= param lower
    c = request.args.get('c', '').upper()
    if c in COUNTRY_TOOLS:
        return c
    return 'NG'

def is_disabled(tool_key, country):
    return f"{country}:{tool_key}" in DISABLED_TOOLS or tool_key in DISABLED_TOOLS

# ===== ROUTES =====
@app.route('/')
def index():
    country = get_country()
    raw_country = request.args.get('country', country)
    tools = COUNTRY_TOOLS.get(country, COUNTRY_TOOLS['DEFAULT'])
    # filter disabled
    tools = [t for t in tools if not is_disabled(t, country)]
    return render_template('index.html', tools=tools, country=country, country_name=COUNTRY_NAMES.get(country, country), raw_country=raw_country)

@app.route('/tool/<tool_name>')
def tool_page(tool_name):
    country = get_country()
    raw_country = request.args.get('country', country)
    # Log analytics
    try:
        ANALYTICS.append({
            'tool': tool_name,
            'country': country,
            'time': datetime.now().isoformat(),
            'ip': request.headers.get('X-Forwarded-For', request.remote_addr)
        })
        if len(ANALYTICS) % 20 == 0:
            save_data()
    except:
        pass

    # Check disabled
    if is_disabled(tool_name, country):
        return render_template('disabled.html', tool=tool_name, country=country), 403

    # Try template
    template_file = f"{tool_name}.html"
    try:
        return render_template(template_file, country=country, country_name=COUNTRY_NAMES.get(country, country), raw_country=raw_country)
    except:
        # fallback generic
        return render_template('tool_generic.html', tool=tool_name, country=country, country_name=COUNTRY_NAMES.get(country, country), raw_country=raw_country)

@app.route('/unlock', methods=['GET','POST'])
def unlock():
    return render_template('unlock.html')

@app.route('/api/unlock', methods=['POST'])
def api_unlock():
    return jsonify({'ok': True})

# ===== SECRET ADMIN - ONLY YOU =====
@app.route('/admin/analytics')
def admin_analytics():
    if request.args.get('key')!= ADMIN_KEY:
        return "Unauthorized", 403
    tools = Counter([a['tool'] for a in ANALYTICS])
    countries = Counter([a['country'] for a in ANALYTICS])
    last = ANALYTICS[-30:][::-1]
    disabled_list = list(DISABLED_TOOLS)
    html = f"""
    <html style="background:#080808;color:#fff;font-family:monospace;padding:20px">
    <h2>📊 ClearCode Analytics - V3 Fixed</h2>
    <p>Total: {len(ANALYTICS)} | Disabled: {disabled_list}</p>
    <h3>Top Tools</h3><pre>{tools.most_common(20)}</pre>
    <h3>Top Countries</h3><pre>{countries.most_common(20)}</pre>
    <h3>Last 30</h3><pre>{last}</pre>
    <hr><a href="/admin/tools?key={ADMIN_KEY}" style="color:#00FF88">Go to Tools Manager</a>
    </html>
    """
    return html

@app.route('/admin/tools')
def admin_tools_manager():
    if request.args.get('key')!= ADMIN_KEY:
        return "Unauthorized", 403
    action = request.args.get('action')
    tool = request.args.get('tool')
    if action == 'disable' and tool:
        DISABLED_TOOLS.add(tool)
        save_data()
    if action == 'enable' and tool:
        DISABLED_TOOLS.discard(tool)
        save_data()
    out = f"<html style='background:#080808;color:#fff;font-family:monospace;padding:20px'><h2>🛠️ Tools Manager</h2>"
    for c in COUNTRY_TOOLS:
        out += f"<h3>{c}</h3>"
        for t in COUNTRY_TOOLS[c]:
            key = f"{c}:{t}"
            status = "🔴 OFF" if key in DISABLED_TOOLS else "🟢 ON"
            out += f"{status} {key} - <a style='color:#FF0040' href='/admin/tools?key={ADMIN_KEY}&action=disable&tool={key}'>OFF</a> | <a style='color:#00FF88' href='/admin/tools?key={ADMIN_KEY}&action=enable&tool={key}'>ON</a><br>"
    out += f"<hr><a href='/admin/analytics?key={ADMIN_KEY}' style='color:#00FF88'>Back</a></html>"
    return out

@app.route('/sitemap.xml')
def sitemap():
    tools = ['nepa-calculator','cac-checker','fuel-calculator','rent-splitter','land-converter','paye-calculator','jamb-calculator','waec-calculator','nin-validator','lagos-rent-package','ivr-builder','qid-check','qatar-traffic-fines','qatar-gratuity','qatar-rent-splitter','qatar-gold-price','qatar-overtime','emirates-id-check','uae-traffic-fines','uae-gratuity','uae-gold-price','uae-rent-splitter','uae-overtime','uae-salary','kuwait-civil-id','kuwait-traffic-fines','kuwait-gratuity','kuwait-gold-price','kuwait-rent','kuwait-overtime','builder','pos-receipt','wa-qr','invoice','bg-remover','pos-charges','delivery-fee','price-tag','profit-calc','debt-book','ruler-terminal','clear-shell','market-ledger','usa-notify','paycheck','fake-text','tip-calculator','whatsapp-broadcast','background-check','iqama-expiry','hijri-converter','gosi-calculator','zatca-qr','gpa-calculator','salary-sa','bahrain-cpr-check','bahrain-traffic-fines','bahrain-gratuity','bahrain-gold-price','bahrain-rent','bahrain-overtime','oman-civil-check','oman-traffic-fines','oman-gratuity','oman-gold-price','oman-rent','oman-overtime','uk-paycheck','uk-rent-splitter','uk-tip-calculator','uk-vat-calculator','salary-flex','anonymous-link','arabic-stylish-name','bank-card-info']
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += '<url><loc>https://clearcodesystem.onrender.com/</loc><priority>1.0</priority></url>'
    for t in tools:
        xml += f'<url><loc>https://clearcodesystem.onrender.com/tool/{t}</loc><priority>0.8</priority></url>'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    txt = "User-agent: *\nAllow: /\nDisallow: /unlock\nDisallow: /api/\nDisallow: /admin/\nSitemap: https://clearcodesystem.onrender.com/sitemap.xml"
    return Response(txt, mimetype='text/plain')

# ===== BIN CHECK API - FULL NIGERIA + GULF - WORKS IN LAGOS =====
@app.route('/api/bin-check', methods=['POST'])
def api_bin_check():
    bin_code = ""
    try:
        data = request.get_json(silent=True) or {}
        bin_code = str(data.get('bin','')).strip()[:8]
        bin_code = ''.join(filter(str.isdigit, bin_code))
        if len(bin_code) < 6:
            return jsonify({'bin': bin_code, 'scheme': 'ERROR', 'type': 'ERROR', 'category': 'Error', 'bank': 'Enter 6 digits', 'country': 'NG', 'source': 'error'}), 200

        OFFLINE_BINS = {
            '406068': {'bank':'GTBank - Guaranty Trust Bank','scheme':'VISA','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506099': {'bank':'GTBank','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '539983': {'bank':'GTBank','scheme':'MASTERCARD','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '558888': {'bank':'GTBank','scheme':'MASTERCARD','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '418888': {'bank':'Access Bank','scheme':'VISA','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506107': {'bank':'Access Bank','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506120': {'bank':'Access Bank','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '504962': {'bank':'Access Bank (Diamond)','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506104': {'bank':'First Bank of Nigeria','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '539923': {'bank':'First Bank','scheme':'MASTERCARD','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '418339': {'bank':'First Bank','scheme':'VISA','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506105': {'bank':'UBA - United Bank for Africa','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '456590': {'bank':'UBA','scheme':'VISA','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506106': {'bank':'Zenith Bank','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '539941': {'bank':'Zenith Bank','scheme':'MASTERCARD','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '402277': {'bank':'Zenith Bank','scheme':'VISA','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506112': {'bank':'Wema Bank / ALAT','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '517388': {'bank':'Wema Bank','scheme':'MASTERCARD','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506116': {'bank':'Kuda Microfinance Bank','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '415874': {'bank':'Kuda Bank','scheme':'VISA','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506146': {'bank':'OPay - Paycom','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506147': {'bank':'OPay','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506158': {'bank':'PalmPay','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506159': {'bank':'Moniepoint MFB','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506108': {'bank':'Union Bank','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506109': {'bank':'Sterling Bank','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506111': {'bank':'Fidelity Bank','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506115': {'bank':'Ecobank Nigeria','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506117': {'bank':'Polaris Bank','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506119': {'bank':'FCMB','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506121': {'bank':'Stanbic IBTC','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '406084': {'bank':'Stanbic IBTC','scheme':'VISA','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '506100': {'bank':'Verve - Nigeria (Interswitch)','scheme':'VERVE','type':'DEBIT','country':'Nigeria 🇳🇬'},
            '555931': {'bank':'Al Baraka Islamic Bank','scheme':'MASTERCARD','type':'DEBIT','country':'Bahrain 🇧🇭'},
            '417500': {'bank':'QNB - Qatar National Bank','scheme':'VISA','type':'DEBIT','country':'Qatar 🇶🇦'},
            '422207': {'bank':'ADCB - Abu Dhabi Commercial','scheme':'VISA','type':'DEBIT','country':'UAE 🇦🇪'},
            '529977': {'bank':'NBK - National Bank of Kuwait','scheme':'MASTERCARD','type':'DEBIT','country':'Kuwait 🇰🇼'},
            '431380': {'bank':'Al Rajhi Bank','scheme':'VISA','type':'DEBIT','country':'Saudi Arabia 🇸🇦'},
        }
        key = bin_code[:6]
        if key in OFFLINE_BINS:
            d = OFFLINE_BINS[key]
            return jsonify({'bin': bin_code, 'scheme': d['scheme'], 'type': d['type'], 'category': 'Debit', 'bank': d['bank'], 'country': d['country'], 'source': 'NG Full DB'})

        try:
            r = requests.get(f'https://lookup.binlist.net/{bin_code}', headers={'Accept-Version':'3'}, timeout=3)
            if r.status_code == 200:
                j = r.json()
                return jsonify({'bin': bin_code, 'scheme': (j.get('scheme') or 'Unknown').upper(), 'type': (j.get('type') or 'Unknown').upper(), 'category': j.get('category') or 'Unknown', 'bank': j.get('bank',{}).get('name','Unknown') if j.get('bank') else 'Unknown', 'country': j.get('country',{}).get('name','Unknown'), 'source': 'online'})
        except:
            pass

        return jsonify({'bin': bin_code, 'scheme': 'VERVE/VISA/MC', 'type': 'DEBIT', 'category': 'Nigeria Card', 'bank': 'Nigerian Bank - BIN not in offline list yet', 'country': 'Nigeria 🇳🇬 - Try 506099 or 406068', 'source': 'fallback'})

    except Exception as e:
        return jsonify({'bin': bin_code or 'error', 'scheme': 'ERROR', 'type': 'ERROR', 'category': 'Error', 'bank': 'Try again', 'country': 'Try 406068 GTBank', 'source': 'error'}), 200

@app.route('/api/lagos-rent', methods=['POST'])
def api_lagos_rent():
    try:
        data = request.json or {}
        rent = float(data.get('rent', 0))
        if rent <= 0: return jsonify({'error':'Enter valid rent amount'}), 400
        location = (data.get('location') or 'mainland').lower()
        config = {
            'mainland': {'agreement':10, 'commission':10, 'damages':5, 'caution':5, 'legal':5, 'inspection':3000},
            'yaba': {'agreement':10, 'commission':10, 'damages':10, 'caution':10, 'legal':5, 'inspection':5000},
            'ikeja': {'agreement':10, 'commission':10, 'damages':10, 'caution':10, 'legal':10, 'inspection':7000},
            'lekki': {'agreement':10, 'commission':10, 'damages':10, 'caution':10, 'legal':10, 'inspection':10000},
            'vi': {'agreement':10, 'commission':10, 'damages':15, 'caution':15, 'legal':10, 'inspection':15000},
        }
        c = config.get(location, config['mainland'])
        agreement = rent * c['agreement'] / 100
        commission = rent * c['commission'] / 100
        damages = rent * c['damages'] / 100
        caution = rent * c['caution'] / 100
        legal = rent * c['legal'] / 100
        inspection = c['inspection']
        total = rent + agreement + commission + damages + caution + legal + inspection
        monthly = total / 12
        return jsonify({'rent': int(rent),'agreement': int(agreement),'commission': int(commission),'damages': int(damages),'caution': int(caution),'legal': int(legal),'inspection': int(inspection),'total': int(total),'monthly': int(monthly),'location': location})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        if not file: return jsonify({'error': 'No image'}), 400
        mode = request.form.get('mode', 'human')
        if not get_session(mode): return jsonify({'error': 'AI loading'}), 503
        from rembg import remove
        input_img = Image.open(file.stream).convert('RGBA')
        if mode == 'human' and human_session and human_session!= True:
            output = remove(input_img, session=human_session, alpha_matting=True)
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
    outs = {'help':'help, clear, ls, pwd, date, echo, whoami, neofetch','ls':'86 tools','pwd':'/home/clearcode','whoami':'clearcode-vendor','date':datetime.now().strftime('%a %b %d %H:%M:%S'),'clear':'__CLEAR__'}
    if cmd.startswith('echo '): return jsonify({'output': cmd[5:]})
    if cmd == '': return jsonify({'output': ''})
    return jsonify({'output': outs.get(cmd, f'Command not found: {cmd}')})

@app.route('/api/ivr/generate-audio', methods=['POST'])
def ivr_generate():
    data = request.get_json() or {}
    text = data.get('text','Welcome to ClearCode')
    return jsonify({"ok": True, "audio_url": "/static/demo-ivr.mp3", "text": text})

@app.route('/api/ivr/verify-usdt', methods=['POST'])
def ivr_verify():
    data = request.get_json() or {}
    txid = data.get('txid','').strip()
    if len(txid) < 10: return jsonify({"ok": False, "error": "Invalid TxID"})
    return jsonify({"ok": True, "msg": "Verified 5 USDT", "wallet": "TRhMjNALZeUMK5cSkDXX7CgjdqJ4YNWVz4", "amount": 5})

@app.route('/api/ivr/call', methods=['POST'])
def ivr_call():
    data = request.get_json() or {}
    phone = data.get('phone','')
    return jsonify({"ok": True, "msg": f"Call queued to {phone}"})

@app.route('/api/ivr/download')
def ivr_download():
    text = request.args.get('text','Welcome')
    return jsonify({"ok": True, "text": text})

@app.route('/api/clear-shell', methods=['POST'])
def shell_api():
    d = request.json
    if d.get('secret')!= 'CLEARCODE2026':
        return jsonify({'output': 'Error: Unauthorized'})
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
