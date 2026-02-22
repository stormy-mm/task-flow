import exceptions as e

from src.TASK_MANAGER import Task
from src.parsing import ParsingDate
from src.task_application import TaskApplication

from messages.commands import EDIT_COMMANDS
from messages.messages import Messages as Ms


class InputOutput:
    """Класс вывода и ввода"""

    @staticmethod
    def run_add() -> tuple:
        """Добавление задачи"""
        while True:
            try:
                id_ = int(input(Ms.ADD_TASK[0]))
                break
            except ValueError:
                print("Ошибка: id должен быть целым числом")

        res = tuple(input(soo) for soo in Ms.ADD_TASK[1:])
        return id_, *res

    @staticmethod
    def run_show(task: Task) -> None:
        """Показ задачи"""
        id_, title, description, status, type_, created_at, updated_at, deadline = task.__dict__.values()

        print(f"\nНайдена задача\n")
        print(f"ID: {id_}")
        print(f"Заголовок: {title}")
        print(f"Описание: {description if description else 'Отсутствует'}")
        print(f"Статус: {status}")
        print(f"Дата создания: {ParsingDate(view_date=created_at).date_format}")
        print(f"Дата обновления: {ParsingDate(view_date=updated_at).date_format}")
        print(f"Дедлайн: {ParsingDate(view_date=deadline).date_format if deadline else 'Отсутствует'}")

    @staticmethod
    def run_edit(id_: int, app: TaskApplication) -> str:
        """Редактирование задачи"""
        user_in = input("Сразу после ввода атрибута вводите новое значение\n"
                        "Редактировать..\n"
                        "- id <id>\n"
                        "- title <title>\n"
                        "- description <description>\n"
                        "- deadline <deadline>\n"
                        ">>>  ")

        user_in = user_in.lower().strip().split()

        if user_in[0] not in EDIT_COMMANDS:
            raise e.IncorrectInput

        try:
            if user_in[0] == "id":
                attribute, value = user_in[0], int(user_in[1])
            else:
                attribute, value = user_in[0], " ".join(user_in[1:])
        except IndexError:
            raise e.IncorrectInput

        match attribute:
            case "id":
                app.edit_id(id_, value)
            case "title":
                app.edit_title(id_, value)
            case "description":
                app.edit_description(id_, value)
            case "deadline":
                app.edit_deadline(id_, value)


class OperationResult:
    """Класс сохранения текста"""
    def __init__(self, success: bool, reason: str = ""):
        self.success = success # результат
        self.reason = reason # текст


class DomainCLI:
    """
    Разбор команды и вызов соответствующего метода на переданном приложении (app).
    Объект app один и тот же — создаётся в main(), сюда только передаётся.
    """
    def __init__(self, app: TaskApplication, command: str, parts: list):
        self._app = app
        self._cmd = command
        self._parts = parts

    @staticmethod
    def _parse_id(parts: list) -> int:
        """Извлечь id из parts[1] для команд start/complete/cancel/delete."""
        try:
            return int(parts[1])
        except (IndexError, ValueError):
            raise e.IncorrectInput

    def run(self) -> OperationResult:
        """По имени команды вызвать нужный метод _app с нужными аргументами."""
        app = self._app
        cmd = self._cmd
        parts = self._parts
        IO = InputOutput()

        try:
            match cmd:
                case "start":
                    app.start(self._parse_id(parts))
                    return OperationResult(True, "Задача начата")
                case "complete":
                    app.complete(self._parse_id(parts))
                    return OperationResult(True, "Задача завершена")
                case "cancel":
                    app.cancel(self._parse_id(parts))
                    return OperationResult(True, "Задача отменена")
                case "delete":
                    app.delete(self._parse_id(parts))
                    return OperationResult(True, "Задача удалена")
                case "list":
                    tasks = app.list_tasks()
                    if not tasks:
                        return OperationResult(False, "Список задач пуст")
                    for task in tasks.values():
                        IO.run_show(task)
                    return OperationResult(True)
                case "add":
                    app.add(*IO.run_add())
                    return OperationResult(True, "Задача добавлена")
                case "show":
                    task = app.show(self._parse_id(parts))
                    IO.run_show(task)
                    return OperationResult(True)
                case "edit":
                    id_ = self._parse_id(parts)
                    app.show(id_)
                    IO.run_edit(id_, app)
                    return OperationResult(True, "Задача изменена")
                case "clear":
                    app.clear()
                    return OperationResult(True, "Список задач очищен")
                case "exit":
                    raise KeyboardInterrupt

        except e.TaskNotFind:
            return OperationResult(False, "Задача не найдена")
        except e.IncorrectInput:
            return OperationResult(False, "Некорректный ввод")
        except e.UnavailableID:
            return OperationResult(False, "ID уже используется")
        except e.TaskAlreadyExists:
            return OperationResult(False, "Задача уже существует")
        except e.TaskCannotStart:
            return OperationResult(False, "Задача не может быть начата")
        except e.TaskCannotCompleted:
            return OperationResult(False, "Задача не может быть завершена")
        except e.TaskCannotCancel:
            return OperationResult(False, "Задача не может быть отменена")
        except e.ParsingError:
            return OperationResult(False, "Ошибка парсинга. Повторите попытку снова")
        except e.DeadlineHasExpired:
            return OperationResult(False, "Дедлайн истек")
        except Exception as ex:
            return OperationResult(False, f"Ошибка: {str(ex)}")