import os

from aiogram.enums import ParseMode
from dotenv import load_dotenv

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, message, FSInputFile,LabeledPrice, pre_checkout_query, PreCheckoutQuery
from aiogram import Dispatcher, html, Router, F, MagicFilter, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.methods.send_invoice import SendInvoice
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()

router = Router()



async def payment(bot: Bot, chat_id):
    await bot.send_invoice(
        chat_id=chat_id,
        title='Оплата',
        description=f'Стоимость отчета в рамках промопериода составляет 100₽',
        payload='Payment',
        provider_token=os.getenv('PROVIDER_TOKEN'),
        currency='RUB',
        start_parameter='pay',
        photo_url='https://i.postimg.cc/KcQMP1pz/photo-2025-01-16-13-38-54.jpg',
        photo_size=100,
        photo_width=800,
        photo_height=500,
        protect_content=True, #это защита от пересылки, копирования и тд

        provider_data=None,
        need_phone_number=True,
        send_phone_number_to_provider=True,


        prices=[
            LabeledPrice(
                label='К оплате',
                # Цена (ЦЕНУ ПИСАТЬ В КОПЕЙКАХ):
                amount = 10000
            )
        ]
    )

























