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
    get_ipa = State()
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

# Этот хэндлер будет срабатывать, если введено корректное
# и переводить в состояние ожидания выбора польщователем команды
@router.message(StateFilter(FSMFillForm.get_ipa), F.text.isalpha(), F.text.isascii())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное ckjdj в хранилище по ключу "ipa"
    trans=get_transcription(message.text)
    await state.update_data(ipa=trans)
    await message.answer(text=trans)
    await message.answer(text=LEXICON_RU['quest'],
                         reply_markup=kb_3
                         )
    # Устанавливаем состояние ожидания дальнейшего ответа
    await state.set_state(FSMFillForm.get_use)

# Этот хэндлер будет срабатывать, если во время ввода французского слова
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.get_ipa))
async def warning_not_name(message: Message):
    await message.answer( text=LEXICON_RU['FMS_4'])

@router.callback_query(StateFilter(FSMFillForm.get_use), F.data == LEXICON_RU['but_non'])
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    user_dict[callback.from_user.id] = await state.get_data()
    # Завершаем машину состояний
    await state.clear()
    # Отправляем в чат сообщение о выходе из машины состояний
    await callback.message.answer(
        text=LEXICON_RU['FMS_2']
    )


@router.callback_query(StateFilter(FSMFillForm.get_use), F.data == (LEXICON_RU['but_oui']))
async def process_fillform_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(text=LEXICON_RU['FMS_1'])
    await state.set_state(FSMFillForm.get_ipa)


@router.message(StateFilter(FSMFillForm.get_ipa), F.text.isalpha(), F.text.isascii())
async def process_name_sent(message: Message, state: FSMContext):
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


