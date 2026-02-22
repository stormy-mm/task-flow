import exceptions as e

from datetime import datetime
from typing import Callable, Optional

from src.checks import CheckOVERDUEStatus
from src.parsing import ParsingDate
from src.TASK_MANAGER import Task, TaskCommand, TaskEdit
from src.repository_task import JsonTaskRepository
from src.time_clock import Clock
from src.types_task import SimpleBehavior, TaskBehaviour, TimedBehavior


def _default_get_now() -> datetime:
    """Дефолтная функция для получения текущего времени"""
    return Clock.now()


class TaskFactory:
    """Фабрика для создания задачи"""

    @staticmethod
    def create_task(
            id_task: int,
            title: str,
            description: str,
            deadline: str | None,
            date: Optional[datetime] = None,
            get_now: Optional[Callable[[], datetime]] = None,
    ) -> Task:
        """Фабричный метод для создания задачи"""
        get_now = get_now or _default_get_now
        now = date if date is not None else get_now()

        behaviour: TaskBehaviour = SimpleBehavior()
        parsed_deadline: Optional[datetime] = None
        if deadline != "":
            parsed_deadline = ParsingDate(deadline).date
            behaviour = TimedBehavior(parsed_deadline, get_now=get_now)
        status = CheckOVERDUEStatus(parsed_deadline, now).run()

        return Task(
            id_task=id_task,
            title=title,
            description=description,
            behaviour=behaviour,
            status=status,
            deadline=parsed_deadline,
            date=now,
            up_date=now,
        )


class RunCommand:
    """Фабрика для запуска команды"""

    def __init__(
            self,
            task: Task,
            memory: JsonTaskRepository,
            get_now: Optional[Callable[[], datetime]] = None,
    ):
        """Инициализация фабрики"""
        self.memory = memory
        self.task = task
        self._get_now = get_now or _default_get_now
        self.command = TaskCommand(self.task, get_now=self._get_now)

    def add(self):
        """Фабричный метод для добавления задачи"""
        self.memory.add_task(self.task)

    def find(self, id_) -> Task:
        """Фабричный метод для нахождения задачи"""
        return self.memory.get_by_id(id_)

    def clear(self):
        """Фабричный метод для очистки всех задач в репозитории"""
        self.memory.clear()

    def start(self) -> None:
        """Фабричный метод для запуска задачи"""
        self.command.start()
        # Обновляем задачу в репозитории
        self.memory.update_task(self.task)

    def complete(self) -> None:
        """Фабричный метод для завершения задачи"""
        self.command.complete()
        self.memory.update_task(self.task)

    def cancel(self) -> None:
        """Фабричный метод для отмены задачи"""
        self.command.cancel()
        self.memory.update_task(self.task)

    def delete(self) -> None:
        """Фабричный метод для удаления задачи"""
        self.memory.delete(self.task.id_task)


class EditTask:
    """Фабрика для редактирования задачи"""

    def __init__(self, task: Task, memory: JsonTaskRepository) -> None:
        """Инициализация фабрики"""
        self.memory = memory
        self.task = task
        self.edit = TaskEdit(self.task)

    def edit_id(self, new_id: int) -> None:
        """Фабричный метод для редактирования id задачи"""
        old_id = self.task.id_task
        try:
            self.memory.get_by_id(new_id)
            raise e.UnavailableID
        except e.TaskNotFind:
            pass
        self.edit.edit_id(new_id)
        self.memory.delete(old_id)
        self.memory.add_task(self.task)

    def edit_title(self, new_title: str) -> None:
        """Фабричный метод для редактирования заголовка задачи"""
        self.edit.edit_title(new_title)
        self.memory.update_task(self.task)

    def edit_description(self, description: str) -> None:
        """Фабричный метод для редактирования описания задачи"""
        self.edit.edit_description(description)
        self.memory.update_task(self.task)

    def edit_deadline(self, deadline: str) -> None:
        """Фабричный метод для редактирования дедлайна задачи"""
        self.edit.edit_deadline(ParsingDate(deadline).date)
        self.memory.update_task(self.task)

    def edit_updated_at(self, date: datetime) -> None:
        """Фабричный метод для редактирования даты обновления задачи"""
        self.edit.edit_updated_at(date)
        self.memory.update_task(self.task)


class OtherCommands:
    """Фабрика других команд"""

    def __init__(self, memory: JsonTaskRepository):
        """Инициализация памяти"""
        self.memory = memory

    def list(self):
        """Фабричный метод для представления структуры данных"""
        return self.memory.view_dict()