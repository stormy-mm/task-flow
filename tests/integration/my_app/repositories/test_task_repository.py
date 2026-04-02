import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pytest import mark, fixture, raises, param

from my_app.common import exceptions as e
from my_app.common.messages import Status as St
from my_app.command_factories.command_factory import TaskFactory, RunCommandFactory, EditTaskFactory, OtherCommandsFactory
from my_app.core.clock import FakeClock
from my_app.core.task_manager import Task
from my_app.core.task_types import TimedBehavior
from my_app.repositories.task_repository import JsonTaskRepository


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
        self.repo = JsonTaskRepository(tmp_path / "data.json")
        self.command = RunCommandFactory(self.task, self.repo, get_now=get_now)
        self.command.add()
        self.edit = EditTaskFactory(self.task, self.repo)

    def test_task_have_date(self, setup):
        """Тест для проверки наличия даты задачи"""
        assert self.command.find(1).created_at == self.clock.now

    def test_updated_date_task_eq_date_today(self, setup):
        """Тест для проверки обновленной даты задачи через 72 часа"""
        self.edit.edit_updated_at(self.clock.advance(timedelta(hours=72)))
        assert self.command.find(1).updated_at == datetime(2026, 1, 15, 12, tzinfo=ZoneInfo("UTC"))

    def test_task_have_type_timed_task(self, setup):
        """Тест для проверки дедлайна задачи"""
        assert isinstance(self.command.find(1).behaviour, TimedBehavior)

    def test_status_task_overdue_if_it_add_deadline(self, setup):
        """Тест для проверки статуса задачи OVERDUE, если она добавлена с истекшим дедлайном"""
        assert self.command.find(1).status == St.OVERDUE


class TestJsonTaskRepository:
    """Класс для проверки сохранения и загрузки задач в JSON"""
    @fixture
    def setup(self, tmp_path):
        """Автоматически вызывается перед каждым тестом"""
        self.json_path = tmp_path / "data.json"
        self.repo = JsonTaskRepository(self.json_path)
        self.task = TaskFactory.create_task(1, "Test id", "Test description", "20 3 2026")
        RunCommandFactory(self.task, self.repo).add()

    def test_save_and_load_tasks(self, setup):
        """Добавленные задачи сохраняются в JSON и восстанавливаются при новой инициализации."""
        assert self.json_path.exists()

        loaded = self.repo.get_by_id(1)
        assert loaded.title == "Test id"
        assert loaded.description == "Test description"
        assert isinstance(loaded.behaviour, TimedBehavior)

    def test_clear_persists_empty_list(self, setup):
        """После clear() файл содержит пустой список."""
        RunCommandFactory(self.task, self.repo).clear()
        assert self.repo._tasks == {}

    def test_not_find_task_delete(self, setup):
        """Тест для проверки исключения при отсутствии задачи при удалении"""
        cmd = RunCommandFactory(self.task, self.repo)
        cmd.clear()
        with raises(e.TaskNotFind):
            cmd.delete()

    def test_task_not_exists(self, setup):
        """Тест для проверки исключения при отсутствии задачи"""
        RunCommandFactory(self.task, self.repo).clear()
        with raises(e.TaskNotFind):
            self.repo.get_by_id(1)

    def test_tash_have_id_after_add_task(self, setup):
        """Тест для проверки наличия задачи по id после добавления задачи"""
        assert isinstance(self.repo.get_by_id(1), Task)

    def test_can_no_input_description(self, setup):
        """Тест для проверки возможности не вводить описание задачи"""
        task = TaskFactory.create_task(2, "Test", None, "20 3 2026 12")
        command = RunCommandFactory(task, self.repo)
        command.add()
        assert command.find(2).description is None

    @mark.parametrize(
        "data", (
            param("INVALID JSON", id="invalid json"),
            param({"id": 1}, id="json not list"),
            param([123, "abc"], id="load with invalid item"),
        )
    )
    def test_json_file(self, setup, data):
        """Тест на JSON файл"""
        if isinstance(data, (list, tuple, dict)):
            data = json.dumps(data)

        self.json_path.write_text(data, encoding="utf-8")

        repo = JsonTaskRepository(self.json_path)
        repo._load()

        assert repo.tasks == {}

    def test_load_task_from_dict_raises(self, monkeypatch, setup):
        """Тест на загрузку задачи из словаря с ошибками"""
        self.json_path.write_text(json.dumps([{"id_task": 1}]), encoding="utf-8")

        def fake_from_dict(_):
            raise ValueError("boom")

        monkeypatch.setattr(Task, "from_dict", fake_from_dict)

        repo = JsonTaskRepository(self.json_path)
        repo._load()

        assert repo.tasks == {}

    def test_load_success(self, monkeypatch, setup):
        """Тест на успешный загрузки"""
        self.json_path.write_text(json.dumps([{"id_task": 1}]), encoding="utf-8")

        class FakeTask:
            def __init__(self, id_task):
                self.id_task = id_task

        def fake_from_dict(data):
            return FakeTask(data["id_task"])

        monkeypatch.setattr(Task, "from_dict", fake_from_dict)

        repo = JsonTaskRepository(self.json_path)
        repo._load()

        assert 1 in repo.tasks
        assert repo.tasks[1].id_task == 1


class TestStatusTaskFromRepository:
    """Класс для проверки статуса задачи из репозитория"""
    @fixture
    def setup(self, tmp_path):
        """Автоматически вызывается перед каждым тестом"""
        self.repo = JsonTaskRepository(tmp_path / "data.json")
        self.task = TaskFactory.create_task(1, "Test id", "Test description", "1 1 3000")
        self.command = RunCommandFactory(self.task, self.repo)
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
        assert isinstance(OtherCommandsFactory(self.repo).list(), dict)

    def test_len_dict(self, setup):
        """Тест для проверки длины словаря"""
        RunCommandFactory(TaskFactory.create_task(2, "Test", "Test", ""), self.repo).add()
        RunCommandFactory(TaskFactory.create_task(3, "Test", "Test", ""), self.repo).add()
        assert len(OtherCommandsFactory(self.repo).list()) == 3 # две тут и одна в фикстуре

    def test_cannot_add_task_id_to_an_existing_id(self, setup):
        """Тест для проверки невозможности добавления задачи с существующим id"""
        with raises(e.TaskAlreadyExists):
            RunCommandFactory(TaskFactory.create_task(1, "Test", "", ""), self.repo).add()