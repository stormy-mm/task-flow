from datetime import datetime

from DOMAINS.parsing import ParsingDate

from DOMAINS.saving_a_task import Task

from DOMAINS.time_clock import Clock

from DOMAINS.types_task import SimpleBehavior, TimedBehavior


class TaskFactory:
    """Фабрика для создания задачи"""

    @staticmethod
    def create_task(
            id_task: int,
            title: str,
            description: str,
            deadline: str | None,
            date: datetime = Clock.now()
    ) -> Task:
        """Фабричный метод для создания задачи"""
        behaviour = SimpleBehavior()
        if not deadline is None:
            deadline = ParsingDate(deadline)
            behaviour = TimedBehavior(deadline.date)
            deadline = deadline.date_format

        return Task(
            id_task=id_task,
            title=title,
            description=description,
            behaviour=behaviour,
            deadline=deadline,
            date=date,
        )