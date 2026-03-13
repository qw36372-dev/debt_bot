"""
services/notifications.py — отправка лида в приватный канал
"""

import logging
from datetime import datetime

from aiogram import Bot
from aiogram.enums import ParseMode

from config import LEADS_CHANNEL_ID

logger = logging.getLogger(__name__)


async def send_lead_to_channel(bot: Bot, data: dict) -> None:
    """
    Отправляет карточку заявки в приватный канал.

    data keys:
        tg_id, tg_username, exec_number, extra_info,
        name, phone, contact_format, submitted_at
    """
    username = f"@{data['tg_username']}" if data.get("tg_username") else "—"
    contact_fmt = ", ".join(data.get("contact_format", [])) or "—"
    submitted_at = data.get("submitted_at", datetime.now().strftime("%d.%m.%Y %H:%M"))

    text = (
        "📥 <b>Новая заявка — Списание долгов ФССП</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Имя:</b> {data.get('name', '—')}\n"
        f"📞 <b>Телефон:</b> {data.get('phone', '—')}\n"
        f"💬 <b>Telegram:</b> {username}\n"
        f"🆔 <b>TG ID:</b> <code>{data.get('tg_id', '—')}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📄 <b>№ Исп. производства:</b>\n"
        f"<code>{data.get('exec_number', '—')}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Доп. сведения:</b>\n"
        f"{data.get('extra_info', '—')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>Формат связи:</b> {contact_fmt}\n"
        f"🕐 <b>Дата заявки:</b> {submitted_at}"
    )

    try:
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        tg_id = data.get("tg_id")
        phone = data.get("phone", "").replace(" ", "").replace("-", "")

        buttons = []
        if tg_id:
            buttons.append(InlineKeyboardButton(
                text="✉️ Написать клиенту",
                url=f"tg://user?id={tg_id}",
            ))
        if phone:
            buttons.append(InlineKeyboardButton(
                text="📞 Позвонить",
                url=f"tel:{phone}",
            ))

        markup = InlineKeyboardMarkup(inline_keyboard=[buttons]) if buttons else None

        await bot.send_message(
            chat_id=LEADS_CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )
        logger.info("Лид отправлен в канал: tg_id=%s, name=%s", tg_id, data.get("name"))
    except Exception as exc:
        logger.error("Ошибка отправки лида в канал: %s", exc)
