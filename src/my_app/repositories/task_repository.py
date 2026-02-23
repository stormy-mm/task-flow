import json

from my_app.common import exceptions as e
from my_app.core.task_manager import Task

from pathlib import Path


class InMemoryTaskRepository:
    """Класс для хранения задач в памяти"""
    def __init__(self):
        """Инициализация репозитория"""
        self._tasks: dict = {}

    @property
    def tasks(self) -> dict:
        """Функция для получения словаря задач"""
        return self._tasks

    def add_task(self, task: Task) -> None:
        """Функция для добавления задачи"""
        if self._tasks.get(task.id_task):
            raise e.TaskAlreadyExists
        self._tasks[task.id_task] = task

    def get_by_id(self, task_id: int) -> Task:
        """Функция для поиска задачи по id"""
        if n := self._tasks.get(task_id):
            return n
        raise e.TaskNotFind

    def delete(self, task_id: int) -> None:
        """Удаление задачи по идентификатору."""
        if task_id not in self._tasks:
            raise e.TaskNotFind
        del self._tasks[task_id]

    def update_task(self, task: Task) -> None:
        """Функция для обновления задачи"""
        self._tasks[task.id_task] = task

    def view_dict(self) -> dict:
        """Функция для просмотра словаря"""
        return self._tasks

    def clear(self) -> None:
        """Очистка всех задач в репозитории"""
        self._tasks.clear()


class JsonTaskRepository(InMemoryTaskRepository):
    """Репозиторий с сохранением задач в JSON-файл."""
    def __init__(self, file_path: str | Path):
        """Инициализация. file_path — путь к JSON-файлу."""
        super().__init__()
        self._file_path = Path(file_path)
        self._load()

    def _load(self) -> None:
        """Загрузка задач из JSON-файла."""
        if not self._file_path.exists():
            return
        try:
            text = self._file_path.read_text(encoding="utf-8")
            data = json.loads(text)
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(data, list):
            return
        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                task = Task.from_dict(item)
                self._tasks[task.id_task] = task
            except (KeyError, TypeError, ValueError):
                continue

    def _save(self) -> None:
        """Сохранение всех задач в JSON-файл."""
        payload = [task.to_dict() for task in self._tasks.values()]
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        self._file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_task(self, task: Task) -> None:
        """Добавление задачи и сохранение в файл."""
        super().add_task(task)
        self._save()

    def update_task(self, task: Task) -> None:
        """Обновление задачи и сохранение в файл."""
        super().update_task(task)
        self._save()

    def delete(self, task_id: int) -> None:
        """Удаление задачи по идентификатору и сохранение в файл."""
        super().delete(task_id)
        self._save()

    def clear(self) -> None:
        """Очистка задач и сохранение пустого списка в файл."""
        super().clear()
        self._save()