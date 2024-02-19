from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

file_path = 'html_source.html'

with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

def main():
    create_ics(html_to_list_of_list(soup))


def html_to_list_of_list(soup):
    table = soup.find_all("td")[15:]
    return_list = []
    l = []
    date_pattern = re.compile(r'\d{4}\.\d{2}\.\d{2}')
    last_found_date = None
    separator_count = 0

    for row in table:
        text = row.text.strip()
        is_separator = not text
        if date_pattern.search(text):
            if last_found_date is not None:
                return_list.append([last_found_date] + l)
                l = []
            last_found_date = text
            separator_count = 0
        elif is_separator:
            separator_count += 1
        else:
            if separator_count > 0:
                l.append(separator_count)
                separator_count = 0
            l.append(text)

    if last_found_date is not None:
        if separator_count > 0:
            l.append(separator_count)
        return_list.append([last_found_date] + l)

    return return_list


def create_ics(data):
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Your Organization//Your Product//EN"
    ]

    for event_list in data:
        date_str = event_list[0]
        start_time = datetime.strptime(date_str, "%Y.%m.%d") + timedelta(hours=8)
        i = 1
        while i < len(event_list):
            item = event_list[i]
            if isinstance(item, int):
                start_time += timedelta(minutes=item * 15)
            else:
                end_time = start_time + timedelta(minutes=90)
                start_str = start_time.strftime("%Y%m%dT%H%M%S")
                end_str = end_time.strftime("%Y%m%dT%H%M%S")
                ics_content += [
                    "BEGIN:VEVENT",
                    f"DTSTART:{start_str}",
                    f"DTEND:{end_str}",
                    f"SUMMARY:{item}",
                    "END:VEVENT"
                ]
                start_time = end_time
            i += 1

    ics_content.append("END:VCALENDAR")

    ics_file_content = "\n".join(ics_content)
    with open("class_schedule.ics", "w") as file:
        file.write(ics_file_content)


if __name__ == '__main__':
    main()

