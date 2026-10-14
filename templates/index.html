import os
from flask import Flask, render_template, request, abort
app = Flask(__name__)
ADMIN_KEY = "CLEARCODE2026"

NG = ["Builder","Cac_Checker","Clan_Logo","Clear_Shell","Debt_Book","Delivery_Fee","Fake_Excuse_Generator","Fake_Text","Fake_Whatsapp_Chat","Fuel_Calculator","Gamer_Tag","Gpa_Calculator","Invoice","Ivr_Builder","Ivr_Software","Jamb_Calculator","Lagos_Rent_Package","Land_Converter","Market_Ledger","Marketwatch_Demo","Nepa_Calculator","Nin_Validator","Paycheck","Paye_Calculator","Pos_Charges","Pos_Receipt","Price_Tag","Profit_Calculator","Rent_Splitter","Ruler_Terminal","Salary_Flex","Sensitivity","Sleep_Calculator","Tip_Calculator","Tournament","Unlock","Bank_Card_Info","Wa_Qr","Waec_Calculator","Whatsapp_Broadcast"]
GULF = ["Arabic_Stylish_Name","Bahrain_Cpr_Check","Bahrain_Gold_Price","Bahrain_Gratuity","Bahrain_Overtime","Bahrain_Rent","Bahrain_Traffic_Fines","Emirates_Id_Check","Gosi_Calculator","Hijri_Converter","Iqama_Expiry","Kuwait_Traffic_Fines","Oman_Civil_Check","Oman_Gold_Price","Oman_Gratuity","Oman_Overtime","Oman_Rent","Oman_Traffic_Fines","Qatar_Gold_Price","Qatar_Overtime","Qatar_Rent_Splitter","Salary_Sa","Uae_Gold_Price","Uae_Gratuity","Uae_Overtime","Uae_Rent_Splitter","Uae_Salary","Uae_Traffic_Fines","Zatca_Qr"]

def get_country():
    try:
        if request.args.get('key')==ADMIN_KEY and request.args.get('test'):
            return request.args.get('test').upper()
        return request.headers.get('CF-IPCountry','NG').upper()
    except:
        return 'NG'

@app.route('/')
def index():
    try:
        country = get_country()
        folder = os.path.join(app.root_path,'templates')
        if not os.path.exists(folder):
            return f"FIX: templates folder missing - Country {country}"
        
        all_files = []
        try:
            all_files = [f[:-5] for f in os.listdir(folder) if f.endswith('.html') and f not in ['base.html','index.html']]
        except Exception as e:
            return f"List error: {e}"

        filtered = [f for f in all_files if f in NG or f in GULF or f in ["Bg_Remover","Uk_Paycheck","Usa_Notify"]]
        # Show NG by default
        tools = [{"name":n, "url":f"/{n}"} for n in sorted(filtered) if (country=='NG' and n in NG) or (country in ['BH','SA','AE','QA','KW','OM'] and n in GULF) or n not in NG+GULF]
        if not tools:
            tools = [{"name":n, "url":f"/{n}"} for n in sorted(all_files[:20])] # emergency show 20

        return render_template('index.html', tools=tools, user_country=country)
    except Exception as e:
        return f"ERROR IN INDEX: {e} <br> Go to /health to check", 500

@app.route('/health')
def health():
    return "ClearCodeSystem LIVE - app.py is working"

@app.route('/admin-tools')
def admin_tools():
    if request.args.get('key')!=ADMIN_KEY: abort(403)
    folder = os.path.join(app.root_path,'templates')
    all_files = [f[:-5] for f in os.listdir(folder) if f.endswith('.html') and f not in ['base.html']]
    tools = [{"name":n, "url":f"/{n}"} for n in sorted(all_files)]
    return render_template('index.html', tools=tools, user_country=f"ADMIN {len(all_files)}")

@app.route('/<tool_name>')
def page(tool_name):
    try:
        return render_template(f'{tool_name}.html')
    except Exception as e:
        return f"Tool {tool_name} not found: {e}", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)