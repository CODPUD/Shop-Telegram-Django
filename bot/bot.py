from telebot import TeleBot, types
from telebot.apihelper import ApiException

import adapter
import config
from databaser import Databaser as db
from locales import locales


bot = TeleBot(config.bot_token)


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel(call):
    dbw = db()
    lang = dbw.get_user_lang(call.from_user.id)

    text = locales[lang][0].format(call.from_user.first_name)
    key = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    bl = locales[lang][1:6]
    key.add(types.KeyboardButton(bl[0]), types.KeyboardButton(bl[1]),
            types.KeyboardButton(bl[2]), types.KeyboardButton(bl[3]))
    key.row(types.KeyboardButton(bl[4]))
    dbw.set_user_state(call.from_user.id, 0)

    bot.send_message(call.message.chat.id, locales[lang][8], reply_markup=key, parse_mode='MARKDOWN')
    bot.send_message(call.message.chat.id, text, reply_markup=key, parse_mode='MARKDOWN')


@bot.message_handler(commands=['start'])
def start(msg):
    key = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    key.add(types.KeyboardButton('Русский'), types.KeyboardButton('English'), types.KeyboardButton("O'zbek"))
    bot.send_message(msg.chat.id, 'Выберите язык | Select language | Tilni tanlang', reply_markup=key)


@bot.message_handler(regexp="Русский|English|O'zbek")
def start_lang(msg):
    if msg.text == 'Русский':
        lang = 'ru'
    elif msg.text == 'English':
        lang = 'en'
    else:
        lang = 'uz'
    db().try_add_user(msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name, lang)

    text = locales[lang][0].format(msg.from_user.first_name)
    key = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    bl = locales[lang][1:6]
    key.add(types.KeyboardButton(bl[0]), types.KeyboardButton(bl[1]),
            types.KeyboardButton(bl[2]), types.KeyboardButton(bl[3]))
    key.row(types.KeyboardButton(bl[4]))

    bot.send_message(msg.chat.id, text, reply_markup=key, parse_mode='MARKDOWN')


@bot.message_handler(regexp=f'{locales["ru"][5]}|{locales["en"][5]}|{locales["uz"][5]}')
def help(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    bot.send_message(msg.chat.id, locales[lang][6])


@bot.message_handler(regexp=f'{locales["ru"][4]}|{locales["en"][4]}|{locales["uz"][4]}')
def contacts(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    bot.send_message(msg.chat.id, locales[lang][7].format(config.delivery_cost), parse_mode='MARKDOWN')


@bot.message_handler(commands=['promo'])
def promo_start(msg):
    dbw = db()
    if not dbw.is_user_admin(msg.from_user.id):
        return
    text = 'Пришлите картинку с описанием акции'
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton('Отмена', callback_data='cancel'))
    dbw.set_user_state(msg.from_user.id, 'promo start')

    bot.send_message(msg.chat.id, text, reply_markup=key)


@bot.message_handler(content_types=['text', 'photo', 'video', 'document'], func=lambda m: db().get_user_state(m.from_user.id)=='promo start')
def promo_set(msg):
    dbw = db()
    # print(msg)
    if msg.content_type == 'text':
        dbw.set_promo(msg.text, None, None)
    elif msg.content_type == 'photo':
        dbw.set_promo(msg.caption, 'photo', msg.photo[-1].file_id)
    elif msg.content_type == 'video':
        dbw.set_promo(msg.caption, 'video', msg.video.file_id)
    elif msg.content_type == 'document':
        dbw.set_promo(msg.caption, 'document', msg.document.file_id)
    
    dbw.set_user_state(msg.from_user.id, 0)
    bot.send_message(msg.chat.id, 'OK')


@bot.message_handler(regexp=f'{locales["ru"][3]}|{locales["en"][3]}|{locales["uz"][3]}')
def promo(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    bot.send_message(msg.chat.id, locales[lang][9], parse_mode='MARKDOWN')
    caption, media_type, media = dbw.get_promo()
    if media_type is None:
        bot.send_message(msg.chat.id, caption, parse_mode='MARKDOWN')
    elif media_type == 'photo':
        bot.send_photo(msg.chat.id, media, caption)
    elif media_type == 'video':
        bot.send_video(msg.chat.id, media, caption=caption)
    elif media_type == 'document':
        bot.send_document(msg.chat.id, media, caption=caption)


@bot.message_handler(regexp=f'{locales["ru"][11]}|{locales["en"][11]}|{locales["uz"][11]}')
def tostart(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    text = locales[lang][12]
    key = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    bl = locales[lang][1:6]
    key.add(types.KeyboardButton(bl[0]), types.KeyboardButton(bl[1]),
            types.KeyboardButton(bl[2]), types.KeyboardButton(bl[3]))
    key.row(types.KeyboardButton(bl[4]))
    dbw.set_user_state(msg.from_user.id, 0)

    bot.send_message(msg.chat.id, text, reply_markup=key, parse_mode='MARKDOWN')


@bot.message_handler(regexp=f'{locales["ru"][2]}|{locales["en"][2]}|{locales["uz"][2]}')
def cart_start(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    key.add(
        types.KeyboardButton(locales[lang][22]),
        types.KeyboardButton(locales[lang][23]),
        types.KeyboardButton(locales[lang][1]),
        types.KeyboardButton(locales[lang][11])
    )
    bot.send_message(msg.chat.id, locales[lang][18], reply_markup=key)
    cart = adapter.get_user_cart(msg.from_user.id)

    if len(cart) == 0:
        key = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        bl = locales[lang][1:6]
        key.add(types.KeyboardButton(bl[0]), types.KeyboardButton(bl[1]),
                types.KeyboardButton(bl[2]), types.KeyboardButton(bl[3]))
        key.row(types.KeyboardButton(bl[4]))
        dbw.set_user_state(msg.from_user.id, 0)
        bot.send_message(msg.chat.id, locales[lang][24], reply_markup=key)
        return
    
    dbw.set_user_state(msg.from_user.id, 0)

    for c in cart:
        total_price = int(c['price']) * int(c['count'])
        text = f"<b>{c['title']}</b>\n\n{c['count']} {locales[lang][19]} x {c['price']} {locales[lang][20]} - {total_price} {locales[lang][20]} <a href=\"{c['image_url']}\">&#8205;</a>"
        key = types.InlineKeyboardMarkup()
        key.row(
            types.InlineKeyboardButton('➖', callback_data=f'cdec_{c["id"]}'),
            types.InlineKeyboardButton(f"{c['count']} {locales[lang][19]}", callback_data=f'cupdate_{c["id"]}'),
            types.InlineKeyboardButton('➕', callback_data=f'cinc_{c["id"]}')
        )
        key.row(types.InlineKeyboardButton(locales[lang][21], callback_data=f'cdel_{c["id"]}'))
        bot.send_message(msg.chat.id, text, reply_markup=key, parse_mode='HTML')


@bot.callback_query_handler(func=lambda c: c.data.startswith('cdec_'))
def cart_decrease(call):
    dbw = db()
    lang = dbw.get_user_lang(call.from_user.id)
    item = call.data.split('_')[1]
    count = dbw.decrease_from_cart(call.from_user.id, item)
    if count <= 0:
        dbw.del_from_cart(call.from_user.id, item)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        c = adapter.get_user_cart_item(call.from_user.id, item)
        total_price = int(c['price']) * int(c['count'])
        text = f"<b>{c['title']}</b>\n\n{c['count']} {locales[lang][19]} x {c['price']} {locales[lang][20]} - {total_price} {locales[lang][20]} <a href=\"{c['image_url']}\">&#8205;</a>"
        key = types.InlineKeyboardMarkup()
        key.row(
            types.InlineKeyboardButton('➖', callback_data=f'cdec_{item}'),
            types.InlineKeyboardButton(f"{count} {locales[lang][19]}", callback_data=f'cupdate_{item}'),
            types.InlineKeyboardButton('➕', callback_data=f'cinc_{item}')
        )
        key.row(types.InlineKeyboardButton(locales[lang][21], callback_data=f'cdel_{c["id"]}'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=key, parse_mode='HTML')
    bot.answer_callback_query(call.id, locales[lang][26])


@bot.callback_query_handler(func=lambda c: c.data.startswith('cinc_'))
def cart_increase(call):
    dbw = db()
    lang = dbw.get_user_lang(call.from_user.id)
    item = call.data.split('_')[1]
    count = dbw.add_to_cart(call.from_user.id, item)
    c = adapter.get_user_cart_item(call.from_user.id, item)
    total_price = int(c['price']) * int(c['count'])
    text = f"<b>{c['title']}</b>\n\n{c['count']} {locales[lang][19]} x {c['price']} {locales[lang][20]} - {total_price} {locales[lang][20]} <a href=\"{c['image_url']}\">&#8205;</a>"
    key = types.InlineKeyboardMarkup()
    key.row(
        types.InlineKeyboardButton('➖', callback_data=f'cdec_{item}'),
        types.InlineKeyboardButton(f"{count} {locales[lang][19]}", callback_data=f'cupdate_{item}'),
        types.InlineKeyboardButton('➕', callback_data=f'cinc_{item}')
    )
    key.row(types.InlineKeyboardButton(locales[lang][21], callback_data=f'cdel_{c["id"]}'))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=key, parse_mode='HTML')
    bot.answer_callback_query(call.id, locales[lang][17])


@bot.callback_query_handler(func=lambda c: c.data.startswith('cupdate_'))
def cart_update(call):
    dbw = db()
    lang = dbw.get_user_lang(call.from_user.id)
    item = call.data.split('_')[1]
    count = dbw.get_user_cart_item(call.from_user.id, item)
    if count <= 0:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        c = adapter.get_user_cart_item(call.from_user.id, item)
        total_price = int(c['price']) * int(c['count'])
        text = f"<b>{c['title']}</b>\n\n{c['count']} {locales[lang][19]} x {c['price']} {locales[lang][20]} - {total_price} {locales[lang][20]} <a href=\"{c['image_url']}\">&#8205;</a>"
        key = types.InlineKeyboardMarkup()
        key.row(
            types.InlineKeyboardButton('➖', callback_data=f'cdec_{item}'),
            types.InlineKeyboardButton(f"{count} {locales[lang][19]}", callback_data=f'cupdate_{item}'),
            types.InlineKeyboardButton('➕', callback_data=f'cinc_{item}')
        )
        key.row(types.InlineKeyboardButton(locales[lang][21], callback_data=f'cdel_{c["id"]}'))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=key, parse_mode='HTML')
        finally:
            bot.answer_callback_query(call.id, locales[lang][25])


@bot.callback_query_handler(func=lambda c: c.data.startswith('cdel_'))
def cart_delete(call):
    dbw = db()
    lang = dbw.get_user_lang(call.from_user.id)
    item = call.data.split('_')[1]
    dbw.del_from_cart(call.from_user.id, item)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, locales[lang][26])


@bot.message_handler(regexp=f'{locales["ru"][1]}|{locales["en"][1]}|{locales["uz"][1]}|/menu')
def menu_start(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    cats = adapter.get_categories()
    key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    row = []
    for c in cats:
        row.append(types.KeyboardButton(c))
        if len(row) == 2:
            key.add(row[0], row[1])
            row.clear()
    if len(row) > 0:
        key.add(*row)
    key.add(types.KeyboardButton(locales[lang][2]), types.KeyboardButton(locales[lang][11]))
    dbw.set_user_state(msg.from_user.id, 'menu start')
    
    bot.send_message(msg.chat.id, locales[lang][10].format(config.min_order), reply_markup=key, parse_mode='MARKDOWN')


@bot.message_handler(func=lambda m: db().get_user_state(m.from_user.id) == 'menu start')
def menu_cat(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    cat = msg.text
    rests = adapter.get_restaurants(cat)
    key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    row = []
    for c in rests:
        row.append(types.KeyboardButton(c))
        if len(row) == 2:
            key.add(row[0], row[1])
            row.clear()
    if len(row) > 0:
        key.add(*row)
    key.add(types.KeyboardButton(locales[lang][2]), types.KeyboardButton(locales[lang][11]))
    dbw.set_user_state(msg.from_user.id, 'menu category')

    bot.send_message(msg.chat.id, locales[lang][13], reply_markup=key, parse_mode='MARKDOWN')


@bot.message_handler(func=lambda m: db().get_user_state(m.from_user.id) == 'menu category')
def menu_rest(msg):
    # ресторан выбран, нужно выбрать категорию в нем    
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    rest = msg.text
    cats = adapter.get_food_categories(rest)
    key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    row = []
    for c in cats:
        row.append(types.KeyboardButton(c))
        if len(row) == 2:
            key.add(row[0], row[1])
            row.clear()
    if len(row) > 0:
        key.add(*row)
    key.add(types.KeyboardButton(locales[lang][2]), types.KeyboardButton(locales[lang][11]))
    dbw.set_user_state(msg.from_user.id, f'menu restaurant {rest}')

    bot.send_message(msg.chat.id, locales[lang][14], reply_markup=key, parse_mode='MARKDOWN')


@bot.message_handler(func=lambda m: db().get_user_state(m.from_user.id).startswith('menu restaurant'))
def menu_foodcat(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    rest = dbw.get_user_state(msg.from_user.id)[16:]
    foodcat = msg.text
    food = adapter.get_food_in_foodcat(rest, foodcat)
    key = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    key.add(types.KeyboardButton(locales[lang][2]))
    key.add(types.KeyboardButton(locales[lang][1]), types.KeyboardButton(locales[lang][11]))
    bot.send_message(msg.chat.id, msg.text, reply_markup=key)
    for f in food:
        text = f"*{f['title']}*\n{locales[lang][15]}: *{f['price']}*\n\n{f['description']}"
        key = types.InlineKeyboardMarkup()
        btn_text = locales[lang][16]
        key.add(types.InlineKeyboardButton(btn_text, callback_data=f'atc_{f["id"]}'))
        try:
            bot.send_photo(msg.chat.id, f['image_url'], caption=text, parse_mode='MARKDOWN', reply_markup=key)
        except ApiException:
            bot.send_message(msg.chat.id, text, reply_markup=key, parse_mode='MARKDOWN')


@bot.callback_query_handler(func=lambda c: c.data.startswith('atc_'))
def add_to_cart(call):
    dbw = db()
    lang = dbw.get_user_lang(call.from_user.id)
    item = call.data.split('_')[1]
    dbw.add_to_cart(call.from_user.id, item)
    bot.answer_callback_query(call.id, locales[lang][17])


@bot.message_handler(regexp=f'{locales["ru"][23]}|{locales["en"][23]}|{locales["uz"][23]}')
def clear_cart(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    dbw.clear_cart(msg.from_user.id)
    key = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    bl = locales[lang][1:6]
    key.add(types.KeyboardButton(bl[0]), types.KeyboardButton(bl[1]),
            types.KeyboardButton(bl[2]), types.KeyboardButton(bl[3]))
    key.row(types.KeyboardButton(bl[4]))
    dbw.set_user_state(msg.from_user.id, 0)
    bot.send_message(msg.chat.id, locales[lang][24], reply_markup=key)


@bot.message_handler(regexp=f'{locales["ru"][22]}|{locales["en"][22]}|{locales["uz"][22]}')
def order_start(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    total_price = adapter.calculate_total_sum(msg.from_user.id)
    text = locales[lang][28].format(total_price)
    bot.send_message(msg.chat.id, text, parse_mode='MARKDOWN')
    if total_price < config.min_order:
        text = locales[lang][45].format(config.min_order)
        bot.send_message(msg.chat.id, text, parse_mode='MARKDOWN')
        return
    if config.delivery_cost == 0:
        text = locales[lang][29].format(locales[lang][46])
    else:
        text = locales[lang][29].format(f'{config.delivery_cost} {locales[lang][20]}')
    key = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    key.add(
        types.KeyboardButton(locales[lang][34], request_location=True),
        types.KeyboardButton(locales[lang][33]),
        types.KeyboardButton(locales[lang][2]),
        types.KeyboardButton(locales[lang][11])
    )
    text = locales[lang][32]
    dbw.set_user_state(msg.from_user.id, 'order start')
    bot.send_message(msg.chat.id, text, reply_markup=key, parse_mode='MARKDOWN')


@bot.message_handler(regexp=f'{locales["ru"][33]}|{locales["en"][33]}|{locales["uz"][33]}', func=lambda m: db().get_user_state(m.from_user.id) == 'order start')
def order_back(msg):
    cart_start(msg)


@bot.message_handler(func=lambda m: db().get_user_state(m.from_user.id) == 'order start', content_types=['text', 'location'])
def order_location(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    if msg.content_type == 'text':
        dbw.set_user_address_text(msg.from_user.id, msg.text)
    elif msg.content_type == 'location':
        dbw.set_user_address_location(msg.from_user.id, msg.location.latitude, msg.location.longitude)
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(
        types.KeyboardButton(locales[lang][36], request_contact=True),
        types.KeyboardButton(locales[lang][33])
    )
    dbw.set_user_state(msg.from_user.id, 'req phone')
    bot.send_message(msg.chat.id, locales[lang][35], reply_markup=key, parse_mode='MARKDOWN')


@bot.message_handler(regexp=f'{locales["ru"][33]}|{locales["en"][33]}|{locales["uz"][33]}', func=lambda m: db().get_user_state(m.from_user.id) == 'req phone')
def back_from_phone(msg):
    order_start(msg)


@bot.message_handler(func=lambda m: db().get_user_state(m.from_user.id) == 'req phone', content_types=['text', 'contact'])
def order_phone(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    if msg.content_type == 'text':
        dbw.set_user_phone(msg.from_user.id, msg.text)
    elif msg.content_type == 'contact':
        dbw.set_user_phone(msg.from_user.id, msg.contact.phone_number)
    key = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for pm in config.payment_methods:
        key.add(types.KeyboardButton(pm))
    key.add(types.KeyboardButton(locales[lang][33]))
    dbw.set_user_state(msg.from_user.id, 'req way')
    bot.send_message(msg.chat.id, locales[lang][37], reply_markup=key, parse_mode='MARKDOWN')


@bot.message_handler(regexp=f'{locales["ru"][33]}|{locales["en"][33]}|{locales["uz"][33]}', func=lambda m: db().get_user_state(m.from_user.id) == 'req way')
def back_from_way(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(
        types.KeyboardButton(locales[lang][36], request_contact=True),
        types.KeyboardButton(locales[lang][33])
    )
    dbw.set_user_state(msg.from_user.id, 'req phone')
    bot.send_message(msg.chat.id, locales[lang][35], reply_markup=key, parse_mode='MARKDOWN')


def order_text_gen(uid):
    dbw = db()
    lang = dbw.get_user_lang(uid)
    cart = adapter.get_user_cart(uid)
    cart_cost = 0
    text = ''
    for c in cart:
        total_price = int(c['price']) * int(c['count'])
        text += f"{c['title']}\n{c['count']} {locales[lang][19]} \\* {c['price']} {locales[lang][20]} - {total_price} {locales[lang][20]}\n\n"
        cart_cost += total_price
    text += f'{locales[lang][38]}: {cart_cost}\n\n'
    
    if dbw.what_is_provided(uid) == 'address':
        address = dbw.get_address(uid)
        text += f'{locales[lang][39]}: {address}'
    else:
        text += locales[lang][41]
    return text, cart_cost


@bot.message_handler(func=lambda m: db().get_user_state(m.from_user.id) == 'req way' and m.text in config.payment_methods)
def payment_selected(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    way = msg.text
    text = f'*{locales[lang][42]}*\n\n'
    text_add, cart_cost = order_text_gen(msg.from_user.id)
    text += text_add
    cart = adapter.get_user_cart(msg.from_user.id)
    # cart_cost = 0
    # for c in cart:
    #     total_price = int(c['price']) * int(c['count'])
    #     text += f"{c['title']}\n{c['count']} {locales[lang][19]} * {c['price']} {locales[lang][20]} - {total_price} {locales[lang][20]}\n\n"
        # cart_cost += total_price
    # text += f'{locales[lang][38]}: {total_price}\n\n'
    
    # if dbw.what_is_provided(msg.from_user.id) == 'address':
    #     address = dbw.get_address(msg.from_user.id)
    #     text += f'{locales[lang][39]}: {address}'
    # else:
    #     text += locales[lang][41]

    dbw.set_way(msg.from_user.id, way)
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(types.KeyboardButton(locales[lang][33]))
    dbw.set_user_state(msg.from_user.id, 'req payment')
    bot.send_message(msg.chat.id, text, reply_markup=key, parse_mode='MARKDOWN')

    prices = [types.LabeledPrice('Pay', int(cart_cost*100))]
    bot.send_invoice(msg.chat.id, 'Restaurant order', 'Restaurant order', 'order', config.payment_methods[way], 'UZS', prices, msg.from_user.id)


@bot.message_handler(regexp=f'{locales["ru"][33]}|{locales["en"][33]}|{locales["uz"][33]}', func=lambda m: db().get_user_state(m.from_user.id) == 'req payment')
def back_from_payment(msg):
    dbw = db()
    lang = dbw.get_user_lang(msg.from_user.id)
    key = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for pm in config.payment_methods:
        key.add(types.KeyboardButton(pm))
    key.add(types.KeyboardButton(locales[lang][33]))
    dbw.set_user_state(msg.from_user.id, 'req way')
    bot.send_message(msg.chat.id, locales[lang][37], reply_markup=key, parse_mode='MARKDOWN')


@bot.pre_checkout_query_handler(func=None)
def pre_checkout(pc):
    dbw = db()
    lang = dbw.get_user_lang(pc.from_user.id)
    bot.answer_pre_checkout_query(pc.id, True)
    text = locales[lang][43].format(pc.from_user.first_name)
    key = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    bl = locales[lang][1:6]
    key.add(types.KeyboardButton(bl[0]), types.KeyboardButton(bl[1]),
            types.KeyboardButton(bl[2]), types.KeyboardButton(bl[3]))
    key.row(types.KeyboardButton(bl[4]))
    dbw.set_user_state(pc.from_user.id, 0)
    bot.send_message(pc.from_user.id, text, reply_markup=key, parse_mode='MARKDOWN')

    phone = dbw.get_phone(pc.from_user.id)
    order_text = f'Заказ от [{pc.from_user.first_name}](tg://user?id={pc.from_user.id})\ntel: {phone[0]}\n\n'
    text_add, cart_cost = order_text_gen(pc.from_user.id)
    order_text += text_add
    
    lat, lon, addr = None, None, None
    if dbw.what_is_provided(pc.from_user.id) == 'location':
        lat, lon = dbw.get_location(pc.from_user.id)
    else:
        addr = dbw.get_address(pc.from_user.id)
    adapter.add_order_to_api(order_text, cart_cost, lat, lon, addr)

    for u in dbw.get_admin_ids():
        try:
            bot.send_message(u[0], order_text, parse_mode='MARKDOWN')
            if lat is not None:
                bot.send_location(u, lat, lon)
        except ApiException:
            continue
    
    dbw.clear_cart(pc.from_user.id)


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=7200)
