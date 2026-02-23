from datetime import datetime

from typing import Optional

from my_app.command_factories.command_factory import (
    default_get_now,
    TaskFactory,
    RunCommandFactory,
    EditTaskFactory,
    OtherCommandsFactory
)
from my_app.core.task_manager import Task
from my_app.repositories.task_repository import JsonTaskRepository


class TaskApplication:
    """
    Единая точка входа для команд над задачами.
    CLI импортирует только этот класс и передаёт ему репозиторий и (опционально) источник времени.
    """

    def __init__(self, repository: JsonTaskRepository):
        self.repo = repository
        self.get_now_datetime = default_get_now

    def add(
            self,
            id_task: int,
            title: str,
            description: str,
            deadline: Optional[str] = None,
    ) -> None:
        """Создать и сохранить задачу."""
        task = TaskFactory.create_task(
            id_task,
            title,
            description,
            deadline,
            get_now=self.get_now_datetime,
        )
        RunCommandFactory(task, self.repo, self.get_now_datetime).add()

    def start(self, task_id: int) -> None:
        """Перевести задачу в статус IN_PROGRESS."""
        task = self.repo.get_by_id(task_id)
        RunCommandFactory(task, self.repo, self.get_now_datetime).start()

    def complete(self, task_id: int) -> None:
        """Перевести задачу в статус DONE."""
        task = self.repo.get_by_id(task_id)
        RunCommandFactory(task, self.repo, self.get_now_datetime).complete()

    def cancel(self, task_id: int) -> None:
        """Перевести задачу в статус CANCELLED."""
        task = self.repo.get_by_id(task_id)
        RunCommandFactory(task, self.repo, self.get_now_datetime).cancel()

    def list_tasks(self) -> dict:
        """Вернуть все задачи (id -> Task)."""
        return OtherCommandsFactory(self.repo).list()

    def clear(self) -> None:
        """Очистить список задач."""
        self.repo.clear()

    def delete(self, task_id: int) -> None:
        """Удалить задачу по id."""
        self.repo.delete(task_id)

    def show(self, task_id: int) -> Task:
        """Вернуть задачу по id."""
        return self.repo.get_by_id(task_id)

    def edit_id(self, task_id: int, new_id: int) -> None:
        """Изменить id задачи."""
        task = self.repo.get_by_id(task_id)
        EditTaskFactory(task, self.repo).edit_id(new_id)

    def edit_title(self, task_id: int, new_title: str) -> None:
        """Изменить заголовок задачи."""
        task = self.repo.get_by_id(task_id)
        EditTaskFactory(task, self.repo).edit_title(new_title)

    def edit_description(self, task_id: int, description: str) -> None:
        """Изменить описание задачи."""
        task = self.repo.get_by_id(task_id)
        EditTaskFactory(task, self.repo).edit_description(description)

    def edit_deadline(self, task_id: int, deadline: str) -> None:
        """Изменить дедлайн задачи."""
        task = self.repo.get_by_id(task_id)
        EditTaskFactory(task, self.repo).edit_deadline(deadline)

    def edit_update_at(self, task_id: int, date: datetime) -> None:
        """Изменить дату обновления задачи."""
        task = self.repo.get_by_id(task_id)
        EditTaskFactory(task, self.repo).edit_updated_at(date)