from flask import Flask, render_template, request, send_file, flash, redirect
import os, zipfile, tempfile, re, shutil, json
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "clearcode-v2-2026"

ALLOWED_ICON = {'png','jpg','jpeg'}

def is_valid_url(url):
    try:
        result = urlparse(url)
        if not result.scheme.startswith('http'): return False
        # block private IPs
        bad = ['localhost','127.0.0.1','192.168.','10.','0.0.0.0']
        if any(x in url for x in bad): return False
        return True
    except: return False

MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.clearcode.{pkg}">
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:allowBackup="true" android:icon="@mipmap/ic_launcher" android:label="{app_name}" android:theme="@android:style/Theme.NoTitleBar">
        <activity android:name=".MainActivity" android:exported="true"><intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter></activity>
    </application>
</manifest>"""

MAIN_ACTIVITY = """
package com.clearcode.{pkg};
import android.app.Activity; import android.os.Bundle; import android.webkit.WebView; import android.webkit.WebViewClient;
public class MainActivity extends Activity {{
    WebView webView;
    @Override protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("{url}");
        setContentView(webView);
    }}
    @Override public void onBackPressed() {{ if(webView.canGoBack()) webView.goBack(); else super.onBackPressed(); }}
}}
"""

BUILD_GRADLE = """
plugins { id 'com.android.application' }
android { namespace 'com.clearcode.{pkg}' compileSdk 34
 defaultConfig { applicationId "com.clearcode.{pkg}" minSdk 21 targetSdk 34 versionCode 1 versionName "1.0" }
 buildTypes { release { minifyEnabled false } } }
dependencies { implementation 'androidx.appcompat:appcompat:1.6.1' }
"""

@app.route('/')
def home(): return render_template('index.html')

@app.route('/builder')
def builder(): return render_template('builder.html')

@app.route('/marketwatch')
def marketwatch(): return render_template('marketwatch_demo.html')

@app.route('/generate', methods=['POST'])
def generate():
    app_name = request.form.get('app_name','MyApp').strip()
    url = request.form.get('url','').strip()
    if not is_valid_url(url): return "Invalid URL. Must start with https:// and not be localhost", 400
    if len(app_name) < 2: app_name = "MyApp"
    pkg = re.sub(r'[^a-z0-9]', '', app_name.lower())[:15] or "myapp"
    
    # Lead saving
    with open("leads.txt","a") as f: f.write(f"{app_name},{url},{request.remote_addr},{request.form.get('phone','')}\n")

    tmp = tempfile.mkdtemp()
    project_dir = os.path.join(tmp, f"{app_name}_Android_Project")
    src_path = os.path.join(project_dir, f"app/src/main/java/com/clearcode/{pkg}")
    res_path = os.path.join(project_dir, "app/src/main/res/mipmap")
    os.makedirs(src_path, exist_ok=True)
    os.makedirs(res_path, exist_ok=True)

    # Manifest
    with open(os.path.join(project_dir, "app/src/main/AndroidManifest.xml"),"w") as f:
        f.write(MANIFEST.format(pkg=pkg, app_name=app_name))
    # MainActivity
    with open(os.path.join(src_path, "MainActivity.java"),"w") as f:
        f.write(MAIN_ACTIVITY.format(pkg=pkg, url=url))
    # build.gradle
    with open(os.path.join(project_dir, "app/build.gradle"),"w") as f:
        f.write(BUILD_GRADLE.format(pkg=pkg))
    # config.json
    with open(os.path.join(project_dir, "config.json"),"w") as f:
        json.dump({"app_name":app_name,"url":url,"builder":"ClearCode System Abuja"}, f, indent=2)
    # Icon upload
    icon = request.files.get('icon')
    if icon and icon.filename:
        ext = icon.filename.rsplit('.',1)[-1].lower()
        if ext in ALLOWED_ICON:
            icon_path = os.path.join(res_path, "ic_launcher.png")
            icon.save(icon_path)

    # README
    with open(os.path.join(project_dir, "README.txt"),"w") as f:
        f.write(f"ClearCode System\nApp: {app_name}\nURL: {url}\n\nHOW TO BUILD APK:\n1. Open this folder in Android Studio\n2. Click Build > Build APK\n3. APK will be in app/build/outputs/\n\nOr upload this zip to https://appetize.io or use GitHub Actions to auto build.\n")

    # Zip it
    zip_path = os.path.join(tmp, f"{app_name}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                full = os.path.join(root,file)
                rel = os.path.relpath(full, project_dir)
                z.write(full, rel)

    return send_file(zip_path, as_attachment=True, download_name=f"{app_name}_Android_Project.zip")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000) 
