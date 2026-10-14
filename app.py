from flask import Flask, render_template, request, jsonify, send_file, abort
from PIL import Image
import io, requests

app = Flask(__name__)
ADMIN_KEY = "CLEARCODE2026"

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
# THIS LIST CONNECTS YOUR TEMPLATES FOLDER TO INDEX
# url = /pos means it will load templates/pos.html

ALL_TOOLS = [
    {"name":"Background Remover AI","url":"/bg-remover","icon":"🤖","desc":"Remove BG 4K HD","country":"ALL","is_new":True},
    {"name":"POS Calculator","url":"/pos","icon":"🧮","desc":"POS profit","country":"NG"},
    {"name":"Price Tag Maker","url":"/price-tag","icon":"🏷️","desc":"Price tags","country":"NG"},
    {"name":"Invoice Generator","url":"/invoice","icon":"📄","desc":"Invoice free","country":"NG"},
    {"name":"Gold Price","url":"/gold","icon":"🪙","desc":"Gold BHD SAR","country":"BH,SA,KW,AE,QA,OM"},
    # PASTE YOUR OTHER 72 TOOLS HERE - SAME FORMAT
]

def filter_tools(country):
    return [t for t in ALL_TOOLS if t["country"]=="ALL" or country in t["country"]]
@app.route('/')
def index():
    country = get_user_country()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    tools = filter_tools(country)
    return render_template('index.html', tools=tools, user_country=country, country_name=COUNTRY_NAMES.get(country,country), user_ip=ip)

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
    if not file:
        return jsonify({"error":"No image"}), 400
    img = Image.open(file.stream).convert("RGBA")
    output = remove(img)
    buf = io.BytesIO()
    output.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)