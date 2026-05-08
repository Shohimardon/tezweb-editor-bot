"""
TezWeb Matn Tahrirlovchi Bot
Guruhda /tahrir yoki teg qilib matn yuboring
"""

import os
import time
import logging
import requests
import threading
import anthropic
from pathlib import Path

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN     = os.environ.get("EDITOR_BOT_TOKEN", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API           = f"https://api.telegram.org/bot{BOT_TOKEN}"
OFFSET_FILE   = "offset.txt"

SYSTEM_PROMPT = """Sen o'zbek tili grammatika ekspertisan.

Foydalanuvchi matn yuborsa:
1. Matnni grammatik jihatdan to'g'irla
2. Imlo xatolarini tuzat
3. Tinish belgilarini to'g'irla
4. 5 xil uslubda qayta yoz

Javobni aniq quyidagi formatda ber (markdown ishlatma):

TUZATILGAN MATN:
[tuzatilgan matn]

XATOLAR:
[qanday xatolar bor edi, qisqacha]

5 VARIANT:

1. Rasmiy uslub:
[matn]

2. Oddiy uslub:
[matn]

3. Ijodiy uslub:
[matn]

4. Qisqa uslub:
[matn]

5. Professional uslub:
[matn]

Faqat o'zbek tilida javob ber."""


def get_offset():
    try:
        return int(Path(OFFSET_FILE).read_text().strip() or "0")
    except Exception:
        return 0

def save_offset(o):
    Path(OFFSET_FILE).write_text(str(o))

def tg_send(chat_id, text, reply_to=None):
    try:
        payload = {"chat_id": chat_id, "text": text[:4096], "disable_web_page_preview": True}
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        r = requests.post(f"{API}/sendMessage", json=payload, timeout=30)
        return r.json()
    except Exception as e:
        logger.error("sendMessage xatosi: %s", e)

def tg_keyboard(chat_id, text, keyboard):
    try:
        requests.post(f"{API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text[:4096],
            "reply_markup": keyboard,
            "disable_web_page_preview": True,
        }, timeout=30)
    except Exception as e:
        logger.error("keyboard xatosi: %s", e)

def tg_typing(chat_id):
    try:
        requests.post(f"{API}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"}, timeout=10)
    except Exception:
        pass

def get_bot_username():
    try:
        r = requests.get(f"{API}/getMe", timeout=10)
        return r.json().get("result", {}).get("username", "")
    except Exception:
        return ""

def ai_edit(text):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Quyidagi matnni tekshirib to'g'irla:\n\n{text}"}]
    )
    return msg.content[0].text

def send_start(chat_id, bot_username):
    keyboard = {"inline_keyboard": [
        [{"text": "➕ Guruhga qo'shish", "url": f"https://t.me/{bot_username}?startgroup=true"}],
        [{"text": "📢 @tezweb_uz", "url": "https://t.me/tezweb_uz"},
         {"text": "🌐 tezweb.uz", "url": "https://tezweb.uz"}],
        [{"text": "💬 @Shohdollar22", "url": "https://t.me/Shohdollar22"}],
    ]}
    tg_keyboard(chat_id,
        "TezWeb Matn Tahrirlovchi Bot\n\n"
        "Men o'zbek tili grammatikasini tekshiruvchi aqlli botman!\n\n"
        "Nima qila olaman:\n"
        "- Grammatik xatolarni topib tuzataman\n"
        "- Imlo va tinish belgilarini tekshiraman\n"
        "- 5 xil uslubda variant taqdim etaman\n\n"
        "Qanday ishlatish:\n"
        "Shaxsiy xabarda: Matnni yuboring\n"
        "Guruhda: /tahrir [matn] yoki @teg orqali\n\n"
        "Misol:\n"
        "/tahrir Men bugun ishga bordim va kop narsalar qildim\n\n"
        "TezWeb.uz botlari:\n"
        "- Matn tahrirlovchi - siz hozir\n"
        "- Antispam boti - @TezWebBot_Antispam\n"
        "- Kontent boti - @tezweb_content_bot\n\n"
        "tezweb.uz | @tezweb_uz | @Shohdollar22",
        keyboard)

def send_info(chat_id, bot_username):
    keyboard = {"inline_keyboard": [
        [{"text": "➕ Guruhga qo'shish", "url": f"https://t.me/{bot_username}?startgroup=true"}],
        [{"text": "Do'stlarga tavsiya", "url": f"https://t.me/share/url?url=https://t.me/{bot_username}&text=O'zbek tili grammatikasini tekshiruvchi aqlli bot!"}],
    ]}
    tg_keyboard(chat_id,
        "Bot haqida\n\n"
        "TezWeb Matn Tahrirlovchi Bot\n\n"
        "Texnologiya: Claude AI (Anthropic)\n"
        "Yaratuvchi: @Shohdollar22\n"
        "Kompaniya: TezWeb.uz\n"
        "Sayt: tezweb.uz\n\n"
        "Funksiyalar:\n"
        "- O'zbek tili grammatikasini tekshirish\n"
        "- Imlo xatolarini tuzatish\n"
        "- 5 xil uslubda variant berish\n"
        "- Guruhda /tahrir buyrug'i bilan ishlash\n"
        "- Guruhda teg orqali ishlash\n"
        "- Shaxsiy xabarda ishlash\n\n"
        "Kanal: @tezweb_uz\n"
        "Bog'lanish: @Shohdollar22",
        keyboard)

def process_text(chat_id, text, msg_id):
    if len(text) < 5:
        tg_send(chat_id, "Minimal 5 ta belgi kiriting.", reply_to=msg_id)
        return
    if len(text) > 3000:
        tg_send(chat_id, f"Matn juda uzun! Maksimal 3000 belgi. Sizniki: {len(text)}", reply_to=msg_id)
        return

    tg_typing(chat_id)
    logger.info("Tekshirilmoqda: %d belgi", len(text))

    try:
        result = ai_edit(text)
        footer = "\n\ntezweb.uz | @tezweb_uz | @Shohdollar22"

        if len(result) + len(footer) > 4096:
            mid = result[:3800].rfind("\n\n")
            if mid == -1:
                mid = 3800
            tg_send(chat_id, result[:mid], reply_to=msg_id)
            tg_send(chat_id, result[mid:].strip() + footer)
        else:
            tg_send(chat_id, result + footer, reply_to=msg_id)

        logger.info("Javob yuborildi")
    except Exception as e:
        logger.error("AI xatosi: %s", e)
        tg_send(chat_id, "Xatolik yuz berdi. Qaytadan urinib ko'ring.\nMuammo: @Shohdollar22", reply_to=msg_id)

def handle_updates():
    offset = get_offset()
    bot_username = get_bot_username()
    logger.info("Bot username: @%s", bot_username)

    while True:
        try:
            r = requests.post(f"{API}/getUpdates", json={
                "offset": offset,
                "timeout": 30,
                "allowed_updates": ["message"]
            }, timeout=40)
            data = r.json()

            if not data.get("ok"):
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                save_offset(offset)

                message = update.get("message", {})
                if not message:
                    continue

                text      = message.get("text", "")
                chat      = message.get("chat", {})
                chat_id   = chat.get("id")
                chat_type = chat.get("type", "")
                msg_id    = message.get("message_id")

                if not text or not chat_id:
                    continue

                # Komanda aniqlash
                parts = text.split()
                cmd = parts[0].lower().split("@")[0] if text.startswith("/") else ""

                # /start /help
                if cmd in ("/start", "/help"):
                    send_start(chat_id, bot_username)
                    continue

                # /info
                if cmd == "/info":
                    send_info(chat_id, bot_username)
                    continue

                # /tahrir - guruhda ham shaxsiy xabarda ham ishlaydi
                if cmd == "/tahrir":
                    tahrir_text = text.replace(parts[0], "", 1).strip()
                    if not tahrir_text:
                        tg_send(chat_id,
                            "Ishlatish: /tahrir [matn]\n\n"
                            "Misol:\n"
                            "/tahrir Men bugun ishga bordim va kop narsalar qildim",
                            reply_to=msg_id)
                        continue
                    process_text(chat_id, tahrir_text, msg_id)
                    continue

                # Guruhda faqat teg yoki reply
                if chat_type in ("group", "supergroup"):
                    is_mention = bot_username and f"@{bot_username}" in text
                    is_reply   = (message.get("reply_to_message", {})
                                  .get("from", {})
                                  .get("username", "") == bot_username)
                    if not is_mention and not is_reply:
                        continue
                    text = text.replace(f"@{bot_username}", "").strip()

                # Shaxsiy xabar - har qanday matn
                if chat_type == "private" and not cmd:
                    process_text(chat_id, text, msg_id)

        except Exception as e:
            logger.error("handle_updates xatosi: %s", e)
            time.sleep(5)

def main():
    if not BOT_TOKEN:
        print("EDITOR_BOT_TOKEN ni Railway Variables ga kiriting!")
        return
    if not ANTHROPIC_KEY:
        print("ANTHROPIC_API_KEY ni Railway Variables ga kiriting!")
        return

    logger.info("TezWeb Editor Bot ishga tushdi!")

    t = threading.Thread(target=handle_updates, daemon=True)
    t.start()

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main())
