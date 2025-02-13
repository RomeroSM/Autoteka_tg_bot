import os
import time
import asyncio
import sqlite3
from itertools import chain
from datetime import datetime
from random import random

from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, message, FSInputFile
from aiogram import Bot, Dispatcher, html, Router, F, MagicFilter
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from main_bot import bot


router = Router()

conn = sqlite3.connect('data_db.db')
cur = conn.cursor()

class Input_again(StatesGroup):
    get_c_num_again = State()

class MyCallback(CallbackData, prefix="User_data"):
    user_tgid: int
    separator: str
    car_num: str




@router.message(Input_again.get_c_num_again)
async def Input_car_num_again(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    car_num = str(message.text)
    await state.update_data(car_num=message.text)

    user_tgid = str(message.from_user.id)

    user_data_str = MyCallback(user_tgid = user_tgid, separator = 'Sep', car_num = car_num)

    builder_correct_num = InlineKeyboardBuilder()
    builder_correct_num.button(text=f"Да", callback_data=user_data_str)
    builder_correct_num.button(text='Нет', callback_data=f'wrong_num_icna')



    if 7 <= len(car_num) <= 17:
        await message.answer(f'Проверьте введенные Вами значения:\n'
                             f'{car_num}', reply_markup=builder_correct_num.as_markup())
    else:
        await message.answer('Введенные Вами значения недопустимы. Проверьте корректность данных и введите их заново.')
        await state.set_state(Input_again.get_c_num_again)



@router.callback_query(F.data == 'wrong_num_icna')
async def wrong_num(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await state.set_state(Input_again.get_c_num_again)
    await call.message.delete()
    await call.message.answer(f"Напоминаю, что вводимая Вами информация должна соответствовать стандартам:\n"
                              f"Гос. номер состоит из 7-9 символов: серии, номера и кода региона.\n"
                              f"Номер кузова состоит из 8-16 символов;\n"
                              f"VIN код состоит из 17 символов.")



@router.callback_query(MyCallback.filter(F.separator == "Sep"))
async def input_again(call: CallbackQuery, state: FSMContext):
    call_data = call.data.replace('User_data','')
    call_data = call_data.replace('Sep', '')
    call_data = call_data.replace(':', '')
    call_data = int(call_data)
    await call.message.delete()

