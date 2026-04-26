from datetime import datetime
from zoneinfo import ZoneInfo

from pytest import param, raises, mark, fixture

from task_flow.application.task_application import TaskApplication
from task_flow.repositories.task_sql import SqliteTaskRepository
from task_flow.common.messages import Status as St
from task_flow.common import exceptions as e


class TestTaskApplication:
    """Тесты для класса TaskApplication"""

    @fixture
    def setup(self, tmp_path):
        """Создает TaskApplication"""
        self.app = TaskApplication(SqliteTaskRepository(":memory:"))
        self.app.add(1, "Test", "", "")

    def test_add_task(self, setup):
        """Тест для добавления задачи"""
        # задача уже добавлена в фикстуре
        assert self.app.show(1).title == "Test" and self.app.show(1).status == St.NEW

    @mark.parametrize("actions, excepted_status", (
        param(("start",), St.IN_PROGRESS, id="test_status_in_progress"),
        param(("start", "complete"), St.DONE, id="test_status_done"),
        param(("cancel",), St.CANCELLED, id="test_status_cancelled"),
    ))
    def test_status(self, setup, actions, excepted_status):
        """Тест для статуса задачи"""
        for action in actions:
            getattr(self.app, action)(1)
        assert self.app.show(1).status == excepted_status

    def test_list_tasks(self, setup):
        """Тест для списка задач"""
        assert len(self.app.list_tasks()) == 1

    def test_clear(self, setup):
        """Тест для очистки списка задач"""
        self.app.clear()
        assert len(self.app.list_tasks()) == 0

    def test_delete(self, setup):
        """Тест для удаления задачи"""
        self.app.delete(1)
        with raises(e.TaskNotFind):
            assert self.app.show(1)

    date_ = datetime(2020, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC"))

    @mark.parametrize(
        "action, task_id, new_value, property_, excepted_value", (
            param("edit_id", 1, 2, "id_task", 2 , id="test_edit_id"),
            param("edit_title", 1, "Test2", "title", "Test2", id="test_edit_title"),
            param("edit_description", 1, "Test description", "description", "Test description",
                  id="test_edit_description"),
            param("edit_deadline", 1, "1 1 2020", "deadline", date_, id="test_edit_deadline"),
            # param("edit_update_at", 1, date_, "updated_at", date_, id="test_edit_update_at"),
    ))
    def test_edit(self, setup, action, property_, excepted_value, task_id, new_value):
        """Тест для редактирования задачи"""
        getattr(self.app, action)(task_id, new_value)
        assert getattr(self.app.show(task_id if action != "edit_id" else 2), property_) == excepted_value