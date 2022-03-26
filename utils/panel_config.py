import json

panel_config = {}

config = {
    'admin_link': {
        'text': 'Страница админа',
        'url': 'https://t.me/UmHelper'
    },
    'Reviews_link': {
        'text': 'Отзывы',
        'url': 'https://t.me/umskulotzivi'
    },
    'Chat_link': {
        'text': 'Чатик',
        'url': 'google.com'
    },
    'Group_link': {
        'text': 'Основная группа',
        'url': 'google.com'
    },
    'Start_message': {
        'text': 'Вас приветствует KrystalShop от @krystal_ka\n\nСпасибо, что решили воспользоваться нашим сервисом. \nОбязательно пишите администратору по всем вопросам.'
    }
}
discount_levels = {
    'Без скидок': [0, 0],
    'Школьник': [850, 5],
    'Студентик': [1400, 10],
    'Магистр': [1700, 15]
}


def update_config():
    with open("utils/config.json", "w") as file:
        json.dump(config, file)


def get_config():
    global panel_config
    with open("utils/config.json", "r") as file:
        data = json.load(file)
        panel_config = data


get_config()
