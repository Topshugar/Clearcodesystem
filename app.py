import os
from flask import Flask, render_template, request, abort, session, redirect, url_for, Response

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
ADMIN_KEY = os.environ.get("ADMIN_KEY")

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
    cf = request.headers.get('CF-IPCountry')
    if cf and len(cf) == 2:
        return cf.upper()
    cc = request.headers.get('X-Country-Code')
    if cc and len(cc) == 2 and request.headers.get('CF-Ray'):
        return cc.upper()
    return 'NG'

def get_tools_for_country(country):
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
    return filtered

@app.route('/robots.txt')
def robots():
    txt = """User-agent: *
Allow: /
Sitemap: https://clearcode.system/sitemap.xml
"""
    return Response(txt, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    domain = "https://clearcode.system"
    folder = os.path.join(app.root_path, 'templates')
    try:
        files = [f for f in os.listdir(folder) if f.endswith('.html') and f.lower() not in ['base.html', 'index.html']]
    except:
        files = []
    urls = [f"{domain}/"]
    for f in files:
        urls.append(f"{domain}/{f[:-5]}")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        xml += f"  <url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n"
    xml += "</urlset>"
    return Response(xml, mimetype='application/xml')

@app.route('/')
def index():
    country = get_country()
    tools_list = get_tools_for_country(country)
    tools = [{"name": pretty(t), "url": f"/{t}", "icon": icon_for(t), "desc": f"{pretty(t)} - Free online {pretty(t)} tool"} for t in sorted(tools_list)]
    return render_template('index.html', tools=tools, user_country=country)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if ADMIN_KEY and request.form.get('key') == ADMIN_KEY:
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
    country = get_country()
    folder = os.path.join(app.root_path, 'templates')
    try:
        allowed_all = [f[:-5] for f in os.listdir(folder) if f.endswith('.html') and f.lower() not in ['base.html', 'index.html']]
    except:
        allowed_all = []
    if tool_name not in allowed_all:
        abort(404)
    allowed_for_ip = get_tools_for_country(country)
    if tool_name not in allowed_for_ip and tool_name not in global_tools:
        if not session.get('is_admin'):
            abort(404)
    seo_title = f"{pretty(tool_name)} - Free Online Tool | ClearCode System"
    seo_desc = f"Use {pretty(tool_name)} free online. Fast, secure, no signup needed at ClearCode System."
    return render_template(f'{tool_name}.html', seo_title=seo_title, seo_desc=seo_desc)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
