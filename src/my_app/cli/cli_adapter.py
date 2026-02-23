from my_app.application.task_application import TaskApplication
from my_app.common import exceptions as e
from my_app.cli.input_output import InputOutput


class OperationResult:
    """Класс сохранения текста"""
    def __init__(self, success: bool, reason: str):
        self.success = success # результат
        self.reason = reason # текст


class DomainCLI:
    """
    Разбор команды и вызов соответствующего метода на переданном приложении (app).
    Объект app один и тот же — создаётся в main(), сюда только передаётся.
    """
    def __init__(self, app: TaskApplication, command: str, parts: list):
        self.app = app
        self.command = command
        self.parts = parts

    @staticmethod
    def _parse_id(parts: list) -> int:
        """Извлечь id из parts[1] для команд start/complete/cancel/delete."""
        try:
            return int(parts[1])
        except (IndexError, ValueError):
            raise e.IncorrectInput

    def run(self) -> OperationResult | None:
        """По имени команды вызвать нужный метод _app с нужными аргументами."""
        io = InputOutput()

        try:
            match self.command:
                case "start":
                    self.app.start(self._parse_id(self.parts))
                    return OperationResult(True, "Задача начата")
                case "complete":
                    self.app.complete(self._parse_id(self.parts))
                    return OperationResult(True, "Задача завершена")
                case "cancel":
                    self.app.cancel(self._parse_id(self.parts))
                    return OperationResult(True, "Задача отменена")
                case "delete":
                    self.app.delete(self._parse_id(self.parts))
                    return OperationResult(True, "Задача удалена")
                case "list":
                    tasks = self.app.list_tasks()
                    if not tasks:
                        return OperationResult(False, "Список задач пуст")
                    for task in tasks.values():
                        io.run_show(*task.__dict__.values())
                    return OperationResult(True, "")
                case "add":
                    self.app.add(*io.run_add())
                    return OperationResult(True, "Задача добавлена")
                case "show":
                    task = self.app.show(self._parse_id(self.parts))
                    io.run_show(*task.__dict__.values())
                    return OperationResult(True, "")
                case "edit":
                    id_ = self._parse_id(self.parts)
                    self.app.show(id_)
                    attribute, value = io.run_edit()
                    match attribute:
                        case "id":
                            self.app.edit_id(id_, value)
                        case "title":
                            self.app.edit_title(id_, value)
                        case "description":
                            self.app.edit_description(id_, value)
                        case "deadline":
                            self.app.edit_deadline(id_, value)
                    return OperationResult(True, "Задача изменена")
                case "clear":
                    self.app.clear()
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
            return OperationResult(False, "Ошибка парсинга")
        except e.DeadlineHasExpired:
            return OperationResult(False, "Дедлайн истек")
        except ValueError:
            return OperationResult(False, "Ошибка: id должен быть целым числом")
        except Exception as ex:
            return OperationResult(False, f"Ошибка: {str(ex)}")