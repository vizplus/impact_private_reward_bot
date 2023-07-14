from aiogram.types import (
    ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
)


k_b = ReplyKeyboardMarkup(resize_keyboard=True)
k_b_exit = ReplyKeyboardMarkup(resize_keyboard=True)

kb_start = '/start'
kb_delete = '/delete'
kb_edit_name = '/edit_name'
kb_edit_regular_key = '/edit_regular_key'
kb_edit_reward_size = '/edit_reward_size'
kb_help = '/help'
kb_show = '/show'

kb_exit = '/exit'

k_b.add(kb_start)
k_b.row(kb_help, kb_show, kb_delete)
k_b.row(kb_edit_name, kb_edit_regular_key, kb_edit_reward_size)

k_b_exit.add(kb_exit)
