'''
1. админы или просто "спонсоры" чата форвардят полезные сообщения в бот;
2. бот запоминает того, кто форварднул (спонсора), автора сообщения и текст сообщения (ты это уже фактически сделал) 
и передаёт эти данные в специальный скрипт на сервере;
3. скрипт сопоставляет телеграм-аккаунты спонсора и получателя награды с их аккаунтами в ВИЗе;
4. скрипт проводит несколько транзакций, в результате которых получатель награды получает токены viz от спонсора на свой аккаунт в ВИЗе.
'''
import asyncio
import asyncpg

import logging

from aiogram import Bot, Dispatcher, executor, types, filters
from config import (
    API_TOKEN, DB_NAME, DB_USER, DB_PASSW, DB_HOST, DB_PORT
)

from db import create_table


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# @dp.message_handler()
# async def echo(message: types.Message):
#     user_id = message.from_user.id
#     author_id = message.forward_from.id if message.forward_from\
#         else message.from_user.id
#     text = message.text
#     await message.answer(f'<b>Ваш ID:</b> {user_id}\n'
#                          f'<b>ID автора сообщения:</b> {author_id}\n'
#                          f'<b>Сообщение:</b> {text}', parse_mode='html')


@dp.message_handler(commands=['start'])
async def handle_start_command(message: types.Message):
    await message.answer(
        'provide name, reg key and reward size divided by comma'
    )


@dp.message_handler(lambda msg: len(msg.text.replace(' ', '').split(',')) == 3)
async def forward_msg(message: types.Message):
    text = message.text
    items = text.replace(' ', '').split(',')
    tg_id = message.from_user.id
    name = items[0]
    reg_key = int(items[1])
    reward_size = float(items[2])

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
        tg_id, viz_account, regular_key, reward
        )
        VALUES ($1, $2, $3, $4);
    ''', tg_id, name, reg_key, reward_size)

    data = await connection.fetch('SELECT * FROM vip_users;')

    await message.answer(data)

    await connection.close()

    await message.reply('Data inserted successfully!')


@dp.message_handler(filters.Text)
async def all(message: types.Message):
    await message.answer(
        'always work'
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
