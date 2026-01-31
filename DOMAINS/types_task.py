from datetime import datetime

from abc import ABC, abstractmethod

from DOMAINS.checks import CheckChangeStatusTask as Check

from DOMAINS.time_clock import Clock


class TaskBehaviour(ABC):
    """Абстрактный класс для поведения задачи"""
    @abstractmethod
    def can_complete(self, task, status) -> bool:
        pass

    def on_complete(self, task):
        pass


class SimpleBehavior(TaskBehaviour):
    """Класс для простой задачи"""
    def can_complete(self, task, status) -> bool:
        """Функция для проверки возможности завершения задачи"""
        return Check(task.status, status).execute()


class TimedBehavior(TaskBehaviour):
    """Класс для задачи с временем"""
    def __init__(self, deadline: datetime):
        self.deadline = deadline

    def can_complete(self, task, status) -> bool:
        if Clock.now() <= self.deadline:
            return Check(task.status, status).execute()
        return False


class RepeatableBehavior(TaskBehaviour):
    """Класс для повторяющейся задачи"""
    def can_complete(self, task, status) -> bool:
        return True

    def on_complete(self, task):
        task.reset()
