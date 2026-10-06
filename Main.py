from flask import Flask, render_template, request, send_file
import io, zipfile, re

app = Flask(__name__)

def safe_package(name):
    name = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    return f"com.clearcode.{name if name else 'app'}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/builder')
def builder():
    return render_template('builder.html')

@app.route('/marketwatch')
def marketwatch():
    return render_template('marketwatch_demo.html')

@app.route('/generate', methods=['POST'])
def generate():
    url = request.form.get('url','').strip()
    app_name_raw = request.form.get('app_name','MyApp').strip()
    app_name = re.sub(r'[^a-zA-Z0-9 ]', '', app_name_raw)[:20] or "MyApp"
    if not url.startswith('http'):
        url = 'https://' + url
    
    package = safe_package(app_name)
    
    # --- ALL ANDROID FILES ---
    manifest_content = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:allowBackup="true" android:label="{app_name}" android:theme="@android:style/Theme.NoTitleBar">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter><action android:name="android.intent.action.MAIN" /><category android:name="android.intent.category.LAUNCHER" /></intent-filter>
        </activity>
    </application>
</manifest>'''

    main_kt = f'''package {package}
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
class MainActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val wv = findViewById<WebView>(R.id.webview)
        wv.webViewClient = WebViewClient()
        wv.settings.javaScriptEnabled = true
        wv.settings.domStorageEnabled = true
        wv.loadUrl("{url}")
    }}
    override fun onBackPressed() {{
        val wv = findViewById<WebView>(R.id.webview)
        if(wv.canGoBack()) wv.goBack() else super.onBackPressed()
    }}
}}'''

    layout_xml = '''<?xml version="1.0" encoding="utf-8"?>
<WebView xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/webview"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />'''

    build_gradle = f'''
plugins {{ id 'com.android.application'; id 'org.jetbrains.kotlin.android' }}
android {{ namespace '{package}'; compileSdk 34
    defaultConfig {{ applicationId "{package}"; minSdk 21; targetSdk 34; versionCode 1; versionName "1.0" }}
    buildTypes {{ release {{ minifyEnabled false }} }}
    compileOptions {{ sourceCompatibility JavaVersion.VERSION_1_8; targetCompatibility JavaVersion.VERSION_1_8 }}
}}
dependencies {{ implementation 'androidx.core:core-ktx:1.12.0'; implementation 'androidx.appcompat:appcompat:1.6.1' }}
'''

    readme = f'''CLEARCODE SYSTEM - APK SOURCE
App: {app_name}
URL: {url}
Package: {package}
Built with ClearCode System Builder - clearcodesystem.onrender.com

STEPS TO BUILD APK:
1. Open Android Studio -> New Project -> Empty Activity
2. Replace files with contents of this ZIP
3. Build -> Build APK(s)
'''

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, 'w') as zf:
        zf.writestr(f"{app_name}/app/src/main/AndroidManifest.xml", manifest_content)
        zf.writestr(f"{app_name}/app/src/main/java/{package.replace('.','/')}/MainActivity.kt", main_kt)
        zf.writestr(f"{app_name}/app/src/main/res/layout/activity_main.xml", layout_xml)
        zf.writestr(f"{app_name}/app/build.gradle", build_gradle)
        zf.writestr(f"{app_name}/README_CLEARCODE.txt", readme)
    mem.seek(0)
    return send_file(mem, download_name=f"{app_name}_by_ClearCode.zip", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
