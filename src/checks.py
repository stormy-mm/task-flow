from datetime import datetime

import exceptions as e

from messages.status import Status as St, Status


class ICheck:
    """Миксин для проверки разрешения изменения статуса задачи"""

    @staticmethod
    def can_change_status(status, exception, *statuses) -> bool:
        if status in statuses:
            raise exception
        return True


class CheckChangeStatusTask:
    """Класс для проверки разрешения изменения статуса задачи"""

    def __init__(self, task_status, status):
        """Инициализация статуса задачи"""
        self.task_status = task_status
        self.status = status

    def execute(self) -> bool:
        """Проверка разрешения изменения статуса задачи"""
        match self.status:
            case St.DONE:
                return self.can_change_to_done()
            case St.IN_PROGRESS:
                return self.can_change_to_start()
            case St.CANCELLED:
                return self.can_change_to_cancel()
        return True

    def can_change_to_done(self) -> bool:
        """Проверка разрешения изменения статуса задачи на DONE"""
        return ICheck.can_change_status(self.task_status, e.TaskCannotCompleted, St.NEW, St.CANCELLED)

    def can_change_to_start(self) -> bool:
        """Проверка разрешения изменения статуса задачи на IN_PROGRESS"""
        return ICheck.can_change_status(self.task_status, e.TaskCannotStart, St.DONE, St.CANCELLED)

    def can_change_to_cancel(self) -> bool:
        """Проверка разрешения изменения статуса задачи на CANCELLED"""
        return ICheck.can_change_status(self.task_status, e.TaskCannotCancel, St.DONE, St.CANCELLED)


class CheckOVERDUEStatus:
    """Класс для проверки статуса задачи на OVERDUE"""
    def __init__(self, deadline: datetime, created_at: datetime):
        """Инициализация дедлайна и времени создания задачи"""
        self.deadline = deadline
        self.created_at = created_at

    def run(self) -> Status:
        """Запуск проверки"""
        if self.deadline is not None:
            if self.deadline < self.created_at:
                return St.OVERDUE
        return St.NEW