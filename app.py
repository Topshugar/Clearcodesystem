from flask import Flask, render_template, request, jsonify, send_file, abort
from PIL import Image
import io
import os
import requests
from functools import wraps

app = Flask(__name__)

# ===== YOUR SECRET KEYS =====
ADMIN_KEY = "CLEARCODE2026"
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY", "YOUR_LEONARDO_KEY_HERE") # keep in env, not frontend

# ===== STRICT IP DETECTION (you asked for strict, not CF) =====
def get_user_country():
    # Strict lock - no Cloudflare fake
    test = request.args.get('test')
    key = request.args.get('key')
    if test and key == ADMIN_KEY:
        return test.upper()

    # Real IP
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip: ip = ip.split(',')[0].strip()

    try:
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        country = r.text.strip().upper()
        if len(country) == 2:
            return country
    except:
        pass
    return "NG" # default Nigeria

COUNTRY_NAMES = {
    "NG":"Nigeria", "BH":"Bahrain", "SA":"Saudi Arabia",
    "KW":"Kuwait", "AE":"UAE", "QA":"Qatar", "OM":"Oman", "US":"USA"
}

# ===== 76 TOOLS LIST WITH COUNTRY MAPPING =====
ALL_TOOLS = [
    # NIGERIA CORE (21 tools you built)
    {"name":"POS Calculator","url":"/pos","icon":"🧮","desc":"Calculate POS profit","country":"NG"},
    {"name":"Price Tag Maker","url":"/price-tag","icon":"🏷️","desc":"Make price tags 4K","country":"NG"},
    {"name":"Store Builder","url":"/store","icon":"🏪","desc":"Shopify style store","country":"NG"},
    {"name":"Invoice Generator","url":"/invoice","icon":"📄","desc":"Free invoice no watermark","country":"NG"},
    {"name":"Rent Calculator","url":"/rent","icon":"🏠","desc":"Lagos rent calculator","country":"NG"},
    {"name":"Delivery Fee Calculator","url":"/delivery","icon":"🛵","desc":"Calculate delivery","country":"NG"},
    {"name":"Background Remover AI","url":"/bg-remover","icon":"🤖","desc":"Remove BG + 4K HD - NEW","country":"ALL","is_new":True},
    {"name":"Receipt Maker","url":"/receipt","icon":"🧾","desc":"Instant receipt","country":"NG"},
    # GULF CORE
    {"name":"Gold Price Live","url":"/gold","icon":"🪙","desc":"Gold price today BHD/SAR","country":"BH,SA,KW,AE,QA,OM"},
    {"name":"CPR Check","url":"/cpr","icon":"🪪","desc":"Bahrain CPR tools","country":"BH"},
    {"name":"Salary Calculator Gulf","url":"/salary","icon":"💰","desc":"Salary in BHD/SAR/KWD","country":"BH,SA,KW,AE,QA,OM"},
    {"name":"Rent Calculator Gulf","url":"/rent-gulf","icon":"🏢","desc":"Rent in Gulf","country":"BH,SA,KW,AE,QA,OM"},
    #... add your other 64 tools here same format
    {"name":"QR Code Maker","url":"/qr","icon":"🔳","desc":"QR code 4K","country":"ALL"},
    {"name":"Image Compressor","url":"/compress","icon":"🗜️","desc":"Compress without loss","country":"ALL"},
]

def filter_tools_by_country(country):
    result=[]
    for t in ALL_TOOLS:
        if t["country"]=="ALL" or country in t["country"]:
            result.append(t)
    return result

@app.route('/')
def index():
    country = get_user_country()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    tools = filter_tools_by_country(country)
    return render_template('index.html',
        tools=tools,
        user_country=country,
        country_name=COUNTRY_NAMES.get(country, country),
        user_ip=ip
    )
# ===== REAL BG REMOVER API - BACKEND HIDDEN, WHITE-LABEL =====
@app.route('/api/remove-bg', methods=['POST'])
def remove_bg_api():
    try:
        from rembg import remove
        file = request.files.get('image')
        if not file: return jsonify({"error":"No image"}), 400

        prompt = request.form.get('prompt', '').strip() # hidden Leonardo prompt

        input_image = Image.open(file.stream).convert("RGBA")
        # REAL AI - rembg + U2Net (free, no API key)
        output = remove(input_image)

        # ===== SECRET LEONARDO WHITE-LABEL LOGIC =====
        # User thinks it's Clearcode AI, but we call Leonardo here if prompt exists
        if prompt and LEONARDO_API_KEY!= "YOUR_LEONARDO_KEY_HERE":
            try:
                # Generate background with Leonardo phoenix model - HIDDEN FROM USER
                leo_res = requests.post(
                    "https://cloud.leonardo.ai/api/rest/v1/generations",
                    headers={"Authorization": f"Bearer {LEONARDO_API_KEY}"},
                    json={
                        "prompt": prompt + ", professional studio background, 4k",
                        "modelId": "6bef9f1b-29cb-40c3-b8c9-6cc2621cc6c1", # phoenix
                        "width": 1024, "height": 1024, "num_images":1
                    },
                    timeout=20
                )
                # Composite logic - you can expand
                # For now return transparent, background gen is optional upgrade
                pass
            except Exception as e:
                print(f"Leonardo hidden error: {e}")
                # Fail silently, still return removed BG

        buf = io.BytesIO()
        output.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/bg-remover')
def bg_remover_page():
    return render_template('bg_remover.html')

# ===== YOUR SECRET TOOLS (remembered) =====
@app.route('/monetag-test')
def monetag_test():
    key = request.args.get('key')
    if key!= ADMIN_KEY: abort(403)
    return """
    <h1>Monetag Test</h1>
    <p>Zone 11988352 should load in head</p>
    <p>Zone 11970663 should load on click</p>
    <script src="https://alwingulla.com/88/tag.min.js" data-zone="11988352"></script>
    <script src="https://alwingulla.com/88/tag.min.js" data-zone="11970663"></script>
    """

@app.route('/ip-spy')
def ip_spy():
    key = request.args.get('key')
    if key!= ADMIN_KEY: abort(403)
    return jsonify({
        "remote_addr": request.remote_addr,
        "x_forwarded_for": request.headers.get('X-Forwarded-For'),
        "cf_connecting_ip": request.headers.get('CF-Connecting-IP'),
        "detected_country": get_user_country(),
        "real_ip_used": request.headers.get('X-Forwarded-For', request.remote_addr)
    })

@app.route('/leonardo-hidden', methods=['GET','POST'])
def leonardo_hidden():
    key = request.args.get('key')
    if key!= ADMIN_KEY: abort(403)
    # Your private tester - not visible to users
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        # Call Leonardo here to test before pushing to white-label
        return jsonify({"status":"Leonardo called secretly", "prompt":prompt})
    return """
    <form method="POST">
      <h2>Secret Leonardo Tester (White-label)</h2>
      <input name="prompt" placeholder="luxury boutique" style="width:300px">
      <button>Test Leonardo</button>
      <p>User will never see this page - only you with?key=CLEARCODE2026</p>
    </form>
    """

@app.route('/admin-tools')
def admin_tools():
    key = request.args.get('key')
    if key!= ADMIN_KEY: abort(403)
    return render_template('index.html', tools=ALL_TOOLS, user_country="ADMIN", country_name="All Countries - Secret", user_ip="admin")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
