from src.repository_task import JsonTaskRepository
from src.task_application import TaskApplication
from src.handlers import Handler


def main():
    """Главная функция: репозиторий и приложение создаются здесь, передаются в Handler."""
    repo = JsonTaskRepository("tasks.json")
    app = TaskApplication(repo)
    handler = Handler(app)

    Handler.show_greeting()
    while True:
        us_in = input(">>> ")
        handler.handler(us_in)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass