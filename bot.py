"""
TezWeb Matn Tahrirlovchi Bot
Guruhda teg qilib matn yuboring - bot grammatikani tuzatadi
Sof requests bilan ishlaydi - python-telegram-bot kerak emas
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

SYSTEM_PROMPT = """Sen o'zbek tili grammatika ekspertisan. Foydalanuvchi matn yuborsa:

1. Matnni grammatik jihatdan to'g'irla
2. Imlo xatolarini tuzat
3. Tinish belgilarini to'g'irla
4. 5 xil uslubda qayta yoz

Javobni aniq quyidagi formatda ber:

✅ TUZATILGAN MATN:
[tuzatilgan matn]

📝 XATOLAR:
[qanday xatolar bor edi]

5 VARIANT:

1 Rasmiy uslub:
[matn]

2 Oddiy uslub:
[matn]

3 Ijodiy uslub:
[matn]

4 Qisqa uslub:
[matn]

5 Professional uslub:
[matn]

Faqat o'zbek tilida javob ber. Markdown formatlashtirish ishlatma."""


def get_offset():
    try:
        return int(Path(OFFSET_FILE).read_text().strip() or "0")
    except Exception:
        return 0

def save_offset(offset):
    Path(OFFSET_FILE).write_text(str(offset))

def tg_send(chat_id, text, reply_to=None):
    try:
        payload = {
            "chat_id": chat_id,
            "text": text[:4096],
            "disable_web_page_preview": True,
        }
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        r = requests.post(f"{API}/sendMessage", json=payload, timeout=30)
        return r.json()
    except Exception as e:
        logger.error("sendMessage xatosi: %s", e)
        return None

def tg_send_with_keyboard(chat_id, text, keyboard):
    try:
        r = requests.post(f"{API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text[:4096],
            "reply_markup": keyboard,
            "disable_web_page_preview": True,
        }, timeout=30)
        return r.json()
    except Exception as e:
        logger.error("sendMessage xatosi: %s", e)
        return None

def tg_typing(chat_id):
    try:
        requests.post(f"{API}/sendChatAction", json={
            "chat_id": chat_id,
            "action": "typing"
        }, timeout=10)
    except Exception:
        pass

def get_bot_username():
    try:
        r = requests.get(f"{API}/getMe", timeout=10)
        return r.json().get("result", {}).get("username", "")
    except Exception:
        return ""

def check_and_edit(text):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Quyidagi matnni tekshirib to'g'irla:\n\n{text}"}]
    )
    return msg.content[0].text

def send_start(chat_id, bot_username):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Guruhga qoshish", "url": f"https://t.me/{bot_username}?startgroup=true"},
            ],
            [
                {"text": "Kanalimiz @tezweb_uz", "url": "https://t.me/tezweb_uz"},
                {"text": "tezweb.uz", "url": "https://tezweb.uz"}
            ],
            [
                {"text": "Yaratuvchi @Shohdollar22", "url": "https://t.me/Shohdollar22"}
            ]
        ]
    }
    text = (
        "TezWeb Matn Tahrirlovchi Bot\n\n"
        "Men o'zbek tili grammatikasini tekshiruvchi aqlli botman!\n\n"
        "Nima qila olaman:\n"
        "- Grammatik xatolarni topib tuzataman\n"
        "- Imlo va tinish belgilarini tekshiraman\n"
        "- 5 xil uslubda variant taqdim etaman\n\n"
        "Qanday ishlatish:\n"
        "Shaxsiy xabarda: Matnni yuboring\n"
        "Guruhda: @botni teg qilib matn yuboring\n\n"
        "TezWeb.uz botlari:\n"
        "- Matn tahrirlovchi - siz hozir\n"
        "- Antispam boti - @TezWebBot_Antispam\n"
        "- Kontent boti - @tezweb_content_bot\n\n"
        "Muammo yoki taklif: @Shohdollar22\n"
        "tezweb.uz | @tezweb_uz"
    )
    tg_send_with_keyboard(chat_id, text, keyboard)

def send_info(chat_id, bot_username):
    keyboard = {
        "inline_keyboard": [
            [{"text": "Guruhga qoshish", "url": f"https://t.me/{bot_username}?startgroup=true"}],
            [{"text": "Do'stlarga tavsiya qiling!", "url": f"https://t.me/share/url?url=https://t.me/{bot_username}&text=O'zbek tili grammatikasini tekshiruvchi aqlli bot!"}],
        ]
    }
    text = (
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
        "- Guruhda teg orqali ishlash\n"
        "- Shaxsiy xabarda ishlash\n\n"
        "Kanal: @tezweb_uz\n"
        "Bog'lanish: @Shohdollar22"
    )
    tg_send_with_keyboard(chat_id, text, keyboard)

def handle_updates():
    offset     = get_offset()
    bot_username = get_bot_username()
    logger.info("Bot username: @%s", bot_username)

    while True:
        try:
            r = requests.post(f"{API}/getUpdates", json={
                "offset": offset,
                "timeout": 30,
                "allowed_updates": ["message", "callback_query"]
            }, timeout=40)
            data = r.json()

            if not data.get("ok"):
                logger.error("getUpdates xato: %s", data)
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                save_offset(offset)

                # Callback tugmalar
                callback = update.get("callback_query")
                if callback:
                    try:
                        requests.post(f"{API}/answerCallbackQuery",
                            json={"callback_query_id": callback["id"]}, timeout=10)
                    except Exception:
                        pass
                    continue

                # Xabar
                message = update.get("message", {})
                if not message:
                    continue

                text      = message.get("text", "")
                chat      = message.get("chat", {})
                chat_id   = chat.get("id")
                chat_type = chat.get("type", "")
                msg_id    = message.get("message_id")
                from_user = message.get("from", {})

                if not text or not chat_id:
                    continue

                # Komandalar
                cmd = text.split()[0].lower().split("@")[0] if text.startswith("/") else ""

                if cmd == "/start" or cmd == "/help":
                    send_start(chat_id, bot_username)
                    continue

                if cmd == "/info":
                    send_info(chat_id, bot_username)
                    continue

                # Guruhda faqat teg yoki reply orqali
                if chat_type in ("group", "supergroup"):
                    is_mention = bot_username and f"@{bot_username}" in text
                    is_reply   = (message.get("reply_to_message", {})
                                  .get("from", {})
                                  .get("username", "") == bot_username)

                    if not is_mention and not is_reply:
                        continue

                    # Teg nomini olib tashlash
                    text = text.replace(f"@{bot_username}", "").strip()

                # Matn tekshirish
                if not text or len(text) < 5:
                    tg_send(chat_id,
                        "Iltimos tekshirilishi kerak bo'lgan matnni yuboring.\n"
                        "Minimal 5 ta belgi bo'lishi kerak.",
                        reply_to=msg_id)
                    continue

                if len(text) > 3000:
                    tg_send(chat_id,
                        f"Matn juda uzun! Maksimal 3000 belgi.\n"
                        f"Sizning matningiz: {len(text)} belgi.",
                        reply_to=msg_id)
                    continue

                logger.info("Matn tekshirilmoqda: %d belgi | %s", len(text), from_user.get("username", "?"))
                tg_typing(chat_id)

                try:
                    result = check_and_edit(text)
                    footer = "\n\ntezweb.uz | @tezweb_uz | @Shohdollar22"

                    if len(result) + len(footer) > 4096:
                        # Ikki qismga bo'lib yuborish
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
                    tg_send(chat_id,
                        "Xatolik yuz berdi. Qaytadan urinib ko'ring.\n"
                        "Muammo davom etsa: @Shohdollar22",
                        reply_to=msg_id)

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

    # Asosiy thread tirik turadi
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
