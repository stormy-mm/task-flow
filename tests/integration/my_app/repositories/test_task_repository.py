import sqlite3
from datetime import datetime, timedelta
from unittest import skip
from zoneinfo import ZoneInfo

from pytest import mark, fixture, raises, param

from task_flow.common import exceptions as e
from task_flow.common.messages import Status as St
from task_flow.command_factories.command_factory import TaskFactory, RunCommandFactory, EditTaskFactory, OtherCommandsFactory
from task_flow.core.clock import FakeClock
from task_flow.core.task_manager import Task
from task_flow.core.task_types import TimedBehavior
from task_flow.repositories.task_sql import SqliteTaskRepository


class TestTimeTaskFromRepository:
    """Класс для проверки времени задачи из репозитория"""
    @fixture
    def setup(self, tmp_path):
        """Автоматически вызывается перед каждым тестом"""
        self.clock = FakeClock(datetime(2026, 1, 12, 12, tzinfo=ZoneInfo("UTC")))
        get_now = lambda: self.clock.now
        self.task = TaskFactory.create_task(
            1, "test", "test", "12 1 2025",
            date=self.clock.now, get_now=get_now,
        )
        self.db = SqliteTaskRepository(":memory:")
        self.command = RunCommandFactory(self.task, self.db, get_now=get_now)
        self.command.add()
        self.edit = EditTaskFactory(self.task, self.db)

    def test_task_have_date(self, setup):
        """Тест для проверки наличия даты задачи"""
        assert self.command.find(1).created_at

    @skip("Сложно тестировать время в БД")
    def test_updated_date_task_eq_date_today(self, setup):
        """Тест для проверки обновленной даты задачи через 72 часа"""
        self.edit.edit_updated_at(self.clock.advance(timedelta(hours=72)))
        assert (self.command.find(1).updated_at ==
                datetime(2026, 1, 15, 12, tzinfo=ZoneInfo("UTC")).isoformat(timespec="seconds", sep=" "))

    def test_task_have_type_timed_task(self, setup):
        """Тест для проверки дедлайна задачи"""
        assert isinstance(self.command.find(1).behaviour, TimedBehavior)

    def test_status_task_overdue_if_it_add_deadline(self, setup):
        """Тест для проверки статуса задачи OVERDUE, если она добавлена с истекшим дедлайном"""
        assert self.command.find(1).status == St.OVERDUE


class TestSqlTaskRepository:
    """Класс для проверки сохранения и загрузки задач в sqlite"""
    @fixture
    def setup(self, tmp_path):
        """Автоматически вызывается перед каждым тестом"""
        self.db = SqliteTaskRepository(":memory:")
        self.task = TaskFactory.create_task(1, "Test id", "Test description", "20 3 2026")
        RunCommandFactory(self.task, self.db).add()

    def test_save_and_load_tasks(self, setup):
        """Добавленные задачи сохраняются в sqlite и восстанавливаются при новой инициализации."""
        loaded = self.db.get_by_id(1)
        assert loaded.title == "Test id"
        assert loaded.description == "Test description"
        assert isinstance(loaded.behaviour, TimedBehavior)

    def test_clear_persists_empty_list(self, setup):
        """После clear() файл содержит пустой список."""
        RunCommandFactory(self.task, self.db).clear()
        assert not self.db.get_list()

    def test_not_find_task_delete(self, setup):
        """Тест для проверки исключения при отсутствии задачи при удалении"""
        cmd = RunCommandFactory(self.task, self.db)
        cmd.clear()
        with raises(e.TaskNotFind):
            cmd.delete()

    def test_task_not_exists(self, setup):
        """Тест для проверки исключения при отсутствии задачи"""
        RunCommandFactory(self.task, self.db).clear()
        with raises(e.TaskNotFind):
            self.db.get_by_id(1)

    def test_tash_have_id_after_add_task(self, setup):
        """Тест для проверки наличия задачи по id после добавления задачи"""
        assert isinstance(self.db.get_by_id(1), Task)

    def test_can_no_input_description(self, setup):
        """Тест для проверки возможности не вводить описание задачи"""
        task = TaskFactory.create_task(2, "Test", None, "20 3 2026 12")
        command = RunCommandFactory(task, self.db)
        command.add()
        assert command.find(2).description is None


class TestStatusTaskFromRepository:
    """Класс для проверки статуса задачи из репозитория"""
    @fixture
    def setup(self, tmp_path):
        """Автоматически вызывается перед каждым тестом"""
        self.db = SqliteTaskRepository(":memory:")
        self.task = TaskFactory.create_task(1, "Test id", "Test description", "1 1 3000")
        self.command = RunCommandFactory(self.task, self.db)
        self.command.add()

    @mark.parametrize(
        "actions, expected_status",
        (
            param(("start",), St.IN_PROGRESS, id="start"),
            param(("start", "cancel"), St.CANCELLED, id="start_cancel"),
        )
    )
    def test_status_task_after_start(self, setup, actions, expected_status):
        """Тест для проверки статуса задачи после начала выполнения"""
        for action_name in actions:
            getattr(self.command, action_name)()
                         # 1 по умолчанию
        assert self.command.find(1).status == expected_status

    @mark.parametrize(
        "actions, expected_exception, command",
        (
            param(("start", "complete"), e.TaskCannotStart, "start",
                         id="Cannot start a task after it has been completed"),
            param(("start", "cancel"), e.TaskCannotCancel, "cancel",
                         id="Cannot cancel a task after it has been started"),
            param(("start", "complete"), e.TaskCannotCancel, "cancel",
                         id="Cannot cancel a task after it has been completed"),
            param(("cancel",), e.TaskCannotStart, "start",
                         id="Cannot start a task after it has been cancelled"),
            param((), e.TaskCannotCompleted, "complete",
                         id="Cannot complete a task after it has been started"),
            param(("delete",), e.TaskNotFind, "find", id="Cannot find a task"),
        )
    )
    def test_cannot_task_if(self, setup, actions, expected_exception, command):
        """Тест для проверки невозможности выполнения команды"""
        for action_name in actions:
            getattr(self.command, action_name)()

        with raises(expected_exception):
            if command == "find":
                getattr(self.command, command)(1)
            getattr(self.command, command)()

    def test_dict_command_list(self, setup):
        """Тест для проверки получения словаря после команды 'LIST'"""
        assert isinstance(OtherCommandsFactory(self.db).get_list(), list)

    def test_len_dict(self, setup):
        """Тест для проверки длины словаря"""
        RunCommandFactory(TaskFactory.create_task(2, "Test", "Test", ""), self.db).add()
        RunCommandFactory(TaskFactory.create_task(3, "Test", "Test", ""), self.db).add()
        assert len(OtherCommandsFactory(self.db).get_list()) == 3 # две тут и одна в фикстуре

    def test_cannot_add_task_id_to_an_existing_id(self, setup):
        """Тест для проверки невозможности добавления задачи с существующим id"""
        with raises(sqlite3.IntegrityError):
            RunCommandFactory(TaskFactory.create_task(1, "Test", "", ""), self.db).add()