'''
1. админы или просто "спонсоры" чата форвардят полезные сообщения в бот;
2. бот запоминает того, кто форварднул (спонсора), автора сообщения и текст сообщения (ты это уже фактически сделал) 
и передаёт эти данные в специальный скрипт на сервере;
3. скрипт сопоставляет телеграм-аккаунты спонсора и получателя награды с их аккаунтами в ВИЗе;
4. скрипт проводит несколько транзакций, в результате которых получатель награды получает токены viz от спонсора на свой аккаунт в ВИЗе.
'''
import asyncio
# import asyncpg

import logging

from aiogram import Bot, Dispatcher, executor, types
from config import (
    API_TOKEN, DB_NAME, DB_USER, DB_PASSW, DB_HOST, DB_PORT, DATABASE_URL
)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from db import create_table
from states import FSMIntro
from filters import Regexp


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def handle_start_command(message: types.Message):
    await message.answer(
        #'provide name, reg key and reward size divided by comma'
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


# @dp.message_handler(
#         #Regexp(),
#         state=FSMIntro.Q_reward_size
# )
# async def handle_fsm_reward_size(message: types.Message, state: FSMContext):
#     answer = message.text
#     async with state.proxy() as data:
#         data['reward_size'] = answer

#     data = await state.get_data()
#     tg_id = message.from_user.id
#     name = data.get('name')
#     reg_key = data.get('reg_key')
#     reward_size = data.get('reward_size')
#     print(
#         type(tg_id),
#         type(name),
#         type(reg_key),
#         type(reward_size)
#     )

#     connection = await asyncpg.connect(
#         user=DB_USER,
#         password=DB_PASSW,
#         database=DB_NAME,
#         host=DB_HOST,
#         port=DB_PORT
#     )

#     await create_table(connection)

#     await connection.execute('''
#         INSERT INTO vip_users (
#         tg_id, viz_account, regular_key, reward_size
#         )
#         VALUES ($1, $2, $3::text, $4);
#     ''', tg_id, name, reg_key, reward_size)

#     await connection.close()

#     await message.answer('Your settings are saved to database!')

#     await state.finish()


# @dp.message_handler()
# async def echo(message: types.Message):
#     user_id = message.from_user.id
#     author_id = message.forward_from.id if message.forward_from\
#         else message.from_user.id
#     text = message.text
#     await message.answer(f'<b>Ваш ID:</b> {user_id}\n'
#                          f'<b>ID автора сообщения:</b> {author_id}\n'
#                          f'<b>Сообщение:</b> {text}', parse_mode='html')


# @dp.message_handler(lambda msg: len(msg.text.replace(' ', '').split(',')) == 3)
# async def forward_msg(message: types.Message):
#     text = message.text
#     print('text:', text)
#     items = text.replace(' ', '').split(',')
#     print('items:', items)
#     tg_id = message.from_user.id
#     name = items[0]
#     reg_key = items[1]
#     reward_size = items[2]

#     connection = await asyncpg.connect(
#         user=DB_USER,
#         password=DB_PASSW,
#         database=DB_NAME,
#         host=DB_HOST,
#         port=DB_PORT
#     )

#     await create_table(connection)

#     await connection.execute('''
#         INSERT INTO vip_users (
#         tg_id, viz_account, regular_key, reward
#         )
#         VALUES ($1, $2, $3::text, $4);
#     ''', tg_id, name, reg_key, reward_size)

#     data = await connection.fetch('SELECT * FROM vip_users;')

#     await message.answer(data)

#     await connection.close()

#     await message.reply('Data inserted successfully!')


@dp.message_handler(content_types='text')
async def all(message: types.Message):
    await message.answer(
        'always work'
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
