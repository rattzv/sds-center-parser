import csv
import os
from collections import OrderedDict


from utils.utils import check_reports_folder_exist


def create_report_file():
    reports_folder = check_reports_folder_exist()
    report_file = os.path.join(reports_folder, "sds-center-parse.csv")
    file = open(report_file, 'w', newline='')
    writer = csv.writer(file, delimiter=';')
    writer.writerow([])
    return writer


def read_report_file():
    reports_folder = check_reports_folder_exist()
    report_file = os.path.join(reports_folder, "sds-center-parse.csv")
    file = open(report_file, 'r+', newline='')
    reader = csv.reader(file)
    return reader


def write_to_csv(characteristics, run_status):
    reports_folder = check_reports_folder_exist()
    report_file = os.path.join(reports_folder, "sds-center-parse.csv")

    unique_characteristics = OrderedDict()
    for chars in characteristics:
        unique_characteristics.update(chars)

    with open(report_file, "w", newline='', encoding='utf-8') as csvfile:
        fieldnames = list(unique_characteristics)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for chars in characteristics:
            writer.writerow(chars)


def extract_exists_from_csv():
    reports_folder = check_reports_folder_exist()
    report_file = os.path.join(reports_folder, "sds-center-parse.csv")

    rows = []
    with open(report_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            rows.append(row)
    return rows
