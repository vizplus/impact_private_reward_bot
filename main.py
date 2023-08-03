import logging
import re

from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from db import create_table, est_connection
from states import FSMIntro, FSMEdit, FSMDelete
from keyboards import k_b, k_b_exit, k_b_deletion
from viz_interactions import (
    check_viz_account,
    check_viz_account_capital,
    check_reg_key_correct,
    count_vip_award_balance,
    reward_user
)


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Constants containing repeatable messages
NEWCOMER_MSG = 'Looks like you are a newcomer here. \
Let\'s begin with /start command.'
KEY_NOT_FOUND = 'There is no such a regular key under your account on VIZ. \
Are you sure you gave me correct data? \
Please, try again.'
VIZ_NAME_NOT_FOUND = 'Hm...I did not find such an account name on VIZ. \
Are you sure you gave me correct data? \
Please, try again.'


@dp.message_handler(commands=['start'])
@dp.message_handler(lambda msg: msg.text and 'start' in msg.text.lower())
async def handle_start_command(message: types.Message):
    '''
    Command 'start' is used by a user at the beginning of the conversation

    :param types.Message message: The message object received from the user
    '''
    user_id = message.from_user.id

    connection = await est_connection()
    await create_table(connection)
    tg_id = await connection.fetchval('''
    SELECT tg_id FROM vip_users WHERE tg_id = $1;
    ''', user_id)
    await connection.close()

    if tg_id is None:
        await message.answer(
            'Hello! Please, write your name (same as in VIZ):',
            reply_markup=k_b_exit
        )
        await FSMIntro.Q_name.set()
    else:
        await message.answer(
            'Nice try! There is already data under your Telegram id. '
            'You can delete your data using /delete command to start over. '
            'Also, you can use these commands to edit data separately: '
            '/name, /key, /reward.',
            reply_markup=k_b
        )


@dp.message_handler(commands=['back'], state='*')
@dp.message_handler(
    lambda msg: msg.text and 'back' in msg.text.lower(),
    state='*'
)
async def handle_back_command(message: types.Message, state: FSMContext):
    '''
    Command 'back' is used by a user when he/she is currently in a FSM state
    and the intent is to quit ceasing the form filling

    :param types.Message message: The message object received from the user
    :param FSMContext state: The current state of Finite State Machine
    '''
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer(
        'You cancelled filling the form. '
        'You can start from the beginning using /start command.',
        reply_markup=k_b
    )


@dp.message_handler(commands=['delete'])
@dp.message_handler(lambda msg: msg.text and 'delete' in msg.text.lower())
async def handle_delete_command(message: types.Message):
    '''
    Command 'delete' is used by a user when he/she intends to delete his/her
    previously provided data, namely: name, regular key and reward size

    :param types.Message message: The message object received from the user
    '''
    user_id = message.from_user.id

    connection = await est_connection()
    data = await connection.fetchval('''
    SELECT * FROM vip_users WHERE tg_id = $1;
    ''', user_id)
    await connection.close()

    if data:
        await FSMDelete.Confirm_deletion.set()
        await message.answer(
            'Are you sure you want to delete your account data?',
            reply_markup=k_b_deletion
        )

    else:
        await message.answer(
            NEWCOMER_MSG,
            reply_markup=k_b
        )


@dp.message_handler(
    lambda msg: msg.text and 'delete' in msg.text.lower(),
    state=FSMDelete.Confirm_deletion
)
async def handle_yes_delete_command(message: types.Message):
    '''
    Command 'delete' accompanied by FSMDelete.Confirm_deletion state will
    wipe out all the previously provided user data from the database.
    This handler is triggered when a user confirms his/her intent to
    delete the data

    :param types.Message message: The message object received from the user
    '''
    user_id = message.from_user.id

    connection = await est_connection()
    await connection.execute('''
    DELETE FROM vip_users WHERE tg_id = $1;
    ''', user_id)
    await connection.close()

    await message.answer(
        'OK, you deleted your data. '
        'Now rewrite your data using /start command',
        reply_markup=k_b
        )


@dp.message_handler(
    lambda msg: msg.text and 'no' in msg.text.lower(),
    state=FSMDelete.Confirm_deletion
)
async def handle_no_delete_command(message: types.Message, state: FSMContext):
    '''
    Command 'no' accompanied by FSMDelete.Confirm_deletion state will
    quit from wiping out all the user data from database.
    This handler is triggered when a user changes his/her decision to
    delete the data

    :param types.Message message: The message object received from the user
    '''
    await state.finish()
    await message.answer(
        'You cancelled deleting your data.',
        reply_markup=k_b
    )


@dp.message_handler(commands=['name'])
@dp.message_handler(
    lambda msg: msg.text and 'name' in msg.text.lower()
)
async def handle_edit_name_command(message: types.Message):
    '''
    Command 'name' is used by a user when he/she intends to change his/her
    name, provided to database, to a new one.

    :param types.Message message: The message object received from the user
    '''
    user_id = message.from_user.id

    connection = await est_connection()
    tg_id = await connection.fetchval('''
    SELECT tg_id FROM vip_users WHERE tg_id = $1;
    ''', user_id)
    await connection.close()

    if tg_id:
        await message.answer(
            'Please, write your new name (same as in VIZ):',
            reply_markup=k_b_exit
        )
        await FSMEdit.E_name.set()
    else:
        await message.answer(
            NEWCOMER_MSG,
            reply_markup=k_b
        )


@dp.message_handler(commands=['key'])
@dp.message_handler(
    lambda msg: msg.text and 'key' in msg.text.lower()
)
async def handle_edit_reg_key_command(message: types.Message):
    '''
    Command 'key' is used by a user when he/she intends to change his/her
    regular key, provided to database, to a new one.

    :param types.Message message: The message object received from the user
    '''
    user_id = message.from_user.id

    connection = await est_connection()
    tg_id = await connection.fetchval('''
    SELECT tg_id FROM vip_users WHERE tg_id = $1;
    ''', user_id)
    await connection.close()

    if tg_id:
        await message.answer(
            'Please, provide your new regular key:',
            reply_markup=k_b_exit
        )
        await FSMEdit.E_reg_key.set()
    else:
        await message.answer(
            NEWCOMER_MSG,
            reply_markup=k_b
        )


@dp.message_handler(commands=['reward'])
@dp.message_handler(lambda msg: msg.text and 'reward' in msg.text.lower())
async def handle_edit_reward_size_command(message: types.Message):
    '''
    Command 'reward' is used by a user when he/she intends to change his/her
    reward size, provided to database, to a new one.

    :param types.Message message: The message object received from the user
    '''
    user_id = message.from_user.id

    connection = await est_connection()
    tg_id = await connection.fetchval('''
    SELECT tg_id FROM vip_users WHERE tg_id = $1;
    ''', user_id)
    await connection.close()

    if tg_id:
        await message.answer(
            'Please, provide your new reward size:',
            reply_markup=k_b_exit
        )
        await FSMEdit.E_reward_size.set()
    else:
        await message.answer(
            NEWCOMER_MSG,
            reply_markup=k_b
        )


@dp.message_handler(commands=['status'])
@dp.message_handler(lambda msg: msg.text and 'status' in msg.text.lower())
async def handle_status_command(message: types.Message):
    '''
    Command 'status' is used by a user when he/she intends to revise his/her
    previously provided data.

    :param types.Message message: The message object received from the user
    '''
    user_id = message.from_user.id

    connection = await est_connection()
    data = await connection.fetchrow('''
    SELECT * FROM vip_users WHERE tg_id = $1;
    ''', user_id)
    await connection.close()

    if data:
        data_name = list(data.values())[2]
        data_reg_key = list(data.values())[3]
        data_reward_size = list(data.values())[4]
        reward_balance = count_vip_award_balance(data_name, data_reward_size)

        await message.answer(
                f'Name: <b>{data_name}</b>\n'
                f'Regular key: <b>{data_reg_key[:5]}</b>...\n'
                f'Reward size: <b>{data_reward_size}</b>\n'
                f'Reward balance: <b>{reward_balance}</b>',
                parse_mode='html',
                reply_markup=k_b
            )
    else:
        await message.answer(
            NEWCOMER_MSG,
            reply_markup=k_b
        )


@dp.message_handler(commands=['help'])
@dp.message_handler(lambda msg: msg.text and 'help' in msg.text.lower())
async def handle_help_command(message: types.Message):
    '''
    Command 'help' will show all the available bot commands.

    :param types.Message message: The message object received from the user
    '''
    await message.answer(
            'This bot is created for VIP VIZ-blockchain users. '
            'If you are one of them, you can start using it by '
            'providing your account name, regular key and reward size. '
            'Once you\'ve done with that, you are allowed to forward any '
            'messages from other users who you want to reward with VIZ-token. '
            'Type /start to begin using this bot.\n'
            'The list of available commands:\n'
            '/start - Start interacting with the bot\n'
            '/delete - Delete the data (name, regular key and reward size) '
            'you provided previously\n'
            '/name - Edit your name\n'
            '/key - Edit your regular key\n'
            '/reward - Edit your reward size\n'
            '/help - Shows the bot description '
            'and the set of available commands\n'
            '/back - Cancel filling a form\n'
            '/status - Shows the data (name, regular key '
            'and reward size) you provided previously',
            reply_markup=k_b
        )


@dp.message_handler(state=FSMIntro.Q_name)
async def handle_fsm_name(message: types.Message, state: FSMContext):
    '''
    When in FSMIntro.Q_name FSM state, user is prompted to provide his/her
    name

    :param types.Message message: The message object received from the user
    :param FSMContext state: The current state of Finite State Machine
    '''
    answer = message.text
    if check_viz_account(answer):
        if check_viz_account_capital(answer):
            async with state.proxy() as data:
                data['name'] = answer
            await message.answer(
                'Good! Now please provide your regular key:',
                reply_markup=k_b_exit
            )
            await FSMIntro.next()
        else:
            await message.answer(
                'You do not have enough social capital to reward anybody!',
                reply_markup=k_b_exit
            )
    else:
        await message.answer(
            VIZ_NAME_NOT_FOUND,
            reply_markup=k_b_exit
        )


@dp.message_handler(state=FSMIntro.Q_reg_key)
async def handle_fsm_reg_key(message: types.Message, state: FSMContext):
    '''
    When in FSMIntro.Q_reg_key FSM state, user is prompted to provide his/her
    regular key

    :param types.Message message: The message object received from the user
    :param FSMContext state: The current state of Finite State Machine
    '''
    answer = message.text
    data = await state.get_data()
    name = data['name']
    if check_reg_key_correct(regular_key=answer, account_name=name):
        async with state.proxy() as data:
            data['reg_key'] = answer
        await message.answer(
            'And lastly set the reward size for the user '
            'you want to gift it with (minimum 1 VIZ):',
            reply_markup=k_b_exit
        )
        await FSMIntro.next()
    else:
        await message.answer(
            KEY_NOT_FOUND,
            reply_markup=k_b_exit
        )


@dp.message_handler(state=FSMIntro.Q_reward_size)
async def handle_fsm_reward_size(message: types.Message, state: FSMContext):
    '''
    When in FSMIntro.Q_reward_size FSM state, user is prompted to provide
    his/her reward size

    :param types.Message message: The message object received from the user
    :param FSMContext state: The current state of Finite State Machine
    '''
    raw_answer = message.text
    filtered_answer = re.sub(r"[^\d.,]+", "", raw_answer).replace(',', '.')

    try:
        data = await state.get_data()
        tg_id = message.from_user.id
        name = data.get('name')
        reg_key = data.get('reg_key')
        reward_size = round(float(filtered_answer), 1)

        if reward_size >= 1:
            connection = await est_connection()
            await connection.execute('''
                INSERT INTO vip_users (
                tg_id, viz_account, regular_key, reward_size
                )
                VALUES ($1, $2, $3, $4);
            ''', tg_id, name, reg_key, reward_size)
            await connection.close()

            reward_balance = count_vip_award_balance(name, reward_size)
            await message.answer(
                f'Your settings are saved to database!\n'
                f'You can do {reward_balance} rewards.',
                reply_markup=k_b
            )

            await state.finish()
        else:
            await message.answer(
                'The reward size can\'t be less than 1. '
                'Please, try again.',
                reply_markup=k_b_exit
            )

    except Exception:
        await message.answer(
            'I take only integer or decimal numbers. '
            'Please, try again.',
            reply_markup=k_b_exit
        )


@dp.message_handler(state=FSMEdit.E_name)
async def handle_edit_name_cmd(message: types.Message, state: FSMContext):
    '''
    When in FSMEdit.E_name FSM state, user is prompted to edit his/her
    name by providing a new one

    :param types.Message message: The message object received from the user
    :param FSMContext state: The current state of Finite State Machine
    '''
    answer = message.text
    if check_viz_account(answer):
        if check_viz_account_capital(answer):
            async with state.proxy() as data:
                data['name'] = answer
            await message.answer(
                'Good! Now please provide your regular key:',
                reply_markup=k_b_exit
            )
            await FSMEdit.E_reg_key.set()
        else:
            await message.answer(
                'You do not have enough social capital to reward anybody!',
                reply_markup=k_b_exit
            )
    else:
        await message.answer(
            VIZ_NAME_NOT_FOUND,
            reply_markup=k_b_exit
        )


@dp.message_handler(state=FSMEdit.E_reg_key)
async def handle_edit_reg_key_cmd(message: types.Message, state: FSMContext):
    '''
    When in FSMEdit.E_reg_key FSM state, user is prompted to edit his/her
    regular key by providing a new one

    :param types.Message message: The message object received from the user
    :param FSMContext state: The current state of Finite State Machine
    '''
    answer = message.text  # reg_key
    user_id = message.from_user.id
    data = await state.get_data()
    name = data.get('name')

    if name:
        if check_reg_key_correct(regular_key=answer, account_name=name):
            connection = await est_connection()
            await connection.execute('''
            UPDATE vip_users SET viz_account = $1, regular_key = $2
            WHERE tg_id = $3;
            ''', name, answer, user_id)
            await connection.close()

            await message.answer(
                'You successfully edited your name and regular key!',
                reply_markup=k_b
            )

            await state.finish()
        else:
            await message.answer(
                KEY_NOT_FOUND,
                reply_markup=k_b_exit
            )
    elif not name:
        connection = await est_connection()
        name = await connection.fetchval('''
        SELECT viz_account FROM vip_users WHERE tg_id = $1;
        ''', user_id)

        if check_reg_key_correct(regular_key=answer, account_name=name):
            connection = await est_connection()
            await connection.execute('''
            UPDATE vip_users SET viz_account = $1, regular_key = $2
            WHERE tg_id = $3;
            ''', name, answer, user_id)
            await connection.close()

            await message.answer(
                'You successfully edited your regular key!',
                reply_markup=k_b
            )
            await state.finish()
        else:
            await message.answer(
                KEY_NOT_FOUND,
                reply_markup=k_b_exit)


@dp.message_handler(state=FSMEdit.E_reward_size)
async def handle_fsm_edit_reward_size(
    message: types.Message, state: FSMContext
):
    '''
    When in FSMEdit.E_reward_size FSM state, user is prompted to edit his/her
    reward size by providing a new one

    :param types.Message message: The message object received from the user
    :param FSMContext state: The current state of Finite State Machine
    '''
    user_id = message.from_user.id
    raw_answer = message.text
    filtered_answer = re.sub(r"[^\d.,]+", "", raw_answer).replace(',', '.')

    try:
        reward_size = round(float(filtered_answer), 1)
        if reward_size >= 1:
            connection = await est_connection()
            await connection.execute('''
            UPDATE vip_users SET reward_size = $1 WHERE tg_id = $2;
            ''', reward_size, user_id)
            await connection.close()
            await message.answer(
                'Your successfully edited the reward size!',
                reply_markup=k_b
            )

            await state.finish()
        else:
            await message.answer(
                'The reward size can\'t be less than 1. '
                'Please, try again.',
                reply_markup=k_b_exit
            )

    except Exception:
        await message.answer(
            'I take only integer or decimal numbers. '
            'Please, try again.',
            reply_markup=k_b_exit
        )


@dp.message_handler(content_types=['any'])
async def handle_forwarded_msgs(message: types.Message):
    '''
    When a user is forwarding a message from another user
    of any types of the content, it triggers the bot to award the user whose
    forwarded message was provided with VIZ energy using viz-python-lib

    :param types.Message message: The message object received from the user
    '''
    user_id = message.from_user.id
    author_id = message.forward_from.id if message.forward_from\
        else message.from_user.id

    if user_id != author_id:
        if message.forward_from.is_bot:
            return await message.answer(
                'You cannot reward a bot 🤷‍♂️', reply_markup=k_b
            )
        message_text = f'\'{message.text[:50]}\'' if message.text\
            else 'THE FORWARDED MESSAGE DOES NOT CONTAIN TEXT'

        connection = await est_connection()
        data = await connection.fetch('''
            SELECT viz_account, reward_size, regular_key
            from vip_users WHERE tg_id = $1;
        ''', user_id)
        await connection.close()

        reward_size = float(data[0]['reward_size'])
        viz_acc = data[0]['viz_account']
        regular_key = data[0]['regular_key']
        reward_balance = count_vip_award_balance(viz_acc, reward_size)

        if reward_size:
            if not check_viz_account_capital(viz_acc):
                return await message.answer(
                    'You don\'t have enough social capital. '
                    'Please, raise your capital and try again.'
                )
            if reward_balance > 0:
                # here the reward code block
                reward_user(
                    account=viz_acc,
                    reward_size=reward_size,
                    forwarded_message=message_text,
                    author_id=author_id,
                    regular_key=regular_key
                )

                # reevaluate the reward_balance
                reward_balance = count_vip_award_balance(viz_acc, reward_size)
                # end of the reward code block
                await message.answer(
                    f'You rewarded a user under Telegram id {author_id}\n'
                    f'with {reward_size} VIZ\n'
                    f'The text from the forwarded message is:\n'
                    f'<em>{message_text}...</em>\n\n'
                    f'You can do <b>{reward_balance}</b> awards.',
                    parse_mode='html',
                    reply_markup=k_b
                )
            else:
                return await message.answer('Your reward balance is too low')
        elif not reward_size:
            await message.answer(
                'You did not provide required data for me '
                'to handle forwarded messages. '
                'Use /start command to fix that.',
                reply_markup=k_b
            )
    elif message.forward_from_chat and message.forward_from is None:
        await message.answer(
            'You cannot reward a channel 🤷‍♂️', reply_markup=k_b
        )
    elif message.forward_from is None:
        await message.answer(
            'You cannot reward the sender of this message!',
            reply_markup=k_b
        )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
