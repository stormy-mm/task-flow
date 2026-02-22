from datetime import datetime
from typing import Optional, Callable

from src.TASK_MANAGER import Task
from src.factories import _default_get_now, TaskFactory, RunCommand, OtherCommands, EditTask
from src.repository_task import InMemoryTaskRepository


class TaskApplication:
    """
    Единая точка входа для команд над задачами.
    CLI импортирует только этот класс и передаёт ему репозиторий и (опционально) источник времени.
    """

    def __init__(
            self,
            repository: InMemoryTaskRepository,
            get_now: Optional[Callable[[], datetime]] = None,
    ):
        self._repo = repository
        self._get_now = get_now or _default_get_now

    def add(
            self,
            id_task: int,
            title: str,
            description: str,
            deadline: Optional[str] = None,
    ) -> None:
        """Создать и сохранить задачу."""
        task = TaskFactory.create_task(
            id_task, title, description, deadline,
            get_now=self._get_now,
        )
        RunCommand(task, self._repo, get_now=self._get_now).add()

    def start(self, task_id: int) -> None:
        """Перевести задачу в статус IN_PROGRESS."""
        task = self._repo.get_by_id(task_id)
        RunCommand(task, self._repo, get_now=self._get_now).start()

    def complete(self, task_id: int) -> None:
        """Перевести задачу в статус DONE."""
        task = self._repo.get_by_id(task_id)
        RunCommand(task, self._repo, get_now=self._get_now).complete()

    def cancel(self, task_id: int) -> None:
        """Перевести задачу в статус CANCELLED."""
        task = self._repo.get_by_id(task_id)
        RunCommand(task, self._repo, get_now=self._get_now).cancel()

    def list_tasks(self) -> dict:
        """Вернуть все задачи (id -> Task)."""
        return OtherCommands(self._repo).list()

    def clear(self) -> None:
        """Очистить список задач."""
        self._repo.clear()

    def delete(self, task_id: int) -> None:
        """Удалить задачу по id."""
        self._repo.delete(task_id)

    def show(self, task_id: int) -> Task:
        """Вернуть задачу по id."""
        return self._repo.get_by_id(task_id)

    def edit_id(self, task_id: int, new_id: int) -> None:
        """Изменить id задачи."""
        task = self._repo.get_by_id(task_id)
        EditTask(task, self._repo).edit_id(new_id)

    def edit_title(self, task_id: int, new_title: str) -> None:
        """Изменить заголовок задачи."""
        task = self._repo.get_by_id(task_id)
        EditTask(task, self._repo).edit_title(new_title)

    def edit_description(self, task_id: int, description: str) -> None:
        """Изменить описание задачи."""
        task = self._repo.get_by_id(task_id)
        EditTask(task, self._repo).edit_description(description)

    def edit_deadline(self, task_id: int, deadline: str) -> None:
        """Изменить дедлайн задачи."""
        task = self._repo.get_by_id(task_id)
        EditTask(task, self._repo).edit_deadline(deadline)

    def edit_updated_at(self, task_id: int, date: datetime) -> None:
        """Изменить дату обновления задачи."""
        task = self._repo.get_by_id(task_id)
        EditTask(task, self._repo).edit_updated_at(date)