"""
⚙️ Конфигурация бота — Списание долгов ФССП

ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (задаются в панели bothost.ru):
  API_TOKEN        — токен от @BotFather
  LEADS_CHANNEL_ID — ID приватного канала (узнать через @getmyid_bot или @username_to_id_bot)
"""

import os
import sys

# ── Токен бота ──────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("API_TOKEN")
if not BOT_TOKEN:
    sys.exit("❌ Переменная окружения API_TOKEN не задана!")

# ── Канал для лидов ──────────────────────────────────────────────────────────
_leads_raw = os.environ.get("LEADS_CHANNEL_ID")
if not _leads_raw:
    sys.exit("❌ Переменная окружения LEADS_CHANNEL_ID не задана!")
LEADS_CHANNEL_ID: int = int(_leads_raw)
