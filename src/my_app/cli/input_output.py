from datetime import datetime

from my_app.cli.date_parser import ParsingDate
from my_app.common.messages import EDIT_COMMANDS, Messages as Ms
from my_app.common import exceptions as e


class InputOutput:
    """Класс вывода и ввода"""

    @staticmethod
    def _default_parsing_date(datetime_user: datetime) -> str:
        """Парсинг даты по умолчанию"""
        return ParsingDate(view_date=datetime_user).date_format

    @staticmethod
    def run_add() -> tuple:
        """Добавление задачи"""
        while True:
            try:
                id_ = int(input(Ms.ADD_TASK[0]))
                break
            except ValueError:
                print("Ошибка: id должен быть целым числом")

        result_user = tuple(input(message) for message in Ms.ADD_TASK[1:])
        return id_, *result_user

    @staticmethod
    def run_show(id_, title, description, status, type_task, created_at, updated_at, deadline) -> None:
        """Показ задачи"""
        print(f"\nЗадача № {id_}")
        print(f"Заголовок: {title}")
        print(f"Описание: {description}")
        print(f"Статус: {status}")
        print(f"Дата создания: {InputOutput._default_parsing_date(created_at)}")
        print(f"Дата обновления: {InputOutput._default_parsing_date(updated_at)}")
        print(f"Дедлайн: {InputOutput._default_parsing_date(deadline) if deadline else ""}")

    @staticmethod
    def run_edit() -> tuple:
        """Редактирование задачи"""
        print("Сразу после ввода атрибута вводите новое значение\n"
                "Редактировать..\n"
                "- id <id>\n"
                "- title <title>\n"
                "- description <description>\n"
                "- deadline <deadline>\n")
        user_in = input(">>>  ").strip().split()

        if not user_in:
            raise e.IncorrectInput

        cmd = user_in[0].lower()
        if cmd not in EDIT_COMMANDS:
            raise e.IncorrectInput

        try:
            if cmd == "id":
                return cmd, int(user_in[1])
            return cmd, " ".join(user_in[1:])
        except ValueError, IndexError:
            raise e.IncorrectInput