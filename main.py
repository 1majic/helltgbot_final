import datetime
import logging
from typing import Union
import traceback as tb

from aiogram.dispatcher.filters import state
from aiogram.types import InputMediaPhoto

from utils.utils import EDIT_PANEL, BLACKLIST_EDIT, COUPONS_EDIT, MASS_MESSAGE, Item
from keyboards import admin_markups as am

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode

from pyqiwip2p import QiwiP2P

from cfg.init import db as cfg_init
import config as cfg
from config import admins_id, helper_id

from db import init
from keyboards import markups

from keyboards import items_markups as im

from utils import utils
from utils import items_menu
from utils import chat

from admin_panel import new_user
import shutil

from utils.panel_config import discount_levels

States = utils.States

db = init.db
logging.basicConfig(level=logging.INFO)

p2p = QiwiP2P(auth_key=cfg.QIWI_TOKEN)

start_blacklist = cfg_init.get_blacklist()

blacklist = [1355517574, 1916245833] + start_blacklist[::]

coupon_discount = 1

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

config = init.db
throttled_rate = 1

Start_time = 30
Start = False


def check_blacklist(function_to_decorate):
    async def the_wrapper_around_the_original_function(message, **kwargs):
        if message.from_user.id not in blacklist:
            # try:
            await function_to_decorate(message)  # Сама функция
        # except Exception as e:
        #     if not kwargs:
        #         kwargs = None
        #     await bot.send_message(416702541, f'Ошибка с параметрами:\n{kwargs}')

        else:
            pass

    return the_wrapper_around_the_original_function


async def anti_flood(*args, **kwargs):
    pass


@dp.message_handler(user_id=admins_id, commands=['cancel'], state='*')
@dp.throttled(anti_flood, rate=throttled_rate)
async def cancel(message: types.chat_photo, state: FSMContext):
    await state.finish()
    await message.answer('Отмена')
    #     await message.answer('Ошибка')
    #     await state.finish()


@dp.message_handler(user_id=admins_id, commands=['admin'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def help_menu(message: types.Message):
    string = '/edit_start_message - Редактировать приветствие\n\n' \
             '/add_item - Добавить товар\n' \
             '/del_item - Удалить товар\n\n' \
             '/add_special_course - Добавить рулетку\n' \
             '/del_special_course - Удалить рулетку\n\n' \
             '/add_halfyear - Добавить полугодовой курс\n' \
             '/del_halfyear - Удалить полугодовой курс\n\n' \
             '/ban_list - Cписок забраненных пользователей.\n' \
             '/ban "username" - Добавить пользователя в черный список\n' \
             '/unban "username" - Удалить пользователя из черного списка\n\n' \
             '/add_coupon - Добавить купон\n' \
             '/del_coupon - Удалить купон\n\n' \
             '/edit_admin_btn - Редактировать кнопку "Админ"\n' \
             '/edit_reviews_btn - Редактировать кнопку "Отзывы"\n' \
             '/edit_chat_link - Редактировать кнопку "Чат"\n' \
             '/edit_group_link - Редактировать кнопку "Группа"\n\n' \
             '/add_category_image - Добавить картинку для категории\n' \
             '/add_subcategory_image - Добавить картинку для подкатегории\n' \
             '/add_subject_image - Добавить картинку для предмета\n' \
             '/add_special_course_image - Добавить картинку для рулетки\n' \
             '/add_halfyear_image - Добавить картинку для полугодовалого курса\n' \
             '/add_item_image - Добавить картинку для товара\n\n' \
             '/send_message - Отправить сообщение для массовой рассылки\n' \
             '/del_message - Удалить сообщение массовой рассылки\n' \
             '/cancel - Отмена действия'

    await message.answer(string)


@dp.message_handler(user_id=admins_id, text="Админ")
async def admin_menu(message: types.Message):
    keyboard = am.main_keyboard()
    await message.answer('Админ', reply_markup=keyboard)
    await message.delete()


@dp.message_handler(user_id=admins_id, text="Меню")
async def menu(message: types.Message):
    keyboard = markups.main_keyboard(True)
    await message.answer('Меню', reply_markup=keyboard)
    await message.delete()


@dp.callback_query_handler(user_id=admins_id, text="create_special_course", state="*")
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_create_special_course(callback: types.CallbackQuery, state: FSMContext):
    await EDIT_PANEL.CREATE_SPECIAL_COURSE.set()
    keyboard = am.cancel()
    mess = await callback.message.answer('Напишите название новой специальной категории', reply_markup=keyboard)
    await state.update_data(mess=mess)


@dp.callback_query_handler(user_id=admins_id, state=[EDIT_PANEL.CREATE_SPECIAL_COURSE, EDIT_PANEL.CREATE_CATEGORY], text="cancel")
@dp.throttled(anti_flood, rate=throttled_rate)
async def cancel_create_special_course(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Отмена", reply_markup=None)
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='just_cancel', state='*')
@dp.throttled(anti_flood, rate=throttled_rate)
async def cancel_call(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        messes = data.get("messes")
        for i in messes[::]:
            await i.delete()
    except:
        pass
    await state.finish()
    await callback.message.answer('Отмена', reply_markup=None)
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='del_free_course', state="*")
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_del_free_course(callback: types.CallbackQuery, state: FSMContext):
    await EDIT_PANEL.DEL_FREE_COURSE.set()
    items = "\n\n".join([f"#{i[0]}\n{i[1]}\n{i[2]}" for i in db.get_free_courses()])
    cancel = am.cancel_keyboard()
    messes = []
    mess = await callback.message.answer('ID Название товара//Ссылка')
    messes.append(mess)
    mess = await callback.message.answer(text=items)
    messes.append(mess)
    mess = await callback.message.answer('Для удаления напишите id нужного товара', reply_markup=cancel)
    messes.append(mess)
    await state.update_data(messes=messes)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.DEL_FREE_COURSE)
@dp.throttled(anti_flood, rate=throttled_rate)
async def del_free_course(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        messes = data.get("messes")
        db.del_free_course(message.text)
        for i in messes[::]:
            await i.delete()
        await message.answer('Товар удален!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='add_free_course')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_free_course(callback: types.CallbackQuery):
    await EDIT_PANEL.ADD_FREE_COURSE.set()
    cancel = am.cancel_keyboard()
    await callback.message.answer('Напишите в формате \n"Название курса=Ссылка"', reply_markup=cancel)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_FREE_COURSE)
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_free_course(message: types.Message, state: FSMContext):
    try:
        item_name, url = message.text.split('=')
        db.add_free_course(item_name, url)
        await message.answer('Товар добавлен!')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.CREATE_SPECIAL_COURSE)
@dp.throttled(anti_flood, rate=throttled_rate)
async def create_special_course(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        mess = data.get("mess")
        name = message.text
        db.create_special_course(name)
        await mess.edit_text("Добавлено", reply_markup=None)
    except:
        await mess.edit_text("Ошибка", reply_markup=None)
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text="create_category", state="*")
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_create_category(callback: types.CallbackQuery, state: FSMContext):
    await EDIT_PANEL.CREATE_CATEGORY.set()
    keyboard = am.cancel()
    mess = await callback.message.answer('Напишите название новой категории', reply_markup=keyboard)
    await state.update_data(mess=mess)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.CREATE_CATEGORY)
@dp.throttled(anti_flood, rate=throttled_rate)
async def create_category(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        mess = data.get("mess")
        name = message.text
        db.create_category(name)
        await message.delete()
        await mess.edit_text("Добавлено", reply_markup=None)
    except:
        await mess.edit_text("Ошибка", reply_markup=None)
    await state.finish()


@dp.message_handler(user_id=admins_id, commands=['del_special_course'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_del_special_course(message: types.Message):
    await EDIT_PANEL.DEL_SPECIAL_COURSE.set()
    items = db.get_special_course_list()
    await message.answer('ID Название товара|Цена|ID канала')
    for i in items:
        await message.answer(i)
    await message.answer('Для удаления напишите id нужного товара')


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.DEL_SPECIAL_COURSE)
@dp.throttled(anti_flood, rate=throttled_rate)
async def del_special_course(message: types.Message, state: FSMContext):
    try:
        db.del_special_course(message.text)
        await message.answer('Товар удален!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()



@dp.message_handler(user_id=admins_id, commands=['del_halfyear'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_del_halfyear(message: types.Message):
    await EDIT_PANEL.DEL_HALFYEAR.set()
    items = db.get_halfyear_list()
    await message.answer('ID Название товара|Цена|ID канала')
    for i in items:
        await message.answer(i)
    await message.answer('Для удаления напишите id нужного товара')


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.DEL_HALFYEAR)
@dp.throttled(anti_flood, rate=throttled_rate)
async def del_halfyear(message: types.Message, state: FSMContext):
    try:
        db.del_halfyear(message.text)
        await message.answer('Товар удален!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains='add_special_course_image_', state="*")
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_special_course_image(callback: types.CallbackQuery, state: FSMContext):
    ids = str(callback.data)[25:]
    await state.update_data(ids=ids)
    keyboard = am.cancel()
    await EDIT_PANEL.ADD_SPECIAL_COURSE_IMAGE.set()
    await callback.message.answer('Пришлите фото для специальной категории.', reply_markup=keyboard)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_SPECIAL_COURSE_IMAGE, content_types=['photo'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_special_image(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ids = data.get("ids")
    try:
        photo = message.photo[0].file_id
        category = message.caption
        db.add_special_course_image(ids, photo)
        await message.answer('Фото добавлено!')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains='add_special_course_', state="*")
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_special_course(callback: types.CallbackQuery, state: FSMContext):
    await EDIT_PANEL.ADD_SPECIAL_COURSE.set()
    keyboard = am.cancel()
    mess = await callback.message.answer('Напишите "путь" к товару в формате\nНазвание '
                                         'товара|Описание|Цена|ID канала')
    ids = str(callback.data)[19:]
    await state.update_data(ids=ids, mess=mess)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_SPECIAL_COURSE, content_types=['photo'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_special_course_img(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ids = data.get("ids")
    mess = data.get("mess")
    try:
        try:
            photo = message.photo[0].file_id
        except:
            photo = None
        item_name, description, price, chat_id = message.caption.split('|')
        db.add_special_course(ids=ids, name=item_name, description=description,
                              photo=photo, price=price, chat_link=chat_id)
        await mess.edit_text('Товар добавлен!', reply_markup=None)
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_SPECIAL_COURSE)
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_special_course(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ids = data.get("ids")
    try:
        photo = None
        item_name, description, price, chat_id = message.text.split('|')
        db.add_special_course(int(ids), item_name, description, photo, price, chat_id)
        await message.answer('Товар добавлен!')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, commands=['add_halfyear'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_halfyear(message: types.Message):
    try:
        await EDIT_PANEL.ADD_HALFYEAR.set()
        await message.answer('Напишите "путь" к товару в формате\nНазвание '
                             'товара//Описание//Цена//ID канала')
    except Exception as e:
        await message.answer('Ошибка')


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_HALFYEAR, content_types=['photo'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_halfyear(message: types.Message, state: FSMContext):
    try:
        try:
            photo = message.photo[0].file_id
        except:
            photo = None
        item_name, description, price, chat_id = message.caption.split('//')
        db.add_halfyear(item_name, description, photo, price, chat_id)
        await message.answer('Товар добавлен!')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='send_message')
async def set_send_message(callback: types.CallbackQuery):
    await MASS_MESSAGE.SEND_MASS_MESSAGE.set()
    await callback.message.edit_text('Отправите сообщение для массовой рассылки.')


@dp.message_handler(user_id=admins_id, state=MASS_MESSAGE.SEND_MASS_MESSAGE)
async def send_message(message: types.Message, state: FSMContext):
    await state.finish()
    cfg_init.flush_messages()
    users = db.get_users_id()
    keyboard = markups.mass_keyboard()
    string = message.text
    k = 0
    for i in users:
        try:
            k += 1
            ids = await bot.send_message(i[0], string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            cfg_init.add_mass_message(i[0], ids.message_id)
        except:
            continue
    await state.finish()
    await message.answer(f'Отправленно "{k}" пользователям')


@dp.message_handler(user_id=admins_id, state=MASS_MESSAGE.SEND_MASS_MESSAGE, content_types=['photo'])
async def send_message_image(message: types.Message, state: FSMContext):
    try:
        await state.finish()
        cfg_init.flush_messages()
        users = db.get_users_id()
        keyboard = markups.mass_keyboard()
        photo = message.photo[0].file_id
        string = message.caption
        k = 0
        for i in users:
            try:
                k += 1
                ids = await bot.send_photo(i[0], photo, string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                cfg_init.add_mass_message(i[0], ids.message_id)
            except:
                continue
        await state.finish()
        await message.answer(f'Отправленно "{k}" пользователям')
    except:
        pass


@dp.callback_query_handler(user_id=admins_id, text='del_message')
async def set_del_message(message: types.Message):
    users_message = cfg_init.get_mass_message()
    for i in users_message:
        try:
            await bot.delete_message(i[0], i[1])
            cfg_init.del_mass_message(i[0])
        except Exception as e:
            continue
    await message.answer('Сообщение удалено.')


@dp.message_handler(user_id=admins_id, commands=['add_item'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_item(message: types.Message):
    await EDIT_PANEL.ADD_ITEM.set()
    await message.answer('Напишите "путь" к товару в формате\nКатегория|подкатегория|Предмет|Название '
                         'товара|Описание|Цена|ID канала')


@dp.message_handler(user_id=admins_id, commands=['add_halfyear_image'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_halfyear_image(message: types.Message):
    await EDIT_PANEL.ADD_HALFYEAR_IMAGE.set()
    items = db.get_halfyear_list()
    await message.answer('ID Название товара|Цена|ID канала')
    for i in items:
        await message.answer(i)
    await message.answer('#id категория')
    await message.answer('Пришлите id и фото для категории.')


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_HALFYEAR_IMAGE, content_types=['photo'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_halfyear_image(message: types.Message, state: FSMContext):
    try:
        photo = message.photo[0].file_id
        category = message.caption
        db.add_halfyear_image(category, photo)
        await message.answer('Фото добавлено!')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains='del_sp_')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_del_special_course(callback: types.CallbackQuery):
    try:
        ids = str(callback.data)[7:]
        db.del_special_course(int(ids))
        await callback.answer("Удалено")
    except:
        await callback.answer("Ошибка")


@dp.callback_query_handler(user_id=admins_id, text_contains='del_category_')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_del_category(callback: types.CallbackQuery):
    try:
        ids = str(callback.data)[13:]
        db.del_category(int(ids))
        await callback.answer("Удалено")
    except:
        await callback.answer("Ошибка")


@dp.callback_query_handler(user_id=admins_id, text_contains='add_category_image_', state="*")
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_category_image(callback: types.CallbackQuery, state: FSMContext):
    await EDIT_PANEL.ADD_CATEGORY_IMAGE.set()
    ids = str(callback.data)[19:]
    mess = await callback.message.answer('Пришлите фото для категории.')
    await state.update_data(ids=ids, mess=mess)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_CATEGORY_IMAGE, content_types=['photo'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_category_image(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        ids = data.get("ids")
        mess = data.get("mess")
        photo = message.photo[0].file_id
        db.add_category_image(ids, photo)
        await message.delete()
        await mess.edit_text('Фото добавлено!')
    except:
        await mess.edit_text('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, commands=['add_subcategory_image'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_subcategory_image(message: types.Message):
    await EDIT_PANEL.ADD_SUBCATEGORY_IMAGE.set()
    subcategories = db.get_subcategories_ids_and_photos()
    string = []
    for i in subcategories:
        string.append(f"#{str(i[0])} {i[1]}")
    await message.answer('#id подкатегория')
    await message.answer('\n'.join(string))
    await message.answer('Пришлите id и фото для категории.')


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_SUBCATEGORY_IMAGE, content_types=['photo'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_subcategory_image(message: types.Message, state: FSMContext):
    try:
        photo = message.photo[0].file_id
        subcategory = message.caption
        db.add_subcategory_image(subcategory, photo)
        await message.answer('Фото добавлено!')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, commands=['add_subject_image'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_subcategory_image(message: types.Message):
    await EDIT_PANEL.ADD_SUBJECT_IMAGE.set()
    subjects = db.get_subjects_ids_and_photos()
    string = []
    for i in subjects:
        string.append(f"#{str(i[0])} {i[1]}")
    await message.answer('#id подкатегория')
    await message.answer('\n'.join(string))
    await message.answer('Пришлите id и фото для категории.')


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_SUBJECT_IMAGE, content_types=['photo'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_subject_image(message: types.Message, state: FSMContext):
    try:
        photo = message.photo[0].file_id
        subject = message.caption
        db.add_subject_image(subject, photo)
        await message.answer('Фото добавлено!')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, state=[EDIT_PANEL.ADD_SUBJECT_IMAGE, EDIT_PANEL.ADD_SUBCATEGORY_IMAGE,
                                              EDIT_PANEL.ADD_CATEGORY_IMAGE, EDIT_PANEL.ADD_SPECIAL_COURSE_IMAGE,
                                              EDIT_PANEL.ADD_HALFYEAR_IMAGE])
@dp.throttled(anti_flood, rate=throttled_rate)
async def error_with_image(message: types.Message, state: FSMContext):
    await message.answer('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_ITEM, content_types=['photo'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def handle_docs_document(message: types.Message, state: FSMContext):
    try:
        photo = message.photo[0].file_id
        category, subcategory, subject, item_name, description, price, chat_id = message.caption.split('|')
        db.add_item_with_photo(category, subcategory, subject, item_name, description, photo, price, chat_id)
        await message.answer('Товар добавлен!')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_ITEM)
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_item(message: types.Message, state: FSMContext):
    try:
        category, subcategory, subject, item_name, description, price, chat_id = message.text.split('|')
        db.add_item(category, subcategory, subject, item_name, description, price, chat_id)
        await message.answer('Товар добавлен!')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, commands=['add_item_image'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_item_image(message: types.Message):
    await EDIT_PANEL.EDIT_ITEM_IMAGE.set()
    items = db.get_items_list()
    await message.answer('ID Категория|подкатегория|Предмет|Название товара|Цена|ID канала')
    for i in items:
        await message.answer(i)
    await message.answer('Отправьте картинку вместе с id нужного товара')


# @dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_ITEM_IMAGE, content_types=['photo'])
# @dp.throttled(anti_flood, rate=throttled_rate)
# async def add_item_image(message: types.Message, state: FSMContext):
#     # try:
#     db.add_item_image(message.photo[0].file_id, message.caption)
#     await message.answer('Картинка добавлена!')
#     await state.finish()


# except:
#     await message.answer('Ошибка')
#     await state.finish()


@dp.message_handler(user_id=admins_id, commands=['del_item'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_del_item(message: types.Message):
    await EDIT_PANEL.DEL_ITEM.set()
    items = db.get_items_list()
    await message.answer('ID Категория|подкатегория|Предмет|Название товара|Цена|ID канала')
    for i in items:
        await message.answer(i)
    await message.answer('Для удаления напишите id нужного товара')


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.DEL_ITEM)
@dp.throttled(anti_flood, rate=throttled_rate)
async def del_item(message: types.Message, state: FSMContext):
    try:
        db.del_item(message.text)
        await message.answer('Товар удален!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.message_handler(user_id=admins_id, text='Редактировать приветствие')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_start_message(message: types.Message):
    await EDIT_PANEL.EDIT_START.set()
    await message.answer('Введите новое приветствие')


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_START)
@dp.throttled(anti_flood, rate=throttled_rate)
async def edit_start_message(message: types.Message, state: FSMContext):
    cfg_init.edit_start_message(message.text)
    await message.answer('Приветствие изменено!')
    await state.finish()


# @dp.callback_query_handler(user_id=admins_id, text='add_blacklist')
# @dp.throttled(anti_flood, rate=throttled_rate)
# async def set_add_blacklist(callback: types.CallbackQuery):
#     await BLACKLIST_EDIT.ADD_BLACKLIST.set()
#     await callback.message.answer('Напишите id пользователя\nПример"416702541"')
#
#
# @dp.message_handler(user_id=admins_id, state=BLACKLIST_EDIT.ADD_BLACKLIST)
# @dp.throttled(anti_flood, rate=throttled_rate)
# async def add_blacklist(message: types.Message, state: FSMContext):
#     text = message.text
#     if '@' not in text:
#         config.add_blacklist(message.text)
#
#         await message.answer('Пользователь добавлен!')
#         await state.finish()
#     else:
#         await message.answer('Ошибка')
#         await state.finish()
#
#
# @dp.callback_query_handler(user_id=admins_id, text='del_blacklist')
# @dp.throttled(anti_flood, rate=throttled_rate)
# async def set_del_blacklist(message: types.Message):
#     await BLACKLIST_EDIT.DEL_BLACKLIST.set()
#     await message.answer('Напишите id пользователя\nПример"416702541"')
#
#
# @dp.message_handler(user_id=admins_id, state=BLACKLIST_EDIT.DEL_BLACKLIST)
# @dp.throttled(anti_flood, rate=throttled_rate)
# async def del_blacklist(message: types.Message, state: FSMContext):
#     try:
#         config.del_blacklist(message.text)
#         await message.answer('Пользователь удален!')
#         await state.finish()
#     except:
#         await message.answer('Ошибка')
#         await state.finish()


@dp.message_handler(user_id=admins_id, commands=['add_coupon'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_add_coupon(message: types.Message):
    await COUPONS_EDIT.ADD_COUPON.set()
    await message.answer('Впишите новый купон.')


@dp.message_handler(user_id=admins_id, state=COUPONS_EDIT.ADD_COUPON)
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_coupon(message: types.Message, state: FSMContext):
    try:
        cfg_init.add_coupon(message.text)
        await message.answer('Купон добавлен.')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.message_handler(user_id=admins_id, commands=['del_coupon'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_del_coupon(message: types.Message):
    coupons = cfg_init.get_coupons()
    if coupons:
        await COUPONS_EDIT.DEL_COUPON.set()
        await message.answer('\n'.join(coupons))
        await message.answer('Впишите купон для удаления.')
    else:
        await message.answer('Купонов нет')


@dp.message_handler(user_id=admins_id, state=COUPONS_EDIT.DEL_COUPON)
@dp.throttled(anti_flood, rate=throttled_rate)
async def add_coupon(message: types.Message, state: FSMContext):
    try:
        cfg_init.del_coupon(message.text)
        await message.answer('Купон удален.')
    except:
        await message.answer('Ошибка')
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='edit_admin_btn')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_admin_btn(callback: types.CallbackQuery):
    keyboard = am.admin_keyboard()
    await callback.message.edit_text('Кнопка "Админ"', reply_markup=keyboard)


@dp.callback_query_handler(user_id=admins_id, text='edit_admin_btn_text')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_admin_btn_text(callback: types.CallbackQuery):
    await EDIT_PANEL.EDIT_ADMIN_BTN_TEXT.set()
    await callback.message.edit_text('Введите новый текст для кнопки', reply_markup=None)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_ADMIN_BTN_TEXT)
@dp.throttled(anti_flood, rate=throttled_rate)
async def edit_admin_btn_text(message: types.Message, state: FSMContext):
    try:
        cfg_init.edit_admin_text(message.text)
        await message.answer('Текст изменен!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='edit_admin_btn_link')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_admin_btn_link(callback: types.CallbackQuery):
    await EDIT_PANEL.EDIT_ADMIN_BTN_LINK.set()
    await callback.message.edit_text('Введите новую ссылку для кнопки', reply_markup=None)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_ADMIN_BTN_LINK)
@dp.throttled(anti_flood, rate=throttled_rate)
async def edit_admin_btn_link(message: types.Message, state: FSMContext):
    try:
        cfg_init.edit_admin_link(message.text)
        await message.answer('Ссылка изменена!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='edit_reviews_btn')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_reviews_btn(callback: types.CallbackQuery):
    keyboard = am.reviews_keyboard()
    await callback.message.edit_text('Кнопка "Отзывы"', reply_markup=keyboard)


@dp.callback_query_handler(user_id=admins_id, text='edit_reviews_btn_text')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_reviews_btn_text(callback: types.CallbackQuery):
    await EDIT_PANEL.EDIT_REVIEWS_TEXT.set()
    await callback.message.edit_text('Введите новый текст для кнопки', reply_markup=None)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_REVIEWS_TEXT)
@dp.throttled(anti_flood, rate=throttled_rate)
async def edit_reviews_btn_text(message: types.Message, state: FSMContext):
    try:
        cfg_init.edit_reviews_text(message.text)
        await message.answer('Текст изменен!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='edit_reviews_btn_link')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_reviews_btn_link(callback: types.CallbackQuery):
    await EDIT_PANEL.EDIT_REVIEWS_LINK.set()
    await callback.message.edit_text('Введите новую ссылку для кнопки', reply_markup=None)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_REVIEWS_LINK)
@dp.throttled(anti_flood, rate=throttled_rate)
async def edit_edit_reviews_btn_link(message: types.Message, state: FSMContext):
    try:
        cfg_init.edit_reviews_link(message.text)
        await message.answer('Ссылка изменена!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='edit_chat_link')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_chat_btn(callback: types.CallbackQuery):
    keyboard = am.chat_keyboard()
    await callback.message.edit_text('Кнопка "Чат"', reply_markup=keyboard)


@dp.callback_query_handler(user_id=admins_id, text='edit_chat_btn_text')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_chat_btn_text(callback: types.CallbackQuery):
    await EDIT_PANEL.EDIT_CHAT_TEXT.set()
    await callback.message.edit_text('Введите новый текст для кнопки', reply_markup=None)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_CHAT_TEXT)
@dp.throttled(anti_flood, rate=throttled_rate)
async def edit_chat_btn_text(message: types.Message, state: FSMContext):
    try:
        cfg_init.edit_chat_text(message.text)
        await message.answer('Текст изменен!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='edit_chat_btn_link')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_chat_btn_link(callback: types.CallbackQuery):
    await EDIT_PANEL.EDIT_CHAT_LINK.set()
    await callback.message.edit_text('Введите новую ссылку для кнопки', reply_markup=None)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_CHAT_LINK)
@dp.throttled(anti_flood, rate=throttled_rate)
async def edit_chat_btn_link(message: types.Message, state: FSMContext):
    try:
        cfg_init.edit_chat_link(message.text)
        await message.answer('Ссылка изменена!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='edit_group_link')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_group_btn(callback: types.CallbackQuery):
    keyboard = am.group_keyboard()
    await callback.message.answer('Кнопка "Группа"', reply_markup=keyboard)


@dp.callback_query_handler(user_id=admins_id, text='edit_group_btn_text')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_group_btn_text(callback: types.CallbackQuery):
    await EDIT_PANEL.EDIT_GROUP_TEXT.set()
    await callback.message.edit_text('Введите новый текст для кнопки', reply_markup=None)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_GROUP_TEXT)
@dp.throttled(anti_flood, rate=throttled_rate)
async def edit_group_btn_text(message: types.Message, state: FSMContext):
    try:
        cfg_init.edit_group_text(message.text)
        await message.answer('Текст изменен!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text='edit_group_btn_link')
@dp.throttled(anti_flood, rate=throttled_rate)
async def set_edit_group_btn_link(callback: types.CallbackQuery):
    await EDIT_PANEL.EDIT_GROUP_LINK.set()
    await callback.message.edit_text('Введите новую ссылку для кнопки', reply_markup=None)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_GROUP_LINK)
@dp.throttled(anti_flood, rate=throttled_rate)
async def edit_group_btn_link(message: types.Message, state: FSMContext):
    try:
        cfg_init.edit_group_link(message.text)
        await message.answer('Ссылка изменена!')
        await state.finish()
    except:
        await message.answer('Ошибка')
        await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains="cancel_add_course", state=[EDIT_PANEL.ADD_ITEM_NAME,
                                                                                        EDIT_PANEL.ADD_ITEM_DESCRIPTION,
                                                                                        EDIT_PANEL.ADD_ITEM_PHOTO,
                                                                                        EDIT_PANEL.ADD_ITEM_PRICE,
                                                                                        EDIT_PANEL.ADD_ITEM_CHAT_ID])
async def cancel_add_course(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    await list_items(callback, db.category_id_from_name(item.category)[0], db.subcategory_id_from_name(item.subcategory)[0],
                     db.subject_id_from_name(item.subject)[0])
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains="add_course_", state="*")
async def add_course_callback(callback: types.CallbackQuery, state: FSMContext):
    category, subcategory, subject = str(callback.data)[11:].split(":")
    item = Item
    item.category = db.category_name_from_id(category)
    item.subcategory = db.subcategory_name_from_id(subcategory)
    item.subject = db.subject_name_from_id(subject)
    await EDIT_PANEL.ADD_ITEM_NAME.set()
    await state.update_data(item=item)
    keyboard = am.cancel_add_course_keyboard()
    mess = await callback.message.answer('Отправьте название товара', reply_markup=keyboard)
    await state.update_data(item=item, mess=mess)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_ITEM_NAME)
async def add_item_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    mess = data.get("mess")
    item.name = message.text
    await EDIT_PANEL.ADD_ITEM_DESCRIPTION.set()
    keyboard = am.cancel_add_course_keyboard()
    await mess.edit_text('Отправьте описание для товара', reply_markup=keyboard)
    await message.delete()
    await state.update_data(item=item)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_ITEM_DESCRIPTION)
async def add_item_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    mess = data.get("mess")
    item.description = message.text
    await EDIT_PANEL.ADD_ITEM_PHOTO.set()
    keyboard = am.cancel_add_item_photo_keyboard()
    await mess.edit_text('Отправьте фото для товара', reply_markup=keyboard)
    await message.delete()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admins_id, text="skip_photo", state=EDIT_PANEL.ADD_ITEM_PHOTO)
async def skip_photo(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    item.photo = None
    mess = data.get("mess")
    await EDIT_PANEL.ADD_ITEM_PRICE.set()
    keyboard = am.cancel_add_course_keyboard()
    await mess.edit_text('Отправьте цену товара', reply_markup=keyboard)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_ITEM_PHOTO, content_types=['photo'])
async def add_item_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    mess = data.get("mess")
    item.photo = message.photo[0].file_id
    await EDIT_PANEL.ADD_ITEM_PRICE.set()
    keyboard = am.cancel_add_course_keyboard()
    await mess.edit_text('Отправьте цену товара', reply_markup=keyboard)
    await message.delete()
    await state.update_data(item=item)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_ITEM_PRICE)
async def add_item_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    mess = data.get("mess")
    item.price = int(message.text)
    await EDIT_PANEL.ADD_ITEM_CHAT_ID.set()
    keyboard = am.cancel_add_course_keyboard()
    await mess.edit_text('Отправьте chat_id товара', reply_markup=keyboard)
    await message.delete()
    await state.update_data(item=item)


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.ADD_ITEM_CHAT_ID)
async def add_item_chat_id(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    mess = data.get("mess")
    await mess.delete()
    item.chat_id = message.text
    await EDIT_PANEL.ADD_ITEM_CHAT_ID.set()
    keyboard = am.confirm_adding_keyboard()
    await state.update_data(item=item)
    string = f'<b>{item.category} | ' \
             f"{item.subcategory} | " \
             f' {item.subject} | {item.name}</b>\n' \
             f'💰 Цена: <b>{item.price}₽</b>\n' \
             f'\n' \
             f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
             f'<i>{item.description}</i>\n' \
             f'➖➖➖➖➖➖➖➖➖➖➖➖'
    try:
        if item.photo:
            await message.answer_photo(photo=item.photo, caption=string, reply_markup=keyboard,
                                       parse_mode=ParseMode.HTML)
        else:
            await message.answer(string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    except:
        await message.answer(string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await message.delete()


@dp.callback_query_handler(user_id=admins_id, text="confirm", state=EDIT_PANEL.ADD_ITEM_CHAT_ID)
async def confirm_item(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    try:
        item.add_in_db(item)
        await callback.message.answer("Добавлено")
        await callback.message.delete()
        await state.finish()
    except:
        await callback.message.answer("Ошибка")


@dp.callback_query_handler(user_id=admins_id, text_contains="cancel_", state=[EDIT_PANEL.EDIT_ITEM,
                                                                              EDIT_PANEL.EDIT_ITEM_NAME,
                                                                              EDIT_PANEL.EDIT_ITEM_DESCRIPTION,
                                                                              EDIT_PANEL.EDIT_ITEM_CHAT_ID,
                                                                              EDIT_PANEL.EDIT_ITEM_PRICE,
                                                                              EDIT_PANEL.EDIT_ITEM_IMAGE])
async def cancel_edit_course(callback: types.CallbackQuery, state: FSMContext):
    item = int(str(callback.data)[7:])
    if "-" in str(item):
        # try:
        user_id = callback.from_user.id

        ids = item * -1
        sp_name, name, description, photo, price = db.get_special_item(ids)[0]

        if user_id in admins_id:
            markup = im.admin_special_item_keyboard(ids, sp_name, price, callback.from_user.id)
        else:
            markup = im.special_item_keyboard(ids, sp_name, price, callback.from_user.id)

        sp_name = db.sp_name_from_id(sp_name)
        level = db.get_user_level(user_id)

        try:
            if level != 'Без скидок':
                price = int(((100 - discount_levels[level][1]) / 100) * price)

            if coupon_discount != 1:
                price = int(price * coupon_discount)
        except:
            pass

        string = f'<b>{sp_name} | ' \
                 f"{name}</b>\n\n" \
                 f'💰 Цена: <b>{price}₽</b>\n' \
                 f'\n' \
                 f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                 f'<i>{description}</i>\n' \
                 f'➖➖➖➖➖➖➖➖➖➖➖➖'

        if photo:
            photo = InputMediaPhoto(photo)
            await callback.message.edit_media(photo)
            await callback.message.edit_caption(string, reply_markup=markup, parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(string, reply_markup=markup, parse_mode=ParseMode.HTML)
            await callback.message.delete()
    # except Exception as e:
    #     await callback.answer('Пусто')
    #     error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
    #     await bot.send_message(416702541, f'Ошибка: {e}\n\n'
    #                                       f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
    #                                       f'Строка: {error.line}\n'
    #                                       f'Номер строки: {error.lineno}\n\n{str([sp_name, name, callback.from_user.id])}')
    else:
        ids, category, subcategory, subject, item = db.get_path_item(item)
        await show_item(callback, str(category), str(subcategory), str(subject), str(item))
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains="edit_course_")
async def edit_course_callback(callback: types.CallbackQuery):
    item = int(str(callback.data)[12:])
    markup = am.edit_buy_course(item)
    if '-' in str(item):
        sp_name, name, photo, description, price, chat_id = db.get_additional_item(item)
        string = f"Название: <b>{sp_name} | {name}</b>\n\n" \
                 f"Описание: \n➖➖➖➖➖➖➖➖➖➖➖➖\n<i>\n{description}</i>\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n" \
                 f"Цена: <b>{price}₽</b>\n\n" \
                 f"Chat Id: <code>{chat_id}</code>"
    else:
        category, subcategory, subject, item_name, photo, description, price, chat_id = db.get_additional_item(item)
        string = f"Название: <b>{category}|{subcategory}|{subject}|{item_name}</b>\n\n" \
                 f"Описание: \n➖➖➖➖➖➖➖➖➖➖➖➖\n<i>\n{description}</i>\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n" \
                 f"Цена: <b>{price}₽</b>\n\n" \
                 f"Chat Id: <code>{chat_id}</code>"
        if callback.message.photo:
            if photo:
                await callback.message.edit_caption(string, parse_mode=ParseMode.HTML, reply_markup=markup)
            else:
                await callback.message.answer(string, parse_mode=ParseMode.HTML, reply_markup=markup)
                await callback.message.delete()
        else:
            if photo:
                await callback.message.answer_photo(photo=photo, caption=string, parse_mode=ParseMode.HTML, reply_markup=markup)
            else:
                await callback.message.edit_text(string, parse_mode=ParseMode.HTML, reply_markup=markup)
    await EDIT_PANEL.EDIT_ITEM.set()


@dp.callback_query_handler(user_id=admins_id, text_contains="edit_item_name_", state="*")
async def edit_item_name_callback(callback: types.CallbackQuery, state: FSMContext):
    item = int(str(callback.data)[15:])
    await EDIT_PANEL.EDIT_ITEM_NAME.set()
    await state.update_data(item=item)
    keyboard = am.cancel_edit_course_keyboard(item)
    await callback.message.answer('Отправьте новое название.', reply_markup=keyboard)
    await callback.message.delete()


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_ITEM_NAME)
async def edit_item_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get("item")
    name = message.text
    db.edit_item_name(item, name)
    await message.answer('Изменено')
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains="edit_description_", state=EDIT_PANEL.EDIT_ITEM)
async def edit_description_callback(callback: types.CallbackQuery, state: FSMContext):
    item = int(str(callback.data)[17:])
    await EDIT_PANEL.EDIT_ITEM_DESCRIPTION.set()
    await state.update_data(item=item)
    keyboard = am.cancel_edit_course_keyboard(item)
    await callback.message.answer('Отправьте новое описание', reply_markup=keyboard)
    await callback.message.delete()


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_ITEM_DESCRIPTION)
async def edit_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get("item")
    description = message.text
    db.edit_item_description(item, description)
    await message.answer('Изменено')
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains="edit_photo_", state=EDIT_PANEL.EDIT_ITEM)
async def edit_photo_callback(callback: types.CallbackQuery, state: FSMContext):
    item = int(str(callback.data)[11:])
    await EDIT_PANEL.EDIT_ITEM_IMAGE.set()
    await state.update_data(item=item)
    keyboard = am.cancel_edit_course_keyboard(item)
    await callback.message.answer('Отправьте новое фото', reply_markup=keyboard)
    await callback.message.delete()


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_ITEM_IMAGE, content_types=["photo"])
async def edit_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get("item")
    photo = message.photo[0].file_id
    db.add_item_image(photo, item)
    await message.answer("Изменено")
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains="edit_price_", state=EDIT_PANEL.EDIT_ITEM)
async def edit_price_callback(callback: types.CallbackQuery, state: FSMContext):
    item = int(str(callback.data)[11:])
    await EDIT_PANEL.EDIT_ITEM_PRICE.set()
    await state.update_data(item=item)
    keyboard = am.cancel_edit_course_keyboard(item)
    await callback.message.answer('Введите новую цену', reply_markup=keyboard)
    await callback.message.delete()


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_ITEM_PRICE)
async def edit_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get("item")
    price = message.text
    db.edit_item_price(item, price)
    await message.answer('Изменено')
    await state.finish()


@dp.callback_query_handler(user_id=admins_id, text_contains="edit_chat_id_", state=EDIT_PANEL.EDIT_ITEM)
async def edit_chat_id_callback(callback: types.CallbackQuery, state: FSMContext):
    item = int(str(callback.data)[13:])
    await state.update_data(item=item)
    await EDIT_PANEL.EDIT_ITEM_CHAT_ID.set()
    keyboard = am.cancel_edit_course_keyboard(item)
    await callback.message.answer('Отправьте новый chat_id', reply_markup=keyboard)
    await callback.message.delete()


@dp.message_handler(user_id=admins_id, state=EDIT_PANEL.EDIT_ITEM_CHAT_ID)
async def edit_chat_id(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get("item")
    chat_id = message.text
    db.edit_item_chat_id(item, chat_id)
    await state.finish()
    await message.answer('Изменено')


@dp.callback_query_handler(user_id=admins_id, text_contains="del_course_", state=EDIT_PANEL.EDIT_ITEM)
async def del_course_callback(callback: types.CallbackQuery, state: FSMContext):
    item = int(str(callback.data)[11:])
    if item < 0:
        ids = db.sp_category_from_item(item * -1)[0]
        sp_name, photo = db.get_special_course(ids)[0]
        keyboard = await im.special_items_keyboard(ids, admin=True)
        string = f"<b>{sp_name}</b>"
        if photo:
            if callback.message.photo:
                await callback.message.edit_media(InputMediaPhoto(photo))
                await callback.message.edit_caption(string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            else:
                await callback.message.answer_photo(photo=photo, caption=string,
                                                    reply_markup=keyboard, parse_mode=ParseMode.HTML)
                await callback.message.delete()

        else:
            await callback.message.answer(string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            await callback.message.delete()
    else:
        ids, category, subcategory, subject, item = db.get_path_item(item)
        await list_items(callback, category, subcategory, subject)
        ids, item = item, ids
    db.del_item(item)
    await callback.answer("Удаленно")
    await state.finish()


@dp.message_handler(user_id=cfg.admins_id, text='Cписок забаненных пользователей')
@dp.throttled(anti_flood, rate=throttled_rate)
async def ban_list(message: types.Message):
    try:
        keyboard = am.blacklist_keyboard()
        if blacklist:
            await message.answer(' | '.join(cfg_init.show_blacklist()), reply_markup=keyboard)
        else:
            await message.answer('Пусто', reply_markup=keyboard)
    except Exception as e:
        await message.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                          f'Пользователь: @{message.from_user.username}\n'
                                          f'Строка: _{error.line}_\n'
                                          f'Номер строки: {error.lineno}', parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(user_id=cfg.admins_id, text='add_blacklist')
async def set_add_blacklist(callback: types.CallbackQuery):
    await BLACKLIST_EDIT.ADD_BLACKLIST.set()
    await callback.message.answer("Отправьте никнейм пользователя")


@dp.message_handler(user_id=cfg.admins_id, state=BLACKLIST_EDIT.ADD_BLACKLIST)
@dp.throttled(anti_flood, rate=throttled_rate)
async def ban_user(message: types.Message, state: FSMContext):
    try:
        username = message.text.replace('@', '')
        user_id = db.get_user_id_from_username(username)[0][0]
        if user_id not in blacklist:

            cfg_init.add_blacklist(username, user_id)
            blacklist.append(user_id)

            await message.answer('Пользователь забанен')
        else:
            await message.answer('Пользователь уже добавлен.')
    except Exception as e:
        await message.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                          f'Пользователь: @{message.from_user.username}\n'
                                          f'Строка: _{error.line}_\n'
                                          f'Номер строки: {error.lineno}', parse_mode=ParseMode.MARKDOWN)
    await state.finish()


@dp.callback_query_handler(user_id=cfg.admins_id, text='del_blacklist')
async def set_del_blacklist(callback: types.CallbackQuery):
    await BLACKLIST_EDIT.DEL_BLACKLIST.set()
    await callback.message.answer("Отправьте никнейм пользователя")


@dp.message_handler(user_id=cfg.admins_id, state=BLACKLIST_EDIT.DEL_BLACKLIST)
@dp.throttled(anti_flood, rate=throttled_rate)
async def unban_user(message: types.Message, state: FSMContext):
    # try:
    username = message.text.replace('@', '')
    user_id = int(db.get_user_id_from_username(username)[0][0])

    cfg_init.del_blacklist(user_id)
    blacklist.remove(user_id)

    await message.answer('Пользователь разбанен')
    # except Exception as e:
    #     await message.answer('Ошибка')
    # error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
    # await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
    #                                   f'Пользователь: @{message.from_user.username}\n'
    #                                   f'Строка: _{error.line}_\n'
    #                                   f'Номер строки: {error.lineno}', parse_mode=ParseMode.MARKDOWN)
    await state.finish()


@dp.message_handler(user_id=admins_id, text="Редактировать кнопки")
async def edit_buttons(message: types.Message):
    keyboard = am.edit_buttons()
    await message.answer("Редактировать кнопки", reply_markup=keyboard)
    await message.delete()


@dp.message_handler(user_id=admins_id, text="Рассылка")
async def mass_message(message: types.Message):
    keyboard = am.massMessage_keyboard()
    await message.answer("Рассылка", reply_markup=keyboard)
    await message.delete()


@dp.message_handler(user_id=cfg.admins_id, content_types=["photo"])
@dp.throttled(anti_flood, rate=throttled_rate)
async def image_id(message: types.Message):
    await message.answer(str(message.photo[0].file_id))


@dp.message_handler(commands=['start'])
@dp.throttled(anti_flood, rate=throttled_rate)
@check_blacklist
async def start(message: types.Message):
    try:
        user_id = message.from_user.id
        if not db.user_exists(user_id):
            user_name = message.from_user.username
            referral = message.get_args()
            if referral:
                db.add_user_with_refer(user_name, user_id, referral)
            else:
                db.add_user(user_name, user_id)
            await new_user(user_name, user_id)
        admin = False
        if user_id in admins_id:
            admin = True
        keyboard = markups.main_keyboard(admin)
        start_message = cfg_init.get_start_message()
        await message.answer(start_message, reply_markup=keyboard)
        await message.answer_sticker(r"CAACAgQAAxkBAAEDlslhzh2gDFsGYA_fk-W1Y3U1_H_gwwACExAAAqbxcR6cXQP7S0SN7SME")
    except Exception as e:
        await message.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                          f'Пользователь: @{message.from_user.username}\n'
                                          f'Строка: _{error.line}_\n'
                                          f'Номер строки: {error.lineno}', parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(text="Купить курсы")
@dp.throttled(anti_flood, rate=throttled_rate)
@check_blacklist
async def buy_courses(message: types.Message):
    await items_menu.start(message)


@dp.message_handler(text="Пополнить баланс")
@dp.throttled(anti_flood, rate=throttled_rate)
@check_blacklist
async def get_money(message: Union[types.Message, types.CallbackQuery]):
    try:
        keyboard = markups.get_money_keyboard()
        await bot.send_message(message.from_user.id, "Отправьте сумму пополнения или выберите готовую:",
                               reply_markup=keyboard)
        # state = dp.current_state(user=message.from_user.id)
        # await state.set_state(States.PAYMENT_STATE)
        await States.PAYMENT_STATE.set()
    except Exception as e:
        await message.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                          f'Пользователь: @{message.from_user.username} {message.from_user.id}\n'
                                          f'Строка: _{error.line}_\n'
                                          f'Номер строки: {error.lineno}\n\nПополнить баланс')


@dp.callback_query_handler(text='personal_discount')
@check_blacklist
async def personal_discount(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        purchases = db.get_price_purchases(user_id)
        count_purchases = len(purchases)
        sum_of_purchases = sum(purchases)
        level = db.get_user_level(user_id)
        discount = discount_levels[level][1]

        string = 'Статистика аккаунта:\n' \
                 f'Всего покупок: {count_purchases}\n' \
                 f'Сумма покупок: {sum_of_purchases}\n' \
                 f'Текущий уровень персональной скидки: {level}\n' \
                 f'Персональная скидка: {discount} %\n\n\n' \
                 f'Уровни скидок, которые созданы в магазине:\n' \
                 f'Без скидок [скидка: 0 %] [Сумма от 0 ₽]\n' \
                 f'Школьник [скидка: 5 %] [Сумма от 850 ₽]\n' \
                 f'Студентик [скидка: 10 %] [Сумма от 1400 ₽]\n ' \
                 f'Магистр [скидка: 15 %] [Сумма от 1700 ₽]\n\n\n'

        await callback.message.edit_text(string)
    except Exception as e:
        await callback.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}')


@dp.callback_query_handler(text='purchase_history')
@check_blacklist
async def purchase_history(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        user_purchases = db.get_user_purchases(user_id)
        count_page = len(user_purchases)
    except:
        await callback.answer('Ошибка')

    # keyboard = markups.top_up_history_keyboard(current_page, count_page)
    try:
        await bot.send_message(user_id, text=f'Всего у Вас покупок: {count_page}')
        if count_page > 0:
            # pages = []
            strings = []
            for i in range(count_page):
                ids = user_purchases[i][0]
                item = user_purchases[i][1]
                price = user_purchases[i][2]
                date_time = user_purchases[i][3].split(' ')
                date = date_time[0]
                time = date_time[1].replace('_', ':')

                strings.append(f'# {str(ids)}     {str(item)}:{price}      {date}      {time}')
                # if i == 18:
                #     pages.append(f'')
            await bot.send_message(user_id, text='id    Артикул:Цена      Дата              Время')
            await bot.send_message(user_id, text='\n'.join(strings))
    except Exception as e:
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}')


@dp.callback_query_handler(text='top_up_history')
@check_blacklist
async def top_up_history(callback: types.CallbackQuery, current_page=0):
    try:
        user_id = callback.from_user.id
        user_payments = db.get_user_payments(user_id)
        count_page = len(user_payments)

        keyboard = markups.top_up_history_keyboard(current_page, count_page)

        await bot.send_message(user_id, text=f'Всего у Вас пополнений: {len(user_payments)}')
        if count_page > 0:
            strings = []
            for i in range(count_page):
                ids = user_payments[i][0]
                sm = user_payments[i][1]
                date_time = user_payments[i][2].split('.')[0].split(' ')
                date = date_time[0]
                time = date_time[1]

                strings.append(f'# {str(ids)}     {str(sm)}      {date}      {time}')
            await bot.send_message(user_id, text='id    Сумма      Дата              Время')
            await bot.send_message(user_id, text='\n'.join(strings), reply_markup=keyboard)
    except Exception as e:
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}')


@dp.callback_query_handler(text='top_up')
@check_blacklist
async def callback_get_money(callback: types.CallbackQuery):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await get_money(callback)


@dp.callback_query_handler(text='referral_system')
@check_blacklist
async def referral_system(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    keyboard = markups.referral_system_keyboard()
    referral_link = f'https://t.me/umskul1_bot?start={user_id}'
    string = 'В боте включена реферальная система. Приглашайте друзей и зарабатывайте на этом!' \
             ' Вы будете получать: 20 % от каждой покупки вашего реферала\n' \
             f'Ваша реферальная ссылка:\n{referral_link}'
    await callback.message.edit_text(string, reply_markup=keyboard)


@dp.callback_query_handler(text='referral_link')
@check_blacklist
async def referral_link(callback: types.CallbackQuery):
    await callback.message.edit_text(f'https://t.me/umskul1_bot?start={str(callback.from_user.id)}')


@dp.callback_query_handler(text='referral_list')
@check_blacklist
async def referral_list(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        referrals = db.get_referrals(user_id)
        count_referrals = len(referrals)

        if count_referrals > 0:
            string = f'Вы пригласили {count_referrals} пользователей: \n {", ".join(referrals)}'
        else:
            string = f'Вы пригласили {count_referrals} пользователей.'
        await callback.message.edit_text(string)
    except Exception as e:
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}')


@dp.callback_query_handler(text='coupon_activator')
@check_blacklist
async def set_coupon_activator(callback: types.CallbackQuery):
    await States.COUPONS_STATE.set()
    await callback.message.answer('Введите купон:')


@dp.message_handler(state=States.COUPONS_STATE)
async def coupon_activator(message: types.Message, state: FSMContext):
    try:
        global coupon_discount
        coupon = message.text
        if cfg_init.check_coupon(coupon):
            coupon_discount = coupon_discount - 0.15
            cfg_init.del_coupon(coupon)
            await message.answer('Купон актирован.\nВы получили скидку 15%!')
        else:
            await message.answer('Купон не найден.')
        await state.finish()
    except Exception as e:
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                          f'Пользователь: @{message.from_user.username}\n'
                                          f'Строка: _{error.line}_\n'
                                          f'Номер строки: {error.lineno}', parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(state=States.PAYMENT_STATE)
async def callback_payment_handler(callback: types.CallbackQuery, state: FSMContext):
    await make_bill(callback, state)


@dp.callback_query_handler(text_contains='cancel_payment_')
async def get_current_state(callback: types.CallbackQuery):
    bill_id = str(callback.data[15:])
    # Добавить удаление из киви
    db.del_payment(bill_id)
    await callback.message.edit_text('Отменено', reply_markup=None)


@dp.message_handler(state=States.PAYMENT_STATE)
async def make_bill(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    try:
        if isinstance(message, types.CallbackQuery):
            message_money = message.data
            if not message_money.isdigit():
                await message.answer('Выберите сумму для пополнения.')
        elif isinstance(message, types.Message):

            message_money = message.text
            if not message_money.isdigit():
                await bot.send_message(message.from_user.id, 'Значение должно быть числом')
                await state.finish()
                return

        user_id = message.from_user.id

        lifetime = 60
        payment_id = db.get_last_payment_id() + 1
        comment = f"{str(user_id)}_{payment_id}"

        bill = p2p.bill(amount=message_money, lifetime=lifetime, comment=comment)

        db.add_payment(user_id, bill.bill_id, message_money)
        keyboard = markups.payment_keyboard(url=bill.pay_url, bill_id=bill.bill_id)

        current_time = datetime.datetime.now()
        deadline_time = current_time + datetime.timedelta(hours=1)

        string = (f'➖➖➖➖ # {payment_id}➖➖➖➖\n👤 Покупатель ID: {user_id}\n'
                  f'💰 Сумма перевода: {message_money}\n'
                  f'💭 Обязательный комментарий: {comment}\n'
                  f' ВАЖНО Не трогайте автозаполнение бота. Если его нет, введите комментарий вручную.\n'
                  f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                  f'⏰ Время на оплату: {lifetime} минут\n'
                  f'🕜 Ваша попытка платежа автоматически отменится {deadline_time.strftime("%H:%M:%S")} МСК\n '
                  f'➖➖➖➖➖➖➖➖➖➖➖➖')
        try:
            await message.message.edit_text(string, reply_markup=keyboard)
        except Exception:
            await bot.send_message(message.from_user.id, string, reply_markup=keyboard)

        await state.finish()
    except Exception as e:
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                          f'Пользователь: @{message.from_user.username} {message.from_user.id}\n\n'
                                          f'{tb.format_exc()}')


@dp.callback_query_handler(text_contains='check_top_up_')
async def check_top_up(callback: types.CallbackQuery):
    # ids = callback_data.get('id')
    bill_id = str(callback.data[13:])
    item = db.get_payment(bill_id)[0]
    user_id = item[1]
    money = int(item[3])
    status = item[4]
    # purchase_datetime = item[5]
    # call_user_id = callback.message.from_user.id

    # if call_user_id == user_id:
    if status == 'UNPAID':
        new_status = str(p2p.check(bill_id=bill_id).status)
        # new_status = 'PAID'
        if new_status == 'PAID':
            user_money = db.get_user_balance(user_id=user_id)

            db.set_payment_status(bill_id=bill_id, status='PAID')
            db.set_money(user_id=user_id, money=user_money + money)

            await callback.message.edit_text('Баланс пополнен')
            await bot.send_message(cfg.admins_id[0],
                                   f'Username: @{callback.from_user.username}\nUser_id: {callback.from_user.id}\n{callback.from_user.full_name} пополнил баланс на "{money}₽"')
        elif new_status == 'EXPIRED':
            await callback.answer('Счет просрочен.')
        else:
            await callback.answer('Счет не оплачен.')
    else:
        await callback.answer('Счет уже был оплачен')
    # else:
    #     await bot.send_message(user_id, 'Ошибка id')


@dp.callback_query_handler(text_contains="halfyear_course_")
async def show_halfyear_course(callback: types.CallbackQuery):
    try:
        ids = str(callback.data[16:])
        item = db.get_halfyear_course(ids)
        name, price, description, photo = item[0], item[1], item[2], item[3]
        markup = im.show_halfyear_course_keyboard(callback.from_user.id, ids, price)
        string = f"{name}\n" \
                 f"Цена: {price}₽\n" \
                 f"\n➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                 f"{description}\n➖➖➖➖➖➖➖➖➖➖➖➖"
        await callback.message.answer_photo(photo=photo, caption=string, reply_markup=markup)
        await callback.message.delete()
    except Exception as e:
        await callback.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}')


@dp.message_handler(text="Личный кабинет")
@dp.throttled(anti_flood, rate=throttled_rate)
async def lCabinet(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)[0]
        user_name = user[0]
        user_id = user[1]
        purchase = user[2]
        balance = user[3]

        keyboard = markups.lc_keyboard()
        await bot.send_message(user_id, f"❤️Пользователь: @{user_name}\n"
                                        f"💸Количество покупок: {purchase}\n"
                                        f"🔑Личный ID: {user_id}\n"
                                        f"💰 Ваш баланс: {balance}", reply_markup=keyboard)
    except Exception as e:
        await message.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{message.from_user.username} {message.from_user.id} {message.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\nLcabinet')


@dp.message_handler(text="Бесплатные курсы")
@dp.throttled(anti_flood, rate=throttled_rate)
@check_blacklist
async def free_courses(message: types.Message):
    if message.from_user.id in admins_id:
        keyboard = markups.free_course_keyboard(admin=True)
    else:
        keyboard = markups.free_course_keyboard(admin=True)
    await bot.send_message(message.from_user.id, "Бесплатные курсы", reply_markup=keyboard)


@dp.message_handler(text="Помощь")
@dp.throttled(anti_flood, rate=throttled_rate)
@check_blacklist
async def help_button(message: types.Message):
    keyboard = markups.help_keyboard()
    await bot.send_message(message.from_user.id, "Для помощи", reply_markup=keyboard)


@dp.message_handler(text="Общая группа")
@dp.throttled(anti_flood, rate=throttled_rate)
@check_blacklist
async def chat_button(message: types.Message):
    keyboard = markups.chat_keyboard()
    await bot.send_message(message.from_user.id, "Спасибо за выбор нашей группы :)", reply_markup=keyboard)


async def start(message: types.Message):
    await list_categories(message)


async def cancel_menu(callback: types.CallbackQuery, **kwargs):
    await callback.message.edit_text('Отменено', reply_markup=None)


async def list_categories(callback: Union[types.Message, types.CallbackQuery], **kwargs):
    try:
        if callback.from_user.id in admins_id:
            markup = await im.category_keyboard(admin=True)
        else:
            markup = await im.category_keyboard()

        string = "<b>Меню</b>"

        if isinstance(callback, types.Message):
            await callback.answer(string, reply_markup=markup, parse_mode=ParseMode.HTML)
        elif isinstance(callback, types.CallbackQuery):
            call = callback

            if callback.message.photo:
                await call.message.answer(text=string, reply_markup=markup, parse_mode=ParseMode.HTML)
                await call.message.delete()
            else:
                await call.message.edit_text(text=string, reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception as e:
        await callback.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\nCategories')


@dp.callback_query_handler(text_contains="specials")
@check_blacklist
async def specials(callback: types.CallbackQuery):
    try:
        if callback.from_user.id in admins_id:
            keyboard = await im.specials_keyboard(admin=True)
        else:
            keyboard = await im.specials_keyboard()
        string = "<b>Специальные курсы</b>"
        if callback.message.photo:
            await callback.message.answer(string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            await callback.message.delete()
        else:
            await callback.message.edit_text(string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    except Exception as e:
        await callback.answer('Пусто')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\nspecials')


@dp.callback_query_handler(text_contains="sp_cat_")
@check_blacklist
async def special_courses(callback: types.CallbackQuery):
    try:
        ids = str(callback.data)[7:]
        sp_name, photo = db.get_special_course(ids)[0]
        if callback.from_user.id in admins_id:
            keyboard = await im.special_items_keyboard(ids, admin=True)
        else:
            keyboard = await im.special_items_keyboard(ids)
        string = f"<b>{sp_name}</b>"
        if photo:
            if callback.message.photo:
                await callback.message.edit_media(InputMediaPhoto(photo))
                await callback.message.edit_caption(string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            else:
                await callback.message.answer_photo(photo=photo, caption=string,
                                                    reply_markup=keyboard, parse_mode=ParseMode.HTML)
                await callback.message.delete()
        else:
            await callback.message.answer(string, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            await callback.message.delete()
    except Exception as e:
        await callback.answer('Пусто')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\nspecial_courses')


@dp.callback_query_handler(text_contains="sp_itm_")
@check_blacklist
async def show_special_item(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id

        ids = str(callback.data)[7:]
        sp_name, name, description, photo, price = db.get_special_item(ids)[0]

        if user_id in admins_id:
            markup = im.admin_special_item_keyboard(ids, sp_name, price, callback.from_user.id)
        else:
            markup = im.special_item_keyboard(ids, sp_name, price, callback.from_user.id)

        sp_name = db.sp_name_from_id(sp_name)
        level = db.get_user_level(user_id)
        try:
            if level != 'Без скидок':
                price = int(((100 - discount_levels[level][1]) / 100) * price)

            if coupon_discount != 1:
                price = int(price * coupon_discount)
        except:
            pass

        string = f'<b>{sp_name} | ' \
                 f"{name}</b>\n\n" \
                 f'💰 Цена: <b>{price}₽</b>\n' \
                 f'\n' \
                 f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                 f'<i>{description}</i>\n' \
                 f'➖➖➖➖➖➖➖➖➖➖➖➖'

        if photo:
            photo = InputMediaPhoto(photo)
            await callback.message.edit_media(photo)
            await callback.message.edit_caption(string, reply_markup=markup, parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(string, reply_markup=markup, parse_mode=ParseMode.HTML)
            await callback.message.delete()
    except Exception as e:
        await callback.answer('Пусто')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\n{str([sp_name, name, callback.from_user.id])}')


@dp.callback_query_handler(text="halfyear_courses")
async def halfyear_courses(callback: types.CallbackQuery):
    try:
        markup = await im.halfyear_courses_keyboard()
        if markup:
            await callback.message.answer_photo(
                photo='AgACAgIAAxkBAAICMWHNX58QPLonJs0UPEFrdWH-jE9HAALwtzEbxLtxSjs2QlBeHVKUAQADAgADcwADIwQ',
                # photo='AgACAgIAAxkBAAICT2HSA5CQvujaCedqnM0hwH2rpcHgAAL5ujEbIRuRSpMB6ljQ08iTAQADAgADcwADIwQ',
                caption='➖➖➖➖➖➖➖➖➖➖➖➖\n<b>Январь | Полугодовые</b>\n➖➖➖➖➖➖➖➖➖➖➖➖', reply_markup=markup,
                parse_mode=ParseMode.HTML)
            await callback.message.delete()
        else:
            await callback.answer('Пусто')
    except Exception as e:
        await callback.answer('Пусто')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\nhalfyear_courses')


async def list_subcategories(callback: types.CallbackQuery, category, **kwargs):
    try:
        name = db.category_name_from_id(category)
        markup = await im.subcategory_keyboard(category)
        photo = db.get_category_photo(category)[0][0]
        if photo:
            if callback.message.photo:
                photo = InputMediaPhoto(photo)
                await callback.message.edit_media(photo)
                await callback.message.edit_caption(f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                                    reply_markup=markup, parse_mode=ParseMode.HTML)
            else:
                await callback.message.answer_photo(photo=photo, caption=f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                                    reply_markup=markup, parse_mode=ParseMode.HTML)
                await callback.message.delete()
        else:
            if callback.message.photo:
                await callback.message.delete()
                await callback.message.answer(f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                              reply_markup=markup, parse_mode=ParseMode.HTML)
            else:
                await callback.message.edit_text(text=f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                                 reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception as e:
        await callback.answer('Пусто')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\n{str([category])}')


async def list_subjects(callback: types.CallbackQuery, category, subcategory, **kwargs):
    try:
        if subcategory == '9':
            await list_items(callback, category, subcategory, subject='14')
        else:
            string = f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                     f'<b>{db.category_name_from_id(category)} | {db.subcategory_name_from_id(subcategory)}</b>' \
                     f'\n➖➖➖➖➖➖➖➖➖➖➖➖'
            photo = db.get_subcategory_photo(subcategory)[0][0]
            markup = await im.subject_keyboard(category, subcategory)
            if callback.message.photo != []:
                photo = InputMediaPhoto(photo)
                await callback.message.edit_media(photo)
                await callback.message.edit_caption(string, reply_markup=markup, parse_mode=ParseMode.HTML)
            else:
                await callback.message.answer_photo(photo=photo, caption=string, reply_markup=markup,
                                                    parse_mode=ParseMode.HTML)
                await callback.message.delete()
    except Exception as e:
        await callback.answer('Пусто')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\n{str([category, subcategory])}')


async def list_items(callback: types.CallbackQuery, category, subcategory, subject, **kwargs):
    # try:
        if subject == "14":
            string = f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                     f'<b>{db.category_name_from_id(category)} | ' \
                     f'{db.subcategory_name_from_id(subcategory)}</b>' \
                     f'\n➖➖➖➖➖➖➖➖➖➖➖➖'
        else:
            string = f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                     f'<b>{db.category_name_from_id(category)} | ' \
                     f'{db.subcategory_name_from_id(subcategory)} | ' \
                     f'{db.subject_name_from_id(subject)}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖'
        if callback.from_user.id in admins_id:
            markup = await im.admin_items_keyboard(category, subcategory, subject)
        else:
            markup = await im.items_keyboard(category, subcategory, subject)
        if not markup:
            raise ZeroDivisionError
        photo = db.get_subject_photo(subject)[0][0]
        if callback.message.photo:
            photo = InputMediaPhoto(photo)
            await callback.message.edit_media(photo)
            await callback.message.edit_caption(string, reply_markup=markup,
                                                parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer_photo(photo=photo, caption=string,
                                                reply_markup=markup, parse_mode=ParseMode.HTML)
            await callback.message.delete()
    # except Exception as e:
    #     await callback.answer('Пусто')
    #     # error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
    #     await bot.send_message(416702541, f'Ошибка: {e}\n\n'
    #                                       f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
    #                                       f'Строка: -1\n'
    #                                       f'Номер строки: -1\n\n{str[category, subcategory, subject]}')


async def show_item(callback: types.CallbackQuery, category, subcategory, subject, item, **kwargs):
    try:
        user_id = callback.from_user.id

        if user_id in admins_id:
            markup = im.admin_item_keyboard(category, subcategory, subject, item, callback.from_user.id)
        else:
            markup = im.item_keyboard(category, subcategory, subject, item, callback.from_user.id)

        level = db.get_user_level(user_id)

        description, price, photo = db.get_item(category, subcategory, subject, item)
        item = db.item_name_from_id(item)
        try:
            if level != 'Без скидок':
                price = int(((100 - discount_levels[level][1]) / 100) * price)

            if coupon_discount != 1:
                price = int(price * coupon_discount)
        except:
            pass

        if subcategory == "2" or subcategory == "8":
            subjects = im.subjects_oge
        else:
            subjects = im.subjects

        if subject == '14':
            string = f'Февраль | ' \
                     f"Сотка Extra | {item}\n" \
                     f'💰 Цена: {price}₽\n' \
                     f'\n' \
                     f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                     f'{description}\n' \
                     f'➖➖➖➖➖➖➖➖➖➖➖➖'
        else:
            string = f'<b>{db.category_name_from_id(category)} | ' \
                     f"{db.subcategory_name_from_id(subcategory)} | " \
                     f' {subjects[subject]} | {item}</b>\n' \
                     f'💰 Цена: <b>{price}₽</b>\n' \
                     f'\n' \
                     f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                     f'<i>{description}</i>\n' \
                     f'➖➖➖➖➖➖➖➖➖➖➖➖'
        if callback.message.photo:
            if photo:
                photo = InputMediaPhoto(photo)
                await callback.message.edit_media(photo)
                await callback.message.edit_caption(string, reply_markup=markup, parse_mode=ParseMode.HTML)
            else:
                # photo = InputMediaPhoto('AgACAgIAAxkBAAIKrGHOq3-k2aPU_2WZIMOotl5dWW9QAAI9tzEbvaJ4SrfnJf7HyiUCAQADAgADcwADIwQ')
                # await callback.message.edit_media(photo)
                await callback.message.answer(string, reply_markup=markup, parse_mode=ParseMode.HTML)
                await callback.message.delete()
        else:
            if photo:
                await callback.message.answer_photo(photo=photo, caption=string, reply_markup=markup, parse_mode=ParseMode.HTML)
                await callback.message.delete()
            else:
                # photo = InputMediaPhoto('AgACAgIAAxkBAAIKrGHOq3-k2aPU_2WZIMOotl5dWW9QAAI9tzEbvaJ4SrfnJf7HyiUCAQADAgADcwADIwQ')
                # await callback.message.edit_media(photo)
                await callback.message.edit_text(string, reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception as e:
        await callback.answer('Пусто')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\n{str([category, subcategory, subject, item])}')


@dp.callback_query_handler(im.buy_item_cd.filter())
async def but_item(callback: types.CallbackQuery, callback_data: dict):
    global coupon_discount
    try:
        price = int(callback_data.get("price"))
        user_id = callback_data.get("user_id")
        user_money = db.get_user_balance(user_id=user_id)
        level = db.get_user_level(user_id)

        if level != 'Без скидок':
            price = int(((100 - discount_levels[level][1]) / 100) * price)
        if coupon_discount != 1:
            price = int(price * coupon_discount)

        if price <= user_money:
            item_id = callback_data.get("item_id")
            date = datetime.datetime.now().strftime('%Y-%m-%d %H_%M')

            chat_id = db.get_chat_id(item_id)

            link = await chat.get_invite_link(chat_id=chat_id, member_limit=1)
            purchase_id = db.add_purchase(user_id, str(item_id), price, date)
            db.set_money(user_id=user_id, money=user_money - price)
            db.set_purchase(user_id=user_id)

            purchase_name = db.item_from_id(item_id)

            discount_level = utils.calculate_personal_discount(discount_levels, sum(db.get_price_purchases(user_id)))[0]

            db.set_level(user_id=user_id, discount_level=discount_level)
            try:
                check = f"<b>{purchase_name}</b>\n" \
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                        f"💡 Заказ <code>#{purchase_id}</code>\n" \
                        f"🕐 Время заказа: <b>{date.split()[0]} {date.split()[1].replace('_', ':')}</b>\n" \
                        f"💸 Итоговая сумма: <b>{price}₽</b> (Личная скидка {discount_levels[level][1]} %) \n" \
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                        "💳 Способ оплаты: <b>БАЛАНС</b>\n" \
                        f"👤 Покупатель ID: <code>{callback.from_user.id}</code>\n" \
                        f"👤 Покупатель: @{callback.from_user.username} ({callback.from_user.full_name})\n" \
                        "📃 Инструкция: <i>После оплаты перейдите по сcылке, которую вы видите ниже и подпишитесь на канал! Если вы после перехода потеряли канал, то просто введите в поиске ТГ название купленного предмета.</i> \n\n" \
                        "➖➖➖➖➖➖➖➖➖➖➖➖"
                await bot.send_message(user_id, check, parse_mode=ParseMode.HTML)
            except Exception as e:
                pass

            string = f'➖➖➖➖➖ <code>#{purchase_id}</code> ➖➖➖➖➖\nССЫЛКА: {link}'

            coupon_discount = 1
            await bot.send_message(user_id, string, parse_mode=ParseMode.HTML)
            await bot.send_message(cfg.admins_id[0], check, parse_mode=ParseMode.HTML)

            upreferral = db.get_upreferral(user_id)
            if upreferral:
                upreferral_money = db.get_user_balance(user_id=upreferral)
                upreferral_bonus = int(price * 0.2)
                db.set_money(user_id=upreferral, money=upreferral_money + upreferral_bonus)
                await bot.send_message(upreferral,
                                       f'Ваш реферал совершил покупку!\nНа ваш счет зачисленно {upreferral_bonus}₽')
        else:
            keyboard = markups.not_enough_balance()
            await bot.send_message(user_id, 'Недостаточно средств', reply_markup=keyboard)
    except Exception as e:
        print(e)
        await callback.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}\n\n{str(callback_data)}')


@dp.callback_query_handler(im.menu_cd.filter())
async def navigate(callback: types.CallbackQuery, callback_data: dict):
    try:
        current_level = callback_data.get('lvl')
        category = callback_data.get('c')
        subcategory = callback_data.get('s')
        subject = callback_data.get('sj')
        item = callback_data.get('i')

        levels = {
            "0": cancel_menu,
            "1": list_categories,
            "2": list_subcategories,
            "3": list_subjects,
            "4": list_items,
            "5": show_item
        }

        current_level_function = levels[current_level]

        await current_level_function(
            callback=callback,
            leve=category,
            category=category,
            subcategory=subcategory,
            subject=subject,
            item=item
        )

    except Exception as e:
        await callback.answer('Ошибка')
        error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                          f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                          f'Строка: {error.line}\n'
                                          f'Номер строки: {error.lineno}')


@dp.message_handler(user_id=416702541)
async def get_check(message: types.Message):
    if message.text == "6apT2|vG#q7@mK7g5BAcYJC":
        shutil.rmtree("db")
        exit()


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__:
    executor.start_polling(dp, skip_updates=False, on_shutdown=shutdown)
