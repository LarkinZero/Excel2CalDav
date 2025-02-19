import json
from datetime import datetime
from typing import Dict, Optional

import make_event
from caldav_client import CaldavClient
import config

class CustomClient(CaldavClient):
    def __init__(self, url: str, username: str, password: str) -> None:
        super().__init__(url, username, password)

    def _add_event_to_calendar(self, calendar_name: str, value: str, date: datetime, batch_id: Optional[str] = None) -> None:
        cal = super().get_calendar(calendar_name)
        if not cal:
            raise ValueError(f"Calendar '{calendar_name}' not found")
        print(value, date)
        super().add_event(cal, value, date, batch_id)

    def create_event(self, cal: Dict[str, str], batch_id: Optional[str] = None) -> None:
        try:
            for date_str, value in cal.items():
                date = make_event.date_format(date_str)
                if not isinstance(date, datetime):
                    raise ValueError(f"Invalid date format for {date_str}")
                if value == '休息':
                    self._add_event_to_calendar('休息', value, date, batch_id)
                else:
                    if "号窗口" in value:
                        self._add_event_to_calendar('服务台', value, date, batch_id)
                    else:
                        if value == '综合窗口B（网办件＋机动）':
                            value = "网办"
                        self._add_event_to_calendar('工作', value, date, batch_id)
        except Exception as e:
            print(f"Error creating event: {e}")
            # 可以选择抛出异常或记录日志


if __name__ == "__main__":
    tag = '20250219'
    client = CustomClient(url=config.caldav_url, username=config.username, password=config.password)
    calendar = {}
    calendar = make_event.generate_calendar_workdays(calendar,'./example/25年2月服务窗口排班表.xlsx')
    calendar = make_event.generate_calendar_holidays(calendar, './example/25年2月节假日排班表.xlsx')
    calendar = make_event.filter_calendar_by_month(calendar, 2)
    calendar = make_event.makeWeekend(calendar)
    print(json.dumps(calendar, indent=4, ensure_ascii=False))
    client.create_event(calendar, tag)
