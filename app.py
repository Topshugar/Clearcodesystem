from flask import Flask, render_template, Response, request, abort, redirect, session
import os
import datetime
import requests
import sqlite3
import ipaddress

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_IPS = os.environ.get("ADMIN_IPS", "")

EXCLUDE = {"base.html", "index.html", "tool.html", "builder.html", "clear_shell.html", "ruler_terminal.html", "unlock.html", "marketwatch_demo.html", "receipt_checker.html"}

GULF_COUNTRIES = ["SA", "AE", "QA", "KW", "OM", "BH"]

GOLD_PRICES = {
    "BH": {"code": "BHD", "price": 32.850, "name": "Bahrain"},
    "AE": {"code": "AED", "price": 320.50, "name": "UAE"},
    "QA": {"code": "QAR", "price": 335.20, "name": "Qatar"},
    "SA": {"code": "SAR", "price": 345.80, "name": "Saudi Arabia"},
    "OM": {"code": "OMR", "price": 35.60, "name": "Oman"},
    "KW": {"code": "KWD", "price": 28.30, "name": "Kuwait"},
    "NG": {"code": "NGN", "price": 145000, "name": "Nigeria"},
    "GB": {"code": "GBP", "price": 65.20, "name": "UK"},
    "US": {"code": "USD", "price": 85.50, "name": "USA"},
}

TOOL_DISPLAY_NAMES = {
    "paycheck": "usa take-home pay calculator",
    "usa_paycheck": "usa take-home pay calculator",
    "paye_calculator": "nigeria paye calculator",
    "gpa_calculator": "nigeria gpa calculator",
    "receipt_checker": "receipt checker",
    "global_ivr_builder": "global ivr builder",
    "global_ivr_software": "global ivr software",
    "global_ruler_terminal": "global ruler terminal",
    "global_whatsapp_broadcast": "global whatsapp broadcast",
    "global_clear_shield": "ClearShield", # <-- NEW - fixes button name
}

DB_PATH = os.path.join(app.root_path, "records.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS records (code TEXT PRIMARY KEY, name TEXT, item TEXT, date TEXT)")
    conn.commit()
    conn.close()

init_db()

def get_client_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()
    return ip

def is_ip_allowed_for_admin():
    if not ADMIN_IPS:
        return True
    client_ip = get_client_ip()
    try:
        allowed = [x.strip() for x in ADMIN_IPS.split(',') if x.strip()]
        return client_ip in allowed
    except:
        return False

def get_country_by_ip():
    try:
        ip = get_client_ip()
        try:
            if ipaddress.ip_address(ip).is_private:
                return "NG"
        except:
            pass
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        country = r.text.strip() if r.status_code == 200 else "NG"
        return country if len(country)==2 else "NG"
    except:
        return "NG"

def get_all_tools():
    folder = os.path.join(app.root_path, "templates")
    files = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith(".html") and f not in EXCLUDE:
                files.append(f[:-5])
    files.append("receipt_checker")
    return sorted(set(files))

def get_grouped_tools(tools, country):
    tools_lower = [t.lower() for t in tools]
    lower_to_orig = {t.lower(): t for t in tools}

    gulf_tools = [lower_to_orig[t] for t in tools_lower if t.startswith("gulf")]
    global_tools = [lower_to_orig[t] for t in tools_lower if t.startswith("global")]
    nigeria_tools = [lower_to_orig[t] for t in tools_lower if t.startswith("nigeria") or t in ["receipt_checker", "gpa_calculator", "nigeria_receipt_checker"]]
    usa_tools = [lower_to_orig[t] for t in tools_lower if t.startswith("usa_") or t in ["usa_paycheck", "paycheck", "usa_background_check", "usa_notify"]]
    uk_tools = [lower_to_orig[t] for t in tools_lower if t.startswith("uk_")]
    bahrain_tools = [lower_to_orig[t] for t in tools_lower if t.startswith("bahrain_")]
    uae_tools = [lower_to_orig[t] for t in tools_lower if t.startswith("uae_") or t.startswith("emirates_")]

    # FIXED: Always return all keys to avoid Jinja crash, global always included
    base = {
        "global": sorted(set(global_tools)),
        "gulf": [],
        "nigeria": [],
        "usa": [],
        "uk": [],
        "bahrain": [],
        "uae": [],
        "country_specific": []
    }

    if country == "NG":
        base["nigeria"] = sorted(set(nigeria_tools))
    elif country in GULF_COUNTRIES:
        base["gulf"] = sorted(set(gulf_tools))
        if country == "BH":
            base["country_specific"] = bahrain_tools
        elif country == "AE":
            base["country_specific"] = uae_tools
    elif country == "US":
        base["usa"] = sorted(set(usa_tools))
    elif country == "GB":
        base["uk"] = sorted(set(uk_tools))

    return base

@app.route('/')
def home():
    all_tools = get_all_tools()
    country = get_country_by_ip()
    grouped = get_grouped_tools(all_tools, country)
    data = GOLD_PRICES.get(country, GOLD_PRICES["NG"])
    country_display = data["name"]

    if country in GULF_COUNTRIES:
        title_country = f"{country_display} - Gulf (GCC)"
    else:
        title_country = country_display

    return render_template('index.html',
        seo_title=f'ClearCode System - Tools for {data["name"]}',
        seo_desc=f'Professional tools for {data["name"]} built with Flask.',
        grouped=grouped,
        display_names=TOOL_DISPLAY_NAMES,
        country_code=data["code"],
        country_name=country_display,
        title_country=title_country,
        detected_country=country,
        is_gulf=country in GULF_COUNTRIES,
        total_tools=len(all_tools))

@app.route('/receipt', methods=['GET', 'POST'])
def receipt_checker():
    country = get_country_by_ip()
    data = GOLD_PRICES.get(country, GOLD_PRICES["NG"])
    record = None
    error = None
    code = ""
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        if code:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT code, name, item, date FROM records WHERE code =?", (code,))
            record = cursor.fetchone()
            conn.close()
            if not record:
                error = f"Receipt {code} not found"
        else:
            error = "Enter a code"
    return render_template('receipt_checker.html', seo_title=f'Receipt Checker - {data["name"]}', seo_desc='Verify Nigeria business receipt', record=record, error=error, code=code, country_code=data["code"], country_name=data["name"], detected_country=country)

@app.route('/receipt/<code>')
def receipt_direct(code):
    country = get_country_by_ip()
    data = GOLD_PRICES.get(country, GOLD_PRICES["NG"])
    record = None
    error = None
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, name, item, date FROM records WHERE code =?", (code,))
    record = cursor.fetchone()
    conn.close()
    if not record:
        error = f"Receipt {code} not found"
    return render_template('receipt_checker.html', seo_title=f'Receipt {code} - ClearCode', seo_desc='Verified receipt', record=record, error=error, code=code, country_code=data["code"], country_name=data["name"], detected_country=country)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if not is_ip_allowed_for_admin():
        abort(403)
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if ADMIN_PASSWORD and pwd == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin/dashboard')
        else:
            return '''<h3 style="color:#ff5555;font-family:system-ui;padding:20px">Invalid password</h3><a href="/admin">Back</a>''', 403
    if session.get('admin'):
        return redirect('/admin/dashboard')
    return '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{background:#0a0a0a;color:#fff;font-family:system-ui;padding:20px}.box{max-width:400px;margin:60px auto;background:#171717;border:1px solid #2a2a2a;border-radius:16px;padding:20px}input{width:100%;padding:13px;border-radius:10px;border:1px solid #333;background:#0f0f0f;color:#fff;box-sizing:border-box}button{width:100%;padding:13px;margin-top:12px;border-radius:10px;border:0;background:#fff;color:#000;font-weight:700}</style></head><body><div class="box"><h3>Admin Login - IP Restricted</h3><form method="post"><input type="password" name="password" placeholder="ADMIN_PASSWORD" required><button type="submit">Login</button></form></div></body></html>'''

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin')
    if not is_ip_allowed_for_admin():
        abort(403)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, name, item, date FROM records ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    import datetime as dt
    today = dt.date.today().isoformat()
    html = f'''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{{background:#0a0a0a;color:#fff;font-family:system-ui;padding:18px}}.box{{max-width:600px;margin:10px auto;background:#171717;border:1px solid #2a2a2a;border-radius:16px;padding:18px}}input{{width:100%;padding:12px;border-radius:10px;border:1px solid #333;background:#0f0f0f;color:#fff;margin-top:8px;box-sizing:border-box}}button{{width:100%;padding:12px;margin-top:12px;border-radius:10px;border:0;background:#fff;color:#000;font-weight:700}}table{{width:100%;margin-top:18px;border-collapse:collapse;font-size:13px}}td,th{{border-bottom:1px solid #222;padding:8px;text-align:left}}a{{color:#888;text-decoration:none}}.del{{color:#ff5555}}</style></head><body><div class="box"><h3>SQL Admin - records.db - IP: {get_client_ip()}</h3><form method="post" action="/admin/add"><input name="code" placeholder="Code e.g. NG-001" required><input name="name" placeholder="Customer Name" required><input name="item" placeholder="Item / Service" required><input name="date" value="{today}" required><button type="submit">Add / Update Record</button></form><table><tr><th>Code</th><th>Name</th><th>Item</th><th>Date</th><th>Action</th></tr>'''
    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td><a href='/receipt/{r[0]}'>View</a> • <a class='del' href='/admin/delete/{r[0]}'>Delete</a></td></tr>"
    html += '''</table><br><a href="/admin/logout">Logout</a> • <a href="/">Home</a></div></body></html>'''
    return html

@app.route('/admin/add', methods=['POST'])
def admin_add():
    if not session.get('admin') or not is_ip_allowed_for_admin():
        return redirect('/admin')
    code = request.form.get('code', '').strip()
    name = request.form.get('name', '').strip()
    item = request.form.get('item', '').strip()
    date = request.form.get('date', '').strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO records (code, name, item, date) VALUES (?,?,?,?)", (code, name, item, date))
    conn.commit()
    conn.close()
    return redirect('/admin/dashboard')

@app.route('/admin/delete/<code>')
def admin_delete(code):
    if not session.get('admin') or not is_ip_allowed_for_admin():
        return redirect('/admin')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE code =?", (code,))
    conn.commit()
    conn.close()
    return redirect('/admin/dashboard')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin')

@app.route('/robots.txt')
def robots():
    txt = "User-agent: *\nAllow: /\nSitemap: https://clearcodesystem.onrender.com/sitemap.xml\n"
    return Response(txt, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    base_url = "https://clearcodesystem.onrender.com"
    today = datetime.date.today().isoformat()
    tools = get_all_tools()
    urls = [base_url + "/", base_url + "/receipt", base_url + "/admin"]
    for t in tools:
        urls.append(f"{base_url}/tools/{t}")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in set(urls):
        xml += f" <url><loc>{url}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>\n"
    xml += "</urlset>"
    return Response(xml, mimetype='application/xml')

@app.route('/tools/<tool_name>')
def tool_page(tool_name):
    all_tools = get_all_tools()
    target = None
    if tool_name in all_tools:
        target = tool_name
    else:
        alt = tool_name.replace("-", "_")
        if alt in all_tools:
            target = alt
    if not target or target == "receipt_checker":
        return abort(404)
    country = get_country_by_ip()
    data = GOLD_PRICES.get(country, GOLD_PRICES["NG"])
    return render_template(target + ".html", seo_title=f'{TOOL_DISPLAY_NAMES.get(target, target.replace("_", " ").lower())} - ClearCode', seo_desc=f'Free {target.replace("_", " ")} tool.', country_code=data["code"], country_name=data["name"], detected_country=country, price_24k=data["price"], price_22k=round(data["price"] * 0.916, 3), price_21k=round(data["price"] * 0.875, 3))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))