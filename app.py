import os
from flask import Flask, render_template, request, abort, jsonify
app = Flask(__name__)
ADMIN_KEY = "CLEARCODE2026"

NG_TOOLS = ["Builder","Cac_Checker","Clan_Logo","Clear_Shell","Debt_Book","Delivery_Fee","Fake_Excuse_Generator","Fake_Text","Fake_Whatsapp_Chat","Fuel_Calculator","Gamer_Tag","Gpa_Calculator","Invoice","Ivr_Builder","Ivr_Software","Jamb_Calculator","Lagos_Rent_Package","Land_Converter","Market_Ledger","Marketwatch_Demo","Nepa_Calculator","Nin_Validator","Paycheck","Paye_Calculator","Pos_Charges","Pos_Receipt","Price_Tag","Profit_Calculator","Rent_Splitter","Ruler_Terminal","Salary_Flex","Sensitivity","Sleep_Calculator","Tip_Calculator","Tournament","Unlock","Bank_Card_Info","Wa_Qr","Waec_Calculator","Whatsapp_Broadcast"]
GULF_TOOLS = ["Arabic_Stylish_Name","Bahrain_Cpr_Check","Bahrain_Gold_Price","Bahrain_Gratuity","Bahrain_Overtime","Bahrain_Rent","Bahrain_Traffic_Fines","Emirates_Id_Check","Gosi_Calculator","Hijri_Converter","Iqama_Expiry","Kuwait_Traffic_Fines","Oman_Civil_Check","Oman_Gold_Price","Oman_Gratuity","Oman_Overtime","Oman_Rent","Oman_Traffic_Fines","Qatar_Gold_Price","Qatar_Overtime","Qatar_Rent_Splitter","Salary_Sa","Uae_Gold_Price","Uae_Gratuity","Uae_Overtime","Uae_Rent_Splitter","Uae_Salary","Uae_Traffic_Fines","Zatca_Qr"]
UK_TOOLS = ["Uk_Paycheck","Uk_Rent_Splitter","Uk_Tip_Calculator","Uk_Vat_Calculator"]
US_TOOLS = ["Usa_Background_Check","Usa_Notify"]
GLOBAL_TOOLS = ["Bg_Remover"]

def get_country():
    if request.args.get('key')==ADMIN_KEY and request.args.get('test'):
        return request.args.get('test').upper()
    return request.headers.get('CF-IPCountry','NG').upper()

def get_filtered(country):
    base = os.path.join(app.root_path,'templates')
    all_files = [f.replace('.html','') for f in os.listdir(base) if f.endswith('.html') and f.lower() not in ['base.html','index.html']]
    out=[]
    for n in all_files:
        if n in GLOBAL_TOOLS: out.append(n)
        elif country=='NG' and n in NG_TOOLS: out.append(n)
        elif country in ['BH','SA','AE','QA','KW','OM'] and n in GULF_TOOLS: out.append(n)
        elif country=='UK' and n in UK_TOOLS: out.append(n)
        elif country=='US' and n in US_TOOLS: out.append(n)
    return sorted(out)

@app.route('/')
def index():
    c=get_country()
    tools=[{"name":n,"url":f"/{n}"} for n in get_filtered(c)]
    return render_template('index.html', tools=tools, user_country=c)

@app.route('/admin-tools')
def admin_tools():
    if request.args.get('key')!=ADMIN_KEY: abort(403)
    base = os.path.join(app.root_path,'templates')
    all_files = [f.replace('.html','') for f in os.listdir(base) if f.endswith('.html') and f.lower() not in ['base.html','index.html']]
    data = {
        "NG": [f for f in all_files if f in NG_TOOLS],
        "GULF": [f for f in all_files if f in GULF_TOOLS],
        "UK": [f for f in all_files if f in UK_TOOLS],
        "US": [f for f in all_files if f in US_TOOLS],
        "GLOBAL": [f for f in all_files if f in GLOBAL_TOOLS],
        "UNMAPPED": [f for f in all_files if f not in NG_TOOLS+GULF_TOOLS+UK_TOOLS+US_TOOLS+GLOBAL_TOOLS]
    }
    tools=[{"name":n,"url":f"/{n}"} for n in sorted(all_files)]
    return render_template('index.html', tools=tools, user_country=f"ADMIN - {len(all_files)} TOTAL", admin_data=data)

@app.route('/<tool_name>')
def tool_page(tool_name):
    try: return render_template(f'{tool_name}.html')
    except: abort(404)

@app.route('/debug')
def debug():
    if request.args.get('key')!=ADMIN_KEY: abort(403)
    return jsonify({"country":get_country(),"ng":len(NG_TOOLS),"gulf":len(GULF_TOOLS),"ip_header":request.headers.get('CF-IPCountry')})

if __name__=='__main__': app.run()