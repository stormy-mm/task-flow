from DOMAINS.types_task import SimpleBehavior, TimedBehavior


class TaskFactory:
    """Фабрика для создания задач"""
    @staticmethod
    def create_simple():
        return SimpleBehavior()

    @staticmethod
    def create_timed(deadline):
        return TimedBehavior(deadline)