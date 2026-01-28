import unittest

import exceptions as e

from MESSAGES.status import Status as St

from DOMAINS.repository_task import InMemoryTaskRepository

from DOMAINS.saving_a_task import Task


class TestInMemoryTaskRepository(unittest.TestCase):
    """Класс для проверки записи задачи в репозитории"""

    def setUp(self):
        """Автоматически вызывается перед каждым тестом"""
        self.memory_task = InMemoryTaskRepository()
        self.task = Task(1, "Task 1", "Description 1")
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


class TestInfoTaskFromRepository(unittest.TestCase):
    """Класс для проверки информации о задаче из репозитория"""

    def setUp(self):
        """Автоматически вызывается перед каждым тестом"""
        self.memory_task = InMemoryTaskRepository()
        self.task1 = Task(1, "Task 1", "Description 1")
        self.task2 = Task(2, "Task 2", "Description 2")
        self.memory_task.add_task(self.task1)
        self.memory_task.add_task(self.task2)

    def tearDown(self):
        """Автоматически вызывается после каждого теста"""
        self.memory_task._tasks.clear()

    def test_status_change_after_start_task(self):
        """Тест для проверки изменения статуса задачи после начала выполнения"""
        self.task1.start()
        result = self.memory_task.get_by_id(1)
        self.assertEqual(result.status, St.IN_PROGRESS)

    def test_cannot_complete_task_if_it_new(self):
        """Тест для проверки невозможности завершения задачи, если она новая"""
        with self.assertRaises(e.TaskCannotCompleted):
            self.task1.complete()

    def test_cannot_start_task_if_it_done(self):
        """Тест для проверки невозможности начала выполнения задачи, если она выполнена"""
        self.task1.start()
        self.task1.complete()
        print(self.task1.status)
        with self.assertRaises(e.TaskCannotStart):
            self.task1.start()
