import re

from aiogram.dispatcher.filters import Filter
from aiogram import types


class Regexp(Filter):
    key = 'is_int_or_float'

    pattern = re.compile(r'[\d]+.[\d]')

    async def check(self, msg: types.Message) -> bool:
        return self.pattern.match(msg.text)