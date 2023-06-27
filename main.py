'''
1. админы или просто "спонсоры" чата форвардят полезные сообщения в бот;
2. бот запоминает того, кто форварднул (спонсора), автора сообщения и текст сообщения (ты это уже фактически сделал) 
и передаёт эти данные в специальный скрипт на сервере;
3. скрипт сопоставляет телеграм-аккаунты спонсора и получателя награды с их аккаунтами в ВИЗе;
4. скрипт проводит несколько транзакций, в результате которых получатель награды получает токены viz от спонсора на свой аккаунт в ВИЗе.
'''


import logging

from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, DATABASE_URL


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(message: types.Message):
    user_id = message.from_user.id
    author_id = message.forward_from.id if message.forward_from\
        else message.from_user.id
    text = message.text
    await message.answer(f'<b>Ваш ID:</b> {user_id}\n'
                         f'<b>ID автора сообщения:</b> {author_id}\n'
                         f'<b>Сообщение:</b> {text}', parse_mode='html')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
