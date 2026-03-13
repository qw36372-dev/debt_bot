"""
FSM состояния бота — сбор заявки на списание долгов
"""

from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    """Сценарий сбора заявки"""
    consent        = State()   # согласие с политикой ПД
    exec_number    = State()   # номер(а) исполнительного производства
    extra_info     = State()   # дополнительные сведения
    name           = State()   # имя пользователя
    phone          = State()   # номер телефона
    contact_format = State()   # удобный формат связи
