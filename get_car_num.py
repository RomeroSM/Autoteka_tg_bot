import asyncio
import time
import os
import random
import sqlite3
import requests
import json
from datetime import datetime
from itertools import chain

from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, message, FSInputFile
from aiogram import Bot, Dispatcher, html, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

import main_bot

router = Router()

conn = sqlite3.connect('data_db.db')
cur = conn.cursor()

class Input(StatesGroup):
    get_c_num = State()
    get_reqest = State()
    get_c_num_again = State()

class MyCallback(CallbackData, prefix="User_data"):
    timestamp: float
    separator: str



cur.execute("SELECT chat_id FROM admin_chat_data WHERE chat_status != 0;")
admin_chat_id_db = (cur.fetchall())
admin_chat_id_db= list(chain(*admin_chat_id_db))
admin_chat_id_db = admin_chat_id_db[0]



noco_port = ''




@router.message(CommandStart())
async def command_start_handler(message: Message, state:FSMContext):
    chat_id = message.chat.id
    user_name = message.from_user.username

    req = requests.get(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/m2kf36uhm3ogx8m/records',
                       params={'where': f'(telegramID,eq,{chat_id})'},
                       headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})
    json_req = req.json()

    req_list = json_req['list']

    current_time = str(datetime.now())
    current_time = current_time.split('.', 1)[0]


    if len(req_list) == 0:
        a = requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/m2kf36uhm3ogx8m/records',
                      data= {"Title": "data",
                             "telegramID": f'{chat_id}',
                             "telegramName": f"{user_name}",
                             "LoginDate": f"{current_time}+03:00"
                            },
                      headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})

    else:
        pass




    builder_start_menu = InlineKeyboardBuilder()
    builder_start_menu.button(text=f"Проверить автомобиль", callback_data=f"start_work")
    builder_start_menu.row(InlineKeyboardButton(text='Обратиться в тех. поддержку', callback_data=f'TS'))
    builder_start_menu.row(InlineKeyboardButton(text='Посмотреть пример отчета', callback_data='report_ex'))


    try:
        await main_bot.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    except:
        pass

    await message.answer(f"Приветствую, {html.bold(message.from_user.full_name)}!\n"
                              f"Я бот, который сформирует отчет по интересующему Вас автомобилю. "
                              f"Осуществляю проверку истории автомобиля по гос. номеру, номеру кузова и VIN коду.", reply_markup = builder_start_menu.as_markup())




@router.callback_query(F.data == 'start_work')
async def start_work(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    await state.set_state(Input.get_c_num)
    await call.message.answer(f"Для того чтобы проверить историю автомобиля, необходимо ввести гос. номер, номер кузова или VIN код.\n\n"
                         f""
                         f"Напоминаю, что вводимая Вами информация должна соответствовать стандартам:\n"
                         f"Гос. номер состоит из 7-9 символов: серии, номера и кода региона.\n"
                         f"Номер кузова состоит из 8-16 символов;\n"
                         f"VIN код состоит из 17 символов.")





@router.callback_query(F.data == 'TS')
async def start_Technical_support(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    await state.set_state(Input.get_reqest)
    await call.message.answer('Введите запрос, который вы хотите отправить в тех. поддержку')


@router.callback_query(F.data == 'report_ex')
async def report_ex(call: CallbackQuery):
    await call.message.delete()

    chat_id = call.message.chat.id

    await call.message.answer('Пример отчета по истории автомобиля')
    await call.message.answer('https://autoteka.ru/report/web/uuid/24de3a5a-b4f7-4c9f-ac6d-ca188722b5a2?fromSource=myReports')

    await call.message.answer('Чтобы продолжить работу, введите команду /start')




@router.message(Input.get_reqest)
async def Technical_support(message: Message, state: FSMContext):
    request = str(message.text)
    await state.update_data(request = request)

    current_time = str(datetime.now())
    current_time = current_time.split('.', 1)[0]

    user_tgid = str(message.from_user.id)

    user_url = str(message.from_user.username)
    if user_url != 'None':
        user_url = '@' + user_url
    else:
        user_url = 'У пользователя нет параметра username'


    await message.bot.send_message(f'{admin_chat_id_db}', f'Пользователь с tg id {user_tgid} подал запрос в тех. поддержку\n'
                                             f'Ссылка на аккаунт: {user_url}\n'
                                             f'Время: {current_time}\n'
                                             f'Текст запроса:\n\n'
                                             f''
                                             f'{request}\n\n'
                                             f''
                                             f'#ТП')

    await message.answer('Запрос в тех. поддержку успешно отправлен.')
    await message.answer('Для формирования отчета по автомобилю введите команду /start"')





@router.message(Input.get_c_num)
async def get_c_num(message: Message, state: FSMContext):
    await main_bot.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    car_num = str(message.text)
    await state.update_data(car_num = message.text)

    builder_correct_num = InlineKeyboardBuilder()
    builder_correct_num.button(text=f"Да", callback_data=f"correct_num")
    builder_correct_num.button(text='Нет', callback_data=f'wrong_num')

    if 7 <= len(car_num) <= 17:
        await message.answer(f'Проверьте введенные Вами значения: \n'
                             f'{car_num}', reply_markup=builder_correct_num.as_markup())
    else:
        await message.answer('Введенные Вами значения недопустимы. Проверьте корректность данных и введите их заново.')
        await state.set_state(Input.get_c_num)





@router.callback_query(F.data == 'wrong_num')
async def wrong_num(call: CallbackQuery, state: FSMContext):
    await main_bot.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
    await state.set_state(Input.get_c_num)
    await call.message.delete()
    await call.message.answer(
        f"Для того чтобы проверить историю автомобиля, необходимо ввести гос. номер, номер кузова или VIN код.\n\n"
        f""
        f"Напоминаю, что вводимая Вами информация должна соответствовать стандартам:\n"
        f"Гос. номер состоит из 7-9 символов: серии, номера и кода региона.\n"
        f"Номер кузова состоит из 8-16 символов;\n"
        f"VIN код состоит из 17 символов.")



@router.callback_query(F.data == 'correct_num')
async def correct_num(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    user_tgid = str(call.from_user.id)
    print(user_tgid)

    data = await state.get_data()
    car_num = data["car_num"]

    current_time = str(datetime.now())
    current_time = current_time.split('.', 1)[0]

    requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/m11xijo7hzn6z24/records',
                  data={"Title": "data",
                        "telegramID": f'{user_tgid}',
                        "car_num": f"{car_num}",
                        "Time": f"{current_time}+03:00"
                        },
                  headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})


    random_code = random.randint(1000,9999)

    await call.message.answer(f'Ваш одноразовый код платежа\n'
                              f'Вам потребуется ввести его в комментарий к платежу.\n'
                              f'<b>ВНИМАНИЕ!</b> Если вы не введете данный код, то платеж<b> НЕ ПРОЙДЕТ</b>.\n')
    await call.message.answer(f'<b>{random_code}</b>')
    await call.message.answer(f'Убедитесь в том, что ввели код в комментарий к платежу.')
    await call.message.answer(f'Стоимость отчета в рамках промопериода составит <b>100 ₽</b>.\n'
                              f'Ссылка для для оплаты: \n'
                              f'https://www.tinkoff.ru/rm/filipov.andrey7/yL5ed52495 \n ')

    await state.clear()

    timestamp = time.time()

    user_data_str = MyCallback(timestamp = timestamp, separator = 'separator')

    builder_approved = InlineKeyboardBuilder()
    builder_approved.button(text='Одобрено', callback_data=user_data_str)

    current_time = str(datetime.now())
    current_time = current_time.split('.', 1)[0]

    user_url = str(call.from_user.username)
    if user_url != 'None':
        user_url = '@' + user_url
    else:
        user_url = 'У пользователя нет параметра username'

    ins_data = (timestamp, user_tgid, car_num, random_code, user_url, current_time)

    cur.execute("INSERT INTO user_data_payment VALUES(?, ?, ?, ?, ?, ?);", ins_data)
    conn.commit()

    await call.bot.send_message(f'{admin_chat_id_db}', text=f'Пользователь с tg id {user_tgid} запросил отчет по автомобилю.\n'
                                          f'Ссылка на аккаунт: {user_url}\n'
                                          f'Время: {current_time}\n'
                                          f'Данные о машине: {car_num}\n'
                                          f'Одноразовый код: {random_code}\n'
                                          f'#Подтверждение_оплаты',
                                          reply_markup=builder_approved.as_markup())

