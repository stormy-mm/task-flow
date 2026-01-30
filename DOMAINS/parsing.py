from DOMAINS.time_clock import Clock


class ParsingDate:
    """Класс для парсинга даты"""

    def __init__(self, date_string):
        """Функция для инициализации класса"""
        self._date = Clock.set_deadline(date_string)

    @property
    def date(self):
        """Функция для получения даты"""
        return self._date

    @property
    def date_format(self):
        """Функция для получения даты в формате строки"""
        return self._date.strftime("%d.%m.%Y %H:%M:%S")