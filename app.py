from flask import Flask, render_template, Response, request, abort
import os
import datetime
import requests

app = Flask(__name__)

EXCLUDE = {"base.html", "index.html", "tool.html", "builder.html", "clear_shell.html", "ruler_terminal.html", "unlock.html", "marketwatch_demo.html"}

COUNTRY_TOOLS = {
    "BH": ["bahrain", "gold_bahrain", "salary_bahrain", "rent_bahrain", "bahrain_gold_price", "bahrain_rent", "bahrain_cpr_check", "bahrain_traffic_fines", "bahrain_gratuity", "bahrain_overtime", "gosi_calculator"],
    "AE": ["uae", "emirates", "uae_gold_price", "uae_salary", "uae_rent_splitter", "uae_gratuity", "uae_overtime", "uae_traffic_fines"],
    "QA": ["qatar", "qatar_gold_price", "qatar_rent_splitter", "qatar_overtime"],
    "SA": ["sa", "salary_sa", "zatca_qr", "iqama_expiry"],
    "OM": ["oman", "oman_gold_price", "oman_rent", "oman_civil_check", "oman_gratuity", "oman_overtime", "oman_traffic_fines"],
    "KW": ["kuwait", "kuwait_traffic_fines"],
    "NG": ["nin", "nepa", "cac_checker", "jamb", "waec", "fuel_calculator", "paye_calculator", "land_converter", "pos_charges", "lagos_rent_package", "tip_calculator", "salary_flex", "nigeria", "naira"],
    "GB": ["uk", "uk_paycheck", "uk_rent_splitter", "uk_tip_calculator", "uk_vat_calculator"],
    "US": ["usa", "usa_background_check", "usa_notify", "paycheck"],
}

GOLD_PRICES = {
    "BH": {"code": "BHD", "price": 32.850, "name": "Bahrain"},
    "AE": {"code": "AED", "price": 320.50, "name": "UAE"},
    "QA": {"code": "QAR", "price": 335.20, "name": "Qatar"},
    "SA": {"code": "SAR", "price": 345.80, "name": "Saudi"},
    "OM": {"code": "OMR", "price": 35.60, "name": "Oman"},
    "KW": {"code": "KWD", "price": 28.30, "name": "Kuwait"},
    "NG": {"code": "NGN", "price": 145000, "name": "Nigeria"},
    "GB": {"code": "GBP", "price": 65.20, "name": "UK"},
    "US": {"code": "USD", "price": 85.50, "name": "USA"},
}

TOOL_EMOJIS = {
    "bahrain_gold_price": "🥇",
    "gold_bahrain": "🥇",
    "uae_gold_price": "🥇",
    "qatar_gold_price": "🥇",
    "oman_gold_price": "🥇",
    "oman_civil_check": "🪪",
    "salary_bahrain": "💰",
    "salary_sa": "💰",
    "uae_salary": "💰",
    "salary_flex": "💰",
    "paycheck": "💰",
    "uk_paycheck": "💰",
    "rent_bahrain": "🏠",
    "bahrain_rent": "🏠",
    "uae_rent_splitter": "🏠",
    "qatar_rent_splitter": "🏠",
    "oman_rent": "🏠",
    "lagos_rent_package": "🏠",
    "rent_splitter": "🏠",
    "uk_rent_splitter": "🏠",
    "bahrain_cpr_check": "🪪",
    "emirates_id_check": "🪪",
    "nin_validator": "🪪",
    "nepa_calculator": "⚡",
    "fuel_calculator": "⛽",
    "cac_checker": "🏢",
    "jamb_calculator": "📚",
    "waec_calculator": "📚",
    "gpa_calculator": "📚",
    "gosi_calculator": "📊",
    "bahrain_gratuity": "🧾",
    "uae_gratuity": "🧾",
    "oman_gratuity": "🧾",
    "paye_calculator": "💸",
    "pos_charges": "💳",
    "bank_card_info": "💳",
    "tip_calculator": "💵",
    "profit_calculator": "📈",
    "invoice": "🧾",
    "zatca_qr": "🔳",
    "wa_qr": "🔳",
}

def get_country_by_ip():
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip:
            ip = ip.split(',')[0].strip()
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        country = r.text.strip() if r.status_code == 200 else "NG"
        return country
    except:
        return "NG"

def get_all_tools():
    folder = os.path.join(app.root_path, "templates")
    files = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith(".html") and f not in EXCLUDE:
                files.append(f[:-5])
    return sorted(files)

def filter_tools_by_country(tools, country):
    keywords = COUNTRY_TOOLS.get(country, COUNTRY_TOOLS["NG"])
    filtered = []
    for t in tools:
        for kw in keywords:
            if kw in t.lower():
                filtered.append(t)
                break
    if len(filtered) < 3:
        return tools
    return filtered

@app.route('/')
def home():
    all_tools = get_all_tools()
    country = get_country_by_ip()
    tools = filter_tools_by_country(all_tools, country)
    data = GOLD_PRICES.get(country, GOLD_PRICES["NG"])
    return render_template('index.html',
        seo_title=f'ClearCode System - Free Tools for {data["name"]}',
        seo_desc=f'Free tools for {data["name"]} - Strictly by IP.',
        tools=tools,
        emojis=TOOL_EMOJIS,
        country_code=data["code"],
        country_name=data["name"],
        detected_country=country,
        total_tools=len(all_tools)
    )

@app.route('/robots.txt')
def robots():
    txt = "User-agent: *\nAllow: /\nSitemap: https://clearcodesystem.onrender.com/sitemap.xml\n"
    return Response(txt, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    base_url = "https://clearcodesystem.onrender.com"
    today = datetime.date.today().isoformat()
    tools = get_all_tools()
    urls = [base_url + "/"]
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
    if not target:
        return abort(404)
    country = get_country_by_ip()
    data = GOLD_PRICES.get(country, GOLD_PRICES["NG"])
    return render_template(target + ".html",
        seo_title=f'{target.replace("_", " ").title()} - ClearCode System',
        seo_desc=f'Free {target.replace("_", " ")} tool.',
        country_code=data["code"],
        country_name=data["name"],
        detected_country=country,
        price_24k=data["price"],
        price_22k=round(data["price"] * 0.916, 3),
        price_21k=round(data["price"] * 0.875, 3)
    )

if __name__ == '__main__':
    app.run(debug=True)