###!/usr/bin/python3.8
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import bot_tools
import os
from database import insert_value
from aiogram import Bot, Dispatcher, types, executor
import dotenv

token_path = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_path=token_path)
TOKEN = os.getenv('TOKEN')
print(TOKEN)
print(token_path)

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

main_path = os.getenv('main_path')


class Test(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()


@dp.message_handler(Command("start"), state=None)
async def enter_test(message: types.Message):
    await bot.send_message(message.chat.id, 'Привет, готов?', reply_markup=keyboard3())
    await Test.Q3.set()


@dp.message_handler(state=Test.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    try:
        user_id = message.chat.id
        files = os.listdir(main_path + '/for_bonus')
        ops = bot_tools.check(user_id)
        if ops is None:
            await bot.send_message(user_id, 'На сегодня фото закончились, попробуйте позже оптравить мне "/start"!')
            bot_tools.remove_file(ops[-1])
            await Test.Q1.set()
        if ops[0] == 'ok':
            with open(main_path + '/for_bonus/' + ops[-1] + '.jpg', 'rb') as file:
                fi = ops[-1]
                await bot.send_photo(user_id, file, caption='Что изображено на фото?')
                async with state.proxy() as data:
                    data["filename"] = fi
            bot_tools.insert_sql(user_id, ops[-1])
            bot_tools.remove_file(ops[-1])
            await Test.Q2.set()
        elif ops == 'finish':
            await bot.send_message(user_id, 'На сегодня фото закончились, попробуйте позже оптравить мне "/start"!')
            bot_tools.remove_file(ops[-1])
            await Test.Q1.set()
    except Exception as e:
        await Test.Q1.set()
        print(e)


@dp.message_handler(state=Test.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    answer = message.text
    user_id = message.chat.id
    async with state.proxy() as data:
        data["answer1"] = answer
        data["user_id"] = user_id

    try:
        insert_value(user_id=int(data.get('user_id')),
                     filename=str(data.get('filename')),
                     value=data.get('answer1'))
    except:
        insert_value(user_id=int(data.get('user_id')),
                     filename=str(data.get('filename')),
                     value='invalid')

    await answer_q1(message=message, state=state)


@dp.callback_query_handler(state="*")
@dp.message_handler(state=Test.Q3)
async def inlin(call: types.CallbackQuery, state: FSMContext):
    try:
        if call.data == 'yes3':
            await answer_q1(message=call.message, state=state)
        elif call.data == 'no3':
            await bot.send_message(call.message.chat.id, 'Как будешь готов '
                                                         'продолжить - просто отправь мне "/start"')
            await state.finish()
    except AttributeError:
        await bot.send_message(call.chat.id, 'Пожалуйста, нажмите на одну из кнопок')


def keyboard3():
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='Да', callback_data='yes3')
    button2 = types.InlineKeyboardButton(text='Нет', callback_data='no3')
    markup.add(button1, button2)
    return markup


executor.start_polling(dp, skip_updates=True)
