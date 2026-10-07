from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Tool list - controls homepage
TOOLS = [
    {"id": 1, "name": "POS Charges Calculator", "desc": "Calculate POS withdrawal charges instantly", "link": "/tools/pos-charges", "icon": "🏧", "file": "pos-charges.html"},
    {"id": 2, "name": "Age Calculator", "desc": "Calculate exact age from DOB", "link": "/tools/age-calculator", "icon": "🎂", "file": "age-calculator.html"},
    {"id": 3, "name": "BVN Checker Format", "desc": "Validate BVN format", "link": "/tools/bvn-checker", "icon": "🏦", "file": "bvn-checker.html"},
    {"id": 4, "name": "Character Counter", "desc": "Count words & characters for captions", "link": "/tools/word-counter", "icon": "📝", "file": "word-counter.html"},
    {"id": 5, "name": "NIN Validator", "desc": "Check NIN format validity", "link": "/tools/nin-validator", "icon": "🪪", "file": "nin-validator.html"},
    {"id": 6, "name": "Love Calculator", "desc": "Fun love compatibility test", "link": "/tools/love-calculator", "icon": "❤️", "file": "love-calculator.html"},
    {"id": 7, "name": "POS Business Daily Profit", "desc": "Track daily POS business profit", "link": "/tools/pos-profit", "icon": "💵", "file": "pos-profit.html"},
    {"id": 8, "name": "Delivery Fee Calculator", "desc": "Calculate delivery fee for Jos vendors", "link": "/tools/delivery-fee", "icon": "🛵", "file": "delivery-fee.html"},
    {"id": 9, "name": "Vendor Profit Calculator", "desc": "Know your real profit after delivery & ads - HOT for IG vendors", "link": "/tools/profit-calculator", "icon": "💰", "file": "profit-calculator.html", "hot": True},
]

@app.route('/')
def home():
    return render_template('index.html', tools=TOOLS)

@app.route('/tools/<tool_name>')
def tool_page(tool_name):
    # map link to file
    # /tools/pos-charges -> pos-charges.html
    filename = f"{tool_name}.html"
    tools_dir = os.path.join(app.root_path, 'tools')
    
    # security check - only allow files in our TOOLS list
    allowed_files = [t['file'] for t in TOOLS]
    if filename not in allowed_files:
        return "Tool not found", 404
    
    if os.path.exists(os.path.join(tools_dir, filename)):
        return send_from_directory(tools_dir, filename)
    else:
        return f"File {filename} not found in /tools folder. Please upload it.", 404

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.root_path, 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.root_path, 'robots.txt')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
