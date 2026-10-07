from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

TOOLS = [
    {"id": "01", "name": "APK Builder", "link": "/tools/apk-builder", "file": "apk-builder.html"},
    {"id": "02", "name": "Ruler Terminal", "link": "/tools/ruler-terminal", "file": "ruler-terminal.html"},
    {"id": "03", "name": "WhatsApp QR Generator", "link": "/tools/whatsapp-qr", "file": "whatsapp-qr.html"},
    {"id": "04", "name": "Invoice Generator", "link": "/tools/invoice-generator", "file": "invoice-generator.html"},
    {"id": "05", "name": "BG Remover - HOT", "link": "/tools/bg-remover", "file": "bg-remover.html"},
    {"id": "06", "name": "Fake Alert Checker", "link": "/tools/fake-alert", "file": "fake-alert.html"},
    {"id": "07", "name": "POS Charges Calculator", "link": "/tools/pos-charges", "file": "pos-charges.html"},
    {"id": "08", "name": "Delivery Fee Calculator", "link": "/tools/delivery-fee", "file": "delivery-fee.html"},
]

@app.route('/')
def home():
    return render_template('index.html', tools=TOOLS)

@app.route('/tools/<tool_name>')
def tool_page(tool_name):
    tools_dir = os.path.join(app.root_path, 'tools')
    filename = f"{tool_name}.html"
    full_path = os.path.join(tools_dir, filename)
    
    if os.path.exists(full_path):
        return send_from_directory(tools_dir, filename)
    
    alt_names = [
        f"{tool_name}.html",
        f"{tool_name.replace('-', '_')}.html",
        f"{tool_name.replace('_', '-')}.html"
    ]
    for alt in alt_names:
        if os.path.exists(os.path.join(tools_dir, alt)):
            return send_from_directory(tools_dir, alt)
            
    return f"Tool {tool_name} not found. Check tools folder has {filename}", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
