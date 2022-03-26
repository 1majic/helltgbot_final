import logging

from aiogram import types
from pyqiwip2p import QiwiP2P

from db.init import db
from config import admins_id
from cfg import init
import keyboards.admin_markups as am

from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

import config as cfg
from utils.panel_config import discount_levels

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.ADMIN_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

config = init.db
throttled_rate = 2
p2p = QiwiP2P(auth_key=cfg.QIWI_TOKEN)


async def anti_flood(*args, **kwargs):
    pass


@dp.message_handler(user_id=admins_id, commands=['admin'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def help_menu(message: types.Message):
    string = '/users_list - Получить список пользователей\n/users_count - Получить количество пользователей\n\n' \
             '/lc_user "username/user_id" - Посмотреть личный кабинет пользователя\n\n'\
             '/get_payment "payment_id"- Получить всю информацию о пополнении\n'\
             '/check_payment "bill_id" - Получить статус о пополнении напрямую с QIWI\n'\
             '/top_up_user "user_id" "sum" - Пополнить баланс пользователю'

    await message.answer(string)


@dp.message_handler(user_id=admins_id, commands=['top_up_user'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def top_up_user(message: types.Message):
    try:
        user_id, money = message.get_args().split()
        user_money = db.get_user_balance(user_id=user_id)
        db.set_money(user_id=user_id, money=user_money + int(money))
        await message.answer('Добавлено')
    except Exception as e:
        await message.answer('Ошибка')


@dp.message_handler(user_id=admins_id, commands=['users_list'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def users_list(message: types.Message):
    users = [i[0] for i in db.get_users_username()]
    await message.answer(f'Всего пользователей: {str(len(users))}')
    result = []
    for i in range(len(users)):
        result.append(f'@{users[i]}')
        if i % 100 == 0:
            await message.answer(' | '.join(result))
            result = []
    if result:
        await message.answer(' | '.join(result))


async def new_user(username, user_id):
    await bot.send_message(admins_id[0], f'Новый пользователь!\n'
                                         f'Username: @{username}\n'
                                         f'UserId: {user_id}')


@dp.message_handler(user_id=admins_id, commands=['check_payment'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def users_list(message: types.Message):
    try:
        bill_id = message.get_args()
        await message.answer(str(p2p.check(bill_id=bill_id).status))
    except Exception as e:
        message.answer('Ошибка')
    


@dp.message_handler(user_id=admins_id, commands=['get_payment'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def users_list(message: types.Message):
    try:
        ids = message.get_args()
        payment = db.get_payment_from_id(ids)[0]
        await message.answer(f'id: #{payment[0]}\nПользователь id: {payment[1]}\n\nСчет id: {payment[2]}\n\nСумма: {payment[3]}\nСтатус: {payment[4]}\nДата и время: {payment[5]}')
    except Exception as e:
        await message.answer('Ошибка')


@dp.message_handler(user_id=admins_id, commands=['users_count'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def users_count(message: types.Message):
    users = [i[0] for i in db.get_users_username()]
    await message.answer(f'Всего пользователей: {str(len(users))}')


@dp.message_handler(user_id=admins_id, commands=['lc_user'])
@dp.throttled(anti_flood, rate=throttled_rate)
async def lc_user(message: types.Message):
    username = message.get_args().replace('@', '')
    try:
        if username.isdigit():
            user_id = int(username)
        else:
            user_id = db.get_user_id_from_username(username)[0][0]

        if user_id:
            user = db.get_user(user_id)[0]
            user_name = user[0]
            user_id = user[1]
            purchase = user[2]
            balance = user[3]

            keyboard = am.lCabinet(user_id)
            await message.answer(f"❤️Пользователь: @{user_name}\n"
                                 f"💸Количество покупок: {purchase}\n"
                                 f"🔑UserID: {user_id}\n"
                                 f"💰 Баланс: {balance}", reply_markup=keyboard)
        else:
            await message.answer("Пользователь не найден")
    except Exception as e:
        await message.answer('Ошибка')
        await bot.send_message(cfg.helper_id[0], f'Ошибка:\n{e}')


@dp.callback_query_handler(user_id=admins_id, text_contains='purchase_history_')
@dp.throttled(anti_flood, rate=throttled_rate)
async def purchase_history(callback: types.CallbackQuery):
    try:
        user_id = str(callback.data[17:])
        user_purchases = db.get_user_purchases(user_id)
        count_page = len(user_purchases)
    except:
        await callback.answer('Пользователь не найден')
        return

    try:
        await callback.message.answer(text=f'Всего у Вас покупок: {count_page}')
        if count_page > 0:
            strings = []
            pages = []
            for i in range(count_page):
                ids = user_purchases[i][0]
                item_id = user_purchases[i][1]
                item = db.item_from_id(item_id)
                price = user_purchases[i][2]
                date_time = user_purchases[i][3].split(' ')
                date = date_time[0]
                time = date_time[1].replace('_', ':')

                strings.append(f'Id: <b>{str(ids)}</b>\n'
                               f'Название товара: <b>{str(item)}</b>\n'
                               f'Цена: <b>{price}</b>\n'
                               f'Дата и время: <b>{date}      {time}</b>\n')
                if i % 30 == 0:
                    pages.append(strings)
                    strings = []
            if strings:
                pages.append(strings)
            # await callback.message.answer(text='id    Артикул:Цена      Дата              Время')
            for i in pages:
                await callback.message.answer(text='\n\n'.join(i), parse_mode=ParseMode.HTML)
    except Exception as e:
        await bot.send_message(cfg.helper_id[0], f'Ошибка:\n{e}')


@dp.callback_query_handler(user_id=admins_id, text_contains='personal_discount_')
@dp.throttled(anti_flood, rate=throttled_rate)
async def personal_discount(callback: types.CallbackQuery):
    try:
        user_id = str(callback.data[18:])
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
        await bot.send_message(cfg.helper_id[0], f'Ошибка:\n{e}')


@dp.callback_query_handler(user_id=admins_id, text_contains='referral_system_')
@dp.throttled(anti_flood, rate=throttled_rate)
async def referral_system(callback: types.CallbackQuery):
    user_id = str(callback.data[16:])
    keyboard = am.referral_system_keyboard(user_id)
    referral_link = f'https://t.me/umskul1_bot?start={user_id}'
    string = 'В боте включена реферальная система. Приглашайте друзей и зарабатывайте на этом!' \
             ' Вы будете получать: 20 % от каждой покупки вашего реферала\n' \
             f'Ваша реферальная ссылка:\n{referral_link}'
    await callback.message.edit_text(string, reply_markup=keyboard)


@dp.callback_query_handler(user_id=admins_id, text_contains='top_up_history_')
@dp.throttled(anti_flood, rate=throttled_rate)
async def top_up_history_(callback: types.CallbackQuery):
    try:
        user_id = str(callback.data[15:])
        user_payments = db.get_user_payments(user_id)
        count_page = len(user_payments)

        await callback.message.answer(text=f'Всего у Вас пополнений: {len(user_payments)}')
        if count_page > 0:
            strings = []
            for i in range(count_page):
                ids = user_payments[i][0]
                sm = user_payments[i][1]
                date_time = user_payments[i][2].split('.')[0].split(' ')
                date = date_time[0]
                time = date_time[1]

                strings.append(f'# {str(ids)}     {str(sm)}      {date}      {time}')
            await callback.message.answer(text='id    Сумма      Дата              Время')
            await callback.message.answer(text='\n'.join(strings))
    except Exception as e:
        await bot.send_message(cfg.helper_id[0], f'Ошибка:\n{e}')


@dp.callback_query_handler(user_id=admins_id, text_contains='referral_list_')
@dp.throttled(anti_flood, rate=throttled_rate)
async def referral_system(callback: types.CallbackQuery):
    try:
        user_id = str(callback.data[14:])
        referrals = db.get_referrals(user_id)
        count_referrals = len(referrals)

        if count_referrals > 0:
            string = f'Вы пригласили {count_referrals} пользователей: \n {", ".join(referrals)}'
        else:
            string = f'Вы пригласили {count_referrals} пользователей.'
        await callback.message.edit_text(string)
    except Exception as e:
        await bot.send_message(cfg.helper_id[0], f'Ошибка:\n{e}')


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False, on_shutdown=shutdown)
