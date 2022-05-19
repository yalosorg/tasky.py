from datetime import datetime

class HandledTask:
    def __init__(self, id: int, time: str):
        self.id = id
        self.time = time # when it was handled

class History:
    def __init__(self):
        self.day = []
        self.long = []

    def add_day_task(self, task: HandledTask):
        self.day.append(task)

    def add_long_task(self, task: HandledTask):
        self.long.append(task)
    
    def day_task_handled(self, id: id) -> bool:
        to_remove = []

        i = 0
        for task in self.day:
            if task.id == id:
                if not self.day_ended(task.time):
                    return True
                else:
                    to_remove.append(i)

            i += 1

        for index in to_remove:
            self.day.pop(index)

        return False
    
    def long_task_handled(self, id: id) -> bool:
        to_remove = []

        i = 0
        for task in self.long:
            if task.id == id:
                if not self.day_ended(task.time):
                    return True
                else:
                    to_remove.append(i)

            i += 1
        
        for index in to_remove:
            self.long.pop(index)
        
        return False

    def day_ended(self, date) -> bool:
        if (datetime.now() - date).days >= 1:
            return True
        else:
            return False
