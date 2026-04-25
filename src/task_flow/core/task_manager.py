from datetime import datetime

from typing import Callable, Optional

from ..command_factories.validators import CheckOverdueStatus
from ..core.clock import Clock
from ..core.task_types import TaskBehaviour, SimpleBehavior, TimedBehavior
from ..common.messages import Status as St


class Task:
    """Запись информации о задачи"""

    def __init__(
            self,
            id_task: int,
            title: str,
            description: Optional[str],
            status: str,
            behaviour: TaskBehaviour,
            deadline: Optional[datetime],
            created_at: datetime = None,
            updated_at: datetime = None
    ):
        """Инициализация задачи"""
        self.id_task = id_task
        self.title = title
        self.description = description
        self.behaviour = behaviour
        self.status = status
        self.deadline = deadline
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_row(cls, row):
        behaviour = SimpleBehavior() if row[3] == "simple" else TimedBehavior()
        deadline = datetime.fromisoformat(row[5]) if row[5] else None
        created_at = datetime.fromisoformat(row[6]) if row[6] else None
        updated_at = datetime.fromisoformat(row[7]) if row[7] else None

        return cls(
            id_task=row[0],
            title=row[1],
            description=row[2],
            behaviour=behaviour,
            status=row[4],
            deadline=deadline,
            created_at=created_at,
            updated_at=updated_at
        )


class TaskCommand:
    """Класс для выполнения команды над задачей"""
    def __init__(self, task: Task, get_now: Optional[Callable[[], datetime]] = None):
        self.task = task
        self._get_now = get_now or Clock.now

    def start(self) -> None:
        """Функция для начала выполнения задачи"""
        self.task.behaviour.can_complete(self.task, St.IN_PROGRESS)
        self.task.status = St.IN_PROGRESS
        self.task.updated_at = self._get_now()

    def complete(self) -> None:
        """Функция для завершения задачи"""
        self.task.behaviour.can_complete(self.task, St.DONE)
        self.task.status = St.DONE
        self.task.updated_at = self._get_now()

    def cancel(self) -> None:
        """Функция для отмены задачи"""
        self.task.behaviour.can_complete(self.task, St.CANCELLED)
        self.task.status = St.CANCELLED
        self.task.updated_at = self._get_now()


class TaskEdit:
    """Класс для редактирования задачи"""
    def __init__(self, task: Task):
        self.task = task

    def edit_id(self, new_id: int) -> None:
        """Функция для редактирования id задачи"""
        self.task.id_task = new_id

    def edit_title(self, new_title: str) -> None:
        """Функция для редактирования заголовка задачи"""
        self.task.title = new_title

    def edit_description(self, new_description: str) -> None:
        """Функция для редактирования описания задачи"""
        self.task.description = new_description

    def edit_deadline(self, new_deadline: datetime) -> None:
        """Функция для редактирования дедлайна задачи"""
        self.task.deadline = new_deadline
        self.task.behaviour = TimedBehavior()
        self.task.status = CheckOverdueStatus(new_deadline, Clock.now()).run()

    def edit_updated_at(self, new_updated_at: datetime) -> None:
        """Функция для редактирования даты обновления задачи"""
        self.task.updated_at = new_updated_at