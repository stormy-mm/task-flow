from my_app.repositories.task_repository import JsonTaskRepository
from my_app.application.task_application import TaskApplication
from my_app.cli.input_handlers import Handler


def main():
    """Главная функция: репозиторий и приложение создаются здесь, передаются в Handler."""
    repo = JsonTaskRepository("tasks.json") # инициализация json репозитория
    app = TaskApplication(repo) # инициализация приложения
    handler = Handler(app) # инициализация обработчика

    handler.show_greeting()
    while True:
        handler.user_handler(input(">>> "))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass