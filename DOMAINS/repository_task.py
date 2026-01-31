import exceptions as e

from DOMAINS.TASK_MANAGER import Task


class InMemoryTaskRepository:
    """Класс для хранения задач в памяти"""

    def __init__(self):
        """Инициализация репозитория"""
        self._tasks: dict = {}

    def add_task(self, task: Task) -> None:
        """Функция для добавления задачи"""
        if self._tasks.get(task.id_task):
            raise e.TaskAlreadyExists
        self._tasks[task.id_task] = task

    def get_by_id(self, task_id: int) -> Task:
        """Функция для поиска задачи по id"""
        if n:=self._tasks.get(task_id):
            return n
        raise e.TaskNotFind

    def update_task(self, task: Task) -> None:
        """Функция для обновления задачи"""
        self._tasks[task.id_task] = task

    def view_dict(self):
        """Функция для просмотра словаря"""
        return self._tasks