from datetime import datetime, timedelta
# import pandas as pd
from pathlib import Path
import logging 
logging.basicConfig(
    filename="resources/running.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)
logging.info("Start due")
RESOURCE_DIR=Path("resources")
RESOURCE_DIR.mkdir(exist_ok=True)
due_file=RESOURCE_DIR / "due.md"

# read task_info.md
def read_tasks_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines

def parse_tasks(lines):
    data = []
    course = ""
    for line in lines:
        line = line.strip()
        if line.startswith("## "):
            course = line[3:]
        elif "|" in line and not line.startswith("| Type"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) == 5:
                data.append((course, parts[1], parts[2], parts[3]))
    return data

# gain today date
today = datetime.today()

def get_due_within_days(data, days):
    upcoming = []
    threshold_date = today + timedelta(days=days)
    for task in data:
        course, description, weight, due = task
        if due in ["Multiple weeks"]:
            upcoming.append((course, description, due))
        else:
            try:
                due_datetime = datetime.strptime(due, "%d %b %Y")
                if today <= due_datetime <= threshold_date:
                    upcoming.append((course, description, due))
            except ValueError:
                continue
    return sorted(upcoming, key=lambda x: datetime.strptime(x[2], "%d %b %Y") if x[2] not in ["Multiple weeks", "Formal exam period"] else today)


tasks_lines = read_tasks_file("resources/task_info.md")
logging.info("Read task_info.md file.")
tasks_data = parse_tasks(tasks_lines)

# gain dues for next 7 days
upcoming_tasks = get_due_within_days(tasks_data, 7)

# generate due.md
due_text = "## Next Week Due\n\n"
html_text = """<html><head><title>Upcoming Due Tasks</title></head><body>
<h2>Upcoming Due Tasks in Next 7 Days</h2>
<ul>"""

for task in upcoming_tasks:
    due_text += f"- **{task[0]}**: {task[1]} (Due: {task[2]})\n"
    html_text += f"<li><strong>{task[0]}</strong>: {task[1]} (Due: {task[2]})</li>"

html_text += "</ul></body></html>"

# write due.md
with due_file.open("w", encoding="utf-8") as f:
    f.write(due_text)
    logging.info("Writing due.md")

# write due.html
with open("due.html", "w", encoding="utf-8") as f:
    f.write(html_text)
    logging.info("Writing due.html")

# print("due.md 和 due.html 文件已更新！") # Just for final check