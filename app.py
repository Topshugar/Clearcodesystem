from flask import Flask, render_template, request, jsonify, redirect
import json, os
from datetime import datetime

app = Flask(__name__)

COUNTRY_NAMES = {
'NG':'Nigeria','BH':'Bahrain','QA':'Qatar','SA':'Saudi Arabia',
'AE':'UAE','KW':'Kuwait','OM':'Oman','US':'USA','UK':'UK'
}

ALL_TOOLS = [
'pos_charges','delivery_fee','price_tag','data_bundle','bank_card_info',
'clear_shell','ruler_terminal','qr_code','age_calc','bmi_calc','loan_calc',
'vat_calc','discount_calc','profit_calc','unit_converter','word_counter',
'password_gen','color_picker','invoice_gen','receipt_gen','business_name',
'hashtag_gen','currency_converter','fuel_calc','rent_calc','salary_calc',
'age_in_days','days_until'
]
def get_user_country():
    param = request.args.get('country','').upper()
    if param in COUNTRY_NAMES:
        return param, param
    cf = request.headers.get('CF-IPCountry','').upper()
    if cf and cf!= 'XX' and cf in COUNTRY_NAMES:
        return cf, cf
    fwd = request.headers.get('X-Forwarded-For','').split(',')[0].strip()
    ip = fwd or request.remote_addr or 'NG'
    raw = 'NG'
    if raw == 'US':
        raw = 'NG'
    return raw, param if param else raw

def get_enabled_tools(country):
    country = country.upper()
    try:
        if os.path.exists('disabled_tools.json'):
            with open('disabled_tools.json','r') as f:
                disabled = json.load(f)
                if country in disabled:
                    return [t for t in ALL_TOOLS if t not in disabled[country]]
    except:
        pass
    return ALL_TOOLS
@app.route('/')
def index():
    raw_country, country = get_user_country()
    # If?country= param exists, use it
    q = request.args.get('country','').upper()
    if q in COUNTRY_NAMES:
        country = q
        raw_country = q
    else:
        if raw_country not in COUNTRY_NAMES:
            raw_country = 'NG'
        country = raw_country

    tools = get_enabled_tools(country)
    return render_template('index.html',
        country=country,
        raw_country=raw_country,
        country_name=COUNTRY_NAMES.get(country,country),
        tools=tools)
@app.route('/tool/<tool_name>')
def tool_page(tool_name):
    raw_country, country = get_user_country()
    q = request.args.get('country','').upper()
    if q in COUNTRY_NAMES:
        country = q
    if tool_name not in ALL_TOOLS:
        return "Tool not found", 404
    try:
        return render_template(f'{tool_name}.html', country=country, raw_country=raw_country)
    except:
        return render_template('bank_card_info.html', country=country, raw_country=raw_country)

@app.route('/admin/tools')
def admin_tools():
    key = request.args.get('key','')
    if key!= 'CLEARCODE2026':
        return "Unauthorized", 403
    country = request.args.get('country','NG').upper()
    tools = ALL_TOOLS
    return render_template('admin_tools.html', tools=tools, country=country)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)