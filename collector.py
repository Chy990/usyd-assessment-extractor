import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import re
import markdown
from PyQt5.QtGui import QIcon
import requests
from bs4 import BeautifulSoup 

from datetime import datetime, timedelta # provided for due.py

RESOURCES_DIR=Path("resources")
RESOURCES_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename="resources/running.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)
logging.info("Start collector")
unit_codes_file = Path("unit_codes.txt")

if unit_codes_file.exists():
    with unit_codes_file.open("r") as file:
        unit_codes = [line.strip() for line in file if line.strip()]  
else:
    unit_codes = []  # if no file exists, save empty

# print(unit_codes)  # print check

# table = '//*[@id="assessment-table"]'
output_file = RESOURCES_DIR / "task_info.md" 
html_output_file=Path("task_info.html")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}


def extract_table_content(html_content, unit_code, output_file):
    soup = BeautifulSoup(html_content, 'html.parser')
    table=soup.find("table",id="assessment-table")
    if not table:
        logging.error(f"Cannot found {unit_code} table")
        return 
    
    # extract table head
    thead = table.find('thead')
    headers = [th.get_text(strip=True) for th in thead.find_all('th')]

    # continue write 'a'
    with open(output_file, 'a', encoding='utf-8') as md_file:
        md_file.write(f"\n## {unit_code}\n\n")
        md_file.write('| ' + ' | '.join(headers) + ' |\n')
        md_file.write('| ' + ' | '.join(['---'] * len(headers)) + ' |\n')

        # read all <tbody>
        all_tbody = table.find_all('tbody')
        if not all_tbody:
            logging.error(f"Cannot find tbody for {unit_code}")
            return

        for tbody in all_tbody:
            for row in tbody.find_all('tr', class_='primary'):
                cells = []
                for cell in row.find_all(['th', 'td']):
                    due_date_span = cell.find('span', class_='dueDate')
                    if due_date_span:
                        due_text = due_date_span.get_text(strip=True)
                        match = re.search(r'(\d{2} \w{3} \d{4})', due_text)
                        cells.append(match.group(1) if match else due_text)
                    else:
                        b_tag = cell.find('b')
                        cells.append(b_tag.get_text(strip=True) if b_tag else cell.get_text(strip=True))

                md_file.write('| ' + ' | '.join(cells) + ' |\n')
        else:
            logging.error(f"Cannot find tbody for {unit_code}")

def convert_markdown_to_html(md_file, html_file):
    """convert markdown to html with css"""
    with open(md_file, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    html_content = markdown.markdown(markdown_text, extensions=['tables'])  

    css_style = """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h2 { color: #2c3e50; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
    """

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Assessment Table</title>
        {css_style}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    logging.info(f"Markdown convert to {html_file}")


class ScraperThread(QThread):
    update_progress = pyqtSignal(int, str) 
    finished = pyqtSignal() 

    def __init__(self, unit_codes, output_file,html_output_file):
        super().__init__()
        self.unit_codes = unit_codes
        self.output_file = output_file
        self.html_output_file = html_output_file

    def run(self):
        if self.output_file.exists():
            open(self.output_file,"w").close()
            logging.info(f"{self.output_file} clear")
        
        
            
        total_units = len(self.unit_codes)
        for i, unit_code in enumerate(self.unit_codes, start=1):
            if self.isInterruptionRequested():
                break
            self.scrape_website(unit_code, self.output_file)
            progress = int((i / total_units) * 100)
            self.update_progress.emit(progress, f"{i}/{total_units}")
        convert_markdown_to_html(self.output_file, self.html_output_file)
        self.finished.emit()

    def scrape_website(self, unit_code, output_file):
        url = f"https://www.sydney.edu.au/units/{unit_code}/2025-S1C-ND-CC"

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 404:
                logging.warning(f"Unit {unit_code} not found (404)")
                return 
            
            response.raise_for_status() 
            
            # save html
            html_output_file.write_text(response.text, encoding="utf-8")

            extract_table_content(response.text, unit_code, output_file)
            logging.info(f"Saved {unit_code} assessment into {output_file}")

        except requests.RequestException as e:
            logging.error(f"Error: {e}")

class App(QWidget):
    def __init__(self, unit_codes, output_file, html_output_file):
        super().__init__()
        self.unit_codes = unit_codes
        self.output_file = output_file
        self.html_output_file = html_output_file
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Process')
        self.setWindowIcon(QIcon('resources/collector_icon.ico'))
        self.setGeometry(300, 300, 400, 150)
        self.setFixedSize(400,150)

        layout = QVBoxLayout()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel('初始化', self)
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        self.stop_button = QPushButton('终止程序', self)
        self.stop_button.clicked.connect(self.stop_scraping)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        self.scraper_thread = ScraperThread(self.unit_codes, self.output_file, self.html_output_file)
        self.scraper_thread.update_progress.connect(self.update_progress)
        self.scraper_thread.finished.connect(self.on_finished)
        self.scraper_thread.start()

    def update_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.progress_label.setText(text)

    def stop_scraping(self):
        self.scraper_thread.requestInterruption()
        self.scraper_thread.quit()
        self.close()

    def on_finished(self):
        self.progress_label.setText('已完成')
        self.stop_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('resources/collector_icon.ico'))
    ex = App(unit_codes, output_file,html_output_file)
    ex.show()
    sys.exit(app.exec_())