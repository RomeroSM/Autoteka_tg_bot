import os
import time
import asyncio
import sqlite3
import requests
from itertools import chain
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, message, FSInputFile
from aiogram import Bot, Dispatcher, html, Router, F, MagicFilter
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


router = Router()

conn = sqlite3.connect('data_db.db')
cur = conn.cursor()

class Input_again(StatesGroup):
    get_c_num_again = State()

class MyCallback(CallbackData, prefix="User_data"):
    timestamp: float
    separator: str


cur.execute("SELECT chat_id FROM admin_chat_data WHERE chat_status != 0;")
admin_chat_id_db = (cur.fetchall())
admin_chat_id_db= list(chain(*admin_chat_id_db))
admin_chat_id_db = admin_chat_id_db[0]

noco_port = ''






@router.callback_query(MyCallback.filter(F.separator == "separator"))
async def correct_num(call: CallbackQuery):
    call_data = call.data.replace('User_data', '')
    call_data = call_data.replace(':', '')
    call_data = call_data.replace('separator', '')

    timestamp = call_data
    timestamp_list = list()
    timestamp_list.append(timestamp)
    timestamp = tuple(timestamp_list)

    cur.execute("SELECT user_tgid, car_num, random_code, user_url, time  FROM user_data_payment WHERE timestamp = ?;", timestamp)
    db_data = cur.fetchall()
    db_data = list(chain(*db_data))

    user_tgid = db_data[0]
    car_num = db_data[1]
    random_code = db_data[2]
    user_url = db_data[3]
    current_time = db_data[4]


    await call.message.edit_text(text=f'Пользователь с tg id {user_tgid} запросил отчет по автомобилю.\n'
                                          f'Ссылка на аккаунт: {user_url}\n'
                                          f'Время: {current_time}\n'
                                          f'Данные о машине: {car_num}\n'
                                          f'Одноразовый код: {random_code}\n'
                                          f'#Оплата_прошла',)

    user_url = str(call.from_user.username)
    if user_url != 'None':
        user_url = '@' + user_url
    else:
        user_url = 'У пользователя нет параметра username'

    current_time = str(datetime.now())
    current_time = current_time.split('.', 1)[0]

    await call.bot.send_message(text='Формирование отчета по автомобилю займет до 5 минут.\n'
                                     'Пожалуйста, ожидайте.', chat_id = user_tgid)

    try:
        cur.execute("SELECT mail FROM accounts WHERE number_of_checks != 0;")
        mail_db = (cur.fetchall())
        mail_db= list(chain(*mail_db))
        mail_db = mail_db[0]

        mail_db_list = list()
        mail_db_list.append(mail_db)

        cur.execute("SELECT password FROM accounts WHERE number_of_checks != 0;")
        password_db = (cur.fetchall())
        password_db = list(chain(*password_db))
        password_db = password_db[0]

    except:
        user_data_str = MyCallback(user_tgid=user_tgid, separator='separator', car_num=car_num)

        builder_approved = InlineKeyboardBuilder()
        builder_approved.button(text='Кол-во проверок восстановлено', callback_data=user_data_str)

        await call.bot.send_message(f'{admin_chat_id_db}', f'Пользователь с tg id {user_tgid} столкнулся с проблемой.\n'
                                                 f'Ссылка на аккаунт: {user_url}\n'
                                                 f'Время: {current_time}\n'
                                                 f'Проблема:\n'
                                                 f'Проблема с БД. Отсутствуют аккаунты с достаточным количеством проверок.\n'
                                                 f'ВНИМАНИЕ! Нажимать на кнопку ниже стоит только в том случае, если достаточное количество проверок восстановлено. '
                                                 f'В противном случае при запуске процесса обработки запроса пользователя снова возникнет данная проблема"\n'
                                                 f'#проблема',
                                                 reply_markup=builder_approved.as_markup())

        await call.bot.send_message(chat_id=user_tgid, text='Просим прощения, сервис временно недоступен.\n'
                                                            'Пожалуйста, ожидайте. Запрос на исправление проблемы отрпавлен администратору.\n'
                                                            'Можете не беспокоиться, ваша оплаченная  проверка никуда не пропадет.\n'
                                                            'Как только будут исправлены все неполадки ваш запрос будет обработан.')

    else:
        driver = webdriver.Edge()
        driver.get('https://autoteka.ru')

        #await asyncio.sleep(999)

        mail_db = str(mail_db)

        enter_btn = driver.find_element(By.CLASS_NAME, 'fotq3')
        enter_btn.click()

        email_inp = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/form/div[1]/div/input')
        email_inp.send_keys(f'{mail_db}' + Keys.RETURN)

        password_inp = driver.find_element(By.XPATH,
                                           '/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/form/div[2]/div/input')
        password_inp.send_keys(f'{password_db}' + Keys.RETURN)

        enter_btn2 = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/form/button')
        enter_btn2.click()

        check_num = driver.find_element(By.XPATH,
                                        '/html/body/div[1]/div/div[2]/div[1]/div/div/div/div[1]/div[4]/form/div/div/input')
        check_num.send_keys(f'{car_num}' + Keys.RETURN)

        await asyncio.sleep(10)

        try:
            get_report_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[3]/div[2]/button')
            get_report_btn.click()
        except:
            try:
                update_report_btn1 = driver.find_element(By.XPATH,
                                                        '/html/body/div[1]/div/div[2]/div/div/div/div[3]/button[2]')
                update_report_btn1.click()

                update_report_btn2 = driver.find_element(By.XPATH,
                                                        '/html/body/div[1]/div/div[2]/div/div/div/div[3]/div[2]/div/div[2]/button')
                update_report_btn2.click()

            except:

                builder_input_again = InlineKeyboardBuilder()
                builder_input_again.button(text=f"Ввести номер заново", callback_data=f"input_again")

                await call.bot.send_message(chat_id=user_tgid,
                                            text='Данных для формирования отчета по указанным Вами значениям недостаточно.\n'
                                                 'Попробуйте ввести другие значения или проверьте правильность введенных данных.',
                                            reply_markup=builder_input_again.as_markup())

            else:
                current_time = str(datetime.now())
                current_time = current_time.split('.', 1)[0]

                try:
                    cur.execute("SELECT number_of_checks FROM accounts WHERE mail = ?;", mail_db_list)
                    number_of_checks_db = (cur.fetchall())
                    number_of_checks_db = list(chain(*number_of_checks_db))
                    number_of_checks_db = int(number_of_checks_db[0])

                    number_of_checks_upd = str(number_of_checks_db - 1)

                    sql_data_list = list()
                    sql_data_list.append(number_of_checks_upd)
                    sql_data_list.append(mail_db)

                    cur.execute('UPDATE accounts SET number_of_checks = ? WHERE mail = ?;', sql_data_list)
                    conn.commit()
                except:
                    await call.bot.send_message(f'{admin_chat_id_db}',
                                                f'Пользователь с tg id {user_tgid} столкнулся с проблемой.\n'
                                                f'Ссылка на аккаунт: {user_url}\n'
                                                f'Время: {current_time}\n'
                                                f'Проблема:\n\n'
                                                f''
                                                f'Проблема с бд. Не удалось уменьшить кол-во проверок на аккаунте.\n'
                                                f'#проблема')

                await asyncio.sleep(200)

                # separator = '/'
                #
                # current_url = driver.current_url
                # splited_current_url = current_url.split(separator, 6)
                #
                # url_part1 = splited_current_url[0]
                # url_part2 = splited_current_url[2]
                # url_part3 = splited_current_url[3]
                # url_part4 = splited_current_url[4]
                # url_part5 = splited_current_url[5]
                #
                # desired_split_url= str(url_part1 + '//' + url_part2 + '/' + url_part3 + '/' + url_part4 + '/' + url_part5)
                #
                #
                # while desired_split_url != 'https://autoteka.ru/report/web/uuid':
                #     time.sleep(5)
                #     current_url = driver.current_url
                #     splited_current_url = current_url.split(separator, 6)
                #
                #     url_part1 = splited_current_url[0]
                #     url_part2 = splited_current_url[2]
                #     url_part3 = splited_current_url[3]
                #     url_part4 = splited_current_url[4]
                #     url_part5 = splited_current_url[5]
                #
                #     desired_split_url = str(url_part1 + '//' + url_part2 + '/' + url_part3 + '/' + url_part4 + '/' + url_part5)

                try:
                    VIN_num = driver.find_element(By.CLASS_NAME, 'Gnn0t')
                except:
                    await call.bot.send_message(f'{admin_chat_id_db}',
                                                f'Пользователь с tg id {user_tgid} столкнулся с проблемой.\n'
                                                f'Ссылка на аккаунт: {user_url}\n'
                                                f'Время: {current_time}\n'
                                                f'Проблема:\n\n'
                                                f''
                                                f'Проблема с web driver. Не удалось скопировать VIN. Пользователю была отправлена ссылка на отчет по автомобилю.\n'
                                                f'#проблема')

                    current_url = driver.current_url

                    await call.bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)
                    await call.bot.send_message(text=current_url, chat_id=user_tgid)
                    await call.bot.send_message(text='Для формирования отчета по другому автомобилю введите команду ',
                                                chat_id=user_tgid)

                    current_time = str(datetime.now())
                    current_time = current_time.split('.', 1)[0]

                    requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/mnjnl9cx9414h9m/records',
                                  data={"Title": "data",
                                        "telegramID": f'{user_tgid}',
                                        "car_num": f"{car_num}",
                                        "time": f"{current_time}+03:00",
                                        "autoteka_link": f"{current_url}"
                                        },
                                  headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})


                else:
                    download_btn = driver.find_element(By.XPATH,
                                                       '/html/body/div[1]/div/div[2]/div/autoteka-report-autotekareportweb/div/div/article/div[1]/header/div/div[2]/button')
                    download_btn.click()

                    await asyncio.sleep(10)

                    doc = FSInputFile(path=f'C:/Users/roman/Downloads/Отчёт Автотеки - {VIN_num}.pdf')

                    current_url = driver.current_url

                    await call.bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)
                    await call.bot.send_message(text=current_url, chat_id=user_tgid)
                    await call.bot.send_document(document=doc, chat_id=user_tgid)
                    await call.bot.send_message(text='Для формирования отчета по другому автомобилю введите команду "\start',
                                                chat_id=user_tgid)

                    os.remove(path=f'C:/Users/roman/Downloads/Отчёт Автотеки - {VIN_num}.pdf')

                    current_time = str(datetime.now())
                    current_time = current_time.split('.', 1)[0]

                    requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/mnjnl9cx9414h9m/records',
                                  data={"Title": "data",
                                        "telegramID": f'{user_tgid}',
                                        "car_num": f"{car_num}",
                                        "time": f"{current_time}+03:00",
                                        "autoteka_link": f"{current_url}"
                                        },
                                  headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})

        else:
            current_time = str(datetime.now())
            current_time = current_time.split('.', 1)[0]

            try:
                cur.execute("SELECT number_of_checks FROM accounts WHERE mail = ?;", mail_db_list)
                number_of_checks_db = (cur.fetchall())
                number_of_checks_db = list(chain(*number_of_checks_db))
                number_of_checks_db = int(number_of_checks_db[0])

                number_of_checks_upd = str(number_of_checks_db - 1)

                sql_data_list = list()
                sql_data_list.append(number_of_checks_upd)
                sql_data_list.append(mail_db)

                cur.execute('UPDATE accounts SET number_of_checks = ? WHERE mail = ?;', sql_data_list)
                conn.commit()
            except:
                await call.bot.send_message(f'{admin_chat_id_db}', f'Пользователь с tg id {user_tgid} столкнулся с проблемой.\n'
                                                           f'Ссылка на аккаунт: {user_url}\n'
                                                           f'Время: {current_time}\n'
                                                           f'Проблема:\n\n'
                                                           f''
                                                           f'Проблема с БД. Не удалось уменьшить кол-во проверок на аккаунте.\n'
                                                           f'#проблема')

            await asyncio.sleep(200)

            try:
                VIN_num = driver.find_element(By.CLASS_NAME, 'Gnn0t')
            except:
                await call.bot.send_message(f'{admin_chat_id_db}', f'Пользователь с tg id {user_tgid} столкнулся с проблемой.\n'
                                                           f'Ссылка на аккаунт: {user_url}\n'
                                                           f'Время: {current_time}\n'
                                                           f'Проблема:\n\n'
                                                           f''
                                                           f'Проблема с web driver. Не удалось скопировать VIN. Пользователю была отправлена ссылка на отчет по автомобилю.\n'
                                                           f'#проблема')

                current_url = driver.current_url

                await call.bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)
                await call.bot.send_message(text=current_url, chat_id=user_tgid)
                await call.bot.send_message(text='Для формирования отчета по другому автомобилю введите команду ', chat_id=user_tgid)

                current_time = str(datetime.now())
                current_time = current_time.split('.', 1)[0]

                requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/mnjnl9cx9414h9m/records',
                              data={"Title": "data",
                                    "telegramID": f'{user_tgid}',
                                    "car_num": f"{car_num}",
                                    "time": f"{current_time}+03:00",
                                    "autoteka_link": f"{current_url}"
                                    },
                              headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})


            else:
                # download_btn = driver.find_element(By.XPATH,
                #                                    '/html/body/div[1]/div/div[2]/div/autoteka-report-autotekareportweb/div/div/article/div[1]/header/div/div[2]/button')
                # download_btn.click()

                await asyncio.sleep(10)

                doc = FSInputFile(path=f'C:/Users/roman/Downloads/Отчёт Автотеки - {VIN_num}.pdf')

                current_url = driver.current_url

                await call.bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)
                await call.bot.send_message(text=current_url, chat_id=user_tgid)
                await call.bot.send_document(document=doc, chat_id=user_tgid)
                await call.bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)

                os.remove(path=f'C:/Users/roman/Downloads/Отчёт Автотеки - {VIN_num}.pdf')

                current_time = str(datetime.now())
                current_time = current_time.split('.', 1)[0]

                requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/mnjnl9cx9414h9m/records',
                              data={"Title": "data",
                                    "telegramID": f'{user_tgid}',
                                    "car_num": f"{car_num}",
                                    "time": f"{current_time}+03:00",
                                    "autoteka_link": f"{current_url}"
                                    },
                              headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})








@router.callback_query(F.data == 'input_again')
async def input_again(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text=f"Напоминаю, что вводимая Вами информация должна соответствовать стандартам:\n"
                         f"Гос. номер состоит из 7-9 символов: серии, номера и кода региона.\n"
                         f"Номер кузова состоит из 8-16 символов;\n"
                         f"VIN код состоит из 17 символов.")

    await state.set_state(Input_again.get_c_num_again)
    print(await state.get_state())











