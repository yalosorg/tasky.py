from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import kb_task_length
from datetime import datetime
from reminder import Reminder, Task, Database
from threading import Thread, Lock
import asyncio

bot = Bot(token = '5303297646:AAHN9XQ83qyyXndZgSUrgBupw5hhMxh4Nz0')
dp = Dispatcher(bot, storage = MemoryStorage())
reminder = Reminder(bot, 'tasks.db')
LOGGING = True


def log(taskid, description, date, length, user):
    if LOGGING:
        print(f'{taskid} {description} {date} {length} {user}')


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


@dp.message_handler(commands = ['tasks'])
async def tasks(message: types.Message):
    db = Database()
    tasks = db.get_tasks()
    # sort tasks by user id
    now = datetime.now()

    await bot.send_message(message.chat.id, 'Ниже будут все ваши задачи')

    for task in tasks:
        formatted = datetime.strptime(task.date, '%Y-%m-%d %H:%M:%S')
        if message.chat.id == task.user:
            print('how many times')
            print(now - formatted)
            if task.length == 1 and (now - formatted).days >= 0:
                await bot.send_message(message.chat.id, f'Ваша задача, которую вы должны выполнить за следующие сутки:\n{task.description}')
            elif task.length == 1 and (now - formatted).days == -1:
                await bot.send_message(message.chat.id, f'Ваша задача на ближайшие сутки начиная с {str(task.date)}:\n{task.description}')
            elif task.length == 2 and (now - formatted).days >= 30:
                await bot.send_message(message.chat.id, f'Ваше задача до конца этого месяца:\n${task.description}')
            elif task.length == 3 and (now - formatted).days >= 365:
                await bot.send_message(message.chat.id, f'Ваша задача до конца этого года:\n${task.description}')


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
    try:
        date = datetime.strptime(f'01-{raw_date}', '%m-%Y')
    except:
        await message.answer('Не удалось распознать дату')
        return

    id = reminder.db.free_id()

    try:
        log(id, description, str(date), 3, message.chat.id)
        reminder.db.insert_task(id, description, str(date), 3, message.chat.id)
        await message.answer('Запомнил!')
    except Exception as e:
        raise e
        await message.answer('Что-то пошло не так :(')
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