import csv
import os
import pandas as pd
from django.conf import settings

class ReportCsv:

    def __init__(self, directory, filename):
        self.directory = directory
        self.name = filename
        self.file_path = os.path.join(settings.BASE_DIR, 'assets', 'reports', directory)
        self.url = f'/static/reports/{directory}/{filename}'
        try:
            os.mkdir(self.file_path)
        except:
            pass
        self.filename = os.path.join(self.file_path, filename)

    def generate(self, titles=[], data=[]):
        with open(self.filename, 'w', encoding='utf-8', newline='') as report:
            writer = csv.writer(report)
            writer.writerow(titles)
            rows = []
            for dat in data:
                rows.append(list(dat.values()))
            writer.writerows(rows)
    
    def to_excel(self, datetime_cols=[]):           
        csv_f = pd.read_csv(self.filename)
        for dt in datetime_cols:
            csv_f[dt] = pd.to_datetime(csv_f[dt]).dt.strftime('%Y-%m-%d %H:%M%:%S')
        csv_f.to_excel(self.filename, index=False, header=True)
        self.url = f'/static/reports/{self.directory}/{self.name}'
    
    def to_html(self, datetime_cols=[]):
        csv_f = pd.read_csv(self.filename)
        for dt in datetime_cols:
            csv_f[dt] = pd.to_datetime(csv_f[dt])
        csv_f.to_html(self.filename, header=True, index=False)
        self.url = f'/static/reports/{self.directory}/{self.name}'
    