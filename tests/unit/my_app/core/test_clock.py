from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from task_flow.cli.date_parser import ParsingDate
from task_flow.common import exceptions as e


class TestParsingDate:
    """Класс для проверки парсинга даты"""

    def test_parsing_date(self):
        """Тест для проверки парсинга корректной даты"""
        assert (ParsingDate("20 3 2026 12 00").date ==
                         datetime(2026, 3, 20, 12, 0, 0, tzinfo=ZoneInfo('UTC')))
        assert (ParsingDate("20 3 2026").date ==
                         datetime(2026, 3, 20, 0, 0, 0, tzinfo=ZoneInfo('UTC')))

    def test_parsing_defective_date(self):
        """Тест для проверки парсинга некорректной даты"""
        with pytest.raises(e.ParsingError):
            ParsingDate("12 01 2026 12:00:00")
        with pytest.raises(e.ParsingError):
            ParsingDate("03/14/2026")