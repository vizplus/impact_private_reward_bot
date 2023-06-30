from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMIntro(StatesGroup):
    Q_name = State()
    Q_reg_key = State()
    Q_reward_size = State()