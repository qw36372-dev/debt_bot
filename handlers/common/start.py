"""
handlers/common/start.py — /start и первое приветственное сообщение
"""

import logging

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline import consent_kb
from states import Form

logger = logging.getLogger(__name__)
router = Router()

# ── Текст первого сообщения ──────────────────────────────────────────────────

MSG_WELCOME = (
    "⚖️ <b>Помощь в списании долгов ФССП</b>\n\n"
    "Списание долга по кредитным обязательствам до <b>10 000 000 руб.</b>, "
    "в случае если судебный акт по взысканию по этим обязательствам вступил "
    "в законную силу до <b>01.12.2024</b>\n\n"
    "<i>(распространяется также и на супругу)</i>"
)

MSG_POLICY = (
    "<i>Продолжая использование бота, вы соглашаетесь с политикой "
    "использования персональных данных в соответствии с ФЗ-152 "
    "и даёте согласие на их обработку.</i>"
)

# ── /start ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()

    # Первое сообщение — информация о программе
    await message.answer(MSG_WELCOME, parse_mode=ParseMode.HTML)

    # Второе сообщение — политика ПД + чек-бокс
    await message.answer(
        MSG_POLICY,
        parse_mode=ParseMode.HTML,
        reply_markup=consent_kb(checked=False),
    )

    await state.set_state(Form.consent)
    await state.update_data(consent_checked=False)


# ── Перезапуск через кнопку ──────────────────────────────────────────────────

@router.callback_query(F.data == "restart")
async def cb_restart(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer(MSG_WELCOME, parse_mode=ParseMode.HTML)
    await cb.message.answer(
        MSG_POLICY,
        parse_mode=ParseMode.HTML,
        reply_markup=consent_kb(checked=False),
    )
    await state.set_state(Form.consent)
    await state.update_data(consent_checked=False)
    await cb.answer()
