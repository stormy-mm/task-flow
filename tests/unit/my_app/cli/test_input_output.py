from datetime import datetime
from zoneinfo import ZoneInfo

from pytest import mark, raises

from task_flow.cli.input_output import InputOutput
from task_flow.common.messages import Status as St
from task_flow.core.task_types import TimedBehavior
from task_flow.common import  exceptions as e


class TestInputOutput:
    """Тесты для класса InputOutput"""

    @mark.parametrize(
        "inputs", (
            (1, "Task 1", "Important", "2 2 2027"),
            (2, "Task 2", "", "3 3 2028"),
            (3, "Task 3", "", ""),
            (4, "", "", "")
        )
    )
    def test_run_add(self, monkeypatch, inputs):
        """Тест для проверки добавления задачи"""
        itr = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(itr))

        result = InputOutput.run_add()

        assert result == inputs

    def test_run_add_id_not_int(self, monkeypatch, capsys):
        """Тест для проверки добавления задачи с неправильным id"""
        inputs = iter(("abc", 10, "Task name", "Description", ""))
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        InputOutput.run_add()
        assert "id должен быть целым числом" in capsys.readouterr().out

    def test_show(self, capsys):
        """Тест для проверки показа задачи"""
        date = datetime(2020, 1, 1, tzinfo=ZoneInfo("UTC"))

        InputOutput().run_show(
            1,
            "Test",
            "Test d",
            St.NEW,
            TimedBehavior,
            date,
            date,
            date
        )
        output = capsys.readouterr()
        assert "Задача №" in output.out
        assert "Описание:" in output.out

    @mark.parametrize(
        "inputs, excepted", (
            (("id 1",), ("id", 1)),
            (("title Test",), ("title", "Test")),
            (("description Test d",), ("description", "Test d")),
            (("deadline 2 2 2027",), ("deadline", "2 2 2027")),
        )
    )
    def test_run_edit(self, monkeypatch, capsys, inputs, excepted):
        """Тест для проверки редактирования задачи"""
        monkeypatch.setattr("builtins.input", lambda _: next(iter(inputs)))
        result = InputOutput.run_edit()

        assert "Редактировать" in capsys.readouterr().out
        assert result == excepted

    def test_run_edit_cmd_not_list(self, monkeypatch):
        """Тест для проверки редактирования задачи с неправильным вводом команды"""
        monkeypatch.setattr("builtins.input", lambda _: next(iter(("delete Test d",))))

        with raises(e.IncorrectInput):
            InputOutput.run_edit()

    def test_run_edit_id_not_int(self, monkeypatch):
        """Тест для проверки редактирования задачи с неправильным вводом id"""
        monkeypatch.setattr("builtins.input", lambda _: next(iter(("id abc",))))

        with raises(e.IncorrectInput):
            InputOutput.run_edit()