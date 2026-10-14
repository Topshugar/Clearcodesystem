from flask import Flask, render_template, request, jsonify
import json, os

app = Flask(__name__)

COUNTRY_NAMES = {
'NG':'Nigeria','BH':'Bahrain','QA':'Qatar','SA':'Saudi Arabia',
'AE':'UAE','KW':'Kuwait','OM':'Oman'
}

ALL_TOOLS = [
'pos_charges','delivery_fee','price_tag','data_bundle','bank_card_info',
'clear_shell','ruler_terminal','qr_code','age_calc','bmi_calc','loan_calc',
'vat_calc','discount_calc','profit_calc','unit_converter','word_counter',
'password_gen','color_picker','invoice_gen','receipt_gen','business_name',
'hashtag_gen','currency_converter','fuel_calc','rent_calc','salary_calc',
'age_in_days','days_until'
]
def get_ip_country():
    # 1. Cloudflare real country (Render fix)
    cf = request.headers.get('CF-IPCountry','').upper()
    if cf and cf!='XX' and cf in COUNTRY_NAMES:
        return cf
    
    # 2. X-Forwarded-For fallback
    raw = request.headers.get('X-Country-Code','NG').upper()
    if raw not in COUNTRY_NAMES:
        raw = 'NG'
    return raw

def get_enabled_tools(country):
    country = country.upper()
    try:
        if os.path.exists('disabled_tools.json'):
            with open('disabled_tools.json','r') as f:
                data = json.load(f)
                disabled = data.get(country, [])
                return [t for t in ALL_TOOLS if t not in disabled]
    except:
        pass
    return ALL_TOOLS
@app.route('/')
def index():
    country = get_ip_country()
    tools = get_enabled_tools(country)
    
    return render_template('index.html',
        country=country,
        raw_country=country,
        country_name=COUNTRY_NAMES.get(country, country),
        tools=tools)
@app.route('/tool/<tool_name>')
def tool_page(tool_name):
    country = get_ip_country()
    
    # Allow admin test ?test=BH only if key present
    test_country = request.args.get('test','').upper()
    test_key = request.args.get('key','')
    if test_country in COUNTRY_NAMES and test_key == 'CLEARCODE2026':
        country = test_country
    
    if tool_name not in ALL_TOOLS:
        return "Tool not found", 404
        
    try:
        return render_template(f'{tool_name}.html', country=country, raw_country=country)
    except:
        return render_template('bank_card_info.html', country=country, raw_country=country)

@app.route('/admin/tools')
def admin_tools():
    key = request.args.get('key','')
    if key != 'CLEARCODE2026':
        return "Unauthorized - use ?key=CLEARCODE2026", 403
    country = request.args.get('country','NG').upper()
    if country not in COUNTRY_NAMES:
        country = 'NG'
    tools = get_enabled_tools(country)
    return render_template('admin_tools.html', tools=tools, country=country, all_tools=ALL_TOOLS)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)