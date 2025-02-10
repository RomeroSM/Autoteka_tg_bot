import os
import time
import asyncio
import sqlite3
import requests
from itertools import chain
from datetime import datetime
from dotenv import load_dotenv


from selenium.webdriver.edge.options import Options
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, message, FSInputFile
from aiogram import Bot, Dispatcher, html, Router, F, MagicFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData



router = Router()

conn = sqlite3.connect('data_db.db')
cur = conn.cursor()

class Input_again(StatesGroup):
    get_c_num_again = State()

class MyCallback(CallbackData, prefix="input_again"):
    user_tgid: int
    separator: str


cur.execute("SELECT chat_id FROM admin_chat_data WHERE chat_status != 0;")
admin_chat_id_db = (cur.fetchall())
admin_chat_id_db= list(chain(*admin_chat_id_db))
admin_chat_id_db = admin_chat_id_db[0]

options = Options()




load_dotenv()
noco_port = os.getenv('NOCO_PORT')




async def correct_num(user_tgid, bot):
    await bot.send_message(text='Оплата прошла успешно.\n'
                                'Я начинаю формирование отчета. Обычно это занимает до 5 минут. Пожалуйста, ожидайте.',chat_id = user_tgid)


    user_tgid_list = list()
    user_tgid_list.append(user_tgid)
    user_tgid_tuple = tuple(user_tgid_list)

    cur.execute("SELECT car_num, user_url, time  FROM user_data_payment WHERE user_tgid = ?;", user_tgid_tuple)
    db_data = cur.fetchall()
    db_data = list(chain(*db_data))

    car_num = db_data[0]
    user_url = db_data[1]
    current_time = db_data[2]


    await bot.send_message(text=f'Пользователь с tg id {user_tgid} запросил отчет по автомобилю.\n'
                                          f'Ссылка на аккаунт: {user_url}\n'
                                          f'Время: {current_time}\n'
                                          f'Данные о машине: {car_num}', chat_id=admin_chat_id_db)


    current_time = str(datetime.now())
    current_time = current_time.split('.', 1)[0]

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

        await bot.send_message(f'{admin_chat_id_db}', f'Пользователь с tg id {user_tgid} столкнулся с проблемой.\n'
                                                 f'Ссылка на аккаунт: {user_url}\n'
                                                 f'Время: {current_time}\n'
                                                 f'Проблема:\n'
                                                 f'Проблема с БД. Отсутствуют аккаунты с достаточным количеством проверок.\n'
                                                 f'ВНИМАНИЕ! Нажимать на кнопку ниже стоит только в том случае, если достаточное количество проверок восстановлено. '
                                                 f'В противном случае при запуске процесса обработки запроса пользователя снова возникнет данная проблема"\n'
                                                 f'#проблема',
                                                 reply_markup=builder_approved.as_markup())

        await bot.send_message(chat_id=user_tgid, text='Просим прощения, сервис временно недоступен.\n'
                                                            'Пожалуйста, ожидайте. Запрос на исправление проблемы отрпавлен администратору.\n'
                                                            'Можете не беспокоиться, ваша оплаченная  проверка никуда не пропадет.\n'
                                                            'Как только будут исправлены все неполадки ваш запрос будет обработан.')

    else:
        options = webdriver.EdgeOptions()
        driver = webdriver.Remote(
            command_executor='http://webdriver:4444/wd/hub',
            options=options
        )
        driver.get('https://autoteka.ru')

        #
        # driver = webdriver.Edge()
        # driver.get('https://autoteka.ru')

        #await asyncio.sleep(999)

        mail_db = str(mail_db)

        enter_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[1]/header/div/div[2]/div[2]/button')
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

                user_data_str = MyCallback(user_tgid=user_tgid, separator='separator')

                builder_input_again = InlineKeyboardBuilder()
                builder_input_again.button(text=f"Ввести номер заново", callback_data=user_data_str)

                await bot.send_message(chat_id=user_tgid,
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
                    await bot.send_message(f'{admin_chat_id_db}',
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
                    await bot.send_message(f'{admin_chat_id_db}',
                                                f'Пользователь с tg id {user_tgid} столкнулся с проблемой.\n'
                                                f'Ссылка на аккаунт: {user_url}\n'
                                                f'Время: {current_time}\n'
                                                f'Проблема:\n\n'
                                                f''
                                                f'Проблема с web driver. Не удалось скопировать VIN. Пользователю была отправлена ссылка на отчет по автомобилю.\n'
                                                f'#проблема')

                    current_url = driver.current_url

                    await bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)
                    await bot.send_message(text=current_url, chat_id=user_tgid)
                    await bot.send_message(text='Для формирования отчета по другому автомобилю введите команду ',
                                                chat_id=user_tgid)

                    current_time = str(datetime.now())
                    current_time = current_time.split('.', 1)[0]

                    try:
                        requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/mnjnl9cx9414h9m/records',
                                      data={"Title": "data",
                                            "telegramID": f'{user_tgid}',
                                            "car_num": f"{car_num}",
                                            "time": f"{current_time}+03:00",
                                            "autoteka_link": f"{current_url}"
                                            },
                                      headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})
                    except:
                        pass


                else:
                    download_btn = driver.find_element(By.XPATH,
                                                       '/html/body/div[1]/div/div[2]/div/autoteka-report-autotekareportweb/div/div/article/div[1]/header/div/div[2]/button')
                    download_btn.click()

                    await asyncio.sleep(10)

                    doc = FSInputFile(path=f'C:/Users/roman/Downloads/Отчёт Автотеки - {VIN_num}.pdf')

                    current_url = driver.current_url

                    current_time = str(datetime.now())
                    current_time = current_time.split('.', 1)[0]

                    await bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)
                    await bot.send_message(text=current_url, chat_id=user_tgid)
                    await bot.send_document(document=doc, chat_id=user_tgid)
                    await bot.send_message(text='Для формирования отчета по другому автомобилю введите команду "\start',
                                                chat_id=user_tgid)

                    await bot.send_message(f'{admin_chat_id_db}',
                                                text=f'Данные по автомобилю пользователя с tg id {user_tgid}.\n'
                                                f'Ссылка на аккаунт: {user_url}\n'
                                                f'Время: {current_time}\n'
                                                f'Данные о машине: {car_num}\n'
                                                f'Ссылка на отчет Автотеки: {current_url}\n'
                                                f'#Отчет получен',)

                    os.remove(path=f'C:/Users/roman/Downloads/Отчёт Автотеки - {VIN_num}.pdf')

                    current_time = str(datetime.now())
                    current_time = current_time.split('.', 1)[0]

                    try:
                        requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/mnjnl9cx9414h9m/records',
                                      data={"Title": "data",
                                            "telegramID": f'{user_tgid}',
                                            "car_num": f"{car_num}",
                                            "time": f"{current_time}+03:00",
                                            "autoteka_link": f"{current_url}"
                                            },
                                      headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})
                    except:
                        pass

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
                await bot.send_message(f'{admin_chat_id_db}', f'Пользователь с tg id {user_tgid} столкнулся с проблемой.\n'
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
                await bot.send_message(f'{admin_chat_id_db}', f'Пользователь с tg id {user_tgid} столкнулся с проблемой.\n'
                                                           f'Ссылка на аккаунт: {user_url}\n'
                                                           f'Время: {current_time}\n'
                                                           f'Проблема:\n\n'
                                                           f''
                                                           f'Проблема с web driver. Не удалось скопировать VIN. Пользователю была отправлена ссылка на отчет по автомобилю.\n'
                                                           f'#проблема')

                current_url = driver.current_url

                current_time = str(datetime.now())
                current_time = current_time.split('.', 1)[0]

                await bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)
                await bot.send_message(text=current_url, chat_id=user_tgid)
                await bot.send_message(text='Для формирования отчета по другому автомобилю введите команду ', chat_id=user_tgid)

                await bot.send_message(f'{admin_chat_id_db}',
                                            text=f'Данные по автомобилю пользователя с tg id {user_tgid}.\n'
                                                 f'Ссылка на аккаунт: {user_url}\n'
                                                 f'Время: {current_time}\n'
                                                 f'Данные о машине: {car_num}\n'
                                                 f'Ссылка на отчет Автотеки: {current_url}\n'
                                                 f'#Отчет получен', )

                try:
                    requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/mnjnl9cx9414h9m/records',
                                  data={"Title": "data",
                                        "telegramID": f'{user_tgid}',
                                        "car_num": f"{car_num}",
                                        "time": f"{current_time}+03:00",
                                        "autoteka_link": f"{current_url}"
                                        },
                                  headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})
                except:
                    pass


            else:
                download_btn = driver.find_element(By.XPATH,
                                                   '/html/body/div[1]/div/div[2]/div/autoteka-report-autotekareportweb/div/div/article/div[1]/header/div/div[2]/button')
                download_btn.click()

                await asyncio.sleep(10)

                doc = FSInputFile(path=f'C:/Users/roman/Downloads/Отчёт Автотеки - {VIN_num}.pdf')

                current_url = driver.current_url

                current_time = str(datetime.now())
                current_time = current_time.split('.', 1)[0]

                await bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)
                await bot.send_message(text=current_url, chat_id=user_tgid)
                await bot.send_document(document=doc, chat_id=user_tgid)
                await bot.send_message(text='Отчет по автомобилю, который Вы запрашивали, сформирован.', chat_id=user_tgid)

                await bot.send_message(f'{admin_chat_id_db}',
                                            text=f'Данные по автомобилю пользователя с tg id {user_tgid}.\n'
                                                 f'Ссылка на аккаунт: {user_url}\n'
                                                 f'Время: {current_time}\n'
                                                 f'Данные о машине: {car_num}\n'
                                                 f'Ссылка на отчет Автотеки: {current_url}\n'
                                                 f'#Отчет получен', )

                os.remove(path=f'C:/Users/roman/Downloads/Отчёт Автотеки - {VIN_num}.pdf')

                try:
                    requests.post(url=f'http://apps.my-remote.space{noco_port}/api/v2/tables/mnjnl9cx9414h9m/records',
                                  data={"Title": "data",
                                        "telegramID": f'{user_tgid}',
                                        "car_num": f"{car_num}",
                                        "time": f"{current_time}+03:00",
                                        "autoteka_link": f"{current_url}"
                                        },
                                  headers={'xc-token': '3eCTw82sEU6HjGi-TZ2PxgBoS38gVpTGPvhuSx32'})
                except:
                    pass








@router.callback_query(MyCallback.filter(F.separator == "separator"))
async def input_again(call: CallbackQuery, state: FSMContext):
    call_data = call.data.replace('input_again','')
    call_data = call_data.replace('separator', '')
    call_data = call_data.replace(':', '')
    call_data = int(call_data)
    await call.message.delete()
    await call.bot.send_message(text=f"Напоминаю, что вводимая Вами информация должна соответствовать стандартам:\n"
                         f"Гос. номер состоит из 7-9 символов: серии, номера и кода региона.\n"
                         f"Номер кузова состоит из 8-16 символов;\n"
                         f"VIN код состоит из 17 символов.", chat_id=call_data)

    await state.set_state(Input_again.get_c_num_again)
    print(await state.get_state())











