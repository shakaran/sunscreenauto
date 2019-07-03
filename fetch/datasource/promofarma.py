#!/usr/bin/env python
# *-* coding: utf8 *-*

import requests
from bs4 import BeautifulSoup
import csv

class PromofarmaFetcher():

    DATA_SOURCE = 'https://www.promofarma.com/cosmetica/proteccion-solar'

    def __init__(self):
        self.data = []
        self.global_counter = 0

    def export_csv(self):
        with open('../../data/promofarma.csv', mode='a+', encoding='utf8') as csv_file:


    def fetch(self, page_link = None):
        if not page_link:
            page_link = self.DATA_SOURCE

        page = requests.get(page_link)

        if page.status_code == 200:

    def run(self):
        print('Running Profarma Fetcher')
        self.fetch(None)

        print('Data to store')
        print(self.data)

        print('Exporting to CSV')
        self.export_csv()
        print('Done')
