from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pytest import fixture, raises

from my_app.command_factories.command_factory import TaskFactory, RunCommandFactory, EditTaskFactory
from my_app.core.clock import FakeClock
from my_app.repositories.task_repository import JsonTaskRepository
from my_app.common import exceptions as e


class TestEditInfoTask:
    """Класс для проверки редактирования информации о задаче"""

    @fixture
    def setup(self, tmp_path):
        """Автоматически вызывается перед каждым тестом"""
        self.repo = JsonTaskRepository(tmp_path / "tasks.json")
        self.task = TaskFactory.create_task(1, "Test id", "", "12 3 2026 12")
        self.command = RunCommandFactory(self.task, self.repo)
        self.command.add()
        self.edit = EditTaskFactory(self.task, self.repo)

    def test_can_edit_id_task(self, setup):
        """Тест для проверки редактирования id задачи"""
        self.edit.edit_id(2)
        assert self.command.find(2).id_task == 2

    def test_can_edit_title_task(self, setup):
        """Тест для проверки редактирования title задачи"""
        self.edit.edit_title("Test 2")
        assert self.command.find(1).title == "Test 2"

    def test_can_edit_description_task(self, setup):
        """Тест для проверки редактирования description задачи"""
        self.edit.edit_description("Test description 2")
        assert self.command.find(1).description == "Test description 2"

    def test_can_edit_deadline_task(self, setup):
        """Тест для проверки редактирования deadline задачи"""
        self.edit.edit_deadline("12 1 2027 12 23")
        expected = datetime(2027, 1, 12, 12, 23, 0, tzinfo=ZoneInfo("UTC"))
        assert self.command.find(1).deadline == expected

    def test_cannot_edit_task_id_to_an_existing_id(self, setup):
        """Тест для проверки невозможности изменить ID задачи на существующий ID"""
        task = TaskFactory.create_task(2, "Test", "", "")
        RunCommandFactory(task, self.repo).add()

        with raises(e.UnavailableID):
            EditTaskFactory(task, self.repo).edit_id(2)

    def test_cannot_done_after_deadline(self, setup):
        """
        Тест для проверки невозможности закончить задачу после дедлайна.
        Дедлайн сдвигается в прошлое, время продвигается — complete() должен выбросить.
        """
        clock = FakeClock(datetime(2026, 1, 12, 12, tzinfo=ZoneInfo("UTC")))
        get_now = lambda: clock.now
        task = TaskFactory.create_task(
            2, "Test", "", "12 3 2026 12",
            date=clock.now, get_now=get_now,
        )
        command = RunCommandFactory(task, self.repo, get_now=get_now)
        command.add()
        command.start()
        EditTaskFactory(task, self.repo).edit_deadline("15 1 2026")
        clock.advance(timedelta(days=3))

        with raises(e.DeadlineHasExpired):
            command.complete()