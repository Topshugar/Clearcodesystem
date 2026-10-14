from flask import Flask, render_template, request, jsonify, send_file, abort
from PIL import Image
import io, requests, os

app = Flask(__name__)
ADMIN_KEY = "CLEARCODE2026"

# ===== STRICT IP LOCK + ADMIN TEST =====
def get_user_country():
    test = request.args.get('test')
    key = request.args.get('key')
    if test and key == ADMIN_KEY:
        return test.upper()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    try:
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=2)
        c = r.text.strip().upper()
        if len(c) == 2:
            return c
    except:
        pass
    return "NG"

COUNTRY_NAMES = {"NG":"Nigeria","BH":"Bahrain","SA":"Saudi Arabia","KW":"Kuwait","AE":"UAE","QA":"Qatar","OM":"Oman"}

def load_tools():
    tools = []
    template_path = os.path.join(app.root_path, 'templates')
    for file in os.listdir(template_path):
        if not file.endswith('.html'): continue
        if file in ['base.html','index.html','coming_soon.html']: continue
        name = file.replace('.html','')
        country = "BH,SA,KW,AE,QA,OM" if name in ['gold','cpr','salary-gulf','rent-gulf','vat-ksa','vat-uae'] else "NG" if name in ['pos','price-tag','invoice','rent-ng','delivery'] else "ALL"
        tools.append({"name": name.replace('-',' ').title(), "url": f"/{name}", "icon": "🤖" if name=="bg-remover" else "🔧", "desc": f"{name} tool", "country": country, "is_new": name=="bg-remover"})
    return sorted(tools, key=lambda x: x['name'])

def filter_tools(country):
    return [t for t in load_tools() if t["country"]=="ALL" or country in t["country"]]

@app.route('/')
def index():
    country = get_user_country()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return render_template('index.html', tools=filter_tools(country), user_country=country, country_name=COUNTRY_NAMES.get(country,country), user_ip=ip)

@app.route('/<tool_name>')
def serve_tool(tool_name):
    try:
        return render_template(f'{tool_name}.html', user_country=get_user_country())
    except:
        abort(404)

@app.route('/api/remove-bg', methods=['POST'])
def remove_bg_api():
    from rembg import remove
    file = request.files.get('image')
    if not file: return jsonify({"error":"No image"}), 400
    img = Image.open(file.stream).convert("RGBA")
    output = remove(img)
    buf = io.BytesIO()
    output.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# ===== ADMIN + SECRET TOOLS =====
@app.route('/admin-tools')
def admin_tools():
    if request.args.get('key')!= ADMIN_KEY: abort(403)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return render_template('index.html', tools=load_tools(), user_country="ADMIN", country_name="All Tools - Admin View", user_ip=ip)

@app.route('/ip-spy')
def ip_spy():
    if request.args.get('key')!= ADMIN_KEY: abort(403)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return jsonify({"ip": ip, "country": get_user_country(), "headers": dict(request.headers)})

if __name__ == '__main__':
    app.run(debug=True)