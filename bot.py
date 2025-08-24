# -*- coding: utf-8 -*-

import logging
import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command

products = {}
product_id_counter = 1
user_states = {}  

API_TOKEN = '8202462879:AAFZHeY6WdPtejpz5eFp8Er4GpcMfnHfM8g' # Замените на ваш токен бота
ADMIN_IDS =  [8349596696] # Список Telegram ID админов

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- Мультиязычность ---
LANGUAGES = {
    "ru": {
        "main_menu": "🏠 Главное меню",
        "catalog": "🛍 Каталог",
        "my_purchases": "🧾 Мои покупки",
        "admin_panel": "⚙️ Админ-панель",
        "add_product": "➕ Добавить товар",
        "edit_price": "✏️ Изменить цену",
        "delete_product": "🗑 Удалить товар",
        "back": "⬅️ Назад",
        "add_more": "➕ Добавить ещё товар",
        "to_main": "🏠 В главное меню",
        "choose_lang": "🇷🇺 Выберите язык / 🇬🇧 Choose language",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "welcome": "👋 Добро пожаловать в магазин цифровых товаров!",
        "catalog_empty": "Каталог пуст.",
        "choose_category": "Выберите категорию:",
        "category_empty": "В этой категории нет товаров.",
        "choose_or_create_category": "Выберите категорию или создайте новую:",
        "new_category": "➕ Новая категория",
        "enter_new_category": "Введите название новой категории:",
        "enter_product_name": "Введите название товара:",
        "enter_product_desc": "Введите краткое описание товара:",
        "choose_currency": "Выберите валюту товара:",
        "enter_price": "Введите цену товара (только число):",
        "enter_content": "Введите цифровой контент (например, ключ, ссылку и т.д.):",
        "enter_pay_url": "Введите ссылку на оплату (например, ЮMoney, Qiwi, PayPal):",
        "product_added": "Товар '{name}' добавлен в каталог!\n\nЧто вы хотите сделать дальше?",
        "access_denied": "Доступ запрещён.",
        "no_products_edit": "Нет товаров для изменения.",
        "choose_product_edit": "Выберите товар для изменения цены:",
        "enter_new_price": "Введите новую цену для товара '{name}':",
        "price_changed": "Цена товара '{name}' изменена на {price} {currency}.",
        "no_products_delete": "Нет товаров для удаления.",
        "choose_product_delete": "Выберите товар для удаления:",
        "product_deleted": "Товар '{name}' удалён.",
        "buy": "Купить: {name}",
        "buy_info": "Для покупки товара <b>{name}</b> ({desc}) оплатите {price} {currency} по ссылке:\n{pay_url}\n\nПосле оплаты пришлите сюда скриншот чека или номер транзакции.",
        "check_sent": "Чек отправлен на проверку админу. Ожидайте подтверждения.",
        "not_found": "Товар не найден.",
        "not_bought": "Вы не совершали покупку. Для покупки выберите товар в каталоге.",
        "approve": "✅ Подтвердить",
        "decline": "❌ Отклонить",
        "payment_approved": "✅ Оплата подтверждена администратором!\nВот ваш товар:\n\n<code>{content}</code>",
        "payment_declined": "❌ Оплата не подтверждена администратором. Если вы считаете это ошибкой, свяжитесь с поддержкой.",
        "your_purchases": "🧾 <b>Ваши покупки:</b>\n\n",
        "no_purchases": "У вас нет покупок.",
        "enter_number": "Введите корректное число.",
        "main": "Главное меню",
        "admin_payment_check": "Поступил чек на оплату!\nПользователь: @{username}\nТовар: {name} ({desc})\nЦена: {price} {currency}\nUser ID: {user_id}",
        "admin_payment_approved": "✅ Оплата подтверждена. Товар выдан.",
        "admin_payment_declined": "❌ Оплата отклонена.",
        "price": "Цена"
    },
    "en": {
        "main_menu": "🏠 Main menu",
        "catalog": "🛍 Catalog",
        "my_purchases": "🧾 My purchases",
        "admin_panel": "⚙️ Admin panel",
        "add_product": "➕ Add product",
        "edit_price": "✏️ Edit price",
        "delete_product": "🗑 Delete product",
        "back": "⬅️ Back",
        "add_more": "➕ Add more product",
        "to_main": "🏠 To main menu",
        "choose_lang": "🇷🇺 Выберите язык / 🇬🇧 Choose language",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "welcome": "👋 Welcome to the digital goods shop!",
        "catalog_empty": "Catalog is empty.",
        "choose_category": "Choose a category:",
        "category_empty": "No products in this category.",
        "choose_or_create_category": "Choose a category or create a new one:",
        "new_category": "➕ New category",
        "enter_new_category": "Enter new category name:",
        "enter_product_name": "Enter product name:",
        "enter_product_desc": "Enter short product description:",
        "choose_currency": "Choose product currency:",
        "enter_price": "Enter product price (numbers only):",
        "enter_content": "Enter digital content (e.g. key, link, etc.):",
        "enter_pay_url": "Enter payment link (e.g. PayPal, Stripe, etc.):",
        "product_added": "Product '{name}' added to catalog!\n\nWhat do you want to do next?",
        "access_denied": "Access denied.",
        "no_products_edit": "No products to edit.",
        "choose_product_edit": "Choose product to edit price:",
        "enter_new_price": "Enter new price for '{name}':",
        "price_changed": "Price for '{name}' changed to {price} {currency}.",
        "no_products_delete": "No products to delete.",
        "choose_product_delete": "Choose product to delete:",
        "product_deleted": "Product '{name}' deleted.",
        "buy": "Buy: {name}",
        "buy_info": "To buy <b>{name}</b> ({desc}) pay {price} {currency} via:\n{pay_url}\n\nAfter payment send a screenshot or transaction number here.",
        "check_sent": "Receipt sent to admin for review. Please wait for confirmation.",
        "not_found": "Product not found.",
        "not_bought": "You have not made a purchase. Please select a product in the catalog.",
        "approve": "✅ Approve",
        "decline": "❌ Decline",
        "payment_approved": "✅ Payment confirmed by admin!\nHere is your product:\n\n<code>{content}</code>",
        "payment_declined": "❌ Payment not confirmed by admin. If you think this is a mistake, contact support.",
        "your_purchases": "🧾 <b>Your purchases:</b>\n\n",
        "no_purchases": "You have no purchases.",
        "enter_number": "Enter a valid number.",
        "main": "Main menu",
        "admin_payment_check": "Payment receipt received!\nUser: @{username}\nProduct: {name} ({desc})\nPrice: {price} {currency}\nUser ID: {user_id}",
        "admin_payment_approved": "✅ Payment confirmed. Product delivered.",
        "admin_payment_declined": "❌ Payment declined.",
        "price": "Price"
    }
}

def get_lang(user_id):
    return user_states.get(user_id, {}).get("lang", "ru")

def t(user_id, key, **kwargs):
    lang = get_lang(user_id)
    return LANGUAGES[lang][key].format(**kwargs)

def main_keyboard(user_id):
    lang = get_lang(user_id)
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text=LANGUAGES[lang]["catalog"])],
        [KeyboardButton(text=LANGUAGES[lang]["my_purchases"])],
        [KeyboardButton(text=LANGUAGES[lang]["admin_panel"])]
    ])

def admin_keyboard(user_id):
    lang = get_lang(user_id)
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text=LANGUAGES[lang]["add_product"])],
        [KeyboardButton(text=LANGUAGES[lang]["edit_price"])],
        [KeyboardButton(text=LANGUAGES[lang]["delete_product"])],
        [KeyboardButton(text=LANGUAGES[lang]["back"])]
    ])

def currency_keyboard(user_id):
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
        [KeyboardButton(text="RUB"), KeyboardButton(text="USD"), KeyboardButton(text="EUR")]
    ])

def add_done_keyboard(user_id):
    lang = get_lang(user_id)
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text=LANGUAGES[lang]["add_more"]), KeyboardButton(text=LANGUAGES[lang]["to_main"])]
    ])

def get_categories():
    return sorted(set(prod["category"] for prod in products.values() if "category" in prod))

def get_category_kb(user_id):
    cats = get_categories()
    lang = get_lang(user_id)
    keyboard = [[KeyboardButton(text=cat)] for cat in cats]
    keyboard.append([KeyboardButton(text=LANGUAGES[lang]["new_category"])])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

@router.message(Command("start"))
async def start(msg: types.Message):
    user_states[msg.from_user.id] = {"lang": "ru"}
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text=LANGUAGES["ru"]["lang_ru"]), KeyboardButton(text=LANGUAGES["en"]["lang_en"])]
    ])
    await msg.answer(LANGUAGES["ru"]["choose_lang"], reply_markup=kb)

@router.message(lambda m: m.text in [LANGUAGES["ru"]["lang_ru"], LANGUAGES["en"]["lang_en"]])
async def set_language(msg: types.Message):
    if msg.from_user.id not in user_states:
        user_states[msg.from_user.id] = {}
    if msg.text == LANGUAGES["ru"]["lang_ru"]:
        user_states[msg.from_user.id]["lang"] = "ru"
    else:
        user_states[msg.from_user.id]["lang"] = "en"
    await msg.answer(t(msg.from_user.id, "welcome"), reply_markup=main_keyboard(msg.from_user.id))

@router.message(lambda m: m.text in [LANGUAGES["ru"]["catalog"], LANGUAGES["en"]["catalog"]])
async def show_categories(msg: types.Message):
    cats = get_categories()
    if not cats:
        await msg.answer(t(msg.from_user.id, "catalog_empty"))
        return
    lang = get_lang(msg.from_user.id)
    keyboard = [
        [InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}")]
        for cat in cats
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await msg.answer(t(msg.from_user.id, "choose_category"), reply_markup=kb)

@router.callback_query(F.data.startswith("cat_"))
async def show_catalog(call: types.CallbackQuery):
    cat = call.data[4:]
    items = [ (pid, prod) for pid, prod in products.items() if prod["category"] == cat ]
    if not items:
        await call.message.answer(t(call.from_user.id, "category_empty"))
        await call.answer()
        return
    text = f"🛒 <b>{cat}</b>\n\n"
    lang = get_lang(call.from_user.id)
    price_word = LANGUAGES[lang]["price"]
    keyboard = [
        [InlineKeyboardButton(text=t(call.from_user.id, "buy", name=prod['name']), callback_data=f"buy_{pid}")]
        for pid, prod in items
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    for pid, prod in items:
        text += (
            f"🔹 <b>{prod['name']}</b>\n"
            f"📝 {prod['desc']}\n"
            f"💵 <b>{price_word}:</b> {prod['price']} {prod['currency']}\n\n"
        )
    await call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()

@router.message(lambda m: m.text in [LANGUAGES["ru"]["admin_panel"], LANGUAGES["en"]["admin_panel"]])
async def admin_panel(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer(t(msg.from_user.id, "access_denied"))
        return
    await msg.answer(t(msg.from_user.id, "admin_panel"), reply_markup=admin_keyboard(msg.from_user.id))

@router.message(lambda m: m.text in [LANGUAGES["ru"]["add_product"], LANGUAGES["en"]["add_product"]])
async def add_product_start(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer(t(msg.from_user.id, "access_denied"))
        return
    user_states[msg.from_user.id]["step"] = "category"
    await msg.answer(t(msg.from_user.id, "choose_or_create_category"), reply_markup=get_category_kb(msg.from_user.id))

@router.message(lambda m: m.from_user.id in ADMIN_IDS and user_states.get(m.from_user.id, {}).get("step") == "category")
async def add_product_category(msg: types.Message):
    lang = get_lang(msg.from_user.id)
    if msg.text == LANGUAGES[lang]["new_category"]:
        user_states[msg.from_user.id]["step"] = "new_category"
        await msg.answer(t(msg.from_user.id, "enter_new_category"), reply_markup=types.ReplyKeyboardRemove())
        return
    cats = get_categories()
    if msg.text not in cats:
        await msg.answer(t(msg.from_user.id, "choose_or_create_category"), reply_markup=get_category_kb(msg.from_user.id))
        return
    user_states[msg.from_user.id]["category"] = msg.text
    user_states[msg.from_user.id]["step"] = "name"
    await msg.answer(t(msg.from_user.id, "enter_product_name"), reply_markup=types.ReplyKeyboardRemove())

@router.message(lambda m: m.from_user.id in ADMIN_IDS and user_states.get(m.from_user.id, {}).get("step") == "new_category")
async def add_product_new_category(msg: types.Message):
    user_states[msg.from_user.id]["category"] = msg.text
    user_states[msg.from_user.id]["step"] = "name"
    await msg.answer(t(msg.from_user.id, "enter_product_name"))

@router.message(lambda m: m.from_user.id in ADMIN_IDS and user_states.get(m.from_user.id, {}).get("step") == "name")
async def add_product_name(msg: types.Message):
    user_states[msg.from_user.id]["name"] = msg.text
    user_states[msg.from_user.id]["step"] = "desc"
    await msg.answer(t(msg.from_user.id, "enter_product_desc"))

@router.message(lambda m: m.from_user.id in ADMIN_IDS and user_states.get(m.from_user.id, {}).get("step") == "desc")
async def add_product_desc(msg: types.Message):
    user_states[msg.from_user.id]["desc"] = msg.text
    user_states[msg.from_user.id]["step"] = "currency"
    await msg.answer(t(msg.from_user.id, "choose_currency"), reply_markup=currency_keyboard(msg.from_user.id))

@router.message(lambda m: m.from_user.id in ADMIN_IDS and user_states.get(m.from_user.id, {}).get("step") == "currency")
async def add_product_currency(msg: types.Message):
    currency = msg.text.upper()
    if currency not in ["RUB", "USD", "EUR"]:
        await msg.answer(t(msg.from_user.id, "choose_currency"), reply_markup=currency_keyboard(msg.from_user.id))
        return
    user_states[msg.from_user.id]["currency"] = currency
    user_states[msg.from_user.id]["step"] = "price"
    await msg.answer(t(msg.from_user.id, "enter_price"), reply_markup=types.ReplyKeyboardRemove())

@router.message(lambda m: m.from_user.id in ADMIN_IDS and user_states.get(m.from_user.id, {}).get("step") == "price")
async def add_product_price(msg: types.Message):
    try:
        price = int(msg.text)
        user_states[msg.from_user.id]["price"] = price
        user_states[msg.from_user.id]["step"] = "content"
        await msg.answer(t(msg.from_user.id, "enter_content"))
    except ValueError:
        await msg.answer(t(msg.from_user.id, "enter_number"))

@router.message(lambda m: m.from_user.id in ADMIN_IDS and user_states.get(m.from_user.id, {}).get("step") == "content")
async def add_product_content(msg: types.Message):
    user_states[msg.from_user.id]["content"] = msg.text
    user_states[msg.from_user.id]["step"] = "pay_url"
    await msg.answer(t(msg.from_user.id, "enter_pay_url"))

@router.message(lambda m: m.from_user.id in ADMIN_IDS and user_states.get(m.from_user.id, {}).get("step") == "pay_url")
async def add_product_pay_url(msg: types.Message):
    global product_id_counter
    state = user_states[msg.from_user.id]
    products[product_id_counter] = {
        "name": state["name"],
        "desc": state["desc"],
        "price": state["price"],
        "currency": state["currency"],
        "content": state["content"],
        "pay_url": msg.text,
        "category": state["category"]
    }
    save_products()
    await msg.answer(
        t(msg.from_user.id, "product_added", name=state["name"]),
        reply_markup=add_done_keyboard(msg.from_user.id)
    )
    product_id_counter += 1
    # Очищаем только временные поля, язык не трогаем!
    lang = user_states[msg.from_user.id].get("lang", "ru")
    user_states[msg.from_user.id] = {"lang": lang}

@router.message(lambda m: m.text in [LANGUAGES["ru"]["add_more"], LANGUAGES["en"]["add_more"]])
async def add_product_start_more(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer(t(msg.from_user.id, "access_denied"))
        return
    user_states[msg.from_user.id]["step"] = "category"
    await msg.answer(t(msg.from_user.id, "choose_or_create_category"), reply_markup=get_category_kb(msg.from_user.id))

@router.message(lambda m: m.text in [LANGUAGES["ru"]["to_main"], LANGUAGES["en"]["to_main"]])
async def back_to_main(msg: types.Message):
    await msg.answer(t(msg.from_user.id, "main"), reply_markup=main_keyboard(msg.from_user.id))

@router.message(lambda m: m.text in [LANGUAGES["ru"]["back"], LANGUAGES["en"]["back"]])
async def back(msg: types.Message):
    await msg.answer(t(msg.from_user.id, "main"), reply_markup=main_keyboard(msg.from_user.id))

# --- Изменение цены товара ---
@router.message(lambda m: m.text in [LANGUAGES["ru"]["edit_price"], LANGUAGES["en"]["edit_price"]])
async def change_price_start(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer(t(msg.from_user.id, "access_denied"))
        return
    if not products:
        await msg.answer(t(msg.from_user.id, "no_products_edit"))
        return
    keyboard = [
        [InlineKeyboardButton(text=f"{prod['name']} ({prod['category']})", callback_data=f"editprice_{pid}")]
        for pid, prod in products.items()
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await msg.answer(t(msg.from_user.id, "choose_product_edit"), reply_markup=kb)

@router.callback_query(F.data.startswith("editprice_"))
async def change_price_choose(call: types.CallbackQuery):
    pid = int(call.data.split("_")[1])
    prod = products.get(pid)
    if not prod:
        await call.answer(t(call.from_user.id, "not_found"), show_alert=True)
        return
    user_states[call.from_user.id] = {"step": "edit_price", "pid": pid, "lang": get_lang(call.from_user.id)}
    await call.message.answer(t(call.from_user.id, "enter_new_price", name=prod['name']))
    await call.answer()

@router.message(lambda m: m.from_user.id in ADMIN_IDS and user_states.get(m.from_user.id, {}).get("step") == "edit_price")
async def change_price_set(msg: types.Message):
    try:
        price = int(msg.text)
        pid = user_states[msg.from_user.id]["pid"]
        products[pid]["price"] = price
        save_products()
        await msg.answer(
            t(msg.from_user.id, "price_changed", name=products[pid]['name'], price=price, currency=products[pid]['currency']),
            reply_markup=admin_keyboard(msg.from_user.id)
        )
        lang = user_states[msg.from_user.id].get("lang", "ru")
        user_states[msg.from_user.id] = {"lang": lang}
    except Exception:
        await msg.answer(t(msg.from_user.id, "enter_number"))

# --- Удаление товара ---
@router.message(lambda m: m.text in [LANGUAGES["ru"]["delete_product"], LANGUAGES["en"]["delete_product"]])
async def delete_product_start(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer(t(msg.from_user.id, "access_denied"))
        return
    if not products:
        await msg.answer(t(msg.from_user.id, "no_products_delete"))
        return
    keyboard = [
        [InlineKeyboardButton(text=f"{prod['name']} ({prod['category']})", callback_data=f"deltovar_{pid}")]
        for pid, prod in products.items()
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await msg.answer(t(msg.from_user.id, "choose_product_delete"), reply_markup=kb)

@router.callback_query(F.data.startswith("deltovar_"))
async def delete_product_confirm(call: types.CallbackQuery):
    pid = int(call.data.split("_")[1])
    prod = products.get(pid)
    if not prod:
        await call.answer(t(call.from_user.id, "not_found"), show_alert=True)
        return
    del products[pid]
    save_products()
    await call.message.answer(t(call.from_user.id, "product_deleted", name=prod['name']), reply_markup=admin_keyboard(call.from_user.id))
    await call.answer("Удалено.")

# --- Покупка и подтверждение ---
user_purchases = {}

@router.callback_query(F.data.startswith("buy_"))
async def buy_product(call: types.CallbackQuery):
    pid = int(call.data.split("_")[1])
    prod = products.get(pid)
    if not prod:
        await call.answer(t(call.from_user.id, "not_found"), show_alert=True)
        return
    await call.message.answer(
        t(call.from_user.id, "buy_info", name=prod['name'], desc=prod['desc'], price=prod['price'], currency=prod['currency'], pay_url=prod['pay_url']),
        parse_mode="HTML"
    )
    user_states[call.from_user.id] = {"waiting_payment": pid, "lang": get_lang(call.from_user.id)}
    await call.answer()

pending_payments = {}  # user_id: {"pid": int, "photo_id": str, "message_id": int}

@router.message(F.content_type == types.ContentType.PHOTO)
async def handle_payment_proof(msg: types.Message):
    state = user_states.get(msg.from_user.id)
    if state and "waiting_payment" in state:
        pid = state["waiting_payment"]
        prod = products.get(pid)
        if prod:
            pending_payments[msg.from_user.id] = {
                "pid": pid,
                "photo_id": msg.photo[-1].file_id,
                "message_id": msg.message_id
            }
            user_lang = get_lang(msg.from_user.id)
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=LANGUAGES[user_lang]["approve"], callback_data=f"approve_{msg.from_user.id}_{pid}"),
                    InlineKeyboardButton(text=LANGUAGES[user_lang]["decline"], callback_data=f"decline_{msg.from_user.id}_{pid}")
                ]
            ])
            admin_text = LANGUAGES[user_lang]["admin_payment_check"].format(
                username=msg.from_user.username or msg.from_user.id,
                name=prod['name'],
                desc=prod['desc'],
                price=prod['price'],
                currency=prod['currency'],
                user_id=msg.from_user.id
            )
            for admin_id in ADMIN_IDS:
                await bot.send_photo(
                    admin_id,
                    msg.photo[-1].file_id,
                    caption=admin_text,
                    reply_markup=kb
                )
            await msg.answer(t(msg.from_user.id, "check_sent"))
        else:
            await msg.answer(t(msg.from_user.id, "not_found"))
    else:
        await msg.answer(t(msg.from_user.id, "not_bought"))

@router.callback_query(lambda c: c.data.startswith("approve_") or c.data.startswith("decline_"))
async def process_payment_decision(call: types.CallbackQuery):
    action, user_id, pid = call.data.split("_")
    user_id = int(user_id)
    pid = int(pid)
    prod = products.get(pid)
    user_lang = get_lang(user_id)
    if not prod:
        await call.answer(t(call.from_user.id, "not_found"), show_alert=True)
        return

    if action == "approve":
        user_purchases.setdefault(user_id, []).append(prod)
        lang = user_states.get(user_id, {}).get("lang", "ru")
        user_states[user_id] = {"lang": lang}
        pending_payments.pop(user_id, None)
        await bot.send_message(
            user_id,
            t(user_id, "payment_approved", content=prod['content']),
            parse_mode="HTML"
        )
        try:
            await call.message.edit_caption(
                call.message.caption + "\n\n" + LANGUAGES[user_lang]["admin_payment_approved"],
                reply_markup=None
            )
        except Exception:
            pass
        await call.answer("Покупка подтверждена.")
    elif action == "decline":
        lang = user_states.get(user_id, {}).get("lang", "ru")
        user_states[user_id] = {"lang": lang}
        pending_payments.pop(user_id, None)
        await bot.send_message(
            user_id,
            t(user_id, "payment_declined")
        )
        try:
            await call.message.edit_caption(
                call.message.caption + "\n\n" + LANGUAGES[user_lang]["admin_payment_declined"],
                reply_markup=None
            )
        except Exception:
            pass
        await call.answer("Покупка отклонена.")

@router.message(lambda m: m.text in [LANGUAGES["ru"]["my_purchases"], LANGUAGES["en"]["my_purchases"]])
async def my_purchases(msg: types.Message):
    items = user_purchases.get(msg.from_user.id, [])
    if not items:
        await msg.answer(t(msg.from_user.id, "no_purchases"))
        return
    text = t(msg.from_user.id, "your_purchases")
    for i, prod in enumerate(items, 1):
        text += f"{i}. <b>{prod['name']}</b> ({prod['desc']}) — <code>{prod['content']}</code>\n"
    await msg.answer(text, parse_mode="HTML")

CATALOG_FILE = "products.json"

def save_products():
    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def load_products():
    global products, product_id_counter
    if os.path.exists(CATALOG_FILE):
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            products.update({int(k): v for k, v in loaded.items()})
        if products:
            product_id_counter = max(products.keys()) + 1

async def main():
    load_products()
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

