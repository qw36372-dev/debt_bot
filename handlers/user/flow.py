"""
handlers/user/flow.py — FSM-сценарий сбора заявки на списание долгов

Шаги:
  1. consent        — чек-бокс + кнопка «Даю согласие»
  2. exec_number    — ввод номера(ов) исполнительного производства
  3. extra_info     — дополнительные сведения
  4. name           — имя
  5. phone          — номер телефона
  6. contact_format — формат связи (мульти-выбор) + «Отправить запрос»
"""

import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline import consent_kb, contact_format_kb, restart_kb
from services.notifications import send_lead_to_channel
from states import Form

logger = logging.getLogger(__name__)
router = Router()


# ═══════════════════════════════════════════════════════════════════
# ШАГ 1 — СОГЛАСИЕ
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(Form.consent, F.data == "toggle_consent")
async def cb_toggle_consent(cb: CallbackQuery, state: FSMContext) -> None:
    """Переключаем чек-бокс."""
    data = await state.get_data()
    checked = not data.get("consent_checked", False)
    await state.update_data(consent_checked=checked)

    await cb.message.edit_reply_markup(reply_markup=consent_kb(checked=checked))
    await cb.answer("✅ Отмечено" if checked else "☐ Снято")


@router.callback_query(Form.consent, F.data == "consent_not_checked")
async def cb_consent_not_checked(cb: CallbackQuery) -> None:
    """Пользователь нажал «Даю согласие» без галочки."""
    await cb.answer(
        "⚠️ Сначала поставьте галочку, нажав кнопку выше",
        show_alert=True,
    )


@router.callback_query(Form.consent, F.data == "give_consent")
async def cb_give_consent(cb: CallbackQuery, state: FSMContext) -> None:
    """Пользователь дал согласие — переходим к следующему шагу."""
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.answer("✅ Согласие получено")

    await cb.message.answer(
        "📄 <b>Введите номер своего Исполнительного производства</b>(номер, дата возбуждения)\n\n"
        "<i>Если у вас их несколько — введите все через запятую</i>\n\n"
        "Например: <code>123456/24/61000-ИП от 20.04.2024, 654321/23/61000.....</code>",
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(Form.exec_number)


# ═══════════════════════════════════════════════════════════════════
# ШАГ 2 — НОМЕР ИСПОЛНИТЕЛЬНОГО ПРОИЗВОДСТВА
# ═══════════════════════════════════════════════════════════════════

@router.message(Form.exec_number)
async def msg_exec_number(message: Message, state: FSMContext) -> None:
    exec_number = message.text.strip()
    if len(exec_number) < 3:
        await message.answer(
            "⚠️ Пожалуйста, введите корректный номер исполнительного производства."
        )
        return

    await state.update_data(exec_number=exec_number)

    await message.answer(
        "📝 <b>Укажите дополнительные сведения</b>\n\n"
        "Любую другую информацию, которую хотите уточнить, или напишите <i>«нет»</i>, "
        "если дополнений нет.",
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(Form.extra_info)


# ═══════════════════════════════════════════════════════════════════
# ШАГ 3 — ДОПОЛНИТЕЛЬНЫЕ СВЕДЕНИЯ
# ═══════════════════════════════════════════════════════════════════

@router.message(Form.extra_info)
async def msg_extra_info(message: Message, state: FSMContext) -> None:
    extra_info = message.text.strip()
    await state.update_data(extra_info=extra_info)

    await message.answer(
        "👤 <b>Введите ваше имя</b>\n\n"
        "<i>Например: Иван</i>",
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(Form.name)


# ═══════════════════════════════════════════════════════════════════
# ШАГ 4 — ИМЯ
# ═══════════════════════════════════════════════════════════════════

@router.message(Form.name)
async def msg_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("⚠️ Пожалуйста, введите корректное имя.")
        return

    await state.update_data(name=name)

    await message.answer(
        "📞 <b>Введите номер телефона</b>\n\n"
        "<i>Например: +7 900 123-45-67</i>",
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(Form.phone)


# ═══════════════════════════════════════════════════════════════════
# ШАГ 5 — ТЕЛЕФОН
# ═══════════════════════════════════════════════════════════════════

@router.message(Form.phone)
async def msg_phone(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()

    # Базовая валидация: хотя бы 7 цифр
    digits = [c for c in phone if c.isdigit()]
    if len(digits) < 7:
        await message.answer(
            "⚠️ Пожалуйста, введите корректный номер телефона.\n"
            "<i>Например: +7 900 123-45-67</i>",
            parse_mode=ParseMode.HTML,
        )
        return

    await state.update_data(phone=phone, contact_format=[])

    await message.answer(
        "📡 <b>Укажите удобный формат связи с вами</b>\n\n"
        "Выберите один или несколько вариантов, затем нажмите «Отправить запрос».",
        parse_mode=ParseMode.HTML,
        reply_markup=contact_format_kb(selected=set()),
    )
    await state.set_state(Form.contact_format)


# ═══════════════════════════════════════════════════════════════════
# ШАГ 6 — ФОРМАТ СВЯЗИ (мульти-выбор)
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(Form.contact_format, F.data.in_({"cf_telegram", "cf_phone"}))
async def cb_contact_format_toggle(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    selected: set = set(data.get("contact_format", []))

    key_map = {"cf_telegram": "telegram", "cf_phone": "phone"}
    key = key_map[cb.data]

    if key in selected:
        selected.discard(key)
    else:
        selected.add(key)

    await state.update_data(contact_format=list(selected))
    await cb.message.edit_reply_markup(reply_markup=contact_format_kb(selected=selected))
    await cb.answer()


@router.callback_query(Form.contact_format, F.data == "cf_need_choice")
async def cb_cf_need_choice(cb: CallbackQuery) -> None:
    await cb.answer(
        "⚠️ Выберите хотя бы один формат связи",
        show_alert=True,
    )


@router.callback_query(Form.contact_format, F.data == "submit_request")
async def cb_submit_request(cb: CallbackQuery, state: FSMContext, bot) -> None:
    """Финальный шаг — сохраняем и отправляем лид в канал."""
    data = await state.get_data()
    user = cb.from_user

    lead = {
        "tg_id":          user.id,
        "tg_username":    user.username,
        "name":           data.get("name", "—"),
        "phone":          data.get("phone", "—"),
        "exec_number":    data.get("exec_number", "—"),
        "extra_info":     data.get("extra_info", "—"),
        "contact_format": data.get("contact_format", []),
        "submitted_at":   datetime.now().strftime("%d.%m.%Y %H:%M"),
    }

    await state.clear()

    # Убираем клавиатуру выбора формата
    await cb.message.edit_reply_markup(reply_markup=None)

    # Отправляем лид в канал
    await send_lead_to_channel(bot, lead)

    # Уведомляем пользователя
    await cb.message.answer(
        "✅ <b>Спасибо за обращение!</b>\n\n"
        "В ближайшее время с вами свяжется наш сотрудник.",
        parse_mode=ParseMode.HTML,
        reply_markup=restart_kb(),
    )
    await cb.answer()
