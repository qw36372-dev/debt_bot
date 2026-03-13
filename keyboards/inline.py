"""
keyboards/inline.py — все inline-клавиатуры бота
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# ── Согласие с политикой ПД ──────────────────────────────────────────────────

def consent_kb(checked: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура с чек-боксом согласия и кнопкой подтверждения."""
    checkbox_label = "✅ Согласен(на)" if checked else "☐ Отметить согласие"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=checkbox_label,
            callback_data="toggle_consent",
        )],
        [InlineKeyboardButton(
            text="✔️ Даю согласие",
            callback_data="give_consent" if checked else "consent_not_checked",
        )],
    ])


# ── Удобный формат связи ─────────────────────────────────────────────────────

def contact_format_kb(selected: set[str]) -> InlineKeyboardMarkup:
    """Клавиатура выбора формата связи (мульти-выбор)."""
    def label(key: str, text: str) -> str:
        return f"✅ {text}" if key in selected else f"☐ {text}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=label("telegram", "Telegram"),
            callback_data="cf_telegram",
        )],
        [InlineKeyboardButton(
            text=label("phone", "Телефон"),
            callback_data="cf_phone",
        )],
        [InlineKeyboardButton(
            text="📤 Отправить запрос",
            callback_data="submit_request" if selected else "cf_need_choice",
        )],
    ])


# ── После отправки ───────────────────────────────────────────────────────────

def restart_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Подать ещё одну заявку", callback_data="restart")],
    ])
