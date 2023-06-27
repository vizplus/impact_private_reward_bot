import os
import logging

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')

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
