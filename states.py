from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMIntro(StatesGroup):
    '''Represents the states when a user is providing the bot with
    his/her name, regular key and reward size
    '''
    Q_name = State()
    Q_reg_key = State()
    Q_reward_size = State()


class FSMEdit(StatesGroup):
    '''Represents the states when a user is editing his/her name, regular key
    and reward size which were provided previously
    '''
    E_name = State()
    E_reg_key = State()
    E_reward_size = State()


class FSMDelete(StatesGroup):
    '''Represents the state when a user confirms deleting the data he/she
    provided previously
    '''
    Confirm_deletion = State()
