from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMIntro(StatesGroup):
    Q_name = State()
    Q_reg_key = State()
    Q_reward_size = State()


class FSMEdit(StatesGroup):
    E_name = State()
    E_reg_key = State()
    E_reward_size = State()


class FSMDelete(StatesGroup):
    Accept_deletion = State()
