from flask import Flask, render_template, Response, request, abort
import os
import datetime

app = Flask(__name__)

EXCLUDE = {"base.html", "index.html", "tool.html", "builder.html", "clear_shell.html", "ruler_terminal.html", "unlock.html", "marketwatch_demo.html"}

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
    # direct match
    if tool_name in tools:
        template = tool_name + ".html"
        return render_template(template,
            seo_title=f'{tool_name.replace("-", " ").replace("_", " ").title()} - Free Tool | ClearCode System',
            seo_desc=f'Free {tool_name.replace("-", " ").replace("_", " ")} tool online.'
        )
    # try underscore version
    alt = tool_name.replace("-", "_")
    if alt in tools:
        template = alt + ".html"
        return render_template(template,
            seo_title=f'{alt.replace("_", " ").title()} - Free Tool | ClearCode System',
            seo_desc=f'Free {alt.replace("_", " ")} tool online.'
        )
    # try dash version
    alt2 = tool_name.replace("_", "-")
    if alt2 in tools:
        template = alt2 + ".html"
        return render_template(template,
            seo_title=f'{tool_name.replace("-", " ").replace("_", " ").title()} - Free Tool | ClearCode System',
            seo_desc=f'Free {tool_name.replace("-", " ").replace("_", " ")} tool online.'
        )
    return abort(404)

if __name__ == '__main__':
    app.run(debug=True)