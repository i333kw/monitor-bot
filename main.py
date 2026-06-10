import os
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USER = os.environ.get("GITHUB_USER")

servers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً! 👋\n\n"
        "الأوامر المتاحة:\n\n"
        "➕ /addserver name url\n"
        "لإضافة سيرفر للمراقبة\n\n"
        "📋 /listservers\n"
        "لعرض السيرفرات\n\n"
        "🔔 /github\n"
        "لعرض آخر إشعارات GitHub\n\n"
        "🐛 /checkcode\n"
        "لفحص كود برمجي"
    )

async def add_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("الاستخدام: /addserver name url")
        return
    name = context.args[0]
    url = context.args[1]
    servers[name] = url
    await update.message.reply_text(f"✅ تمت إضافة {name}")

async def list_servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not servers:
        await update.message.reply_text("❌ لا يوجد سيرفرات مضافة")
        return
    msg = "📋 السيرفرات:\n\n"
    for name, url in servers.items():
        try:
            r = requests.get(url, timeout=5)
            status = "✅ يعمل" if r.status_code == 200 else "⚠️ مشكلة"
        except:
            status = "❌ لا يستجيب"
        msg += f"{name}: {status}\n"
    await update.message.reply_text(msg)

async def github_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GITHUB_TOKEN or not GITHUB_USER:
        await update.message.reply_text("❌ لم يتم إعداد GitHub Token")
        return
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get("https://api.github.com/notifications", headers=headers)
    if r.status_code != 200:
        await update.message.reply_text("❌ خطأ في الاتصال بـ GitHub")
        return
    data = r.json()
    if not data:
        await update.message.reply_text("✅ لا توجد إشعارات جديدة")
        return
    msg = "🔔 إشعارات GitHub:\n\n"
    for n in data[:5]:
        msg += f"• {n['subject']['title']}\n"
        msg += f"  📁 {n['repository']['full_name']}\n\n"
    await update.message.reply_text(msg)

async def check_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل الكود الذي تريد فحصه 👇")

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    issues = []
    if "print " in code:
        issues.append("⚠️ استخدم print() بدلاً من print")
    if "==" in code and "if" not in code:
        issues.append("⚠️ تأكد من استخدام == داخل شرط")
    if "except:" in code:
        issues.append("⚠️ حدد نوع الخطأ في except")
    if not issues:
        await update.message.reply_text("✅ الكود يبدو جيداً!")
    else:
        msg = "🐛 ملاحظات على الكود:\n\n"
        for i in issues:
            msg += f"{i}\n"
        await update.message.reply_text(msg)

async def monitor_loop(app):
    while True:
        for name, url in servers.items():
            try:
                r = requests.get(url, timeout=5)
                if r.status_code != 200:
                    await app.bot.send_message(chat_id=CHAT_ID, text=f"⚠️ {name} يواجه مشكلة!")
            except:
                await app.bot.send_message(chat_id=CHAT_ID, text=f"❌ {name} لا يستجيب!")
        await asyncio.sleep(300)

async def post_init(app):
    asyncio.create_task(monitor_loop(app))

app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addserver", add_server))
app.add_handler(CommandHandler("listservers", list_servers))
app.add_handler(CommandHandler("github", github_notifications))
app.add_handler(CommandHandler("checkcode", check_code))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
app.run_polling()
