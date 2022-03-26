from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from db import init

from cfg.init import db as cfg_init

db = init.db


def main_keyboard():
    edit_panel_btn = KeyboardButton("Редактировать приветствие")
    blacklist_btn = KeyboardButton("Cписок забаненных пользователей")
    check_stats_btn = KeyboardButton("Редактировать кнопки")
    coupons_btn = KeyboardButton("Рассылка")

    MainMenu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    MainMenu.row(edit_panel_btn, check_stats_btn).row(blacklist_btn, coupons_btn).row(KeyboardButton("Меню"))
    return MainMenu


def blacklist_keyboard():
    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(text="Добавить пользователя", callback_data="add_blacklist")
    ).row(
        InlineKeyboardButton(text="Удалить пользователя", callback_data="del_blacklist")
    )

    return markup


def edit_buttons():
    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(text='Кнопка "Админ"', callback_data="edit_admin_btn")
    ).row(
        InlineKeyboardButton(text='Кнопка "Отзывы"', callback_data="edit_reviews_btn")
    ).row(
        InlineKeyboardButton(text='Кнопка "Чат"', callback_data="edit_chat_link")
    ).row(
        InlineKeyboardButton(text='Кнопка "Группа"', callback_data="edit_group_link")
    )

    return markup


def edit_buy_course(item):
    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(text="Редактировать название", callback_data=f"edit_item_name_{str(item)}")
    ).row(
        InlineKeyboardButton(text="Редактировать описание", callback_data=f"edit_description_{str(item)}")
    ).row(
        InlineKeyboardButton(text="Редактировать фото", callback_data=f"edit_photo_{str(item)}")
    ).row(
        InlineKeyboardButton(text="Редактировать цену", callback_data=f"edit_price_{str(item)}")
    ).row(
        InlineKeyboardButton(text="Редактировать chat id", callback_data=f"edit_chat_id_{str(item)}")
    ).row(
        InlineKeyboardButton(text="Удалить", callback_data=f"del_course_{str(item)}")
    ).row(
        InlineKeyboardButton(text="Назад", callback_data=f"cancel_{str(item)}")
    )

    return markup


def cancel_edit_course_keyboard(item):
    markup = InlineKeyboardMarkup()
    return markup.row(
        InlineKeyboardButton(text="Назад", callback_data=f"cancel_{item}")
    )


def cancel_keyboard():
    markup = InlineKeyboardMarkup()
    return markup.row(InlineKeyboardButton(text="Отмена", callback_data="just_cancel"))


def cancel_add_course_keyboard():
    markup = InlineKeyboardMarkup()
    return markup.row(
        InlineKeyboardButton(text="Назад", callback_data="cancel_add_course")
    )


def cancel_add_item_photo_keyboard():
    markup = InlineKeyboardMarkup()
    return markup.row(
        InlineKeyboardButton(text="Пропустить", callback_data="skip_photo")
    ).row(
        InlineKeyboardButton(text="Назад", callback_data="cancel_add_course")
    )


def confirm_adding_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text="Подтвердить", callback_data="confirm")
    ).row(
        InlineKeyboardButton(text="Отмена", callback_data="cancel_add_course")
    )

    return markup


def lCabinet(user_id):
    markup = InlineKeyboardMarkup(row_width=2)

    purchase_history_btn = InlineKeyboardButton(text="История заказов", callback_data=f"purchase_history_{user_id}")
    personal_discount_btn = InlineKeyboardButton(text="Личная скидка", callback_data=f"personal_discount_{user_id}")
    referral_system_btn = InlineKeyboardButton(text="Реферальная система", callback_data=f"referral_system_{user_id}")
    top_up_history_btn = InlineKeyboardButton(text="История начислений", callback_data=f"top_up_history_{user_id}")

    markup.row(purchase_history_btn).row(personal_discount_btn).row(referral_system_btn).row(top_up_history_btn)

    return markup


def referral_system_keyboard(user_id):
    markup = InlineKeyboardMarkup()

    referral_list_button = InlineKeyboardButton(text="Список рефералов", callback_data=f"referral_list_{user_id}")

    markup.row(referral_list_button)

    return markup


def admin_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    markup.insert(
        InlineKeyboardButton(text='Редактировать надпись', callback_data='edit_admin_btn_text')
    ).insert(
        InlineKeyboardButton(text='Редактировать ссылку', callback_data='edit_admin_btn_link')
    )

    return markup


def reviews_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    markup.insert(
        InlineKeyboardButton(text='Редактировать надпись', callback_data='edit_reviews_btn_text')
    ).insert(
        InlineKeyboardButton(text='Редактировать ссылку', callback_data='edit_reviews_btn_link')
    )

    return markup


def massMessage_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    markup.insert(
        InlineKeyboardButton(text="Новое сообщение", callback_data="send_message")
    ).insert(
        InlineKeyboardButton(text="Удалить последнюю рассылку", callback_data="del_message")
    )

    return markup


def chat_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    markup.insert(
        InlineKeyboardButton(text='Редактировать надпись', callback_data='edit_chat_btn_text')
    ).insert(
        InlineKeyboardButton(text='Редактировать ссылку', callback_data='edit_chat_btn_link')
    )
    return markup


def group_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    markup.insert(
        InlineKeyboardButton(text='Редактировать надпись', callback_data='edit_group_btn_text')
    ).insert(
        InlineKeyboardButton(text='Редактировать ссылку', callback_data='edit_group_btn_link')
    )
    return markup


def edit_panel_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    buy_course_btn = InlineKeyboardButton(text="Купить курсы", callback_data='edit_buy_course')
    free_course_btn = InlineKeyboardButton(text="Бесплатные курсы", callback_data='edit_free_course')
    help_btn = InlineKeyboardButton(text="Помощь", callback_data='edit_help')
    chat_btn = InlineKeyboardButton(text="Чатик и общая группа", callback_data='edit_chat')

    markup.row(buy_course_btn).row(free_course_btn, help_btn).row(chat_btn)

    return markup


def edit_buy_course_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    add_course = InlineKeyboardButton(text='Добавить курс', callback_data='add_course')
    del_course = InlineKeyboardButton(text='Удалить курс', callback_data='del_course')

    markup.row(add_course, del_course)

    return markup


def edit_free_course_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    add_free_course = InlineKeyboardButton(text='Добавить бесплатный курс', callback_data='add_free_course')
    del_free_course = InlineKeyboardButton(text='Удалить бесплатный курс', callback_data='del_free_course')

    markup.row(add_free_course, del_free_course)

    return markup


def edit_help_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    edit_admin_btn = InlineKeyboardButton(text='Редактировать кнопку "Админа"', callback_data='edit_admin_btn')
    edit_reviews_btn = InlineKeyboardButton(text='Редактировать кнопку "Отзывы"', callback_data='edit_reviews_btn')

    markup.row(edit_admin_btn, edit_reviews_btn)

    return markup


def edit_chat_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    edit_chat_btn = InlineKeyboardButton(text='Редактировать кнопку чата', callback_data='edit_chat_btn')
    edit_group_btn = InlineKeyboardButton(text='Редактировать кнопку группы', callback_data='edit_group_btn')

    markup.row(edit_chat_btn, edit_group_btn)

    return markup


def cancel():
    markup = InlineKeyboardMarkup()

    return markup.row(
        InlineKeyboardButton(text="Назад", callback_data="cancel")
    )
