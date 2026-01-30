from datetime import datetime

from zoneinfo import ZoneInfo

from exceptions import ParsingError


class Clock:
    """Класс для работы с часами"""

    @staticmethod
    def _date_is_valid(date_string: str) -> tuple:
        """Функция для проверки и парсинга даты"""
        try:
            day, month, year, *time = tuple(map(int, date_string.split()))
        except (ValueError, TypeError):
            raise ParsingError

        DATE_DICT = {
            'day': 0,
            'month': 0,
            'year': 0,
            'hour': 0,
            'minute': 0,
            'second': 0,
        }

        try:
            DATE_DICT['day'] = day
            DATE_DICT['month'] = month
            DATE_DICT['year'] = year
            DATE_DICT['hour'] = time[0]
            DATE_DICT['minute'] = time[1]
            DATE_DICT['second'] = time[2]
        except IndexError:
            pass
        return DATE_DICT.get("year"), DATE_DICT.get("month"), DATE_DICT.get("day"), *tuple(DATE_DICT.values())[3:]

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
    def str_spaces(self):
        """Функция для получения строки с пробелами"""
        return self._now.strftime('%d %m %Y %H %M %S')

    @property
    def now(self):
        """Функция для получения текущего времени"""
        return self._now

    def advance(self, delta):
        """Функция для перемещения времени"""
        self._now += delta
        return self._now