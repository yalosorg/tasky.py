from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import kb_task_length
from datetime import datetime
from reminder import Reminder, Task
from threading import Thread
import asyncio

bot = Bot(token = '')
dp = Dispatcher(bot, storage = MemoryStorage())
reminder = Reminder(bot, 'tasks.db')


class DateInput(StatesGroup):
    r = State()


class MonthInput(StatesGroup):
    r = State()


class YearInput(StatesGroup):
    r = State()


async def init(_):
    print('INIT')


@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    await message.answer('Привет!\nЯ - бот для таск менеджмента, буду напоминать тебе о твоих задачах!')


@dp.message_handler(commands = ['newtask'])
async def newtask(message: types.Message):
    await message.answer('За какой промежуток времени вам нужно сделать задачу?', reply_markup = kb_task_length)


@dp.message_handler(commands = ['День'])
async def day(message: types.Message):
    await message.answer('Введите дату и время в которое вам следует начать выполнять задачу и на следующей линии опишите её\nОтправьте время в формате \'DD-MM-YYYY-hh:mm\'')
    await DateInput.r.set()


@dp.message_handler(state = DateInput.r)
async def time(message: types.Message, state: FSMContext):
    raw = message.text
    if '\n' not in raw:
        await message.answer('Извини, я ничего не понял(')
        return

    splitted = raw.split('\n')
    raw_date = splitted[0]
    splitted.pop(0)
    description = '\n'.join(splitted)
    try:
        date = datetime.strptime(raw_date, '%d-%m-%Y-%H:%M')
    except:
        await message.answer(f'Не возможно распознать дату: {raw_date}')
    
    id = reminder.db.free_id()

    try:
        reminder.db.insert_task(id, description, str(date), 1, message.chat.id)
        await message.answer('Запомнил!')
    except:
        await message.answer('Что-то пошло не так')
    finally:
        await state.finish()


@dp.message_handler(commands = ['Месяц'])
async def month(message: types.Message):
    await message.answer('Введите год и месяц для выполнения задачи и на следующей линии опишите её\nОтправьте дату в формате \'MM-YYYY\'')
    await MonthInput.r.set()


@dp.message_handler(state = MonthInput.r)
async def month_selected(message: types.Message, state: FSMContext):
    raw = message.text
    if '\n' not in raw:
        await message.answer('Извини, я ничего не понял(')
        return

    splitted = raw.split('\n')
    raw_date = splitted[0]
    splitted.pop(0)
    description = '\n'.join(splitted)
    try:
        date = datetime.strptime(raw_date, '%m-%Y')
    except:
        await message.answer(f'Не возможно распознать дату: {raw_date}')

    id = reminder.db.free_id()

    try:
        reminder.db.insert_task(id, description, str(date), 2, message.chat.id)
        await message.answer('Запомнил!')
    except:
        await message.answer('Что-то пошло не так')
    finally:
        await state.finish()


@dp.message_handler(commands = ['Год'])
async def year(message: types.Message):
    await message.answer('Введите год за который вам нужно выполнить поставленную задачу и на следующей линии опишите её')
    await YearInput.r.set()


@dp.message_handler(state = YearInput.r)
async def year_selected(message: types.Message, state: FSMContext):
    raw = message.text
    if '\n' not in raw:
        await message.answer('Извини, я ничего не понял :(')

    splitted = raw.split('\n')
    raw_date = splitted[0]
    splitted.pop(0)
    description = '\n'.join(splitted)
    date = datetime.strptime(raw_date, '%Y')

    try:
        reminder.db.insert_task(id, description, str(date), 2, message.chat.id)
        await message.answer('Запомнил!')
    except:
        await message.answer('Не возможно распознать дату')
    finally:
        await state.finish()


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer('Не знаю что ты хотел этим сказать :(')

# Launch bot
def polling():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    reminder.set_bloop(loop)
    executor.start_polling(dp, skip_updates = True, on_startup = init)

Thread(target = polling).start()

# Launch reminder
loop = asyncio.new_event_loop()
loop.run_until_complete(reminder.run())
loop.close()