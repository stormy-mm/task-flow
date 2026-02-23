from datetime import datetime

from zoneinfo import ZoneInfo

from my_app.common.exceptions import ParsingError


class Clock:
    """Класс для работы с часами"""

    @staticmethod
    def _date_is_valid(date_string: str) -> tuple:
        """Функция для проверки и парсинга даты"""
        try:
            day, month, year, *time = tuple(map(int, date_string.split()))
        except (ValueError, TypeError):
            raise ParsingError

        date_dict = {
            'day': 0,
            'month': 0,
            'year': 0,
            'hour': 0,
            'minute': 0,
            'second': 0,
        }

        try:
            date_dict['day'] = day
            date_dict['month'] = month
            date_dict['year'] = year
            date_dict['hour'] = time[0]
            date_dict['minute'] = time[1]
            date_dict['second'] = time[2]
        except IndexError:
            pass
        return date_dict.get("year"), date_dict.get("month"), date_dict.get("day"), *tuple(date_dict.values())[3:]

    @staticmethod
    def now() -> datetime:
        """Функция для получения текущего времени"""
        return datetime.now(ZoneInfo('UTC'))

    @staticmethod
    def set_deadline(date: str) -> datetime:
        """Функция для установки дедлайна"""
        return datetime(*Clock._date_is_valid(date), tzinfo=ZoneInfo('UTC'))


class FakeClock(Clock):
    """Класс для работы с часами в тестовых целях"""

    def __init__(self, start_time: datetime):
        """Функция для инициализации класса"""
        self._now = start_time

    @property
    def now(self):
        """Функция для получения текущего времени"""
        return self._now

    def advance(self, delta):
        """Функция для перемещения времени"""
        self._now += delta
        return self._now