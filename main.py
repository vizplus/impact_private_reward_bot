import logging

# from viz import Client as VIZ

from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from db import create_table, est_connection
from states import FSMIntro
from viz_interactions import (
    check_viz_account, check_viz_account_capital, check_reg_key_correct
)


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def handle_start_command(message: types.Message):
    user_id = message.from_user.id

    connection = await est_connection()

    await create_table(connection)

    tg_id = await connection.fetchval('''
    SELECT tg_id FROM vip_users WHERE tg_id = $1;
    ''', user_id)

    await connection.close()

    if tg_id is None:
        await message.answer(
            'Hello! Please, write your name (same as in VIZ):'
        )
        await FSMIntro.Q_name.set()
    else:
        await message.answer(
            'Nice try! There is already data under your Telegram id. '
            'You can delete your data using /delete command to start over.'
        )


@dp.message_handler(commands=['delete'])
async def handle_edit_command(message: types.Message):
    user_id = message.from_user.id

    connection = await est_connection()

    await connection.execute('''
    DELETE FROM vip_users WHERE tg_id = $1;
    ''', user_id)

    await message.answer(
        'OK, you deleted your data. '
        'Now rewrite your data using /start command'
        )


@dp.message_handler(state=FSMIntro.Q_name)
async def handle_fsm_name(message: types.Message, state: FSMContext):
    answer = message.text
    if check_viz_account(answer):
        if check_viz_account_capital(answer):
            async with state.proxy() as data:
                data['name'] = answer
            await message.answer(
                'Good! Now please provide you regular key:'
            )
            await FSMIntro.next()
        else:
            await message.answer(
                'You do not have enought social capital to reward anybody!'
            )
    else:
        await message.answer(
            'Hm...I did not find such an account name. '
            'Are you sure you gave me correct data?'
            'Please, try again.'
        )


@dp.message_handler(state=FSMIntro.Q_reg_key)
async def handle_fsm_reg_key(message: types.Message, state: FSMContext):
    answer = message.text
    data = await state.get_data()
    name = data['name']
    if check_reg_key_correct(regular_key=answer, account_name=name):
        async with state.proxy() as data:
            data['reg_key'] = answer
        await message.answer(
            'And lastly set the reward size for the user '
            'you want to gift it with (minimum 1 VIZ):'
        )
        await FSMIntro.next()
    else:
        await message.answer(
            'Hm...I did not find such a regular key under your account name. '
            'Are you sure you gave me correct data?'
            'Please, try again.'
        )


@dp.message_handler(
        state=FSMIntro.Q_reward_size
)
async def handle_fsm_reward_size(message: types.Message, state: FSMContext):
    answer = message.text
    try:
        if int(answer) >= 1:
            async with state.proxy() as data:
                data['reward_size'] = answer

            data = await state.get_data()
            tg_id = message.from_user.id
            name = data.get('name')
            reg_key = data.get('reg_key')
            reward_size = data.get('reward_size')

            connection = await est_connection()

            await connection.execute('''
                INSERT INTO vip_users (
                tg_id, viz_account, regular_key, reward_size
                )
                VALUES ($1, $2, $3, $4);
            ''', tg_id, name, reg_key, reward_size)

            await connection.close()

            await message.answer('Your settings are saved to database!')

            await state.finish()
        else:
            await message.answer(
                'Please, provide a number that is bigger (or equal) than 1'
            )
    except Exception:
        await message.answer(
            'I take only integer numbers',
            'Please, try again.'
        )


@dp.message_handler(content_types=['any'])
async def handle_forwarded_text_msgs(message: types.Message):
    user_id = message.from_user.id
    author_id = message.forward_from.id if message.forward_from\
        else message.from_user.id

    if user_id != author_id:
        if message.forward_from.is_bot:
            return await message.answer('You cannot reward a bot 🤷‍♂️')

        message_text = f'\'{message.text[:50]}\'' if message.text\
            else 'THE FORWARDED MESSAGE DOES NOT CONTAIN TEXT'

        connection = await est_connection()

        reward_size = await connection.fetchrow('''
            SELECT reward_size from vip_users WHERE tg_id = $1;
        ''', user_id)

        await connection.close()

        if reward_size:
            await message.answer(
                f'You rewarded a user under Telegram id {author_id}\n'
                f'with {reward_size[0]} VIZ\n'
                f'The text from the forwarded message is:\n'
                f'<em>{message_text}...</em>',
                parse_mode='html'
            )
        elif not reward_size:
            await message.answer(
                'You did not provide required data for me '
                'to handle forwarded messages. '
                'Use /start command to fix that.'
            )
    elif message.forward_from_chat and message.forward_from is None:
        await message.answer('You cannot reward a channel 🤷‍♂️')
    elif message.forward_from is None:
        await message.answer(
            'You cannot reward the sender of this message!'
        )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
