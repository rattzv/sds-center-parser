import requests
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from typing import List
from utils.utils import is_first_run, print_template, random_sleep, update_progress
from utils.csv_exporter import extract_exists_from_csv, read_report_file, write_to_csv
from models.product import Product


def parse_sitemap_xml(sitemap_content: bytes) -> List:
    root = ET.fromstring(sitemap_content)
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    links = [element.text for element in root.findall('ns:url/ns:loc', namespace)
             if 'https://www.sds-center.ru/goods/' in element.text]

    return links


def parse_characteristics(table):
    characteristics = {}

    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            name = cells[0].text.strip()
            value = cells[1].strong.text.strip()
            characteristics[name] = value
    return characteristics


def start_site_parsing(links):
    success_count = 0
    failure_count = 0
    skipped_count = 0

    all_characteristics = []

    first_run_status = is_first_run()
    exists_urls = []
    if not first_run_status:
        rows = extract_exists_from_csv()
        if len(rows) > 0:
            if 'article' in rows[0]:
                headers = rows[0]
                for row in rows[1:]:
                    exists_urls.append(row[5])
                    restore_row = dict(zip(headers, row))
                    all_characteristics.append(restore_row)

    for iteration, link in enumerate(links):
        try:
            if link in exists_urls:
                skipped_count += 1
                print(print_template("Link has been checked before, skip ({})".format(link)))
                continue

            response = requests.get(link)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            if soup.find('div', 'breadcrumbs') is None or soup.find('div', 'product-card') is None:
                print(print_template("Error loading html page, key elements not found ({}).".format(link)))
                random_sleep(10)
                continue

            product = Product()
            product.url = link

            categories_elements = soup.find('div', 'breadcrumbs').find_all('span', attrs={'itemprop': 'name'})
            product.categories = ', '.join([span.text.strip() for span in categories_elements])

            product_card = soup.find('div', 'product-card')

            product.name = product_card.find('h1', attrs={'itemprop': 'name'}).text.strip()
            product.article = product_card.find('span', attrs={'id': 'article'}).text.strip()
            product.price = product_card.find('div', 'contr2').find('span', attrs={'itemprop': 'price'}).text.strip()
            product.unit = product_card.find('div', 'contr2').find('p').find('span').find('strong').text.strip()

            characteristics = parse_characteristics(product_card.find('div', 'short').find('table'))
            characteristics = {**vars(product), **characteristics}

            # Добавить характеристики в список
            all_characteristics.append(characteristics)

            # Записать характеристики в CSV файл
            write_to_csv(all_characteristics, first_run_status)
            update_progress(iteration, len(links), link)
            success_count += 1
            # random_sleep(1)
        except Exception as e:
            failure_count += 1
            print(print_template("Unhandled exception: {}".format(e)))
            random_sleep(10)

    return success_count, failure_count, skipped_count
