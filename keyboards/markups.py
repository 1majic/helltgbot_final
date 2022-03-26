from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from db import init

from utils import panel_config as pc

from cfg.init import db as cfg_db

db = init.db

payment_cd = CallbackData("show_menu", "bill_id")
cancel_payment_cd = CallbackData("show_menu", "bill_id", "cancel_payment")


def make_callback_data(bill_id="0"):
    return payment_cd.new(bill_id=bill_id)


def mass_keyboard():
    markup = InlineKeyboardMarkup()

    markup.insert(
        InlineKeyboardButton(text="Отзывы", url="https://t.me/umskulotzivi")
    ).insert(
        InlineKeyboardButton(text="Менеджер", url="https://t.me/UmHelper")
    )

    return markup


def main_keyboard(admin=False):
    buy_course_btn = KeyboardButton("Купить курсы")
    top_up_balance_btn = KeyboardButton("Пополнить баланс")
    lc_btn = KeyboardButton("Личный кабинет")
    free_course_btn = KeyboardButton("Бесплатные курсы")
    help_btn = KeyboardButton("Помощь")
    chat_btn = KeyboardButton("Общая группа")

    MainMenu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    MainMenu.row(buy_course_btn, top_up_balance_btn).row(lc_btn, free_course_btn).row(help_btn, chat_btn)

    if admin:
        MainMenu.row(
            InlineKeyboardButton(text="Админ", callback_data="admin")
        )
    return MainMenu


def free_course_keyboard(admin=False):
    markup = InlineKeyboardMarkup(row_width=1)

    courses = db.get_free_courses()
    for course in courses:
        name = course[1]
        link = course[2]
        markup.row(
            InlineKeyboardButton(text=name, url=link)
        )

    if admin:
        markup.row(InlineKeyboardButton(text='$ Добавить бесплатный курс $', callback_data='add_free_course')
                   ).row(InlineKeyboardButton(text='$ Удалить бесплатный курс $', callback_data='del_free_course'))
    return markup


def get_money_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_200 = InlineKeyboardButton(text="200₽", callback_data="200")
    btn_250 = InlineKeyboardButton(text="250₽", callback_data="250")
    btn_350 = InlineKeyboardButton(text="350₽", callback_data="350")
    btn_400 = InlineKeyboardButton(text="400₽", callback_data="400")
    # btn_2000 = InlineKeyboardButton(text="2000₽", callback_data="2000")

    markup.row(btn_200, btn_250).row(btn_350, btn_400)
        # .row(btn_398).row(btn_498).row(btn_2000)

    return markup


def payment_keyboard(isUrl=True, url='', bill_id=""):
    markup = InlineKeyboardMarkup()

    if isUrl:
        pay_btn = InlineKeyboardButton(text='Перейти к оплате', url=url)
        markup.insert(pay_btn)
    check_payment_btn = InlineKeyboardButton(text='✅Я оплатил!', callback_data=f"check_top_up_{bill_id}")
    cancel_payment_btn = InlineKeyboardButton(text='❌Передумал оплачивать',
                                              callback_data=f"cancel_payment_{bill_id}")

    markup.row(check_payment_btn).row(cancel_payment_btn)
    return markup


def lc_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    purchase_history_btn = InlineKeyboardButton(text="История заказов", callback_data="purchase_history")
    personal_discount_btn = InlineKeyboardButton(text="Личная скидка", callback_data="personal_discount")
    referral_system_btn = InlineKeyboardButton(text="Реферальная система", callback_data="referral_system")
    top_up_btn = InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up")
    top_up_history_btn = InlineKeyboardButton(text="История начислений", callback_data="top_up_history")
    coupon_activator_btn = InlineKeyboardButton(text="Активировать купон", callback_data="coupon_activator")

    markup.row(purchase_history_btn).row(personal_discount_btn).row(referral_system_btn).row(top_up_btn,
                                                                                             top_up_history_btn).row(
        coupon_activator_btn)

    return markup


def referral_system_keyboard():
    markup = InlineKeyboardMarkup()

    referral_list_button = InlineKeyboardButton(text="Список рефералов", callback_data="referral_list")
    referral_link_button = InlineKeyboardButton(text="Получить ссылку отдельным сообщением", callback_data="referral_link")

    markup.row(referral_list_button).row(referral_link_button)

    return markup


def help_keyboard():
    markup = InlineKeyboardMarkup()

    admin_btn = InlineKeyboardButton(text=cfg_db.get_admin_text(), url=cfg_db.get_admin_link())
    Reviews_Btn = InlineKeyboardButton(text=cfg_db.get_reviews_text(), url=cfg_db.get_reviews_link())
    rekv_btn = InlineKeyboardButton(text='РЕКВИЗИТЫ', url='https://t.me/vipumskul/4')

    markup.insert(admin_btn)
    markup.insert(Reviews_Btn)
    markup.row(rekv_btn)

    return markup


def chat_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    # chat_btn = InlineKeyboardButton(text=cfg_db.get_chat_text(), url=cfg_db.get_chat_link())
    group_btn = InlineKeyboardButton(text=cfg_db.get_group_text(), url=cfg_db.get_group_link())

    # markup.insert(
    #     chat_btn
    # )
    markup.insert(
        group_btn
    )

    return markup


def top_up_history_keyboard(pages_count, current_page):
    markup = InlineKeyboardMarkup(row_width=2)

    next_page = InlineKeyboardButton(text='->', callback_data='next_page')
    back_page = InlineKeyboardButton(text='<-', callback_data='back_page')

    if pages_count != 1:
        if current_page == 1:
            markup.insert(next_page)

            return markup

        elif 1 < current_page < pages_count:
            markup.row(next_page, back_page)

            return markup

        elif current_page == pages_count:
            markup.insert(back_page)

            return markup
    return None


def not_enough_balance():
    markup = InlineKeyboardMarkup(row_width=2)

    top_up_btn = InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up")

    markup.row(top_up_btn)

    return markup