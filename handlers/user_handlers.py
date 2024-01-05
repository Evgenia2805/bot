from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards.keyboards import kb_1, kb_2, kb_3
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.types import Message, CallbackQuery
from services.services import get_transcription


router = Router()
storage = MemoryStorage()

user_dict: dict[int, dict[str, str | int | bool]] = {}

class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    get_ipa = State()        # Состояние ожидания ввода имени
    get_use = State()

# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    user = message.from_user
    await message.answer(f"Coucou, {user.first_name}!")
    await message.answer(text=LEXICON_RU['/start'], reply_markup=kb_1)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

@router.message(Command(commands='stop'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text=LEXICON_RU['stop_2'], reply_markup=kb_2)

@router.message(Command(commands='stop'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['stop_1'], reply_markup=kb_2)
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()

@router.message(F.text == LEXICON_RU['but_no'], StateFilter(default_state))
async def process_yes_answer(message: Message):
    await message.answer(text=LEXICON_RU['rep_no'], reply_markup=kb_2)

# @router.message(F.text == LEXICON_RU['but_yes'], StateFilter(default_state))
# async def process_no_answer(message: Message):
#     await message.answer(text=LEXICON_RU['rep_yes'], reply_markup=kb_2)

@router.message(Command(commands='transcription'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['FMS_1'])
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.get_ipa)

# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@router.message(StateFilter(FSMFillForm.get_ipa), F.text.isalpha(), F.text.isascii())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    trans=get_transcription(message.text)
    await state.update_data(ipa=trans)
    await message.answer(text=trans)
    await message.answer(text=LEXICON_RU['quest'],
                         reply_markup=kb_3
                         )
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.get_use)

# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.get_ipa))
async def warning_not_name(message: Message):
    await message.answer( text=LEXICON_RU['FMS_4'])

@router.callback_query(StateFilter(FSMFillForm.get_use), F.data == LEXICON_RU['but_non'])
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    # Добавляем в "базу данных" анкету пользователя
    # по ключу id пользователя
    user_dict[callback.from_user.id] = await state.get_data()
    # Завершаем машину состояний
    await state.clear()
    # Отправляем в чат сообщение о выходе из машины состояний
    await callback.message.answer(
        text=LEXICON_RU['FMS_2']
    )

# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе пола и переводить в состояние отправки фото
@router.callback_query(StateFilter(FSMFillForm.get_use), F.data == (LEXICON_RU['but_oui']))
async def process_fillform_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(text=LEXICON_RU['FMS_1'])
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.get_ipa)


@router.message(StateFilter(FSMFillForm.get_ipa), F.text.isalpha(), F.text.isascii())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    trans=get_transcription(message.text)
    await state.update_data(ipa=trans)
    await message.answer(text=trans)
    await message.answer(text=LEXICON_RU['quest'],
                         reply_markup=kb_3
                         )


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@router.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text=LEXICON_RU['other_answer'])

@router.message(Command(commands='delmenu'))
async def del_main_menu(message: Message, bot: Bot):
    await bot.delete_my_commands()
    await message.answer(text='Кнопка "Menu" удалена')

@router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    # Отправляем пользователю анкету, если она есть в "базе данных"
    if message.from_user.id in user_dict:
        await message.answer_photo(
            caption=f'Транскрипции: {user_dict[message.from_user.id]["ipa"]}',
        )
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(
            text='Вы еще не заполняли анкету. Чтобы приступить - '
            'отправьте команду /transcription'
        )
