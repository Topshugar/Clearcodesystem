from flask import Flask, render_template, request
import json, os, glob

app = Flask(__name__)

COUNTRY_NAMES = {
'NG':'Nigeria','BH':'Bahrain','QA':'Qatar','SA':'Saudi Arabia',
'AE':'UAE','KW':'Kuwait','OM':'Oman'
}

def get_all_tools():
    files = glob.glob('templates/*.html')
    exclude = {'base.html','index.html','admin_tools.html','admin.html'}
    tools = []
    for f in files:
        name = os.path.basename(f).replace('.html','')
        if os.path.basename(f) not in exclude and not name.startswith('_'):
            tools.append(name)
    return sorted(tools)

ALL_TOOLS = get_all_tools()
print(f"DETECTED TOOLS: {ALL_TOOLS}")
def get_ip_country():
    cf = request.headers.get('CF-IPCountry','').upper()
    if cf and cf!='XX' and cf in COUNTRY_NAMES:
        return cf
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
    except Exception as e:
        print(f"Error reading disabled_tools: {e}")
    return ALL_TOOLS
@app.route('/')
def index():
    country = get_ip_country()
    tools = get_enabled_tools(country)
    return render_template('index.html',
        country=country,
        raw_country=country,
        country_name=COUNTRY_NAMES.get(country, country),
        tools=tools,
        all_tools=ALL_TOOLS)

@app.route('/tool/<tool_name>')
def tool_page(tool_name):
    country = get_ip_country()
    test_country = request.args.get('test','').upper()
    test_key = request.args.get('key','')
    if test_country in COUNTRY_NAMES and test_key == 'CLEARCODE2026':
        country = test_country
    
    template_file = f'{tool_name}.html'
    template_path = os.path.join('templates', template_file)
    if not os.path.exists(template_path):
        return f"Template {template_file} not found. Available: {ALL_TOOLS}", 404
    
    try:
        return render_template(template_file, country=country, raw_country=country, country_name=COUNTRY_NAMES.get(country, country))
    except Exception as e:
        return f"Error loading {template_file}: {str(e)}", 500
@app.route('/admin/tools')
def admin_tools():
    key = request.args.get('key','')
    if key != 'CLEARCODE2026':
        return "Unauthorized - use ?key=CLEARCODE2026", 403
    country = request.args.get('country','NG').upper()
    if country not in COUNTRY_NAMES:
        country = 'NG'
    tools = get_enabled_tools(country)
    return render_template('admin_tools.html', tools=tools, country=country, all_tools=ALL_TOOLS, country_name=COUNTRY_NAMES.get(country))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)