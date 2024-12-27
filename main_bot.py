from dotenv import load_dotenv
import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import Input_car_num_again
import get_car_num
import after_payment
import parasitic_browser

BOT_TOKEN='7975991113:AAF1I6DFbCipiX0WBuqw7iHKzdcAPIZfcHs'

default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=BOT_TOKEN, default=default)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

async def main_bot_routers():
    dp.include_routers(
        get_car_num.router,
        after_payment.router,
        Input_car_num_again.router,
        parasitic_browser.router
    )

    driver = webdriver.Edge()
    driver.get('https://autoteka.ru')
    enter_btn = driver.find_element(By.CLASS_NAME, 'fotq3')
    enter_btn.click()

    # while True:
    #     driver = webdriver.Edge()
    #     driver.get('https://autoteka.ru')
    #     enter_btn = driver.find_element(By.CLASS_NAME, 'fotq3')
    #     enter_btn.click()
    #     await asyncio.sleep(999)
    #     print('рррррр')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)








if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main_bot_routers())
