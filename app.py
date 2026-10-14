import os
from flask import Flask, render_template, request, abort, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clearcode-admin-2026-change-me")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "CLEARCODE2026")

def n(s):
    return s.lower().replace('.html','').strip()

def pretty(s):
    return s.replace('_',' ').title()

def icon_for(t):
    t = t.lower()
    if "bank" in t or "card" in t: return "💳"
    if "bg_remover" in t: return "🖼"
    if "builder" in t: return "🛠"
    if "cac" in t: return "🏢"
    if "logo" in t: return "🎨"
    if "debt" in t or "ledger" in t: return "📒"
    if "delivery" in t or "fee" in t: return "🛵"
    if "fake" in t and "whatsapp" in t: return "💬"
    if "fake" in t: return "😜"
    if "fuel" in t: return "⛽"
    if "gamer" in t: return "🎮"
    if "gpa" in t or "jamb" in t or "waec" in t: return "🎓"
    if "invoice" in t: return "🧾"
    if "ivr" in t: return "📞"
    if "rent" in t: return "🏠"
    if "land" in t: return "📐"
    if "market" in t: return "📈"
    if "nepa" in t: return "💡"
    if "nin" in t: return "🪪"
    if "paycheck" in t or "salary" in t or "paye" in t: return "💰"
    if "pos" in t: return "💵"
    if "price" in t or "profit" in t: return "🏷"
    if "ruler" in t: return "📏"
    if "sleep" in t: return "😴"
    if "tip" in t: return "💸"
    if "tournament" in t: return "🏆"
    if "unlock" in t: return "🔓"
    if "qr" in t: return "🔳"
    if "gold" in t: return "🪙"
    if "traffic" in t: return "🚦"
    if "cpr" in t or "id" in t or "civil" in t or "iqama" in t: return "🪪"
    if "gratuity" in t or "overtime" in t: return "💼"
    if "arabic" in t or "hijri" in t: return "🕌"
    if "vat" in t: return "🧮"
    if "background" in t: return "🔍"
    return "🔧"

ng = ["builder","cac_checker","clan_logo","clear_shell","debt_book","delivery_fee","fake_excuse_generator","fake_text","fake_whatsapp_chat","fuel_calculator","gamer_tag","gpa_calculator","invoice","ivr_builder","ivr_software","jamb_calculator","lagos_rent_package","land_converter","market_ledger","marketwatch_demo","nepa_calculator","nin_validator","paycheck","paye_calculator","pos_charges","pos_receipt","price_tag","profit_calculator","rent_splitter","ruler_terminal","salary_flex","sensitivity","sleep_calculator","tip_calculator","tournament","unlock","bank_card_info","wa_qr","waec_calculator","whatsapp_broadcast"]
gulf = ["arabic_stylish_name","bahrain_cpr_check","bahrain_gold_price","bahrain_gratuity","bahrain_overtime","bahrain_rent","bahrain_traffic_fines","emirates_id_check","gosi_calculator","hijri_converter","iqama_expiry","kuwait_traffic_fines","oman_civil_check","oman_gold_price","oman_gratuity","oman_overtime","oman_rent","oman_traffic_fines","qatar_gold_price","qatar_overtime","qatar_rent_splitter","salary_sa","uae_gold_price","uae_gratuity","uae_overtime","uae_rent_splitter","uae_salary","uae_traffic_fines","zatca_qr"]
uk = ["uk_paycheck","uk_rent_splitter","uk_tip_calculator","uk_vat_calculator"]
us = ["usa_background_check","usa_notify"]
global_tools = ["bg_remover","data_to_earn"]

def get_country():
    c = request.headers.get('CF-IPCountry')
    if c: return c.upper()
    c = request.headers.get('X-Country-Code')
    if c: return c.upper()
    return 'NG'

@app.route('/')
def index():
    country = get_country()
    folder = os.path.join(app.root_path, 'templates')
    try:
        files = [f for f in os.listdir(folder) if f.endswith('.html') and f.lower() not in ['base.html', 'index.html']]
    except:
        files = []
    filtered = []
    for f in files:
        orig = f[:-5]
        low = n(f)
        if low in global_tools:
            filtered.append(orig)
        elif country == 'NG' and low in ng:
            filtered.append(orig)
        elif country in ['BH','SA','AE','QA','KW','OM'] and low in gulf:
            filtered.append(orig)
        elif country in ['GB','UK'] and low in uk:
            filtered.append(orig)
        elif country == 'US' and low in us:
            filtered.append(orig)
        elif country == 'NG':
            filtered.append(orig)
    tools = [{"name": pretty(t), "url": f"/{t}", "icon": icon_for(t)} for t in sorted(filtered)]
    return render_template('index.html', tools=tools, user_country=country)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('key') == ADMIN_KEY:
            session['is_admin'] = True
            return redirect(url_for('admin_tools'))
        return "<h3>Wrong Admin Key</h3><a href='/admin/login'>Try again</a>", 403
    return '''
    <div style="max-width:400px;margin:100px auto;font-family:sans-serif;padding:20px;border:1px solid #ccc;border-radius:10px;">
    <h2>ClearCode Admin</h2>
    <form method="POST">
    <input type="password" name="key" placeholder="Enter Admin Key" style="width:100%;padding:12px;box-sizing:border-box;" required>
    <button type="submit" style="width:100%;padding:12px;margin-top:10px;background:black;color:white;border:0;border-radius:5px;">Login</button>
    </form></div>
    '''

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin-tools')
def admin_tools():
    if not session.get('is_admin'):
        abort(404)
    folder = os.path.join(app.root_path, 'templates')
    files = [f for f in os.listdir(folder) if f.endswith('.html') and f.lower() != 'base.html']
    tools = [{"name": pretty(f[:-5]), "url": f"/{f[:-5]}", "icon": icon_for(f[:-5])} for f in sorted(files)]
    return render_template('index.html', tools=tools, user_country=f"ADMIN {len(tools)}")

@app.route('/health')
def health():
    return "OK"

@app.route('/<tool_name>')
def page(tool_name):
    folder = os.path.join(app.root_path, 'templates')
    try:
        allowed = [f[:-5] for f in os.listdir(folder) if f.endswith('.html') and f.lower() not in ['base.html', 'index.html']]
    except:
        allowed = []
    if tool_name not in allowed:
        abort(404)
    return render_template(f'{tool_name}.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
