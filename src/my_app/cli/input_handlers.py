"""
Обработчик команд cli.
Импортирует только фасад TaskApplication и DomainCLI — вся бизнес-логика в ядре.
"""

from my_app.application.task_application import TaskApplication
from my_app.cli.cli_adapter import DomainCLI
from my_app.common.messages import Messages as Ms, COMMANDS


class Handler:
    """Обработчик: получает приложение (фасад) и делегирует ему команды."""
    def __init__(self, app: TaskApplication):
        self._app = app
        self.handler_cli = DomainCLI

    @staticmethod
    def show_unknow_command() -> None:
        """Вывод о неизвестной команде"""
        print(Ms.UNKNOW_COMMAND)

    @staticmethod
    def show_greeting() -> None:
        """Вывод приветствия (используется из main)."""
        print(Ms.GREETING)

    def user_handler(self, user_input: str) -> None:
        """Обработчик пользовательского ввода"""
        parts = user_input.lower().strip().split()

        if not parts:
            return

        cmd = parts[0]
        if cmd in COMMANDS:
            cli = self.handler_cli(self._app, cmd, parts) # Приложение, команда, аргументы

            # Здесь происходит обработка команды
            result = cli.run()

            try:
                if result.reason:
                    print(result.reason) # вывод результата
            except AttributeError:
                ...
        else:
            Handler.show_unknow_command()