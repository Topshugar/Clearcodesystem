import os
from flask import Flask, render_template, request, abort

app = Flask(__name__)
ADMIN_KEY = "CLEARCODE2026"

def n(s):
    return s.lower().replace('.html','').strip()

ng = ["builder","cac_checker","clan_logo","clear_shell","debt_book","delivery_fee","fake_excuse_generator","fake_text","fake_whatsapp_chat","fuel_calculator","gamer_tag","gpa_calculator","invoice","ivr_builder","ivr_software","jamb_calculator","lagos_rent_package","land_converter","market_ledger","marketwatch_demo","nepa_calculator","nin_validator","paycheck","paye_calculator","pos_charges","pos_receipt","price_tag","profit_calculator","rent_splitter","ruler_terminal","salary_flex","sensitivity","sleep_calculator","tip_calculator","tournament","unlock","bank_card_info","wa_qr","waec_calculator","whatsapp_broadcast"]
gulf = ["arabic_stylish_name","bahrain_cpr_check","bahrain_gold_price","bahrain_gratuity","bahrain_overtime","bahrain_rent","bahrain_traffic_fines","emirates_id_check","gosi_calculator","hijri_converter","iqama_expiry","kuwait_traffic_fines","oman_civil_check","oman_gold_price","oman_gratuity","oman_overtime","oman_rent","oman_traffic_fines","qatar_gold_price","qatar_overtime","qatar_rent_splitter","salary_sa","uae_gold_price","uae_gratuity","uae_overtime","uae_rent_splitter","uae_salary","uae_traffic_fines","zatca_qr"]
uk = ["uk_paycheck","uk_rent_splitter","uk_tip_calculator","uk_vat_calculator"]
us = ["usa_background_check","usa_notify"]
global_tools = ["bg_remover"]

def get_country():
    c = request.headers.get('CF-IPCountry')
    if c:
        return c.upper()
    c = request.headers.get('X-Country-Code')
    if c:
        return c.upper()
    return 'NG'

@app.route('/')
def index():
    country = get_country()
    folder = os.path.join(app.root_path, 'templates')
    files = [f for f in os.listdir(folder) if f.endswith('.html') and f.lower() not in ['base.html', 'index.html']]
    
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

    tools = [{"name": t, "url": f"/{t}"} for t in sorted(filtered)]
    return render_template('index.html', tools=tools, user_country=country)

@app.route('/admin-tools')
def admin_tools():
    if request.args.get('key') != ADMIN_KEY:
        abort(403)
    folder = os.path.join(app.root_path, 'templates')
    files = [f for f in os.listdir(folder) if f.endswith('.html') and f.lower() != 'base.html']
    tools = [{"name": f[:-5], "url": f"/{f[:-5]}"} for f in sorted(files)]
    return render_template('index.html', tools=tools, user_country=f"ADMIN {len(tools)}")

@app.route('/health')
def health():
    return "OK"

@app.route('/<tool_name>')
def page(tool_name):
    try:
        return render_template(f'{tool_name}.html')
    except:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)