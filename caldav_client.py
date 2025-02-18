from typing import List, Optional, Dict

import caldav
from caldav.objects import Event as BaseEvent
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import uuid
import config


class CaldavClient:
    def __init__(self, url: str, username: str, password: str) -> None:
        self.client = caldav.DAVClient(url=url, username=username, password=password)
        self.principal = self.client.principal()
        self.calendars = self.principal.calendars()

    def get_calendars(self, name: Optional[str] = None) -> List[caldav.Calendar]:
        if name:
            return [x for x in self.calendars if x.name == name]
        return self.calendars

    def get_calendar(self, name: str) -> Optional[caldav.Calendar]:
        calendars = self.get_calendars(name)
        if calendars:
            return calendars[0]
        return None

    def event_info(self, event: BaseEvent) -> Dict[str, str]:
        # 解析事件数据
        data = event.data
        data_list = data.split('\n')
        event_info = {}
        for line in data_list:
            if ':' in line:
                key, value = line.split(':', 1)
                event_info[key.strip()] = value.strip()
        return event_info

    def add_event(self, cal: caldav.Calendar, event_data: str, date: datetime, batch_id: Optional[str] = None) -> None:
        temp_cal = Calendar()
        temp_cal.add('version', '2.0')
        temp_cal.add('prodid', '-//Apple Inc.//iPhone OS 18.1//EN')
        temp_cal.add('calscale', 'GREGORIAN')

        # 创建事件
        event = Event()
        event.add('uid', str(uuid.uuid4()))
        event.add('dtstart', date, parameters={'VALUE': 'DATE'})
        event.add('dtend', date + timedelta(days=1), parameters={'VALUE': 'DATE'})
        event.add('created', datetime.now())
        event.add('dtstamp', datetime.now())
        event.add('last-modified', datetime.now())
        event.add('sequence', 0)
        event.add('summary', event_data)
        event.add('transp', 'OPAQUE')
        event.add('batch-id', batch_id)

        # 将事件添加到日历
        temp_cal.add_component(event)

        # 保存事件到服务器
        cal.save_event(temp_cal.to_ical().decode('utf-8'))


class EventExt(BaseEvent):
    def __init__(self, event=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        self.parent = event.parent
        self._date = None

    @property
    def batch_id(self):
        batch_id_content = self.event.vobject_instance.vevent.contents.get('batch-id')
        return batch_id_content[0].value if batch_id_content and len(batch_id_content) > 0 else None

    @property
    def date(self):
        if self._date is None:
            # 从事件中提取日期
            dtstart = self.event.vobject_instance.vevent.dtstart.value
            if isinstance(dtstart, datetime):
                self._date = dtstart.date()
            else:
                self._date = dtstart
        return self._date

    @property
    def summary(self):
        return self.event.vobject_instance.vevent.summary.value

    def __lt__(self, other):
        return self.date < other.date

    # 修改日程的方法，传入日期和日程内容，返回修改后的日程和日期
    def modify_event(self, date=None, summary=None):
        if date is not None:
            self.event.vobject_instance.vevent.dtstart.value = date
            # dtend也要修改，否则会报错
            self.event.vobject_instance.vevent.dtend.value = date + timedelta(days=1)
        if summary is not None:
            self.event.vobject_instance.vevent.summary.value = summary
        self.event.save()
        return self.event, date

    def delete_event(self):
        self.event.delete()


def dateObj(date: str):
    return datetime.strptime(date, '%Y-%m-%d').date()


if __name__ == '__main__':
    client = CaldavClient(url=config.caldav_url, username=config.username, password=config.password)
    event_list = []
    for calendar in client.calendars:
        events = calendar.events()
        for i in events:
            event_list.append(EventExt(i))
        # extended_events = [Event(event) for event in events]
    sorted_events = sorted(event_list)
    for i in sorted_events:
        # if i.date == dateObj('2024-11-09'):
        # i.modify_event(summary = '休息')
        print(i.date, i.summary, i.parent.name)
