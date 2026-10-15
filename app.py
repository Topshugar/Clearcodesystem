from flask import Flask, render_template, Response, request, abort
import os
import datetime
import requests

app = Flask(__name__)

EXCLUDE = {"base.html", "index.html", "tool.html", "builder.html", "clear_shell.html", "ruler_terminal.html", "unlock.html", "marketwatch_demo.html"}

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

def get_country_by_ip():
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip:
            ip = ip.split(',')[0].strip()
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        country = r.text.strip() if r.status_code == 200 else "BH"
        return country
    except:
        return "BH"

def get_all_tools():
    folder = os.path.join(app.root_path, "templates")
    files = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith(".html") and f not in EXCLUDE:
                files.append(f[:-5])
    return sorted(files)

@app.route('/')
def home():
    tools = get_all_tools()
    return render_template('index.html',
        seo_title='ClearCode System - 100+ Free Online Tools for Nigeria, Gulf, UK, USA',
        seo_desc='Free online tools - NIN validator, salary calculator, Bahrain gold price, rent splitter. Fast, secure, no signup.',
        tools=tools
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
        urls.append(f"{base_url}/tools/{t.replace('_', '-')}")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in set(urls):
        xml += f" <url><loc>{url}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>\n"
    xml += "</urlset>"
    return Response(xml, mimetype='application/xml')

@app.route('/tools/<tool_name>')
def tool_page(tool_name):
    tools = get_all_tools()
    if tool_name in tools:
        template = tool_name + ".html"
        country = get_country_by_ip()
        data = GOLD_PRICES.get(country, GOLD_PRICES["BH"])
        return render_template(template,
            seo_title=f'{tool_name.replace("-", " ").replace("_", " ").title()} - Free Tool | ClearCode System',
            seo_desc=f'Free {tool_name.replace("-", " ").replace("_", " ")} tool online.',
            country_code=data["code"],
            country_name=data["name"],
            detected_country=country
        )
    alt = tool_name.replace("-", "_")
    if alt in tools:
        template = alt + ".html"
        country = get_country_by_ip()
        data = GOLD_PRICES.get(country, GOLD_PRICES["BH"])
        return render_template(template,
            seo_title=f'{alt.replace("_", " ").title()} - Free Tool | ClearCode System',
            seo_desc=f'Free {alt.replace("_", " ")} tool online.',
            country_code=data["code"],
            country_name=data["name"],
            detected_country=country
        )
    alt2 = tool_name.replace("_", "-")
    if alt2 in tools:
        template = alt2 + ".html"
        country = get_country_by_ip()
        data = GOLD_PRICES.get(country, GOLD_PRICES["BH"])
        return render_template(template,
            seo_title=f'{tool_name.replace("-", " ").replace("_", " ").title()} - Free Tool | ClearCode System',
            seo_desc=f'Free {tool_name.replace("-", " ").replace("_", " ")} tool online.',
            country_code=data["code"],
            country_name=data["name"],
            detected_country=country
        )
    return abort(404)

def gold_price_bahrain():
    country = get_country_by_ip()
    data = GOLD_PRICES.get(country, GOLD_PRICES["BH"])
    return render_template('gold_bahrain.html',
        seo_title=f'Gold Price {data["name"]} Today - Gold Price in {data["code"]} | ClearCode',
        seo_desc=f'Live gold price in {data["name"]} today in {data["code"]}. Strictly by IP location.',
        price_24k=data["price"],
        price_22k=round(data["price"] * 0.916, 3),
        price_21k=round(data["price"] * 0.875, 3),
        country_code=data["code"],
        country_name=data["name"],
        detected_country=country)

def salary_bahrain():
    country = get_country_by_ip()
    data = GOLD_PRICES.get(country, GOLD_PRICES["BH"])
    return render_template('salary_bahrain.html',
        seo_title=f'Salary Calculator {data["name"]} - {data["code"]} | ClearCode',
        seo_desc=f'Salary calculator {data["name"]} strictly by IP.',
        country_code=data["code"],
        country_name=data["name"],
        detected_country=country)

def rent_bahrain():
    country = get_country_by_ip()
    data = GOLD_PRICES.get(country, GOLD_PRICES["BH"])
    return render_template('rent_bahrain.html',
        seo_title=f'Rent Splitter {data["name"]} - {data["code"]} | ClearCode',
        seo_desc=f'Rent splitter {data["name"]} strictly by IP.',
        country_code=data["code"],
        country_name=data["name"],
        detected_country=country)

if __name__ == '__main__':
    app.run(debug=True)