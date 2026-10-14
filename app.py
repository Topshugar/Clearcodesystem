import os
from flask import Flask, render_template, request, abort
app = Flask(__name__)
ADMIN_KEY = "CLEARCODE2026"

NG = ["Builder","Cac_Checker","Clan_Logo","Clear_Shell","Debt_Book","Delivery_Fee","Fake_Excuse_Generator","Fake_Text","Fake_Whatsapp_Chat","Fuel_Calculator","Gamer_Tag","Gpa_Calculator","Invoice","Ivr_Builder","Ivr_Software","Jamb_Calculator","Lagos_Rent_Package","Land_Converter","Market_Ledger","Marketwatch_Demo","Nepa_Calculator","Nin_Validator","Paycheck","Paye_Calculator","Pos_Charges","Pos_Receipt","Price_Tag","Profit_Calculator","Rent_Splitter","Ruler_Terminal","Salary_Flex","Sensitivity","Sleep_Calculator","Tip_Calculator","Tournament","Unlock","Bank_Card_Info","Wa_Qr","Waec_Calculator","Whatsapp_Broadcast"]
GULF = ["Arabic_Stylish_Name","Bahrain_Cpr_Check","Bahrain_Gold_Price","Bahrain_Gratuity","Bahrain_Overtime","Bahrain_Rent","Bahrain_Traffic_Fines","Emirates_Id_Check","Gosi_Calculator","Hijri_Converter","Iqama_Expiry","Kuwait_Traffic_Fines","Oman_Civil_Check","Oman_Gold_Price","Oman_Gratuity","Oman_Overtime","Oman_Rent","Oman_Traffic_Fines","Qatar_Gold_Price","Qatar_Overtime","Qatar_Rent_Splitter","Salary_Sa","Uae_Gold_Price","Uae_Gratuity","Uae_Overtime","Uae_Rent_Splitter","Uae_Salary","Uae_Traffic_Fines","Zatca_Qr"]
UK = ["Uk_Paycheck","Uk_Rent_Splitter","Uk_Tip_Calculator","Uk_Vat_Calculator"]
US = ["Usa_Background_Check","Usa_Notify"]
GLOBAL = ["Bg_Remover"]

def get_country():
    if request.args.get('key')==ADMIN_KEY and request.args.get('test'):
        return request.args.get('test').upper()
    # Render gives this header
    return request.headers.get('CF-IPCountry', 'NG').upper()

@app.route('/')
def index():
    country = get_country()
    folder = os.path.join(app.root_path,'templates')
    all_files = [f[:-5] for f in os.listdir(folder) if f.endswith('.html') and f not in ['base.html','index.html']]
    
    filtered = []
    for name in all_files:
        if name in GLOBAL: filtered.append(name)
        elif country == 'NG' and name in NG: filtered.append(name)
        elif country in ['BH','SA','AE','QA','KW','OM'] and name in GULF: filtered.append(name)
        elif country == 'UK' and name in UK: filtered.append(name)
        elif country == 'US' and name in US: filtered.append(name)
    
    tools = [{"name":n, "url":f"/{n}"} for n in sorted(filtered)]
    return render_template('index.html', tools=tools, user_country=country)

@app.route('/admin-tools')
def admin_tools():
    if request.args.get('key')!=ADMIN_KEY: abort(403)
    folder = os.path.join(app.root_path,'templates')
    all_files = [f[:-5] for f in os.listdir(folder) if f.endswith('.html') and f not in ['base.html','index.html']]
    tools = [{"name":n, "url":f"/{n}"} for n in sorted(all_files)]
    return render_template('index.html', tools=tools, user_country=f"ADMIN {len(all_files)}")

@app.route('/<tool_name>')
def page(tool_name):
    try: return render_template(f'{tool_name}.html')
    except: abort(404)