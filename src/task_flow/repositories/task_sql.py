import sqlite3
from typing import Any

from ..core.task_types import SimpleBehavior
from ..core.task_manager import Task
from ..common import exceptions as e

from pathlib import Path


class SqliteTaskRepository:
    """Сохранение задач в sql файл"""

    def __init__(self, db_path: str | Path):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self) -> None:
        """Создание таблицы"""
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                title TEXT NOT NULL,
                description TEXT NULL,
                behaviour_type TEXT NOT NULL,
                status TEXT NOT NULL,
                deadline DATETIME NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)

    def add_task(self, task: Task) -> None:
        """Создание задачи"""
        with self.conn:
            self.conn.execute("""
                INSERT INTO 
                    tasks (id, title, description, behaviour_type, status, deadline)
                VALUES 
                    (?, ?, ?, ?, ?, ?)
            """,
                  (
                task.id_task,
                task.title,
                task.description,
                'simple' if isinstance(task.behaviour, SimpleBehavior) else 'timed',
                task.status,
                task.deadline,
            ))

    def update_task(self, task: Task) -> None:
        """Обновление задачи"""
        with self.conn:
            self.conn.execute("""
                UPDATE tasks
                SET title = ?,
                    description = ?,
                    behaviour_type = ?,
                    status = ?,
                    deadline = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                task.title,
                task.description,
                'simple' if isinstance(task.behaviour, SimpleBehavior) else 'timed',
                task.status,
                task.deadline,
                task.id_task
            ))


    def get_list(self) -> list[Any]:
        """Получить список задач"""
        cursor = self.conn.execute("SELECT * FROM tasks")
        return cursor.fetchall()

    def clear(self) -> None:
        """Удаляет строки в БД"""
        with self.conn:
            self.conn.execute("DELETE FROM tasks")

    def get_by_id(self, task_id) -> Task:
        """Возвращает задачу по ID"""
        cursor = self.conn.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )

        row = cursor.fetchone()
        if row is None:
            raise e.TaskNotFind
        return Task.from_row(row)

    def delete(self, task_id: int) -> None:
        """Удаляет строку в БД по ID"""
        if self.get_by_id(task_id):
            with self.conn:
                self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id, ))


