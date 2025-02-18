from caldav_client import CaldavClient, EventExt
import config

if __name__ == '__main__':
    client = CaldavClient(url=config.caldav_url, username=config.username, password=config.password)
    event_list = []
    for calendar in client.calendars:
        events = calendar.events()
        event_list.extend(map(EventExt, events))
    sorted_events = sorted(event_list)
    for i in filter(lambda x: x.batch_id == '20250204', sorted_events):
        print(i.date, i.summary, i.parent.name, i.batch_id)
        # i.delete_event()
