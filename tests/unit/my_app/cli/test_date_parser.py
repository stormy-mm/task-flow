from datetime import datetime
from zoneinfo import ZoneInfo

from task_flow.cli.date_parser import ParsingDate

def test_date_parser():
    """Тест для проверки парсинга даты"""
    assert ParsingDate(view_date=datetime(2020, 1, 1, tzinfo=ZoneInfo('UTC'))).date_format == '01.01.2020 00:00:00'