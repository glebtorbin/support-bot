from aiogram.dispatcher.filters.state import State, StatesGroup


class GlobalState(StatesGroup):
    forward = State()
    wait_admin_ans = State()