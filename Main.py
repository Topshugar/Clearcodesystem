from flask import Flask, render_template, request, send_file
import io, zipfile

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/builder')
def builder():
    return render_template('builder.html')

@app.route('/generate', methods=['POST'])
def generate():
    url = request.form.get('url', '').strip()
    app_name = request.form.get('app_name', 'MyApp').strip()
    if not url.startswith('http'):
        url = 'https://' + url

    # Generate the Android files content
    manifest = f'''<uses-permission android:name="android.permission.INTERNET" />'''
    
    main_kt = f'''
package com.clearcode.system

import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val webView = findViewById<WebView>(R.id.webview)
        webView.webViewClient = WebViewClient()
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.loadUrl("{url}")
    }}
}}
'''

    # Create zip in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        zf.writestr(f"{app_name}/MainActivity.kt", main_kt)
        zf.writestr(f"{app_name}/README.txt", f"ClearCode System - APK Source\nApp: {app_name}\nURL: {url}\n\n1. Create new Empty Activity in Android Studio\n2. Replace MainActivity.kt with this file\n3. Add internet permission in AndroidManifest.xml\n4. Build APK")
    memory_file.seek(0)
    
    return send_file(memory_file, download_name=f"{app_name}_ClearCode_Source.zip", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True) 
