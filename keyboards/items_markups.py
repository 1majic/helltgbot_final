from datetime import datetime
from unicodedata import category

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from db.init import db

menu_cd = CallbackData("show_menu", "lvl", "c", "s", "sj", "i")
buy_item_cd = CallbackData("show_menu", "user_id", "item_id", "price")
special_courses = CallbackData("show_menu", "id", 'cds', 'cfd', 'dfg')
buy_special_courses = CallbackData("show_menu", "user_id", "item_id", "price", 'cds', 'cfd', 'dfg', 'space')

subjects = {"1": "РУССКИЙ ЯЗЫК📔",
            "2": "ПРОФ🧮",
            "3": "БАЗА📐",
            "4": "ФИЗИКА📈",
            "5": "ОБЩЕСТВОЗНАНИЕ📒",
            "6": "ИСТОРИЯ📖",
            "7": "БИОЛОГИЯ🧬",
            "8": "ХИМИЯ🧪",
            "9": "ЛИТЕРАТУРА📚",
            "10": "АНГЛИЙСКИЙ ЯЗЫК📓",
            "11": "ИНФОРМАТИКА🖥",
            "12": "ГЕОГРАФИЯ🔭"}

subjects_oge = {"1": "РУССКИЙ ЯЗЫК📔",
                "15": "МАТЕМАТИКА📐",
                "5": "ОБЩЕСТВОЗНАНИЕ📒",
                "7": "БИОЛОГИЯ🧬",
                "8": "ХИМИЯ🧪"}

categories = {
                # "1": "Сентябрь",
              # "2": "Октябрь",
              # "3": "Ноябрь",
              "9": "Декабрь",
              "8": "Январь",
              "7": "Февраль",
              "6": "Март",
              "5": "Апрель"
              # "4": "Май"
              }

subcategories = {"1": "ЕГЭ",
                 "2": "ОГЭ"}

subcategories_january = {
    "5": "Годовые ЕГЭ",
    "4": "Полугодовые ЕГЭ",
    "2": "ОГЭ"
}

subcategories_february = {
    "1": "ЕГЭ",
    "7": "НЕО УМСКУЛ",
    "2": "ОГЭ"
}


def make_special_course(ids, cds="sdc", cfd="cfd", dfg="dfg"):
    return special_courses.new(id=ids, cds=cds, cfd=cfd, dfg=dfg)


def make_callback_data(level=1, category='0', subcategory="0", subject="0", item="0"):
    return menu_cd.new(lvl=level, c=category, s=subcategory, sj=subject, i=item)


# async def special_courses_keyboard():
#     markup = InlineKeyboardMarkup(row_width=1)
#     courses = db.get_special_courses()
#     for i in courses:
#         ids, name, price = i[0], i[1], i[2]
#         callback_data = make_special_course(ids)
#         markup.row(
#             InlineKeyboardButton(text=f"{name} | {price}₽", callback_data=callback_data)
#         )
#     markup.row(
#         InlineKeyboardButton(text="Вернуться◀️",
#                              callback_data=make_callback_data(level=1))
#     )
#
#     return markup


async def category_keyboard(admin=False):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=3)

    for category_id, category_name in db.get_categories():
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category_id)

        markup.insert(
            InlineKeyboardButton(text=category_name, callback_data=callback_data)
        )


    markup.row(
        InlineKeyboardButton(text="Специальные курсы", callback_data="specials")
    )
    # for category_id, category_name in db.get_special_courses():
    #
    #     markup.row(
    #         InlineKeyboardButton(text=category_name, callback_data=f"sp_cat_{category_id}")
    #     )

    if admin:
        markup.row(
            InlineKeyboardButton(text="$ Добавить категорию $", callback_data="create_category")
        )

    markup.row(
        InlineKeyboardButton(text="Закрыть🚫", callback_data=make_callback_data(level=CURRENT_LEVEL - 1))
    )

    return markup


async def specials_keyboard(admin=False):

    markup = InlineKeyboardMarkup(row_width=3)

    for category_id, category_name in db.get_special_courses():

        markup.row(
            InlineKeyboardButton(text=category_name, callback_data=f"sp_cat_{category_id}")
        )

    if admin:
        markup.row(
            InlineKeyboardButton(text="$ Добавить специальную категорию $", callback_data="create_special_course")
        )

    markup.row(
        InlineKeyboardButton(text="Вернуться◀️",
                             callback_data=make_callback_data(level=1))
    )

    return markup


async def special_items_keyboard(ids, admin=False):
    markup = InlineKeyboardMarkup()

    for ids, name, price in db.get_special_items(ids):
        markup.row(
            InlineKeyboardButton(text=f"{name} | {price}", callback_data=f"sp_itm_{ids}")
        )

    if admin:
        markup.row(
            InlineKeyboardButton(text="$ Добавить курс $", callback_data=f"add_special_course_{ids}")
        ).row(
            InlineKeyboardButton(text="$ Добавить изображение $", callback_data=f"add_special_course_image_{ids}")
        ).row(
            InlineKeyboardButton(text="$ Удалить специальную категорию $", callback_data=f"del_sp_{ids}")
        )

    markup.row(
        InlineKeyboardButton(text="Вернуться◀️",
                             callback_data="specials")
    )

    return markup


async def subcategory_keyboard(category, admin=False):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=3)
    if category == "5":
        markup.row(
            InlineKeyboardButton(text="Годовые ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      category=category,
                                                                                      subcategory="5"))
        ).row(
            InlineKeyboardButton(text="Полугодовые ЕГЭ", callback_data="halfyear_courses")
        ).row(
            InlineKeyboardButton(text="ОГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      category=category,
                                                                                      subcategory="2"))
        )

        markup.row(
            InlineKeyboardButton(text="$ Удалить категорию $",
                                 callback_data=f"del_category_{category}")
        ).row(
            InlineKeyboardButton(text="Вернуться◀️",
                                 callback_data=make_callback_data(level=CURRENT_LEVEL - 1, category=category))
        )
    # elif category == "7":
    #     # markup.row(
    #     #     InlineKeyboardButton(text="ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
    #     #                                                                       category=category,
    #     #                                                                       subcategory="1"))
    #     # ).row(
    #     #     InlineKeyboardButton(text="NEO ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
    #     #                                                                              category=category,
    #     #                                                                              subcategory="7"))
    #     # ).row(
    #     #     InlineKeyboardButton(text="ОГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
    #     #                                                                       category=category,
    #     #                                                                       subcategory="2"))
    #     # ).row(
    #     #     InlineKeyboardButton(text="NEO ОГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
    #     #                                                                       category=category,
    #     #                                                                       subcategory="8"))
    #     # )
    #     markup.row(
    #         InlineKeyboardButton(text="ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
    #                                                                                  category=category,
    #                                                                                  subcategory="7"))
    #     ).row(
    #         InlineKeyboardButton(text="ОГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
    #                                                                           category=category,
    #                                                                           subcategory="8"))
    #     ).row(
    #         InlineKeyboardButton(text="Сотка EXTRA", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
    #                                                                               category=category,
    #                                                                               subcategory="9"))
    #     )

    #     markup.row(
    #         InlineKeyboardButton(text="Вернуться◀️",
    #                              callback_data=make_callback_data(level=CURRENT_LEVEL - 1, category=category))
    #     )
    else:
        for subcategory_id, subcategory_name in db.get_subcategories():
            callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category, subcategory=subcategory_id)

            markup.row(
                InlineKeyboardButton(text=subcategory_name, callback_data=callback_data)
            )
        markup.row(
            InlineKeyboardButton(text="$ Добавить картинку $",
                                 callback_data=f"add_category_image_{category}")
        ).row(
            InlineKeyboardButton(text="$ Удалить категорию $",
                                 callback_data=f"del_category_{category}")
        ).row(
            InlineKeyboardButton(text="Вернуться◀️",
                                 callback_data=make_callback_data(level=CURRENT_LEVEL - 1, category=category))
        )

    return markup


def admin_special_item_keyboard(ids, sp_name, price, user_id):
    markup = InlineKeyboardMarkup(row_width=2)

    callback_data = buy_item_cd.new(user_id=user_id, item_id=f"-{ids}", price=price)

    markup.row(
        InlineKeyboardButton(text=f'Купить', callback_data=callback_data)
    )

    markup.row(
        InlineKeyboardButton(text="$ Редактировать $", callback_data=f"edit_course_-{ids}")
    ).row(
        InlineKeyboardButton(text=f'Вернуться◀️', callback_data=f"sp_cat_{sp_name}")
    )

    markup.row(
        InlineKeyboardButton(text=f'Назад к категориям🚫', callback_data=make_callback_data(level=1))
    )

    return markup


def special_item_keyboard(ids, sp_name, price, user_id):
    markup = InlineKeyboardMarkup(row_width=2)

    callback_data = buy_item_cd.new(user_id=user_id, item_id=f"-{ids}", price=price)

    markup.row(
        InlineKeyboardButton(text=f'Купить', callback_data=callback_data)
    )

    markup.row(
        InlineKeyboardButton(text=f'Вернуться◀️', callback_data=f"sp_cat_{sp_name}")
    )

    markup.row(
        InlineKeyboardButton(text=f'Назад к категориям🚫', callback_data=make_callback_data(level=1))
    )

    return markup


async def admin_special_items_keyboard(category, subcategory, subject):
    CURRENT_LEVEL = 4
    markup = InlineKeyboardMarkup()

    items = db.get_items(category, subcategory, subject)
    if not items:
        return False
    for item in items:
        name, price, ids = item[0], item[1], item[2]
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category, subcategory=subcategory,
                                           subject=subject, item=ids)
        markup.row(
            InlineKeyboardButton(text=f'{name} | {price}₽', callback_data=callback_data)
        )
    if subject == '14':
        markup.row(
            InlineKeyboardButton(text="$ Добавить курс $", callback_data=f"add_course_{category}:{subcategory}:{subject}")
        ).row(
            InlineKeyboardButton(text="Вернуться◀️", callback_data=make_callback_data(
                level=CURRENT_LEVEL - 2, category=category, subcategory=subcategory))
        )
    else:
        markup.row(
            InlineKeyboardButton(text="$ Добавить курс $", callback_data=f"add_course_{category}:{subcategory}:{subject}")
        ).row(
            InlineKeyboardButton(text="Вернуться◀️", callback_data=make_callback_data(
                level=CURRENT_LEVEL - 1, category=category, subcategory=subcategory,
                subject=subject))
        )

    return markup


def admin_item_keyboard(category, subcategory, subject, item, user_id):
    CURRENT_LEVEL = 5
    markup = InlineKeyboardMarkup(row_width=2)

    ids, price = db.get_item_id_price(category, subcategory, subject, item)

    callback_data = buy_item_cd.new(user_id=user_id, item_id=ids, price=price)

    markup.row(
        InlineKeyboardButton(text=f'Купить', callback_data=callback_data)
    )

    markup.row(
        InlineKeyboardButton(text="$ Редактировать $", callback_data=f"edit_course_{ids}")
    ).row(
        InlineKeyboardButton(text=f'Вернуться◀️', callback_data=make_callback_data(
            level=CURRENT_LEVEL - 1, category=category, subcategory=subcategory, subject=subject, item=item))
    )

    markup.row(
        InlineKeyboardButton(text=f'Назад к категориям🚫', callback_data=make_callback_data(level=1))
    )

    return markup


async def admin_items_keyboard(category, subcategory, subject):
    CURRENT_LEVEL = 4
    markup = InlineKeyboardMarkup()

    items = db.get_items(category, subcategory, subject)
    if items:
        for item in items:
            name, price, ids = item[0], item[1], item[2]
            callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category, subcategory=subcategory,
                                               subject=subject, item=ids)
            markup.row(
                InlineKeyboardButton(text=f'{name} | {price}₽', callback_data=callback_data)
            )
    if subject == '14':
        markup.row(
            InlineKeyboardButton(text="$ Добавить курс $", callback_data=f"add_course_{category}:{subcategory}:{subject}")
        ).row(
            InlineKeyboardButton(text="Вернуться◀️", callback_data=make_callback_data(
                level=CURRENT_LEVEL - 2, category=category, subcategory=subcategory))
        )
    else:
        markup.row(
            InlineKeyboardButton(text="Добавить курс", callback_data=f"add_course_{category}:{subcategory}:{subject}")
        ).row(
            InlineKeyboardButton(text="Вернуться◀️", callback_data=make_callback_data(
                level=CURRENT_LEVEL - 1, category=category, subcategory=subcategory,
                subject=subject))
        )

    return markup


async def marathon_keyboard():
    markup = InlineKeyboardMarkup()
    courses = db.get_marathon_courses()
    for i in courses:
        ids, name, price = i[0], i[1], i[2]
        markup.row(InlineKeyboardButton(text=f'{name} | {price}₽', callback_data=f"marathon_{ids}"))

    markup.row(
        InlineKeyboardButton(text="Вернуться◀️",
                             callback_data=make_callback_data(level=1))
    )

    return markup


async def show_marathon_keyboard(user_id, item_id, price):
    markup = InlineKeyboardMarkup()

    callback_data = buy_item_cd.new(user_id=user_id, item_id=f"|{item_id}", price=price)

    markup.row(
        InlineKeyboardButton(text="Купить", callback_data=callback_data)
    )

    markup.row(
        InlineKeyboardButton(text=f'Вернуться◀️', callback_data="marathon")
    )

    markup.row(
        InlineKeyboardButton(text=f'Назад к категориям🚫', callback_data=make_callback_data(level=1))
    )

    return markup


async def subject_keyboard(category, subcategory):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup()
    if subcategory == "2" or subcategory == "8":
        global subjects_oge
        for subject_id, subject_name in subjects_oge.items():
            if subject_name == "ХИМИЯ🧪" and category in ["9"]:
                continue
            else:
                callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category, subcategory=subcategory,
                                                   subject=subject_id)

                markup.row(
                    InlineKeyboardButton(text=subject_name, callback_data=callback_data)
                )
    else:
        global subjects
        for subject_id, subject_name in subjects.items():
            callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category, subcategory=subcategory,
                                               subject=subject_id)

            markup.row(
                InlineKeyboardButton(text=subject_name, callback_data=callback_data)
            )
    markup.row(
        InlineKeyboardButton(text="Вернуться◀️",
                             callback_data=make_callback_data(level=CURRENT_LEVEL - 1, category=category,
                                                              subcategory=subcategory))
    )
    return markup


async def items_keyboard(category, subcategory, subject):
    CURRENT_LEVEL = 4
    markup = InlineKeyboardMarkup()

    items = db.get_items(category, subcategory, subject)
    if not items:
        return False
    for item in items:
        name, price, ids = item[0], item[1], item[2]
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category, subcategory=subcategory,
                                           subject=subject, item=ids)
        markup.row(
            InlineKeyboardButton(text=f'{name} | {price}₽', callback_data=callback_data)
        )
    if subject == '14':
        markup.row(
            InlineKeyboardButton(text="Вернуться◀️", callback_data=make_callback_data(
                level=CURRENT_LEVEL - 2, category=category, subcategory=subcategory))
        )
    else:
        markup.row(
            InlineKeyboardButton(text="Вернуться◀️", callback_data=make_callback_data(
                level=CURRENT_LEVEL - 1, category=category, subcategory=subcategory,
                subject=subject))
        )

    return markup


def item_keyboard(category, subcategory, subject, item, user_id):
    CURRENT_LEVEL = 5
    markup = InlineKeyboardMarkup(row_width=2)

    ids, price = db.get_item_id_price(category, subcategory, subject, item)

    callback_data = buy_item_cd.new(user_id=user_id, item_id=ids, price=price)

    markup.row(
        InlineKeyboardButton(text=f'Купить', callback_data=callback_data)
    )

    markup.row(
        InlineKeyboardButton(text=f'Вернуться◀️', callback_data=make_callback_data(
            level=CURRENT_LEVEL - 1, category=category, subcategory=subcategory, subject=subject, item=item))
    )

    markup.row(
        InlineKeyboardButton(text=f'Назад к категориям🚫', callback_data=make_callback_data(level=1))
    )

    return markup


async def halfyear_courses_keyboard():
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup()
    courses = db.get_halfyear_courses()
    for i in courses:
        ids, name, price = i[0], i[1], i[2]
        markup.row(InlineKeyboardButton(text=f'{name} | {price}₽', callback_data=f"halfyear_course_{ids}"))
    markup.row(
        InlineKeyboardButton(text="Вернуться◀️",
                             callback_data=make_callback_data(level=CURRENT_LEVEL - 1, category="8"))
    )

    return markup


def show_halfyear_course_keyboard(user_id, item_id, price):
    markup = InlineKeyboardMarkup(row_width=2)
    callback_data = buy_item_cd.new(user_id=user_id, item_id=f"*{str(item_id)}", price=price)

    markup.row(
        InlineKeyboardButton(text=f'Купить', callback_data=callback_data)
    )

    markup.row(
        InlineKeyboardButton(text=f'Вернуться◀️', callback_data="halfyear_courses")
    )

    markup.row(
        InlineKeyboardButton(text=f'Назад к категориям🚫', callback_data=make_callback_data(level=1))
    )

    return markup