from abc import ABC, abstractmethod

from datetime import datetime
from typing import Callable, Optional

from my_app.common import exceptions as e
from my_app.command_factories.validators import CheckChangeStatusTask as CheckStatus
from my_app.core.clock import Clock


class TaskBehaviour(ABC):
    """Абстрактный класс для поведения задачи"""
    @abstractmethod
    def can_complete(self, task, status: str) -> bool:
        """Функция для проверки возможности завершения задачи"""
        pass


class SimpleBehavior(TaskBehaviour):
    """Класс для простой задачи"""
    def can_complete(self, task, status) -> bool:
        return CheckStatus(task.status, status).execute()


class TimedBehavior(TaskBehaviour):
    """Класс для задачи с дедлайном"""
    def __init__(self, get_now: Optional[Callable[[], datetime]] = None):
        self._get_now = get_now or Clock.now

    def can_complete(self, task, status) -> bool:
        if self._get_now() <= task.deadline:
            return CheckStatus(task.status, status).execute()
        raise e.DeadlineHasExpired