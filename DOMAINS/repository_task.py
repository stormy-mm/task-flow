import exceptions as e

from DOMAINS.saving_a_task import Task


class InMemoryTaskRepository:
    """Класс для хранения задач в памяти"""

    def __init__(self):
        """Инициализация репозитория"""
        self._tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Функция для добавления задачи"""
        self._tasks.append(task)

    def get_by_id(self, task_id: int) -> Task:
        """Функция для поиска задачи по id"""
        for task in self._tasks:
            if task.id_task == task_id:
                return task
        raise e.TaskNotFind