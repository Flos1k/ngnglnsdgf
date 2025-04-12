from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ Бот работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import datetime

# 🔑 API-ключи для запроса к callerapi
API_KEYS = [
    'd414a23d-c22e-4a7b-aebd-31e26fd73b01',
    '5de8ddfd-e434-4913-88fa-fd3feb0e9d24',
    '181a4965-dbda-4d58-b450-2e251195d73e',
    '5b0a4f65-c41e-43f0-a674-feb9754cc321',
    '648d6e6e-faa6-42ff-809c-75f0c735a887',
    'b15a6afd-df5e-4065-86ea-16b4467228ae',
    'ead57f17-04b2-4a3b-994b-9f4b60cabf9f',
    'b53c1bcc-34b1-4f95-8ac0-d7184f4b367e',
    '2217dec8-e988-42f0-be88-74c48592a20b',
    '8fac49d8-0fca-4501-8cc1-2ae3b20a76dd',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    ''
]

BOT_TOKEN = "7671549843:AAHTOyWWuqTj0jb0QhGZQqIr2xphBG-EX3A"

# 🔐 Ключи доступа и ограничения
keys = {
    # 3 ключа на 2 запроса
    "lvBLdQ9YAC-0XYMY#m8M": ["uses", 2],
    "O&(M00*kfnHV#$*mG5d-": ["uses", 2],
    "t(>sp)l^G9=U-KwlZjEZ": ["uses", 2],

    # 5 ключей на 1 день
    "2C&MVv3jS_P-=80#6btm": ["date", datetime.datetime.now() + datetime.timedelta(days=1)],
    "4T7a>Rv&Tw@V%$#tEZ9U": ["date", datetime.datetime.now() + datetime.timedelta(days=1)],
    "_@=v4o=M>h43*HyPgvt<": ["date", datetime.datetime.now() + datetime.timedelta(days=1)],
    "kjrvz1RthY2FXv>&B%<8": ["date", datetime.datetime.now() + datetime.timedelta(days=1)],
    "y2D@kqHMaTv6_Cnofy!F": ["date", datetime.datetime.now() + datetime.timedelta(days=1)],

    # 5 ключей на неделю
    "E8Cw=Tw3T1vq2KW*t-Za": ["date", datetime.datetime.now() + datetime.timedelta(weeks=1)],
    "G#X7$9WvZAph%+9jr=@*": ["date", datetime.datetime.now() + datetime.timedelta(weeks=1)],
    "cyy@EeQ-Q$-5_yPjN03d": ["date", datetime.datetime.now() + datetime.timedelta(weeks=1)],
    "q#3F)jvxg(BX_cq0qRX^": ["date", datetime.datetime.now() + datetime.timedelta(weeks=1)],
    "^4_3D_WG4cpuNgi9)92N": ["date", datetime.datetime.now() + datetime.timedelta(weeks=1)],

    # 5 ключей на 1 запрос
    "R1qZ@1kPo*&p=V^yk0MH": ["uses", 1],
    "6=bjG+UYeC8+1NCwzqZ#": ["uses", 1],
    "k3%8X*Tr2qXTDko<4dEe": ["uses", 1],
    "W(^DN<JuVwZ&3qFeKGHZ": ["uses", 1],
    "t@8K_#o4!3vhN(MhQ7cu": ["uses", 1],

# 5 ключей навсегда
    "2N&Ugs1=^0^h8k+BY&NS": ["forever", None],
    "u^8tHaWwc^sKyw1fB_hS": ["forever", None],
    "5(lHa#K@%l@i*s&!eYk(": ["forever", None],
    "P+bPQD8UDuKyPVmHq7re": ["forever", None],
    "oQ+d)6fugYsil=zCvJNu": ["forever", None],
}

user_access = {}

# 🔍 Поиск имени по данным

def find_name(data):
    if isinstance(data, dict):
        for key in data:
            if key.lower() in ["name", "caller_name", "caller name"]:
                val = data[key]
                if isinstance(val, str) and val.strip():
                    return val
            found = find_name(data[key])
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = find_name(item)
            if found:
                return found
    return None

# 🔧 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_access:
        await update.message.reply_text("✅ Вы уже активировали доступ. Напиши номер для поиска.")
    else:
        await update.message.reply_text("👋 Привет! Введите ключ доступа для использования бота:")

# 🔍 Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_access:
        if text in keys:
            access_type, value = keys[text]
            if access_type == "uses":
                user_access[user_id] = ["uses", value]
            elif access_type == "date":
                user_access[user_id] = ["date", value]
            elif access_type == "forever":
                user_access[user_id] = ["forever", None]
            await update.message.reply_text("🔓 Ключ принят! Теперь отправьте номер телефона для поиска.")
        else:
            await update.message.reply_text("❌ Неверный ключ. Повторите ввод.")
        return

    # Проверка доступа
    access_type, value = user_access[user_id]
    if access_type == "uses":
        if value <= 0:
            await update.message.reply_text("❌ Лимит запросов по вашему ключу исчерпан.")
            return
        user_access[user_id][1] -= 1
    elif access_type == "date":
        if datetime.datetime.now() > value:
            await update.message.reply_text("⏰ Срок действия ключа истёк.")
            return

    # Запрос по номеру
    await update.message.reply_text(f"🔎 Начинаю поиск по номеру: {text}...")
    url_template = f"https://callerapi.com/api/phone/info/{text}"

    for key in API_KEYS:
        headers = {"X-Auth": key}
        try:
            r = requests.get(url_template, headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                name = find_name(data)
                if name:
                    await update.message.reply_text(f"✅ Имя: {name}")
                else:
                    await update.message.reply_text("❌ Имя не найдено.")
                return
        except Exception:
            continue

    await update.message.reply_text("❗ Все ключи не сработали или сервер недоступен.")

# 🚀 Запуск бота
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
