"""
Обработчик команд CLI.
Импортирует только фасад TaskApplication и репозиторий — вся бизнес-логика в ядре.
"""

from src.task_application import TaskApplication
from src.domain_cli import DomainCLI

from messages.messages import Messages as Ms
from messages.commands import COMMANDS


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

    def handler(self, user_input: str) -> None:
        parts = user_input.lower().strip().split()

        if not parts:
            return

        cmd = parts[0]
        if cmd in COMMANDS:
            cli = self.handler_cli(self._app, cmd, parts)
            result = cli.run()
            try:
                if not result.success or result.success:
                    print(result.reason)
            except AttributeError:
                ...
        else:
            Handler.show_unknow_command()
