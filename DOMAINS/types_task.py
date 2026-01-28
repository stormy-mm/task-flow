import exceptions as e

from datetime import datetime

from zoneinfo import ZoneInfo

from abc import ABC, abstractmethod

from DOMAINS.checks import CheckChangeStatusTask as Check


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
        return Check(task.status, status).execute()


class TimedBehavior(TaskBehaviour):
    """Класс для задачи с временем"""
    def __init__(self, deadline):
        self.deadline = deadline

    def can_complete(self, task, status) -> bool:
        return datetime.now(ZoneInfo("UTC")) <= self.deadline


class RepeatableBehavior(TaskBehaviour):
    """Класс для повторяющейся задачи"""
    def can_complete(self, task, status) -> bool:
        return True

    def on_complete(self, task):
        task.reset()
