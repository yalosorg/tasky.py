#from db import Database
import sqlite3
import asyncio
from sys import maxsize
#from time import sleep
from aiogram import Bot
from history import History, HandledTask
from threading import Thread, Lock
from datetime import datetime

class Database:
    def __init__(self, name: str = 'tasks.db'):
        self.name = name

        mutex = Lock()
        mutex.acquire()
        try:
            conn = sqlite3.connect(self.name)
            cursor = conn.cursor()

            cursor.execute('''CREATE TABLE IF NOT EXISTS tasks(taskid INT, description TEXT, date TEXT, length INT, user INT)''')

            conn.commit()
            conn.close()
        finally: mutex.release()
    

    def insert_task(self, taskid: int, description: str, date: str, length: int, user: int):
        mutex = Lock()
        mutex.acquire()

        try:
            conn = sqlite3.connect(self.name)
            cursor = conn.cursor()

            cursor.execute(f'''INSERT INTO tasks VALUES({taskid}, '{description}', '{date}', {length}, {user})''')

            conn.commit()
            conn.close()
        finally: mutex.release()
    

    #def insert_task(self, task: Task):
        #self.insert_task(task.taskid, task.description, task.date, task.length, task.user)

    def get_tasks(self) -> list:
        mutex = Lock()
        mutex.acquire()

        try:
            conn = sqlite3.connect(self.name)
            cursor = conn.cursor()

            cursor.execute(f'''SELECT * FROM tasks''')
            rows = cursor.fetchall()
            tasks = []

            for row in rows:
                tasks.append(Task(row[0], row[1], row[2], row[3], row[4]))

            conn.close()

            return tasks
        finally:
            mutex.release()
        
        return []
    
    def free_id(self) -> int:
        res = None

        mutex = Lock()
        mutex.acquire()

        try:
            conn = sqlite3.connect(self.name)
            cursor = conn.cursor()

            for i in range(1, maxsize + 1):
                cursor.execute(f'''SELECT * FROM tasks WHERE taskid = {i}''')
                data = cursor.fetchall()

                if len(data) == 0:
                    res = i
                    break

            conn.close()
        finally:
            mutex.release()

        return res

class Task:
    def __init__(self, taskid: int, description: str, date: str, length: int, user: int):
        self.taskid = taskid
        self.description = description
        self.date = date
        self.length = length
        self.user = user

class Reminder:
    def __init__(self, bot: Bot, db: str = 'tasks.db'):
        self.bot = bot
        self.db = Database(db)
        self.history = History()
        self.bloop = None

    def set_bloop(self, bloop):
        self.bloop = bloop

    async def work(self):
        while True:
            tasks = self.db.get_tasks()
            print(tasks)

            for task in tasks:
                if task.length == 1:
                    await self.handle_day(task)
                elif task.length == 2 or task.length == 3:
                    await self.handle_long(task)
                else:
                    raise Exception('Че за хуйня, либо 1 либо 2 либо 3 в длине таски')

            await asyncio.sleep(10)

    async def handle_day(self, task: Task):
        if self.history.day_task_handled(task.taskid): return

        now = datetime.now()
        formatted = datetime.strptime(task.date, '%Y-%m-%d %H:%M:%S')
        delta = formatted - now
        if delta.days == 0 and delta.seconds <= 300:
            asyncio.run_coroutine_threadsafe(self.bot.send_message(task.user, f'Напоминаю вам о вашей задаче на сегодня!\n{task.description}'), self.bloop)
            self.history.add_day_task(HandledTask(task.taskid, now))

    async def handle_long(self, task: Task):
        if self.history.long_task_handled(task.taskid): return

        now = datetime.now()
        formatted = datetime.strptime(task.date, '%Y-%m-%d %H:%M:%S')
        delta = formatted - now
        if task.length == 2 and delta.days <= 30:
            asyncio.run_coroutine_threadsafe(self.bot.send_message(task.user, f'Напоминаю вам о вашей задаче на этот месяц!\n{task.description}'), self.bloop)
            self.history.add_long_task(HandledTask(task.taskid, now))
        elif task.length == 3 and delta.days <= 365:
            asyncio.run_coroutine_threadsafe(self.bot.send_message(task.user, f'Напоминаю вам о вашей задаче на этот год!\n{task.description}'), self.bloop)
            self.history.add_long_task(HandledTask(task.taskid, now))

    async def run(self):
        await self.work()
