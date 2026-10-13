from flask import Flask, render_template, request, jsonify, Response
import qrcode, os, io, base64, requests
from datetime import datetime
from collections import Counter
import paramiko
from PIL import Image

REMBG_AVAILABLE = False
human_session = None
cloth_session = None

def get_session(mode='human'):
    global human_session, cloth_session, REMBG_AVAILABLE
    try:
        from rembg import remove, new_session
        REMBG_AVAILABLE = True
        if mode == 'human' and human_session is None:
            try: human_session = new_session("u2net_human_seg")
            except: human_session = True
        elif cloth_session is None:
            try: cloth_session = new_session("isnet-general-use")
            except: cloth_session = True
        return True
    except Exception as e:
        print(f"rembg error: {e}")
        return False

app = Flask(__name__)

# ===== CLEAN ADMIN CONFIG - SECRET =====
ADMIN_KEY = "CLEARCODE2026"
ANALYTICS = [] # last 5000 hits
DISABLED_TOOLS = set() # format "NG:lagos-rent-package" etc

# 9 COUNTRIES - 85 TOOLS - GULF VIRAL ONLY IN GULF + IVR EVERYWHERE
COUNTRY_TOOLS = {
 'NG': ['nepa_calculator','cac_checker','fuel_calculator','rent_splitter','land_converter','paye_calculator','jamb_calculator','waec_calculator','nin_validator','pos_charges','wa_qr','whatsapp_broadcast','invoice','bg_remover','delivery_fee','fake_text','debt_book','price_tag','profit_calc','ruler_terminal','clear_shell','market_ledger','builder','pos_receipt','lagos_rent_package','ivr_builder'],
 'US': ['paycheck','background_check','tip_calculator','usa_notify','builder','pos_receipt','ivr_builder'],
 'SA': ['iqama_expiry','hijri_converter','gosi_calculator','zatca_qr','gpa_calculator','salary_sa','builder','pos_receipt','ivr_builder','salary_flex','anonymous_link','arabic_stylish_name'],
 'QA': ['qid_check','qatar_traffic_fines','qatar_gratuity','qatar_rent_splitter','qatar_gold_price','qatar_overtime','builder','pos_receipt','ivr_builder','salary_flex','anonymous_link','arabic_stylish_name'],
 'AE': ['emirates_id_check','uae_traffic_fines','uae_gratuity','uae_gold_price','uae_rent_splitter','uae_overtime','uae_salary','builder','pos_receipt','ivr_builder','salary_flex','anonymous_link','arabic_stylish_name'],
 'KW': ['kuwait_civil_id','kuwait_traffic_fines','kuwait_gratuity','kuwait_gold_price','kuwait_rent','kuwait_overtime','builder','pos_receipt','ivr_builder','salary_flex','anonymous_link','arabic_stylish_name'],
 'BH': ['bahrain_cpr_check','bahrain_traffic_fines','bahrain_gratuity','bahrain_gold_price','bahrain_rent','bahrain_overtime','builder','pos_receipt','ivr_builder','salary_flex','anonymous_link','arabic_stylish_name'],
 'OM': ['oman_civil_check','oman_traffic_fines','oman_gratuity','oman_gold_price','oman_rent','oman_overtime','builder','pos_receipt','ivr_builder','salary_flex','anonymous_link','arabic_stylish_name'],
 'UK': ['uk_paycheck','uk_rent_splitter','uk_tip_calculator','uk_vat_calculator','builder','pos_receipt','ivr_builder'],
}

COUNTRY_NAME = {
'NG':'🇳🇬 Nigeria','US':'🇺🇸 USA','SA':'🇸🇦 Saudi','QA':'🇶🇦 Qatar','AE':'🇦🇪 UAE','KW':'🇰🇼 Kuwait',
'BH':'🇧🇭 Bahrain','OM':'🇴🇲 Oman','UK':'🇬🇧 UK',
'GH':'🇳🇬 Nigeria','KE':'🇳🇬 Nigeria','CA':'🇺🇸 USA','GB':'🇬🇧 UK','AU':'🇺🇸 USA','EG':'🇸🇦 Saudi'
}

IP_CACHE = {}

def get_country():
    forced = request.args.get('country') or request.args.get('c')
    if forced and forced.upper() in COUNTRY_TOOLS:
        return forced.upper()
    try:
        cf = request.headers.get('CF-IPCountry')
        if cf and len(cf)==2 and cf.upper()!='XX':
            return cf.upper()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()
        if ip in ['127.0.0.1','::1',''] or ip.startswith('192.'):
            return 'NG'
        if ip in IP_CACHE:
            return IP_CACHE[ip]
        r = requests.get(f'https://ipapi.co/{ip}/country/', timeout=2)
        code = r.text.strip().upper()
        if len(code)==2:
            IP_CACHE[ip]=code
            return code
        return 'NG'
    except:
        return 'NG'

def map_to_group(code):
    code = code.upper()
    if code in COUNTRY_TOOLS: return code
    if code in ['GH','KE','ZA','NG']: return 'NG'
    if code in ['US','CA','AU']: return 'US'
    if code in ['SA','EG']: return 'SA'
    if code in ['QA']: return 'QA'
    if code in ['AE']: return 'AE'
    if code in ['KW']: return 'KW'
    if code in ['BH']: return 'BH'
    if code in ['OM']: return 'OM'
    if code in ['GB','UK']: return 'UK'
    return 'NG'

# ===== TRACK CLEAN - BEFORE REQUEST =====
@app.before_request
def track_clean():
    if request.path.startswith('/tool/'):
        try:
            tool = request.path.split('/')[-1].replace('-','_')
            raw = get_country()
            country = map_to_group(raw)
            ANALYTICS.append({
                "tool": tool,
                "country": country,
                "raw": raw,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ip": request.headers.get('X-Forwarded-For', request.remote_addr)[:20]
            })
            if len(ANALYTICS) > 5000:
                ANALYTICS.pop(0)
        except:
            pass

@app.route('/')
def home():
    raw_country = get_country()
    country = map_to_group(raw_country)
    allowed = COUNTRY_TOOLS.get(country, COUNTRY_TOOLS['NG'])
    # filter disabled
    allowed = [t for t in allowed if f"{country}:{t}" not in DISABLED_TOOLS and f"{country}:{t.replace('_','-')}" not in DISABLED_TOOLS]
    display_name = COUNTRY_NAME.get(raw_country, COUNTRY_NAME.get(country, f'🌍 {country}'))
    return render_template('index.html', country=country, raw_country=raw_country, country_name=display_name, allowed=allowed, all_groups=COUNTRY_TOOLS)

# -- STATIC ROUTES --
@app.route('/unlock')
def unlock(): return render_template('unlock.html')

def render_with_country(template_name):
    raw=get_country(); country=map_to_group(raw)
    # check disabled
    tool_key = template_name.replace('.html','')
    if f"{country}:{tool_key}" in DISABLED_TOOLS or f"{country}:{tool_key.replace('_','-')}" in DISABLED_TOOLS:
        return "<h2 style='background:#080808;color:#fff;padding:40px;text-align:center'>Tool temporarily disabled in your region</h2>", 403
    return render_template(template_name, country=country, raw_country=raw, country_name=COUNTRY_NAME.get(raw, COUNTRY_NAME.get(country)))

@app.route('/tool/builder')
@app.route('/tool/store-builder')
def builder(): return render_with_country('builder.html')
@app.route('/tool/pos-receipt')
@app.route('/tool/receipt-generator')
def pos_receipt(): return render_with_country('pos_receipt.html')

@app.route('/tool/salary-flex')
def salary_flex(): return render_with_country('salary_flex.html')
@app.route('/tool/anonymous-link')
@app.route('/tool/saraha')
def anonymous_link(): return render_with_country('anonymous_link.html')
@app.route('/tool/arabic-stylish-name')
@app.route('/tool/stylish-name')
@app.route('/tool/zakharfa')
def arabic_stylish_name(): return render_with_country('arabic_stylish_name.html')

@app.route('/tool/wa-qr')
def wa_qr(): return render_with_country('wa_qr.html')
@app.route('/tool/invoice')
def invoice(): return render_with_country('invoice.html')
@app.route('/tool/bg-remover')
def bg_remover(): return render_with_country('bg_remover.html')
@app.route('/tool/pos-charges')
def pos_charges(): return render_with_country('pos_charges.html')
@app.route('/tool/delivery-fee')
def delivery_fee(): return render_with_country('delivery_fee.html')
@app.route('/tool/price-tag')
def price_tag(): return render_with_country('price_tag.html')
@app.route('/tool/profit-calc')
def profit_calc(): return render_with_country('profit_calculator.html')
@app.route('/tool/debt-book')
def debt_book(): return render_with_country('debt_book.html')
@app.route('/tool/ruler-terminal')
def ruler_terminal(): return render_with_country('ruler_terminal.html')
@app.route('/tool/clear-shell')
def clear_shell(): return render_with_country('clear_shell.html')
@app.route('/tool/market-ledger')
def market_ledger(): return render_with_country('market_ledger.html')
@app.route('/tool/usa-notify')
def usa_notify(): return render_with_country('usa_notify.html')
@app.route('/tool/paycheck')
def paycheck(): return render_with_country('paycheck.html')
@app.route('/tool/fake-text')
def fake_text(): return render_with_country('fake_text.html')
@app.route('/tool/tip-calculator')
def tip_calculator(): return render_with_country('tip_calculator.html')
@app.route('/tool/whatsapp-broadcast')
@app.route('/tool/whatsapp_broadcast')
def whatsapp_broadcast(): return render_with_country('whatsapp_broadcast.html')
@app.route('/tool/background-check')
@app.route('/tool/usa-background-check')
@app.route('/tool/background_check')
def background_check(): return render_with_country('usa_background_check.html')

@app.route('/tool/iqama-expiry')
def iqama_expiry(): return render_with_country('iqama_expiry.html')
@app.route('/tool/hijri-converter')
def hijri_converter(): return render_with_country('hijri_converter.html')
@app.route('/tool/gosi-calculator')
def gosi_calculator(): return render_with_country('gosi_calculator.html')
@app.route('/tool/zatca-qr')
def zatca_qr(): return render_with_country('zatca_qr.html')
@app.route('/tool/gpa-calculator')
def gpa_calculator(): return render_with_country('gpa_calculator.html')
@app.route('/tool/salary-sa')
def salary_sa(): return render_with_country('salary_sa.html')

@app.route('/tool/nepa-calculator')
def nepa_calculator(): return render_with_country('nepa_calculator.html')
@app.route('/tool/cac-checker')
def cac_checker(): return render_with_country('cac_checker.html')
@app.route('/tool/fuel-calculator')
def fuel_calculator(): return render_with_country('fuel_calculator.html')
@app.route('/tool/rent-splitter')
def rent_splitter(): return render_with_country('rent_splitter.html')
@app.route('/tool/land-converter')
def land_converter(): return render_with_country('land_converter.html')
@app.route('/tool/paye-calculator')
def paye_calculator(): return render_with_country('paye_calculator.html')
@app.route('/tool/jamb-calculator')
def jamb_calculator(): return render_with_country('jamb_calculator.html')
@app.route('/tool/waec-calculator')
def waec_calculator(): return render_with_country('waec_calculator.html')
@app.route('/tool/nin-validator')
def nin_validator(): return render_with_country('nin_validator.html')
@app.route('/tool/lagos-rent-package')
def lagos_rent_package(): return render_with_country('lagos_rent_package.html')
@app.route('/tool/ivr-builder')
def ivr_builder(): return render_with_country('ivr_builder.html')

@app.route('/tool/qid-check')
def qid_check(): return render_with_country('qid_check.html')
@app.route('/tool/qatar-traffic-fines')
def qatar_traffic_fines(): return render_with_country('qatar_traffic_fines.html')
@app.route('/tool/qatar-gratuity')
def qatar_gratuity(): return render_with_country('qatar_gratuity.html')
@app.route('/tool/qatar-rent-splitter')
def qatar_rent_splitter(): return render_with_country('qatar_rent_splitter.html')
@app.route('/tool/qatar-gold-price')
def qatar_gold_price(): return render_with_country('qatar_gold_price.html')
@app.route('/tool/qatar-overtime')
def qatar_overtime(): return render_with_country('qatar_overtime.html')

@app.route('/tool/emirates-id-check')
def emirates_id_check(): return render_with_country('emirates_id_check.html')
@app.route('/tool/uae-traffic-fines')
def uae_traffic_fines(): return render_with_country('uae_traffic_fines.html')
@app.route('/tool/uae-gratuity')
def uae_gratuity(): return render_with_country('uae_gratuity.html')
@app.route('/tool/uae-gold-price')
def uae_gold_price(): return render_with_country('uae_gold_price.html')
@app.route('/tool/uae-rent-splitter')
def uae_rent_splitter(): return render_with_country('uae_rent_splitter.html')
@app.route('/tool/uae-overtime')
def uae_overtime(): return render_with_country('uae_overtime.html')
@app.route('/tool/uae-salary')
def uae_salary(): return render_with_country('uae_salary.html')

@app.route('/tool/kuwait-civil-id')
def kuwait_civil_id(): return render_with_country('kuwait_civil_id.html')
@app.route('/tool/kuwait-traffic-fines')
def kuwait_traffic_fines(): return render_with_country('kuwait_traffic_fines.html')
@app.route('/tool/kuwait-gratuity')
def kuwait_gratuity(): return render_with_country('kuwait_gratuity.html')
@app.route('/tool/kuwait-gold-price')
def kuwait_gold_price(): return render_with_country('kuwait_gold_price.html')
@app.route('/tool/kuwait-rent')
def kuwait_rent(): return render_with_country('kuwait_rent.html')
@app.route('/tool/kuwait-overtime')
def kuwait_overtime(): return render_with_country('kuwait_overtime.html')

@app.route('/tool/bahrain-cpr-check')
def bahrain_cpr_check(): return render_with_country('bahrain_cpr_check.html')
@app.route('/tool/bahrain-traffic-fines')
def bahrain_traffic_fines(): return render_with_country('bahrain_traffic_fines.html')
@app.route('/tool/bahrain-gratuity')
def bahrain_gratuity(): return render_with_country('bahrain_gratuity.html')
@app.route('/tool/bahrain-gold-price')
def bahrain_gold_price(): return render_with_country('bahrain_gold_price.html')
@app.route('/tool/bahrain-rent')
def bahrain_rent(): return render_with_country('bahrain_rent.html')
@app.route('/tool/bahrain-overtime')
def bahrain_overtime(): return render_with_country('bahrain_overtime.html')

@app.route('/tool/oman-civil-check')
def oman_civil_check(): return render_with_country('oman_civil_check.html')
@app.route('/tool/oman-traffic-fines')
def oman_traffic_fines(): return render_with_country('oman_traffic_fines.html')
@app.route('/tool/oman-gratuity')
def oman_gratuity(): return render_with_country('oman_gratuity.html')
@app.route('/tool/oman-gold-price')
def oman_gold_price(): return render_with_country('oman_gold_price.html')
@app.route('/tool/oman-rent')
def oman_rent(): return render_with_country('oman_rent.html')
@app.route('/tool/oman-overtime')
def oman_overtime(): return render_with_country('oman_overtime.html')

@app.route('/tool/uk-paycheck')
def uk_paycheck(): return render_with_country('uk_paycheck.html')
@app.route('/tool/uk-rent-splitter')
def uk_rent_splitter(): return render_with_country('uk_rent_splitter.html')
@app.route('/tool/uk-tip-calculator')
def uk_tip_calculator(): return render_with_country('uk_tip_calculator.html')
@app.route('/tool/uk-vat-calculator')
def uk_vat_calculator(): return render_with_country('uk_vat_calculator.html')

# ===== SECRET ADMIN - ONLY YOU =====
@app.route('/admin/analytics')
def admin_analytics():
    if request.args.get('key')!= ADMIN_KEY:
        return "Unauthorized", 403
    tools = Counter([a['tool'] for a in ANALYTICS])
    countries = Counter([a['country'] for a in ANALYTICS])
    last = ANALYTICS[-30:][::-1]
    return f"""
    <html style="background:#080808;color:#fff;font-family:monospace;padding:20px">
    <h2>📊 ClearCode Analytics - Clean</h2>
    <p>Total Hits: {len(ANALYTICS)} | Disabled: {list(DISABLED_TOOLS)[:20]}</p>
    <h3>Top Tools</h3><pre>{tools.most_common(20)}</pre>
    <h3>Top Countries</h3><pre>{countries.most_common(20)}</pre>
    <h3>Last 30</h3><pre>{last}</pre>
    <hr><a href="/admin/tools?key={ADMIN_KEY}" style="color:#00FF88">Go to Tools Manager →</a>
    </html>
    """

@app.route('/admin/tools')
def admin_tools_manager():
    if request.args.get('key')!= ADMIN_KEY:
        return "Unauthorized", 403
    action = request.args.get('action')
    tool = request.args.get('tool')
    if action == 'disable' and tool:
        DISABLED_TOOLS.add(tool)
    if action == 'enable' and tool:
        DISABLED_TOOLS.discard(tool)
    html = f"<html style='background:#080808;color:#fff;font-family:monospace;padding:20px'><h2>🛠️ Tools Manager - {len(COUNTRY_TOOLS)} groups</h2><p>Click OFF to hide in that country only</p>"
    for c in COUNTRY_TOOLS:
        html += f"<h3>{c}</h3>"
        for t in COUNTRY_TOOLS[c]:
            key = f"{c}:{t}"
            key2 = f"{c}:{t.replace('_','-')}"
            status = "🔴 OFF" if key in DISABLED_TOOLS or key2 in DISABLED_TOOLS else "🟢 ON"
            html += f"{status} {key} - <a style='color:#FF0040' href='/admin/tools?key={ADMIN_KEY}&action=disable&tool={key}'>OFF</a> | <a style='color:#00FF88' href='/admin/tools?key={ADMIN_KEY}&action=enable&tool={key}'>ON</a><br>"
    html += f"<hr><a href='/admin/analytics?key={ADMIN_KEY}' style='color:#00FF88'>Back to Analytics</a></html>"
    return html

@app.route('/sitemap.xml')
def sitemap():
    tools = ['nepa-calculator','cac-checker','fuel-calculator','rent-splitter','land-converter','paye-calculator','jamb-calculator','waec-calculator','nin-validator','lagos-rent-package','ivr-builder','qid-check','qatar-traffic-fines','qatar-gratuity','qatar-rent-splitter','qatar-gold-price','qatar-overtime','emirates-id-check','uae-traffic-fines','uae-gratuity','uae-gold-price','uae-rent-splitter','uae-overtime','uae-salary','kuwait-civil-id','kuwait-traffic-fines','kuwait-gratuity','kuwait-gold-price','kuwait-rent','kuwait-overtime','builder','pos-receipt','wa-qr','invoice','bg-remover','pos-charges','delivery-fee','price-tag','profit-calc','debt-book','ruler-terminal','clear-shell','market-ledger','usa-notify','paycheck','fake-text','tip-calculator','whatsapp-broadcast','background-check','iqama-expiry','hijri-converter','gosi-calculator','zatca-qr','gpa-calculator','salary-sa','bahrain-cpr-check','bahrain-traffic-fines','bahrain-gratuity','bahrain-gold-price','bahrain-rent','bahrain-overtime','oman-civil-check','oman-traffic-fines','oman-gratuity','oman-gold-price','oman-rent','oman-overtime','uk-paycheck','uk-rent-splitter','uk-tip-calculator','uk-vat-calculator','salary-flex','anonymous-link','arabic-stylish-name']
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += '<url><loc>https://clearcodesystem.onrender.com/</loc><priority>1.0</priority></url>'
    for t in tools:
        xml += f'<url><loc>https://clearcodesystem.onrender.com/tool/{t}</loc><priority>0.8</priority><changefreq>weekly</changefreq></url>'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    txt = "User-agent: *\nAllow: /\nDisallow: /unlock\nDisallow: /api/\nDisallow: /admin/\nSitemap: https://clearcodesystem.onrender.com/sitemap.xml"
    return Response(txt, mimetype='text/plain')

@app.route('/api/lagos-rent', methods=['POST'])
def api_lagos_rent():
    try:
        data = request.json or {}
        rent = float(data.get('rent', 0))
        if rent <= 0: 
            return jsonify({'error':'Enter valid rent amount'}), 400
        if rent < 10000: 
            return jsonify({'error':'Rent too low'}), 400
        location = (data.get('location') or 'mainland').lower()
        config = {
            'mainland': {'agreement':10, 'commission':10, 'damages':5, 'caution':5, 'legal':5, 'inspection':3000, 'label':'Mainland'},
            'yaba': {'agreement':10, 'commission':10, 'damages':10, 'caution':10, 'legal':5, 'inspection':5000, 'label':'Yaba'},
            'ikeja': {'agreement':10, 'commission':10, 'damages':10, 'caution':10, 'legal':10, 'inspection':7000, 'label':'Ikeja'},
            'lekki': {'agreement':10, 'commission':10, 'damages':10, 'caution':10, 'legal':10, 'inspection':10000, 'label':'Lekki'},
            'vi': {'agreement':10, 'commission':10, 'damages':15, 'caution':15, 'legal':10, 'inspection':15000, 'label':'VI'},
        }
        c = config.get(location, config['mainland'])
        agreement = rent * c['agreement'] / 100
        commission = rent * c['commission'] / 100
        damages = rent * c['damages'] / 100
        caution = rent * c['caution'] / 100
        legal = rent * c['legal'] / 100
        inspection = c['inspection']
        total = rent + agreement + commission + damages + caution + legal + inspection
        monthly = total / 12
        return jsonify({
            'rent': int(rent),
            'agreement': int(agreement),
            'commission': int(commission),
            'damages': int(damages),
            'caution': int(caution),
            'legal': int(legal),
            'inspection': int(inspection),
            'total': int(total),
            'monthly': int(monthly),
            'location': location,
            'location_label': c['label']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500