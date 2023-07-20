from aiogram.types import ReplyKeyboardMarkup


k_b = ReplyKeyboardMarkup(resize_keyboard=True)
k_b_exit = ReplyKeyboardMarkup(resize_keyboard=True)
k_b_deletion = ReplyKeyboardMarkup(resize_keyboard=True)

kb_start = 'Start'
kb_delete = 'Delete'
kb_edit_name = 'Name'
kb_edit_regular_key = 'Key'
kb_edit_reward_size = 'Reward'
kb_help = 'Help'
kb_show = 'Status'

kb_exit = 'Back'

kb_yes_del = 'Delete'
kb_no = 'No'

# k_b.add(kb_start)  # remove big Start button from the kb
k_b.row(kb_edit_name, kb_edit_regular_key, kb_edit_reward_size)
k_b.row(kb_help, kb_show, kb_delete)

k_b_exit.add(kb_exit)

k_b_deletion.add(kb_yes_del)
k_b_deletion.add(kb_exit)
