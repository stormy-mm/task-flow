import exceptions as e



from datetime import datetime

from zoneinfo import ZoneInfo

from DOMAINS.factories import TaskFactory

from DOMAINS.types_task import TaskBehaviour

from MESSAGES.status import Status as St


class Task:
    """Запись информации о задачи"""

    def __init__(self, id_task, title, description, behaviour: TaskBehaviour = TaskFactory.create_simple()):
        """Инициализация задачи"""
        self.id_task = id_task
        self.title = title
        self.description = description
        self.behaviour = behaviour
        self.status = St.NEW
        self.created_at = datetime.now(ZoneInfo("UTC"))
        self.updated_at = self.created_at

    def start(self):
        """Функция для начала выполнения задачи"""
        self.behaviour.can_complete(self, St.IN_PROGRESS)

        self.status = St.IN_PROGRESS
        self.updated_at = datetime.now(ZoneInfo("UTC"))

    def complete(self):
        """Функция для завершения задачи"""
        self.behaviour.can_complete(self, St.DONE)

        self.status = St.DONE
        self.updated_at = datetime.now(ZoneInfo("UTC"))
        self.behaviour.on_complete(self)

    def cancel(self):
        """Функция для отмены задачи"""
        self.behaviour.can_complete(self, St.CANCELLED)

        self.status = St.CANCELLED
        self.updated_at = datetime.now(ZoneInfo("UTC"))