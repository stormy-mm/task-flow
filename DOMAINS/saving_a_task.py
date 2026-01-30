from datetime import datetime

from DOMAINS.types_task import TaskBehaviour

from MESSAGES.status import Status as St


class Task:
    """Запись информации о задачи"""

    def __init__(
            self,
            id_task: int,
            title: str,
            description : str,
            behaviour: TaskBehaviour,
            deadline: datetime,
            date: datetime,
    ):
        """Инициализация задачи"""
        self.id_task = id_task
        self.title = title
        self.description = description
        self.behaviour = behaviour
        self.status = St.NEW
        self.created_at = date
        self.updated_at = self.created_at
        self.deadline = deadline

    def start(self):
        """Функция для начала выполнения задачи"""
        self.behaviour.can_complete(self, St.IN_PROGRESS)

        self.status = St.IN_PROGRESS
        self.updated_at = self.created_at

    def complete(self):
        """Функция для завершения задачи"""
        self.behaviour.can_complete(self, St.DONE)

        self.status = St.DONE
        self.updated_at = self.created_at
        self.behaviour.on_complete(self)

    def cancel(self):
        """Функция для отмены задачи"""
        self.behaviour.can_complete(self, St.CANCELLED)

        self.status = St.CANCELLED
        self.updated_at = self.created_at

    def edit_deadline(self, new_deadline: datetime):
        """Функция для редактирования дедлайна задачи"""
        self.updated_at = new_deadline

    # def edit_id(self, new):
    #     """Функция для редактирования id задачи"""
    #     self.id_task =