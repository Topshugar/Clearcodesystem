import os, io, requests
from flask import Flask, render_template, request, jsonify, send_file, abort
from PIL import Image

app = Flask(__name__)
ADMIN_KEY = "CLEARCODE2026"

def get_user_country():
    test = request.args.get('test')
    key = request.args.get('key')
    if test and key == ADMIN_KEY:
        return test.upper()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or "")
    if ',' in ip: ip = ip.split(',')[0].strip()
    try:
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        c = r.text.strip().upper()
        if len(c)==2 and c.isalpha(): return c
    except: pass
    return "NG"

TOOL_COUNTRY = {
    # NG ONLY - Will NEVER show in Gulf
    "Builder":"NG", "Cac_Checker":"NG", "Clan_Logo":"NG", "Clear_Shell":"NG", "Debt_Book":"NG",
    "Delivery_Fee":"NG", "Fake_Excuse_Generator":"NG", "Fake_Text":"NG", "Fake_Whatsapp_Chat":"NG",
    "Fuel_Calculator":"NG", "Gamer_Tag":"NG", "Gpa_Calculator":"NG", "Invoice":"NG", "Ivr_Builder":"NG",
    "Ivr_Software":"NG", "Jamb_Calculator":"NG", "Lagos_Rent_Package":"NG", "Land_Converter":"NG",
    "Market_Ledger":"NG", "Marketwatch_Demo":"NG", "Nepa_Calculator":"NG", "Nin_Validator":"NG",
    "Paycheck":"NG", "Paye_Calculator":"NG", "Pos_Charges":"NG", "Pos_Receipt":"NG", "Price_Tag":"NG",
    "Profit_Calculator":"NG", "Rent_Splitter":"NG", "Ruler_Terminal":"NG", "Salary_Flex":"NG",
    "Sensitivity":"NG", "Sleep_Calculator":"NG", "Tip_Calculator":"NG", "Tournament":"NG", "Unlock":"NG",
    "Bank_Card_Info":"NG", "Wa_Qr":"NG", "Waec_Calculator":"NG", "Whatsapp_Broadcast":"NG",
    "Paycheck":"NG", "Fuel_Calculator":"NG",
    # GULF ONLY - Will NEVER show in NG
    "Arabic_Stylish_Name":"BH,SA,AE,QA,KW,OM", "Bahrain_Cpr_Check":"BH", "Bahrain_Gold_Price":"BH",
    "Bahrain_Gratuity":"BH", "Bahrain_Overtime":"BH", "Bahrain_Rent":"BH", "Bahrain_Traffic_Fines":"BH",
    "Emirates_Id_Check":"AE", "Gosi_Calculator":"SA", "Hijri_Converter":"SA,AE,BH,QA,KW,OM",
    "Iqama_Expiry":"SA", "Kuwait_Traffic_Fines":"KW", "Oman_Civil_Check":"OM", "Oman_Gold_Price":"OM",
    "Oman_Gratuity":"OM", "Oman_Overtime":"OM", "Oman_Rent":"OM", "Oman_Traffic_Fines":"OM",
    "Qatar_Gold_Price":"QA", "Qatar_Overtime":"QA", "Qatar_Rent_Splitter":"QA", "Salary_Sa":"SA",
    "Uae_Gold_Price":"AE", "Uae_Gratuity":"AE", "Uae_Overtime":"AE", "Uae_Rent_Splitter":"AE",
    "Uae_Salary":"AE", "Uae_Traffic_Fines":"AE", "Zatca_Qr":"SA",
    # UK / USA ONLY
    "Uk_Paycheck":"UK", "Uk_Rent_Splitter":"UK", "Uk_Tip_Calculator":"UK", "Uk_Vat_Calculator":"UK",
    "Usa_Background_Check":"US", "Usa_Notify":"US",
    # GLOBAL
    "Bg_Remover":"ALL",
}

def load_tools():
    tools = []
    t_path = os.path.join(app.root_path, 'templates')
    for file in os.listdir(t_path):
        if not file.endswith('.html'): continue
        if file.lower() in ['base.html','index.html','coming_soon.html']: continue
        name = file.replace('.html','')
        country = TOOL_COUNTRY.get(name, "ALL")
        # Fallback detect if new file added
        if name not in TOOL_COUNTRY:
            low = name.lower()
            if 'bahrain' in low or 'emirates' in low or 'uae' in low or 'qatar' in low or 'oman' in low or 'kuwait' in low or 'saudi' in low or 'gosi' in low or 'iqama' in low: country = "BH,SA,AE,QA,KW,OM"
        tools.append({"name": name, "url": f"/{name}", "country": country})
    return sorted(tools, key=lambda x: x["name"])

def filter_tools(user_country):
    out = []
    for t in load_tools():
        c = t["country"]
        if c == "ALL" or user_country in c.split(','):
            out.append(t)
    return out

@app.route('/')
def index():
    country = get_user_country()
    return render_template('index.html', tools=filter_tools(country), user_country=country)
@app.route('/<tool_name>')
def tool_page(tool_name):
    try:
        return render_template(f'{tool_name}.html', user_country=get_user_country())
    except:
        abort(404)

@app.route('/api/remove-bg', methods=['POST'])
def remove_bg_api():
    try:
        from rembg import remove
        file = request.files.get('image')
        if not file: return jsonify({"error":"No image"}), 400
        img = Image.open(file.stream).convert("RGBA")
        buf = io.BytesIO()
        remove(img).save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin-tools')
def admin_tools():
    if request.args.get('key')!= ADMIN_KEY:
        abort(403)
    # ADMIN SEES ALL - No filter
    return render_template('index.html', tools=load_tools(), user_country="ADMIN")

@app.route('/test-ip')
def test_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    country = get_user_country()
    return jsonify({"ip": ip, "country": country, "filtered_count": len(filter_tools(country))})

if __name__ == '__main__':
    app.run(debug=True)