import os
import requests

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USER = os.environ.get("GITHUB_USER")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def check_servers():
    servers = {
        "Google": "https://google.com",
        "GitHub": "https://github.com",
    }
    msg = "🖥 حالة السيرفرات:\n\n"
    for name, url in servers.items():
        try:
            r = requests.get(url, timeout=5)
            status = "✅ يعمل" if r.status_code == 200 else "⚠️ مشكلة"
        except:
            status = "❌ لا يستجيب"
        msg += f"{name}: {status}\n"
    send(msg)

def check_github():
    if not GITHUB_TOKEN:
        return
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get("https://api.github.com/notifications", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data:
            msg = "🔔 إشعارات GitHub:\n\n"
            for n in data[:5]:
                msg += f"• {n['subject']['title']}\n"
            send(msg)

check_servers()
check_github()
