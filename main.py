import logging
import os
import telebot
from db_layer import db_access, type_const, states

from telebot import types
from flask import Flask, request

# -------- variables path --------

# если в окуржении есть переменная HEROKU, значит получаем токен из переменной окружения
TOKEN = '578281810:AAEXdtP1g5zm6hSvR59RCl1ef7O3rV68TjY'

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
ADMIN_NIKITA_ID = 450048975
ADMIN_OGANES_ID = 291826906
ADMIN_GERMAN_ID = 410634632

greeting_text = '*Добро пожаловать, модник!*😎🤙🏼\n\nДля того, чтобы опубликовать свой рарный айтем нужно быть ' \
                'подписанным на наш канал!\n\n👉️ *@BrandPlace* 👈️ '


# -------- end of variables path --------

# -------- markups of main path --------

def get_greeting_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row('💰Опубликовать💰')
    markup.row('👀 Очередь на публикацию 👀')
    markup.row('⚡Правила⚡️', '🔥Инструкция для публикации🔥')
    markup.row('🛠Связаться с админами🛠', '💻О разработчике💻')
    markup.resize_keyboard = True
    return markup


def get_types_publishing():
    markup = types.ReplyKeyboardMarkup()
    markup.row('💫Бесплатная публикация💫 (free)')
    markup.row('💵Закреплённый пост💵 (300 руб.)')
    markup.row('💶Пост вне очереди💶 (150 руб.)')
    markup.row('Главное меню📲')
    markup.resize_keyboard = True
    return markup


# -------- end markups of main path --------


# -------- main path --------


@bot.message_handler(func=lambda message: message.text == 'Главное меню📲')
@bot.message_handler(commands=['start'])
def greeting(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Подписаться на топ-канал", url="https://t.me/brandplace")
    keyboard.add(url_button)
    bot.send_message(message.from_user.id, greeting_text, reply_markup=get_greeting_markup(),
                     parse_mode='Markdown')
    bot.send_message(message.from_user.id, '*Давай*, подписывайся, если не сделал',
                     parse_mode='Markdown', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == '🔥Инструкция для публикации🔥')
def manual(message: types.Message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('1️⃣ Создаем nickname')
    markup.row('2️⃣ Инструкция публикации поста')
    markup.row('Главное меню📲')
    markup.resize_keyboard = True
    bot.send_message(message.from_user.id, 'Выбери одну из предложенных кнопок🔘',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '💰Опубликовать💰')
def types_of_publish(message: types.Message):
    required = '🔴*ОБЯЗАТЕЛЬНО* надо создать никнейм. Это нужно для того, чтобы с тобой *смог* связаться ' \
               'покупатель🔴\n\n📝В телеграме заходим в Настройки(Settings) ▶️ Имя пользователя(Username)📝 '
    info = 'Каким способом будем публиковать твой айтем❓'
    username = message.from_user.username
    if username is not None:
        bot.send_message(message.from_user.id, info, reply_markup=get_types_publishing())
    else:
        bot.send_message(message.from_user.id, required, parse_mode='Markdown',
                         reply_markup=get_types_publishing())


@bot.message_handler(func=lambda message: message.text == '💫Бесплатная публикация💫 (free)'
                     or message.text == '💵Закреплённый пост💵 (300 руб.)'
                     or message.text == '💶Пост вне очереди💶 (150 руб.)')
def check_username(message: types.Message):
    username = message.from_user.username
    if username is None:
        bot.send_message(message.from_user.id, '*У тебя не создан USERNAME❌*\nСоздай его и попробуй снова\n'
                                               'инструкция: http://telegra.ph/1-Sozdayom-nickname-03-06',
                         parse_mode='Markdown')
    else:
        user = db_access.get_user(message.from_user.id)
        if user is None:
            db_access.create_user(message.from_user.first_name,
                                  message.from_user.id,
                                  message.from_user.username)
        markup = types.ReplyKeyboardMarkup()
        markup.row('Отмена')
        markup.resize_keyboard = True
        if message.text == '💫Бесплатная публикация💫 (free)':
            text = '💫Бесплатная публикация💫 (free)\n\n(🔥*ЗДЕСЬ НУЖЕН ТОЛЬКО ТЕКСТ. ОДНИМ СООБЩЕНИЕМ*🔥)\n\n' \
                   'Правила для ' \
                   'публикации поста о продаже: \nФорма произвольная, но она должна содержать в себе следующую ' \
                   'информацию: \n\n1️⃣ Полное название предмета\n\n2️⃣ Размер\n\n' \
                   '3️⃣ Состояние (от 1 до 10, где 10 это не ' \
                   'распакованная вещь)\n\n4️⃣ Город, возможность отправки по почте.\n\n5️⃣ Цена '
            bot.send_message(message.from_user.id, text,
                             reply_markup=markup, parse_mode='Markdown')
            db_access.set_user_type_of_post(message.from_user.id, type_const.FREE_PUBLISH)
            db_access.set_user_state(message.from_user.id, states.WRITE_TEXT_FOR_POST)
        elif message.text == '💵Закреплённый пост💵 (300 руб.)':
            text = '💵Закреплённый пост💵 (300 руб.)\n•Висит 24 часа в закрепе•\n\n💡(После редактирования поста, ' \
                   'с тобой свяжется один из администраторов канала)💡\n\n(🔥ЗДЕСЬ НУЖЕН ТОЛЬКО ТЕКСТ. ОДНИМ ' \
                   'СООБЩЕНИЕМ🔥)\n\nПравила для публикации поста о продаже: \nФорма произвольная, но она должна ' \
                   'содержать в себе следующую информацию: \n\n1️⃣ Полное название предмета\n\n2️⃣ Размер\n\n3️⃣ ' \
                   'Состояние (от 1 до 10, где 10 это не распакованная вещь)\n\n4️⃣ Город, возможность отправки по ' \
                   'почте.\n\n5️⃣ Цена '
            bot.send_message(message.from_user.id, text,
                             reply_markup=markup, parse_mode='Markdown')
            db_access.set_user_type_of_post(message.from_user.id, type_const.FIXED_PUBLISH)
            db_access.set_user_state(message.from_user.id, states.WRITE_TEXT_FOR_POST)
        elif message.text == '💶Пост вне очереди💶 (150 руб.)':
            text = '💶Пост вне очереди💶 (150 руб.)\n\n💡(После редактирования поста, с тобой свяжется один из ' \
                   'администраторов канала)💡\n\n(🔥ЗДЕСЬ НУЖЕН ТОЛЬКО ТЕКСТ. ОДНИМ СООБЩЕНИЕМ🔥)\n\nПравила для ' \
                   'публикации поста о продаже: \nФорма произвольная, но она должна содержать в себе следующую ' \
                   'информацию: \n\n1️⃣ Полное название предмета\n\n2️⃣ Размер\n\n3️⃣ Состояние (от 1 до 10, ' \
                   'где 10 это не распакованная вещь)\n\n4️⃣ Город, возможность отправки по почте.\n\n5️⃣ Цена '
            bot.send_message(message.from_user.id, text,
                             reply_markup=markup, parse_mode='Markdown')
            db_access.set_user_type_of_post(message.from_user.id, type_const.OUT_OF_TURN_PUBLISH)
            db_access.set_user_state(message.from_user.id, states.WRITE_TEXT_FOR_POST)


def send_info_to_admins(text: str):
    bot.send_message(ADMIN_OGANES_ID, text, parse_mode='Markdown')
    bot.send_message(ADMIN_GERMAN_ID, text, parse_mode='Markdown', disable_notification=True)
    bot.send_message(ADMIN_NIKITA_ID, text, parse_mode='Markdown')


@bot.message_handler(content_types=['photo', 'text'], func=lambda message: db_access.get_user_state(message.from_user.id) == states.WRITE_TEXT_FOR_POST)
def reg_production(message: types.Message):
    if message.content_type == 'text' and not message.text == 'Отмена':
        post = db_access.get_post_by_text(message.text)
        count_text = len(message.text)
        if post is None and count_text > 10:
            type_of = db_access.get_user_type_of_post(message.from_user.id)
            result = db_access.create_post(type_of, message.text, '', message.from_user.id)
            if result:
                markup = types.ReplyKeyboardMarkup()
                markup.row('Отмена')
                markup.resize_keyboard = True
                bot.send_message(message.from_user.id, 'Такс😌, супер, теперь отправь несколько фото📷,'
                                                       ' *но по одному* 1️⃣',
                                 parse_mode='Markdown', reply_markup=markup)
                db_access.set_user_state(message.from_user.id, states.ADD_PHOTO)
            else:
                bot.send_message(message.from_user.id, 'Упс 🙄, что-то пошло не так😒')
        else:
            bot.send_message(message.from_user.id, 'Такс, такс, в твоем описании товара слишком *мало символов* 😏'
                                                   ' или такое описание *уже существует* 🙄',
                             parse_mode='Markdown')
            bot.send_message(message.from_user.id, 'Пришли текст еще раз 👉')
    elif message.text == 'Отмена':
        db_access.set_user_state(message.from_user.id, states.NONE_STATE)
        bot.send_message(message.from_user.id, 'Публикация отменена❌', reply_markup=get_greeting_markup())
    else:
        bot.send_message(message.from_user.id, 'Ну слушай, первым отправляем текст о товаре, фотки чутка позже 😉')


@bot.message_handler(content_types=['photo', 'text'],
                     func=lambda message: db_access.get_user_state(message.from_user.id) == states.ADD_PHOTO)
def add_photo(message: types.Message):
    post = db_access.get_latest_post(message.from_user.id)
    markup = types.ReplyKeyboardMarkup()
    markup.row('Закончить добавление фото')
    markup.row('Отмена')
    markup.resize_keyboard = True
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        link = db_access.upload_photo(file)
        post.links_of_photos += ' {link}'.format(link=link)
        post.save()
        bot.send_message(message.from_user.id, 'Если есть еще фото - присылай👉',
                         reply_markup=markup)
    elif message.text == 'Закончить добавление фото':
        queue = post.queue
        text = 'Создан отложенный пост в канал «BrandPlace» @brandplace\n\n*Твое место в общей очереди на ' \
               'публикацию: {n}*\n\n💶Постов вне очереди💶: *{p1}*\n💵Закреплённых постов💵: *{p2}*\n\nСпасибо, ' \
               'что воспользовались нашей площадкой🤙🏼'
        fxc = db_access.get_all_fixed_post().count()
        outc = db_access.get_all_out_of_turn_post().count()
        bot.send_message(message.from_user.id, text.format(n=queue, p1=outc, p2=fxc),
                         parse_mode='Markdown', reply_markup=get_greeting_markup())
        type_str = 'бесплатный'
        if post.type_of == type_const.FIXED_PUBLISH:
            type_str = '💵*Закреплённый*💵'
        elif post.type_of == type_const.OUT_OF_TURN_PUBLISH:
            type_str = '💶*внеочередной*💶'
        send_info_to_admins('Успешно добавлен {t} пост №{q} в очередь'.format(q=str(post.queue),
                                                                              t=type_str))
        db_access.set_user_state(message.from_user.id, states.NONE_STATE)
    elif message.text == 'Отмена':
        result = db_access.delete_latest_post(message.from_user.id)
        if result:
            bot.send_message(message.from_user.id, 'Публикация отменена❌', reply_markup=get_greeting_markup())
            db_access.set_user_state(message.from_user.id, states.NONE_STATE)
    else:
        bot.send_message(message.from_user.id, 'Сейчас нужны *только фотографии*, присылай их '
                                               'по очереди или нажми кнопку📲',
                         parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '👀 Очередь на публикацию 👀')
def queue_of_post(message: types.Message):
    all_posts = db_access.get_all_posts().count()
    fixed_post = db_access.get_all_fixed_post().count()
    oof_post = db_access.get_all_out_of_turn_post().count()
    text = 'Так, вот сводка по очереди на публикацию ✅ \n\n' \
           'Общее количество постов на публикацию 👉 *{cp1}*\n' \
           '💶Постов вне очереди💶 👉 *{cp2}*\n' \
           '💵Закреплённых постов💵 👉 *{cp3}*'.format(cp1=all_posts, cp2=oof_post, cp3=fixed_post)

    bot.send_message(message.from_user.id, text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == '1️⃣ Создаем nickname')
def manual_create_nickname(message: types.Message):
    bot.send_message(message.from_user.id, 'http://telegra.ph/1-Sozdayom-nickname-03-06')


@bot.message_handler(func=lambda message: message.text == '2️⃣ Инструкция публикации поста')
def manual_create_post(message: types.Message):
    bot.send_message(message.from_user.id, 'http://telegra.ph/2-Kak-vylozhitnajti-shmot-03-06')


@bot.message_handler(func=lambda message: message.text == '⚡Правила⚡️')
def rules(message: types.Message):
    rule = '*Дорогие* подписчики и гости канала, спешим донести до вас правила нашей торговой площадки.\nВ целях ' \
           'сохранения актуальности информации, каждый пост будет выходить с интервалом в 1 час, в порядке очереди. ' \
           '*Для того, чтобы опубликовать пост с вашим айтемом*, нужно перейти в главное меню бота и нажать на кнопку ' \
           '\n«💰Опубликовать💰»\n\n❌За попытку продажи/продажу не оригинального предмета - выдаётся *бан*.❌ '
    bot.send_message(message.from_user.id, rule, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == '💻О разработчике💻')
def about_developer(message: types.Message):
    about_me = 'German Nikolishin\n\nPython and .NET developer👨‍💻\nTelegram👉 @german_nikolishin\nGitHub👉 ' \
               'https://github.com/SkymanOne\nVK👉 https://vk.com/german_it\nInst👉 ' \
               'https://www.instagram.com/german.nikolishin/\nTelegram Channel👉 https://t.me/VneUrokaDev '
    keyboard = types.InlineKeyboardMarkup()
    telegram_button = types.InlineKeyboardButton('🔷 Telegram Profile 🔷', url='t.me/german_nikolishin')
    vk_button = types.InlineKeyboardButton('🔷 VK 🔷', url='https://vk.com/german_it')
    inst_button = types.InlineKeyboardButton('🔶 Inst 🔶', url='https://www.instagram.com/german.nikolishin/')
    github_button = types.InlineKeyboardButton('⚡️ GitHub ⚡️', url='https://github.com/SkymanOne')
    channel_button = types.InlineKeyboardButton('💠 Telegram Channel 💠', url='https://t.me/SkyMenDev')
    keyboard.add(github_button, vk_button, inst_button, telegram_button, channel_button)
    bot.send_message(message.from_user.id, about_me, reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == '🛠Связаться с админами🛠')
def connect_to_admins(message: types.Message):
    info = '❓Если возникли какие-то вопросы, то их можно задать одному из администраторов канала❓\n\n📲 @ogan3s\n\n📲 ' \
           '@code1n '
    bot.send_message(message.from_user.id, info)


# -------- end of main path --------


# -------- admin path --------


def get_admin_panel_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row('✅ Следующая публикация 👉')
    markup.row('✅ Следующая закрепленная публикация 👉')
    markup.row('✅ Следующая публикация вне очереди 👉')
    return markup


def parse_links(string: str):
    list_of_links = map(str, string.split())
    return list_of_links


@bot.message_handler(commands=['admin'])
def admin_greeting(message: types.Message):
    if message.from_user.id == ADMIN_NIKITA_ID or \
            message.from_user.id == ADMIN_OGANES_ID or \
            message.from_user.id == ADMIN_GERMAN_ID:
        bot.send_message(message.from_user.id, 'Приветствую тебя, мой *повелитель* 🙌\n\nТы находишься в админ-панеле '
                                               'бота *BrandBot*\n\nP.S. Функционал еще будет расширяться😏',
                         parse_mode='Markdown', reply_markup=get_admin_panel_markup())
    else:
        bot.send_message(message.from_user.id, 'Прости😒, у тебя *недостаточно прав* для этой команды',
                         parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == '✅ Следующая публикация 👉'
                     and (message.from_user.id == ADMIN_NIKITA_ID or
                          message.from_user.id == ADMIN_OGANES_ID or
                          message.from_user.id == ADMIN_GERMAN_ID))
def get_next_publication(message: types.Message):
    post = db_access.get_post()
    if post is not None:
        type_of_post = 'Бесплатная публикация'
        if post.type_of == type_const.FIXED_PUBLISH:
            type_of_post = 'Закрепленный пост'
        elif post.type_of == type_const.OUT_OF_TURN_PUBLISH:
            type_of_post = 'Пост вне очереди'
        info = '⚡️ Публикация товара от 👉 {name}\n' \
               '⚡️ username 👉 *{username}*\n' \
               '⚡️ ссылка на профиль 👉 [http://t.me/{username}](http://t.me/{username})\n' \
               '⚡️ Тип поста 👉 *{type}*\n'\
            .format(name=post.seller.name, username=post.seller.nickname, type=type_of_post)
        bot.send_message(message.from_user.id, info, reply_markup=types.ReplyKeyboardRemove(),
                         parse_mode='Markdown')
        bot.send_message(message.from_user.id, 'Текст 👉')
        bot.send_message(message.from_user.id, post.text)
        bot.send_message(message.from_user.id, 'Фото товара 👉')
        list_of_links = parse_links(post.links_of_photos)
        n = 1
        for l in list_of_links:
            bot.send_message(message.from_user.id,
                             '<a href="{link}">Вот фотка №{n}</a>'.format(link=l, n=n),
                             parse_mode='HTML')
            n += 1
        bot.send_message(message.from_user.id, '🙌Всё🙌', reply_markup=get_admin_panel_markup())
        db_access.delete_post_from_queue()
    else:
        bot.send_message(message.from_user.id, 'Постов на публикацию нет 🙄')


@bot.message_handler(func=lambda message: message.text == '✅ Следующая закрепленная публикация 👉'
                     and (message.from_user.id == ADMIN_NIKITA_ID or
                          message.from_user.id == ADMIN_OGANES_ID or
                          message.from_user.id == ADMIN_GERMAN_ID))
def get_next_fixed_publication(message: types.Message):
    post = db_access.get_fixed_post()
    if post is not None:
        type_of_post = 'Закрепленный пост'
        info = '⚡️ Публикация товара от 👉 {name}\n' \
               '⚡️ username 👉 *{username}*\n' \
               '⚡️ ссылка на профиль 👉 [http://t.me/{username}](http://t.me/{username})\n' \
               '⚡️ Тип поста 👉 *{type}*\n'\
            .format(name=post.seller.name, username=post.seller.nickname, type=type_of_post)
        bot.send_message(message.from_user.id, info, reply_markup=types.ReplyKeyboardRemove(),
                         parse_mode='Markdown')
        bot.send_message(message.from_user.id, 'Текст 👉')
        bot.send_message(message.from_user.id, post.text)
        bot.send_message(message.from_user.id, 'Фото товара 👉')
        list_of_links = parse_links(post.links_of_photos)
        n = 1
        for l in list_of_links:
            bot.send_message(message.from_user.id,
                             '<a href="{link}">Вот фотка №{n}</a>'.format(link=l, n=n),
                             parse_mode='HTML')
            n += 1
        bot.send_message(message.from_user.id, '🙌Всё🙌', reply_markup=get_admin_panel_markup())
        db_access.delete_fixed_post()
    else:
        bot.send_message(message.from_user.id, 'Постов на публикацию нет 🙄')


@bot.message_handler(func=lambda message: message.text == '✅ Следующая публикация вне очереди 👉'
                     and (message.from_user.id == ADMIN_NIKITA_ID or
                          message.from_user.id == ADMIN_OGANES_ID or
                          message.from_user.id == ADMIN_GERMAN_ID))
def get_next_fixed_publication(message: types.Message):
    post = db_access.get_out_of_turn_post()
    if post is not None:
        type_of_post = 'Пост вне очереди'
        info = '⚡️ Публикация товара от 👉 {name}\n' \
               '⚡️ username 👉 *{username}*\n' \
               '⚡️ ссылка на профиль 👉 [http://t.me/{username}](http://t.me/{username})\n' \
               '⚡️ Тип поста 👉 *{type}*\n'\
            .format(name=post.seller.name, username=post.seller.nickname, type=type_of_post)
        bot.send_message(message.from_user.id, info, reply_markup=types.ReplyKeyboardRemove(),
                         parse_mode='Markdown')
        bot.send_message(message.from_user.id, 'Текст 👉')
        bot.send_message(message.from_user.id, post.text)
        bot.send_message(message.from_user.id, 'Фото товара 👉')
        list_of_links = parse_links(post.links_of_photos)
        n = 1
        for l in list_of_links:
            bot.send_message(message.from_user.id,
                             '<a href="{link}">Вот фотка №{n}</a>'.format(link=l, n=n),
                             parse_mode='HTML')
            n += 1
        bot.send_message(message.from_user.id, '🙌Всё🙌', reply_markup=get_admin_panel_markup())
        db_access.delete_out_of_turn_post()
    else:
        bot.send_message(message.from_user.id, 'Постов на публикацию нет 🙄')


# если в окуржении есть переменная HEROKU, значит поднимаем сервер
# иначе запускаем прослушку
if 'HEROKU' in list(os.environ.keys()):
    @server.route('/' + TOKEN, methods=['POST'])
    def get_message():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


    @server.route('/')
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://brand-bot.herokuapp.com/' + TOKEN)
        return '!', 200


    if __name__ == '__main__':
        db_access.init_db()
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
else:
    bot.remove_webhook()
    bot.polling(True)
