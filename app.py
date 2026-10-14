from flask import Flask, render_template, request, jsonify, send_file, abort
import os, io, requests
from PIL import Image

app = Flask(__name__)
ADMIN_KEY = "CLEARCODE2026"

# ===== STRICT IP - NO BYPASS =====
def get_user_country():
    # Only allow test if key matches
    test = request.args.get('test')
    key = request.args.get('key')
    if test and key == ADMIN_KEY:
        return test.upper()

    # Real IP from Render
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip:
        ip = ip.split(',')[0].strip()

    # Try ipapi
    try:
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        c = r.text.strip().upper()
        if len(c) == 2 and c.isalpha():
            return c
    except:
        pass
    return "NG" # fallback only if API fails

COUNTRY_NAMES = {"NG":"Nigeria","BH":"Bahrain","SA":"Saudi Arabia","AE":"UAE","QA":"Qatar","KW":"Kuwait","OM":"Oman"}

# ===== STRICT TOOL COUNTRY MAP =====
TOOL_COUNTRY = {
    # GULF ONLY
    "emirates-id-check": "BH,SA,KW,AE,QA,OM",
    "emirates-id": "BH,SA,KW,AE,QA,OM",
    "gold": "BH,SA,KW,AE,QA,OM",
    "cpr": "BH,SA,KW,AE,QA,OM",
    "vat-ksa": "SA",
    "vat-uae": "AE",
    "salary-gulf": "BH,SA,KW,AE,QA,OM",
    "rent-gulf": "BH,SA,KW,AE,QA,OM",
    # NG ONLY
    "builder": "NG",
    "cac-checker": "NG",
    "cac": "NG",
    "clan-logo": "NG",
    "clear-shell": "NG",
    "debt-book": "NG",
    "delivery-fee": "NG",
    "delivery": "NG",
    "fake-excuse-generator": "NG",
    "fake-text": "NG",
    "fake-whatsapp-chat": "NG",
    "fuel-calculator": "NG",
    "pos": "NG",
    "price-tag": "NG",
    "invoice": "NG",
    "rent-ng": "NG",
}

def load_tools():
    tools = []
    path = os.path.join(app.root_path, 'templates')
    for f in os.listdir(path):
        if not f.endswith('.html'): continue
        if f in ['base.html','index.html','coming_soon.html']: continue
        name = f.replace('.html','')
        country = TOOL_COUNTRY.get(name, "ALL") # bg-remover and others = ALL
        if country == "ALL" and name.startswith('fake'): country = "NG"

        tools.append({
            "name": name.replace('-',' ').title(),
            "url": f"/{name}",
            "icon": "🔧",
            "country": country
        })
    return sorted(tools, key=lambda x: x['name'])

def filter_tools(user_country):
    all_tools = load_tools()
    filtered = []
    for t in all_tools:
        c = t["country"]
        if c == "ALL" or user_country in c.split(','):
            filtered.append(t)
    return filtered

@app.route('/')
def index():
    country = get_user_country()
    tools = filter_tools(country)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return render_template('index.html', tools=tools, user_country=country, country_name=COUNTRY_NAMES.get(country,country), user_ip=ip)

@app.route('/<tool_name>')
def serve_tool(tool_name):
    try: return render_template(f'{tool_name}.html', user_country=get_user_country())
    except: abort(404)

@app.route('/api/remove-bg', methods=['POST'])
def remove_bg_api():
    from rembg import remove
    file = request.files.get('image')
    if not file: return jsonify({"error":"No image"}), 400
    img = Image.open(file.stream).convert("RGBA")
    buf = io.BytesIO()
    remove(img).save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/admin-tools')
def admin_tools():
    if request.args.get('key')!=ADMIN_KEY: abort(403)
    return render_template('index.html', tools=load_tools(), user_country="ADMIN", country_name="All Tools", user_ip="ADMIN")

if __name__ == '__main__':
    app.run(debug=True)