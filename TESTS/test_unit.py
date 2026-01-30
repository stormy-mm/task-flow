import unittest
import exceptions as e

from DOMAINS.time_clock import FakeClock

from MESSAGES.status import Status as St

from DOMAINS.repository_task import InMemoryTaskRepository

from DOMAINS.factories import TaskFactory

from DOMAINS.parsing import ParsingDate

from datetime import datetime, timedelta

from zoneinfo import ZoneInfo


class TestInMemoryTaskRepository(unittest.TestCase):
    """Класс для проверки записи задачи в репозитории"""

    def setUp(self):
        """Автоматически вызывается перед каждым тестом"""
        self.memory_task = InMemoryTaskRepository()
        self.task = TaskFactory.create_task(1, "Task 1", "Description 1", "20 3 2026 12")
        self.memory_task.add_task(self.task)

    def tearDown(self):
        """Автоматически вызывается после каждого теста"""
        self.memory_task._tasks.clear()

    def test_tash_not_have_id(self):
        """Тест для проверки отсутствия задачи по id"""
        with self.assertRaises(e.TaskNotFind):
            self.memory_task.get_by_id(2)

    def test_tash_have_id_after_add_task(self):
        """Тест для проверки наличия задачи по id после добавления задачи"""
        self.assertTrue(self.memory_task.get_by_id(1))


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
        self.memory_task = InMemoryTaskRepository()
        self.task1 = TaskFactory.create_task(1, "Task 1", "Description 1", "12 3 2026 12")
        self.memory_task.add_task(self.task1)

    def tearDown(self):
        """Автоматически вызывается после каждого теста"""
        self.memory_task._tasks.clear()

    def test_status_IN_PROGRESS_after_start_task(self):
        """Тест для проверки 'IN_PROGRESS' после начала выполнения"""
        self.task1.start()
        result = self.memory_task.get_by_id(1)
        self.assertEqual(result.status, St.IN_PROGRESS)

    def test_cannot_DONE_task_if_it_new(self):
        """Тест для проверки невозможности 'DONE' задачи, если она новая"""
        with self.assertRaises(e.TaskCannotCompleted):
            self.task1.complete()

    def test_cannot_START_task_if_it_done(self):
        """Тест для проверки невозможности 'START' задачи, если она выполнена"""
        self.task1.start()
        self.task1.complete()
        with self.assertRaises(e.TaskCannotStart):
            self.task1.start()

    def test_can_CANCELLED_task(self):
        """Тест для проверки 'CANCELLED' задачи"""
        self.task1.start()
        self.task1.cancel()
        res1 = self.memory_task.get_by_id(1)
        self.assertEqual(res1.status, St.CANCELLED)

    def test_cannot_CANCELLED_task_if_it_done(self):
        """Тест для проверки невозможности 'CANCELLED', если она выполнена"""
        self.task1.start()
        self.task1.complete()
        with self.assertRaises(e.TaskCannotCancel):
            self.task1.cancel()

    def test_cannot_START_task_if_it_cancelled(self):
        """Тест для проверки невозможности 'START' задачи, если она отменена"""
        self.task1.cancel()
        with self.assertRaises(e.TaskCannotStart):
            self.task1.start()


class TestEditInfoTask(unittest.TestCase):
    """Класс для проверки редактирования информации о задаче"""

    def setUp(self):
        """Автоматически вызывается перед каждым тестом"""
        self.memory_task = InMemoryTaskRepository()
        self.task1 = TaskFactory.create_task(1, "Task 1", "Description 1", "12 1 2026")
        self.memory_task.add_task(self.task1)

    def tearDown(self):
        """Автоматически вызывается после каждого теста"""
        self.memory_task._tasks.clear()

    # def test_can_edit_id_task(self):
    #     """Тест для проверки редактирования id задачи"""
    #     self.task1.edit_id(2)
    #     self.assertEqual(self.memory_task.get_by_id(2).id_task, 2)


class TestTimeTaskFromRepository(unittest.TestCase):
    """Класс для проверки времени задачи из репозитория"""

    def setUp(self):
        """Автоматически вызывается перед каждым тестом"""
        self.memory_task = InMemoryTaskRepository()
        self.clock = FakeClock(datetime(2026, 1, 12, 12, tzinfo=ZoneInfo("UTC")))
        self.task1 = TaskFactory.create_task(1, "Task 1", "Description 1", None, self.clock.now)
        self.memory_task.add_task(self.task1)

    def tearDown(self):
        """Автоматически вызывается после каждого теста"""
        self.memory_task._tasks.clear()

    def test_task_have_date(self):
        """Тест для проверки наличия даты задачи"""
        date_task = self.memory_task.get_by_id(1).created_at
        self.assertEqual(date_task, self.clock.now)

    def test_updated_date_task_eq_date_today(self):
        """Тест для проверки обновленной даты задачи через 72 часа"""
        self.task1.edit_deadline(self.clock.advance(timedelta(hours=72)))
        updated_date_task = self.memory_task.get_by_id(1).updated_at
        self.assertEqual(updated_date_task, datetime(2026, 1, 15, 12, tzinfo=ZoneInfo("UTC")))

    # def test_task_have_type_Timed_task(self):
    #     """Тест для проверки дедлайна задачи"""
    #     type_task = self.memory_task.get_by_id(1).behaviour.type

