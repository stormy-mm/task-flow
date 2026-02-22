import tempfile
import unittest
import exceptions as e
from pathlib import Path

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.TASK_MANAGER import Task
from src.time_clock import FakeClock
from src.types_task import TimedBehavior
from src.repository_task import InMemoryTaskRepository, JsonTaskRepository
from src.factories import TaskFactory, RunCommand, EditTask, OtherCommands
from src.parsing import ParsingDate

from messages.status import Status as St



class TestInMemoryTaskRepository(unittest.TestCase):
    """Класс для проверки записи задачи в репозитории"""

    def setUp(self):
        """Автоматически вызывается перед каждым тестом"""
        self.task = TaskFactory.create_task(1, "Task 1", "Description 1", "20 3 2026 12")
        self.command = RunCommand(self.task, InMemoryTaskRepository())
        self.command.add()

    def tearDown(self):
        """Автоматически вызывается после каждого теста"""
        self.command.clear()

    def test_tash_not_have_id(self):
        """Тест для проверки отсутствия задачи по id"""
        with self.assertRaises(e.TaskNotFind):
            self.command.find(2)

    def test_tash_have_id_after_add_task(self):
        """Тест для проверки наличия задачи по id после добавления задачи"""
        self.assertIsInstance(self.command.find(1), Task)

    def test_can_no_input_description(self):
        """Тест для проверки возможности не вводить описание задачи"""
        self.task2 = TaskFactory.create_task(2, "Task 2", None, "20 3 2026 12")
        self.command2 = RunCommand(self.task2, InMemoryTaskRepository())
        self.command2.add()
        self.assertIsNone(self.command2.find(2).description)

class TestParsingDate(unittest.TestCase):
    """Класс для проверки парсинга даты"""

    def test_parsing_date(self):
        """Тест для проверки парсинга корректной даты"""
        self.assertEqual(ParsingDate("20 3 2026 12 00").date,
                         datetime(2026, 3, 20, 12, 0, 0, tzinfo=ZoneInfo('UTC')))
        self.assertEqual(ParsingDate("20 3 2026").date,
                         datetime(2026, 3, 20, 0, 0, 0, tzinfo=ZoneInfo('UTC')))

    def test_parsing_defective_date(self):
        """Тест для проверки парсинга некорректной даты"""
        with self.assertRaises(e.ParsingError):
            ParsingDate("12 01 2026 12:00:00")
        with self.assertRaises(e.ParsingError):
            ParsingDate("03/14/2026")


class TestStatusTaskFromRepository(unittest.TestCase):
    """Класс для проверки статуса задачи из репозитория"""

    def setUp(self):
        """Автоматически вызывается перед каждым тестом"""
        self.memory = InMemoryTaskRepository()
        self.task1 = TaskFactory.create_task(1, "Task 1", "Description 1", "12 3 2026 12")
        self.command = RunCommand(self.task1, self.memory)
        self.command.add()

    def tearDown(self):
        """Автоматически вызывается после каждого теста"""
        self.command.clear()

    def test_status_IN_PROGRESS_after_start_task(self):
        """Тест для проверки 'IN_PROGRESS' после начала выполнения"""
        self.command.start()
        result = self.command.find(1)
        self.assertEqual(result.status, St.IN_PROGRESS)

    def test_cannot_DONE_task_if_it_new(self):
        """Тест для проверки невозможности 'DONE' задачи, если она новая"""
        with self.assertRaises(e.TaskCannotCompleted):
            self.command.complete()

    def test_cannot_START_task_if_it_done(self):
        """Тест для проверки невозможности 'START' задачи, если она выполнена"""
        self.command.start()
        self.command.complete()
        with self.assertRaises(e.TaskCannotStart):
            self.command.start()

    def test_can_CANCELLED_task(self):
        """Тест для проверки 'CANCELLED' задачи"""
        self.command.start()
        self.command.cancel()
        res1 = self.command.find(1)
        self.assertEqual(res1.status, St.CANCELLED)

    def test_cannot_CANCELLED_task_if_it_cancel(self):
        """Тест для проверки невозможности 'CANCELLED', если она отменена"""
        self.command.start()
        self.command.cancel()
        with self.assertRaises(e.TaskCannotCancel):
            self.command.cancel()

    def test_cannot_CANCELLED_task_if_it_done(self):
        """Тест для проверки невозможности 'CANCELLED', если она выполнена"""
        self.command.start()
        self.command.complete()
        with self.assertRaises(e.TaskCannotCancel):
            self.command.cancel()

    def test_cannot_START_task_if_it_cancelled(self):
        """Тест для проверки невозможности 'START' задачи, если она отменена"""
        self.command.cancel()
        with self.assertRaises(e.TaskCannotStart):
            self.command.start()

    def test_dict_command_LIST(self):
        """Тест для проверки получения словаря после команды 'LIST'"""
        self.task2 = TaskFactory.create_task(456, "ДР Киры", "Поздравить", "23 9 2026")
        self.task3 = TaskFactory.create_task(3, "324", "что то такое", "")
        self.command2 = RunCommand(self.task2, self.memory)
        self.command2.add()
        self.command3 = RunCommand(self.task3, self.memory)
        self.command3.add()

        self.assertIsInstance(OtherCommands(self.memory).list(), dict)

    def test_cannot_add_task_id_to_an_existing_id(self):
        """Тест для проверки невозможности добавления задачи с существующим id"""
        self.task2 = TaskFactory.create_task(1, "Task 1", "Description 1", "12 3 2026 12")
        self.command2 = RunCommand(self.task2, self.memory)
        with self.assertRaises(e.TaskAlreadyExists):
            self.command2.add()

    def test_can_del_task(self):
        """Тест для проверки удаления задачи"""
        self.command.delete()
        with self.assertRaises(e.TaskNotFind):
            self.command.find(1)

    def test_status_task_OVERDUE_if_it_add_deadline(self):
        """Тест для проверки статуса задачи OVERDUE, если она добавлена с истекшим дедлайном"""
        self.task2 = TaskFactory.create_task(3, "Task 1", "Description 1", "12 1 2026")
        self.command2 = RunCommand(self.task2, self.memory)
        self.command2.add()
        self.assertEqual(self.command2.find(3).status, St.OVERDUE)

class TestEditInfoTask(unittest.TestCase):
    """Класс для проверки редактирования информации о задаче"""

    def setUp(self):
        """Автоматически вызывается перед каждым тестом"""
        self.memory = InMemoryTaskRepository()
        self.task1 = TaskFactory.create_task(1, "Task 1", "Description 1", "12 3 2026 12")
        self.command = RunCommand(self.task1, self.memory)
        self.command.add()
        self.edit = EditTask(self.task1, self.memory)

    def tearDown(self):
        """Автоматически вызывается после каждого теста"""
        self.command.clear()

    def test_can_edit_id_task(self):
        """Тест для проверки редактирования id задачи"""
        self.edit.edit_id(2)
        self.assertEqual(self.command.find(2).id_task, 2)

    def test_can_edit_title_task(self):
        """Тест для проверки редактирования title задачи"""
        self.edit.edit_title("Task 2")
        self.assertEqual(self.command.find(1).title, "Task 2")

    def test_can_edit_description_task(self):
        """Тест для проверки редактирования description задачи"""
        self.edit.edit_description("Description 2")
        self.assertEqual(self.command.find(1).description, "Description 2")

    def test_can_edit_deadline_task(self):
        """Тест для проверки редактирования deadline задачи"""
        self.edit.edit_deadline("12 1 2027 12 23")
        expected = datetime(2027, 1, 12, 12, 23, 0, tzinfo=ZoneInfo("UTC"))
        self.assertEqual(self.command.find(1).deadline, expected)

    def test_cannot_edit_task_id_to_an_existing_id(self):
        """Тест для проверки невозможности изменить ID задачи на существующий ID"""
        self.task2 = TaskFactory.create_task(2, "Task 2", "Description 2", "")
        self.command2 = RunCommand(self.task2, self.memory)
        self.edit2 = EditTask(self.task2, self.memory)
        self.command2.add()

        with self.assertRaises(e.UnavailableID):
            self.edit.edit_id(2)

    def test_cannot_DONE_after_deadline(self):
        """
        Тест для проверки невозможности закончить задачу после дедлайна.
        Дедлайн сдвигается в прошлое, время продвигается — complete() должен выбросить.
        """
        self.clock = FakeClock(datetime(2026, 1, 12, 12, tzinfo=ZoneInfo("UTC")))
        get_now = lambda: self.clock.now
        self.task2 = TaskFactory.create_task(
            2, "Task 2", "Description 2", "12 3 2026 12",
            date=self.clock.now, get_now=get_now,
        )
        self.command2 = RunCommand(self.task2, self.memory, get_now=get_now)
        self.command2.add()
        self.command2.start()
        self.edit2 = EditTask(self.task2, self.memory)
        self.edit2.edit_deadline("15 1 2026")
        self.clock.advance(timedelta(days=3))

        with self.assertRaises(e.DeadlineHasExpired):
            self.command2.complete()


class TestTimeTaskFromRepository(unittest.TestCase):
    """Класс для проверки времени задачи из репозитория"""

    def setUp(self):
        """Автоматически вызывается перед каждым тестом"""
        self.clock = FakeClock(datetime(2026, 1, 12, 12, tzinfo=ZoneInfo("UTC")))
        get_now = lambda: self.clock.now
        self.task1 = TaskFactory.create_task(
            1, "Task 1", "Description 1", "12 1 2025",
            date=self.clock.now, get_now=get_now,
        )
        self.memory = InMemoryTaskRepository()
        self.command = RunCommand(self.task1, self.memory, get_now=get_now)
        self.command.add()
        self.edit = EditTask(self.task1, self.memory)

    def tearDown(self):
        """Автоматически вызывается после каждого теста"""
        self.command.clear()

    def test_task_have_date(self):
        """Тест для проверки наличия даты задачи"""
        date_task = self.command.find(1).created_at
        self.assertEqual(date_task, self.clock.now)

    def test_updated_date_task_eq_date_today(self):
        """Тест для проверки обновленной даты задачи через 72 часа"""
        self.edit.edit_updated_at(self.clock.advance(timedelta(hours=72)))
        updated_date_task = self.command.find(1).updated_at
        self.assertEqual(updated_date_task, datetime(2026, 1, 15, 12, tzinfo=ZoneInfo("UTC")))

    def test_task_have_type_Timed_task(self):
        """Тест для проверки дедлайна задачи"""
        type_task = self.command.find(1)
        self.assertIsInstance(type_task.behaviour, TimedBehavior)


class TestJsonTaskRepository(unittest.TestCase):
    """Проверка сохранения и загрузки задач из JSON."""

    def setUp(self):
        self.tmp_dir = Path(tempfile.gettempdir())
        self.json_path = self.tmp_dir / "taskflow_test_json.json"

    def tearDown(self):
        if self.json_path.exists():
            self.json_path.unlink()

    def test_save_and_load_tasks(self):
        """Добавленные задачи сохраняются в JSON и восстанавливаются при новой инициализации."""
        repo = JsonTaskRepository(self.json_path)
        task = TaskFactory.create_task(1, "Задача 1", "Описание", "20 3 2026 12")
        RunCommand(task, repo).add()
        self.assertTrue(self.json_path.exists())

        repo2 = JsonTaskRepository(self.json_path)
        loaded = repo2.get_by_id(1)
        self.assertEqual(loaded.title, "Задача 1")
        self.assertEqual(loaded.description, "Описание")
        self.assertIsInstance(loaded.behaviour, TimedBehavior)

    def test_clear_persists_empty_list(self):
        """После clear() файл содержит пустой список."""
        repo = JsonTaskRepository(self.json_path)
        task = TaskFactory.create_task(1, "Задача", "", "")
        RunCommand(task, repo).add()
        RunCommand(task, repo).clear()
        self.assertEqual(repo._tasks, {})

        repo2 = JsonTaskRepository(self.json_path)
        with self.assertRaises(e.TaskNotFind):
            repo2.get_by_id(1)