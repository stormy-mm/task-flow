from datetime import datetime
from typing import Callable, Optional

from DOMAINS.time_clock import Clock
from DOMAINS.types_task import TaskBehaviour, SimpleBehavior, TimedBehavior

from MESSAGES.status import Status as St


def _status_from_string(s: str) -> St:
    """Преобразование строки статуса в значение Status."""
    return getattr(St, s) if hasattr(St, s) else St.NEW


class Task:
    """Запись информации о задачи"""

    def __init__(
            self,
            id_task: int,
            title: str,
            description: Optional[str],
            status: St,
            behaviour: TaskBehaviour,
            deadline: Optional[datetime],
            date: datetime,
            up_date: datetime
    ):
        """Инициализация задачи"""
        self._id_task = id_task
        self.title = title
        self.description = description
        self._status = status
        self._behaviour = behaviour
        self._created_at = date
        self._updated_at = up_date
        self.deadline = deadline

    @property
    def id_task(self):
        """Получение ID задачи"""
        return self._id_task

    @property
    def status(self) -> St:
        """Получение статуса задачи"""
        return self._status

    @property
    def created_at(self) -> datetime:
        """Получение даты создания задачи"""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Получение даты обновления задачи"""
        return self._updated_at

    @property
    def behaviour(self) -> TaskBehaviour:
        """Получение поведения задачи"""
        return self._behaviour

    def to_dict(self) -> dict:
        """Сериализация задачи в словарь для JSON."""
        return {
            "id_task": self.id_task,
            "title": self.title,
            "description": self.description if self.description is not None else "",
            "status": self._status,
            "behaviour_type": "timed" if isinstance(self._behaviour, TimedBehavior) else "simple",
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> Task:
        """Восстановление задачи из словаря (после загрузки из JSON)."""
        deadline = datetime.fromisoformat(d["deadline"]) if d.get("deadline") else None
        behaviour: TaskBehaviour = (
            TimedBehavior(deadline) if d["behaviour_type"] == "timed" else SimpleBehavior()
        )
        return cls(
            id_task=d["id_task"],
            title=d["title"],
            description=d["description"] or "",
            status=_status_from_string(d["status"]),
            behaviour=behaviour,
            deadline=deadline,
            date=datetime.fromisoformat(d["created_at"]),
            up_date=datetime.fromisoformat(d["updated_at"]),
        )


class TaskCommand:
    """Класс для выполнения команды над задачей"""

    def __init__(self, task: Task, get_now: Optional[Callable[[], datetime]] = None):
        self.task = task
        self._get_now = get_now or (lambda: Clock.now())

    def start(self) -> None:
        """Функция для начала выполнения задачи"""
        self.task._behaviour.can_complete(self.task, St.IN_PROGRESS)
        self.task._status = St.IN_PROGRESS
        self.task._updated_at = self._get_now()

    def complete(self) -> None:
        """Функция для завершения задачи"""
        self.task._behaviour.can_complete(self.task, St.DONE)
        self.task._status = St.DONE
        self.task._updated_at = self._get_now()

    def cancel(self) -> None:
        """Функция для отмены задачи"""
        self.task._behaviour.can_complete(self.task, St.CANCELLED)
        self.task._status = St.CANCELLED
        self.task._updated_at = self._get_now()


class TaskEdit:
    """Класс для редактирования задачи"""

    def __init__(self, task: Task):
        self.task = task

    def edit_id(self, new_id: int) -> None:
        """Функция для редактирования id задачи"""
        self.task._id_task = new_id

    def edit_title(self, new_title: str) -> None:
        """Функция для редактирования заголовка задачи"""
        self.task.title = new_title

    def edit_description(self, new_description: str) -> None:
        """Функция для редактирования описания задачи"""
        self.task.description = new_description

    def edit_deadline(self, new_deadline: datetime) -> None:
        """Функция для редактирования дедлайна задачи"""
        self.task.deadline = new_deadline

    def edit_updated_at(self, new_updated_at: datetime) -> None:
        """Функция для редактирования даты обновления задачи"""
        self.task._updated_at = new_updated_at