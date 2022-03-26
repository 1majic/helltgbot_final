import logging
import random
from typing import Union

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery
from aiogram.types.message import ContentTypes
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import admins_id

import config as cfg
from db import init
from pyqiwip2p import QiwiP2P

from keyboards import items_markups as im

# from markups import menu_cd

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)

db = init.db
p2p = QiwiP2P(auth_key=cfg.QIWI_TOKEN)


async def start(message: types.Message):
    await list_categories(message)


async def cancel_menu(callback: types.CallbackQuery, **kwargs):
    await callback.message.edit_text('Отменено', reply_markup=None)


async def list_categories(callback: Union[types.Message, types.CallbackQuery], **kwargs):
    if callback.from_user.id in admins_id:
        markup = await im.category_keyboard(admin=True)
    else:
        markup = await im.category_keyboard()

    if isinstance(callback, types.Message):
        await callback.answer("Меню", reply_markup=markup)
    elif isinstance(callback, types.CallbackQuery):
        await callback.message.edit_reply_markup(markup)


async def list_schools(callback: types.CallbackQuery, category, **kwargs):
    markup = await im.subcategory_keyboard(category)
    await callback.message.edit_text('Выбери категорию')
    await callback.message.edit_reply_markup(markup)


async def list_months(callback: types.CallbackQuery, category, subcategory, **kwargs):
    markup = await im.subject_keyboard(category, subcategory)
    await callback.message.edit_text('Выбери месяц')
    await callback.message.edit_reply_markup(markup)


async def list_subjects(callback: types.CallbackQuery, category, subcategory, subject, **kwargs):
    markup = await im.items_keyboard(category, subcategory, subject)
    await callback.message.edit_text('Выбери предмет')
    await callback.message.edit_reply_markup(markup)


async def show_item(callback: types.CallbackQuery, category, subcategory, subject, item):
    item = db.get_item(category, subcategory, subject, item)
    # Ekz1 = item[0]
    # school1 = item[1]
    # month1 = item[2]
    # subject1 = item[3]
    # price1 = item[4]
    # string = f"{str(Ekz)}|{str(school)}|{str(month)}|{str(subject)}"
    #
    # comment = str(callback.from_user.id) + "_" + string
    # bill = p2p.bill(amount=int(price1), lifetime=15, comment=comment)
    # db.add_check(callback.from_user.id, price1, string, bill.bill_id)
    # keyboard = markups.item_keyboard(Ekz1, school1, month1, subject1, url=bill.pay_url, bill=bill.bill_id)
    # await callback.message.edit_text(f'{Ekz1} | {school1} | {markups.months_dict[month1]} | {subject1}\n\nЦена - {price1}', reply_markup=keyboard)
    #
    pass


@dp.callback_query_handler(im.menu_cd.filter())
async def navigate(callback: types.CallbackQuery, callback_data: dict):
    print(callback_data.get('level'))
    current_level = callback_data.get('level')
    category = callback_data.get('category')
    subcategory = callback_data.get('subcategory')
    subject = callback_data.get('subject')
    item = callback_data.get('item')

    levels = {
        "0": cancel_menu,
        "1": list_categories,
        "2": list_schools,
        "3": list_months,
        "4": list_subjects,
        "5": show_item
    }

    current_level_funtion = levels[current_level]

    await current_level_funtion(
        callback=callback,
        leve=category,
        category=category,
        subcategory=subcategory,
        subject=subject,
        item=item
    )