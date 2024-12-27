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
