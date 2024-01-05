from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_RU

#клавиатура /start

but_yes = KeyboardButton(text=LEXICON_RU['but_yes'])
but_no = KeyboardButton(text=LEXICON_RU['but_no'])

kb_1 = ReplyKeyboardMarkup(
    keyboard=[[but_yes],
              [but_no]],
    resize_keyboard=True
)

ipa = KeyboardButton(text=LEXICON_RU['ipa'])
kb_2 = ReplyKeyboardMarkup(
    keyboard=[[ipa]],
    resize_keyboard=True
)

but_oui = InlineKeyboardButton(
    text='да',
    callback_data='oui'
)

but_non = InlineKeyboardButton(
    text='нет',
    callback_data='non'
)

# Создаем объект инлайн-клавиатуры
kb_3 = InlineKeyboardMarkup(
    inline_keyboard=[[but_oui],
                     [but_non]])

but_oui = KeyboardButton(text=LEXICON_RU['but_oui'])
but_non = KeyboardButton(text=LEXICON_RU['but_non'])

