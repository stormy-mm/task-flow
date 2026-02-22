import exceptions as e

from datetime import datetime
from typing import Callable, Optional

from abc import ABC, abstractmethod

from DOMAINS.checks import CheckChangeStatusTask as CheckStatus
from DOMAINS.time_clock import Clock
from MESSAGES.status import Status


class TaskBehaviour(ABC):
    """Абстрактный класс для поведения задачи"""
    @abstractmethod
    def can_complete(self, task, status: Status) -> bool:
        """Функция для проверки возможности завершения задачи"""
        pass


class SimpleBehavior(TaskBehaviour):
    """Класс для простой задачи"""
    def can_complete(self, task, status) -> bool:
        return CheckStatus(task.status, status).execute()


class TimedBehavior(TaskBehaviour):
    """Класс для задачи с временем"""
    def __init__(self, deadline: datetime, get_now: Optional[Callable[[], datetime]] = None):
        self.deadline = deadline
        self._get_now = get_now or (lambda: Clock.now())

    def can_complete(self, task, status) -> bool:
        if self._get_now() <= task.deadline:
            return CheckStatus(task.status, status).execute()
        raise e.DeadlineHasExpired