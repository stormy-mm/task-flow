import exceptions as e

from datetime import datetime

from DOMAINS.parsing import ParsingDate
from DOMAINS.TASK_MANAGER import Task, TaskCommand, TaskEdit
from DOMAINS.repository_task import InMemoryTaskRepository
from DOMAINS.time_clock import Clock
from DOMAINS.types_task import SimpleBehavior, TimedBehavior

from MESSAGES.status import Status as St


class TaskFactory:
    """Фабрика для создания задачи"""

    @staticmethod
    def create_task(
            id_task: int,
            title: str,
            description: str,
            deadline: str | None,
            date: datetime = Clock.now()
    ) -> Task:
        """Фабричный метод для создания задачи"""
        behaviour = SimpleBehavior()
        if not deadline is None:
            deadline = ParsingDate(deadline).date
            behaviour = TimedBehavior(deadline)

        return Task(
            id_task=id_task,
            title=title,
            description=description,
            behaviour=behaviour,
            status=St.NEW,
            deadline=deadline,
            date=date,
            up_date=date
        )


class RunCommand:
    """Фабрика для запуска команды"""

    def __init__(self, task: Task, memory: InMemoryTaskRepository):
        """Инициализация фабрики"""
        self.memory = memory
        self.task_ = task
        self.command = TaskCommand(self.task_)

    def add(self):
        """Фабричный метод для добавления задачи"""
        self.memory.add_task(self.task_)

    def find(self, id_) -> Task:
        """Фабричный метод для нахождения задачи"""
        return self.memory.get_by_id(id_)

    def clear(self):
        """Фабричный метод для очистки задачи"""
        self.memory._tasks.clear()

    def start(self) -> None:
        """Фабричный метод для запуска задачи"""
        self.command.start()
        # Обновляем задачу в репозитории
        self.memory.update_task(self.task_)

    def complete(self) -> None:
        """Фабричный метод для завершения задачи"""
        self.command.complete()
        self.memory.update_task(self.task_)

    def cancel(self) -> None:
        """Фабричный метод для отмены задачи"""
        self.command.cancel()
        self.memory.update_task(self.task_)


class EditTask:
    """Фабрика для редактирования задачи"""

    def __init__(self, task: Task, memory: InMemoryTaskRepository) -> None:
        """Инициализация фабрики"""
        self.memory = memory
        self.task_ = task
        self.edit = TaskEdit(self.task_)

    def edit_id(self, new_id: int) -> None:
        """Фабричный метод для редактирования id задачи"""
        # Сохраняем старый ID
        old_id = self.task_.id_task

        if RunCommand(self.task_, self.memory).find(new_id):
            raise e.UnavailableID

        # Изменяем ID задачи
        self.edit.edit_id(new_id)

        # Удаляем старую запись и добавляем новую с новым ID
        if self.memory._tasks.get(old_id, False):
            del self.memory._tasks[old_id]

        RunCommand(self.task_, self.memory).add()

    def edit_title(self, new_title: str) -> None:
        """Фабричный метод для редактирования заголовка задачи"""
        self.edit.edit_title(new_title)
        self.memory.update_task(self.task_)

    def edit_description(self, description: str) -> None:
        """Фабричный метод для редактирования описания задачи"""
        self.edit.edit_description(description)
        self.memory.update_task(self.task_)

    def edit_deadline(self, deadline: str) -> None:
        """Фабричный метод для редактирования дедлайна задачи"""
        self.edit.edit_deadline(ParsingDate(deadline).date)
        self.memory.update_task(self.task_)

    def edit_updated_at(self, date: datetime) -> None:
        """Фабричный метод для редактирования даты обновления задачи"""
        self.edit.edit_updated_at(date)
        self.memory.update_task(self.task_)


class OtherCommands:
    """Фабрика других команд"""

    def __init__(self, memory: InMemoryTaskRepository):
        """Инициализация памяти"""
        self.memory = memory

    def list(self):
        """Фабричный метод для представления структуры данных"""
        return self.memory.view_dict()