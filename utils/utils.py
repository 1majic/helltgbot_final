from aiogram.dispatcher.filters.state import State, StatesGroup
from db.init import db


class Item:
    def __init__(self, category, subcategory, subject, name, description, photo=None, price=200, chat_id=0):
        self.category = category
        self.subcategory = subcategory
        self.subject = subject
        self.name = name
        self.description = description
        self.photo = photo
        self.price = price
        self.chat_id = chat_id

    def add_in_db(self):
        if self.photo:
            db.add_item_with_photo(self.category, self.subcategory, self.subject,
                                   self.name, self.description, self.photo, self.price, self.chat_id)
        else:
            db.add_item(self.category, self.subcategory, self.subject,
                        self.name, self.description, self.price, self.chat_id)


class States(StatesGroup):
    DEFAULT_STATE = State()
    PAYMENT_STATE = State()
    COUPONS_STATE = State()


class EDIT_PANEL(StatesGroup):
    CREATE_CATEGORY = State()
    EDIT_START = State()

    ADD_ITEM = State()
    ADD_ITEM_NAME = State()
    ADD_ITEM_DESCRIPTION = State()
    ADD_ITEM_PHOTO = State()
    ADD_ITEM_PRICE = State()
    ADD_ITEM_CHAT_ID = State()
    EDIT_ITEM = State()
    EDIT_ITEM_NAME = State()
    EDIT_ITEM_DESCRIPTION = State()
    EDIT_ITEM_IMAGE = State()
    EDIT_ITEM_PRICE = State()
    EDIT_ITEM_CHAT_ID = State()
    DEL_ITEM = State()

    ADD_CATEGORY_IMAGE = State()
    ADD_SUBCATEGORY_IMAGE = State()
    ADD_SUBJECT_IMAGE = State()

    ADD_HALFYEAR = State()
    ADD_HALFYEAR_IMAGE = State()
    DEL_HALFYEAR = State()

    ADD_SPECIAL_COURSE = State()
    CREATE_SPECIAL_COURSE = State()
    ADD_SPECIAL_COURSE_IMAGE = State()
    DEL_SPECIAL_COURSE = State()

    ADD_FREE_COURSE = State()
    DEL_FREE_COURSE = State()

    EDIT_ADMIN_BTN = State()
    EDIT_ADMIN_BTN_LINK = State()
    EDIT_ADMIN_BTN_TEXT = State()

    EDIT_REVIEWS = State()
    EDIT_REVIEWS_TEXT = State()
    EDIT_REVIEWS_LINK = State()

    EDIT_CHAT = State()
    EDIT_CHAT_TEXT = State()
    EDIT_CHAT_LINK = State()

    EDIT_GROUP = State()
    EDIT_GROUP_TEXT = State()
    EDIT_GROUP_LINK = State()


class BLACKLIST_EDIT(StatesGroup):
    ADD_BLACKLIST = State()
    DEL_BLACKLIST = State()


class COUPONS_EDIT(StatesGroup):
    ADD_COUPON = State()
    DEL_COUPON = State()


class MASS_MESSAGE(StatesGroup):
    SEND_MASS_MESSAGE = State()
    DEL_MASS_MESSAGE = State()


def calculate_personal_discount(discount_levels: dict, sum_of_purchases: int):
    last = []
    for x, y in discount_levels.items():
        if sum_of_purchases >= y[0]:
            last = [x, y[1]]
        else:
            return last
    return last
