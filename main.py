import asyncpg

import logging

from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, DB_NAME, DB_USER, DB_PASSW, DB_HOST, DB_PORT
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from db import create_table
from states import FSMIntro


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def handle_start_command(message: types.Message):
    await message.answer(
        'Hello! Please, write your name:'
    )
    await FSMIntro.Q_name.set()


@dp.message_handler(state=FSMIntro.Q_name)
async def handle_fsm_name(message: types.Message, state: FSMContext):
    answer = message.text
    async with state.proxy() as data:
        data['name'] = answer
    await message.answer(
        'Good! Now please provide you regular key:'
    )
    await FSMIntro.next()


@dp.message_handler(state=FSMIntro.Q_reg_key)
async def handle_fsm_reg_key(message: types.Message, state: FSMContext):
    answer = message.text
    async with state.proxy() as data:
        data['reg_key'] = answer
    await message.answer(
        'And lastly set the reward size for the user'
        'you want to gift it with (minimum 1 VIZ):'
    )
    await FSMIntro.next()


@dp.message_handler(
        state=FSMIntro.Q_reward_size
)
async def handle_fsm_reward_size(message: types.Message, state: FSMContext):
    answer = message.text
    async with state.proxy() as data:
        data['reward_size'] = answer

    data = await state.get_data()
    tg_id = message.from_user.id
    name = data.get('name')
    reg_key = data.get('reg_key')
    reward_size = data.get('reward_size')

    connection = await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSW,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )

    await create_table(connection)

    await connection.execute('''
        INSERT INTO vip_users (
        tg_id, viz_account, regular_key, reward_size
        )
        VALUES ($1, $2, $3::text, $4);
    ''', tg_id, name, reg_key, reward_size)

    await connection.close()

    await message.answer('Your settings are saved to database!')

    await state.finish()


@dp.message_handler()
async def echo(message: types.Message):
    user_id = message.from_user.id
    author_id = message.forward_from.id if message.forward_from\
        else message.from_user.id
    if user_id != author_id:
        # text = message.text
        #  What do I need to safe the text of the forwarded msg for?

        connection = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASSW,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT
        )

        reward_size = await connection.fetchrow('''
            SELECT reward_size from vip_users
            WHERE tg_id = $1 ORDER BY id DESC LIMIT 1;
        ''', user_id)

        await message.answer(f'You rewarded a user under {author_id} TG-ID\n'
                             f'with {reward_size[0]} VIZ')

    else:
        await message.answer('Please, end forwarded message, not your own!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
