import os
import sys
import asyncio
import logging

from aiogram.types import PreCheckoutQuery
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, message, FSInputFile,LabeledPrice, pre_checkout_query, PreCheckoutQuery

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import Input_car_num_again
import get_car_num
import after_payment
from after_payment import correct_num


load_dotenv()
default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=os.getenv('TOKEN'), default=default)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery, bot: bot):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)
    user_tgid = pre_checkout_query.from_user.id
    await correct_num(user_tgid=user_tgid, bot=bot)

async def main_bot_routers():
    dp.include_routers(
        get_car_num.router,
        after_payment.router,
        Input_car_num_again.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())








if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main_bot_routers())
