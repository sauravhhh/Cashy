"""Cashy - Telegram currency converter bot (@cashyfy_bot).

Setup:
  export TELEGRAM_BOT_TOKEN="your-bot-token"
  python3 bot.py

Commands:
  /start - welcome message
  /convert <amount> <FROM> <TO> - e.g. /convert 100 USD INR
  /rates - popular rates vs INR
  /help - help message

Rates come from the free exchangerate-api (no key needed).
"""
import json
import os
import time
import urllib.request

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API = "https://api.telegram.org/bot"
RATES_URL = "https://open.er-api.com/v6/latest/USD"

CACHE = {"ts": 0, "rates": None}
CACHE_TTL = 3600  # 1 hour


def get_rates():
    now = time.time()
    if CACHE["rates"] and now - CACHE["ts"] < CACHE_TTL:
        return CACHE["rates"]
    req = urllib.request.Request(RATES_URL, headers={"User-Agent": "CashyBot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    rates = data.get("rates", {})
    if rates:
        CACHE["rates"] = rates
        CACHE["ts"] = now
    return rates


def api_call(method, payload):
    url = f"{API}{TOKEN}/{method}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def send_message(chat_id, text):
    return api_call("sendMessage", {"chat_id": chat_id, "text": text})


def handle_update(update):
    msg = update.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip()
    if not chat_id or not text:
        return
    parts = text.split()
    cmd = parts[0].lower().split("@")[0]

    if cmd == "/start":
        send_message(chat_id, "Hi, I'm Cashy! Send me an amount like this:\n\n100 USD to INR\n\nOr use: /convert 100 USD INR\n\nTry /rates for popular rates vs INR.")
        return

    if cmd == "/help":
        send_message(chat_id, "How to use Cashy:\n\n100 USD to INR - convert an amount\n/convert 100 USD INR - same thing\n/rates - popular rates vs INR")
        return

    if cmd == "/rates":
        try:
            rates = get_rates()
            inr = rates.get("INR", 0)
            lines = ["Popular rates vs INR (1 USD = X):"]
            for code in ["USD", "EUR", "GBP", "AED", "JPY", "AUD", "CAD", "SGD"]:
                if code in rates:
                    lines.append(f"1 {code} = {inr / rates[code]:.2f} INR")
            lines.append(f"\n1 USD = {inr:.2f} INR")
            send_message(chat_id, "\n".join(lines))
        except Exception:
            send_message(chat_id, "Rates are unavailable right now. Please try again in a bit.")
        return

    if cmd == "/convert":
        parts = parts[1:]
        do_convert(chat_id, parts)
        return

    # Plain text like "100 USD to INR"
    words = [w for w in parts if w.lower() != "to"]
    if len(words) >= 3:
        do_convert(chat_id, words)
        return

    send_message(chat_id, "Send an amount like: 100 USD to INR")


def do_convert(chat_id, parts):
    try:
        amount = float(parts[0].replace(",", ""))
        from_cur = parts[1].upper()
        to_cur = parts[2].upper()
    except (ValueError, IndexError):
        send_message(chat_id, "Use this format: /convert 100 USD INR")
        return
    try:
        rates = get_rates()
        if from_cur not in rates or to_cur not in rates:
            send_message(chat_id, f"Sorry, I don't know {from_cur} or {to_cur}. Try USD, EUR, GBP, INR, AED, JPY.")
            return
        result = amount * rates[to_cur] / rates[from_cur]
        send_message(chat_id, f"{amount:,.2f} {from_cur} = {result:,.2f} {to_cur}\nRate: 1 {from_cur} = {rates[to_cur] / rates[from_cur]:.4f} {to_cur}")
    except Exception:
        send_message(chat_id, "Rates are unavailable right now. Please try again in a bit.")


def main():
    if not TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN first.")
    offset = 0
    print("Cashy bot running. Press Ctrl+C to stop.")
    while True:
        try:
            url = f"{API}{TOKEN}/getUpdates?offset={offset}&timeout=30"
            with urllib.request.urlopen(url, timeout=40) as r:
                data = json.load(r)
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                try:
                    handle_update(update)
                except Exception as e:
                    print("update error:", e)
        except Exception as e:
            print("poll error:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
