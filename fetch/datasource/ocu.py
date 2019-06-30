#!/usr/bin/env python
# *-* coding: utf8 *-*

import requests
from bs4 import BeautifulSoup


class OcuFetcher():

    DATA_SOURCE = 'https://www.ocu.org/salud/cuidado-piel/test/cremas-solares/results'

    def __init__(self):
        self.data = []

    def fetch(self):
        page = requests.get(self.DATA_SOURCE)

        if page.status_code == 200:

            soup = BeautifulSoup(page.content, 'html.parser')

            # MAGIC HERE
            listing = soup.find('div', attrs={'data-type' : 'PsfProductListController'})

            if listing:
                elements = listing.find_all('div', attrs={'class' : 'recommended__listing__item'})

                if elements:
                    for counter, element in enumerate(elements):
                        print('Element ' + str(counter) + ' found:')

                        title = element.find('div', attrs={'class' : 'recommended__listing__item__title'})

                        if title:
                            data_title = title.find('a').text
                            data_link = title.find('a').get('href')
                            print('Link: ' + data_link)
                            print('Title: ' + data_title)

                        else:
                            print('No title')
                            continue

                        self.data.append({'title': data_title, 'link': data_link})

                        print

            print('Data to store')
            print(self.data)

    def run(self):
        print('Running Ocu Fetcher')
        self.fetch()


OcuFetcher().run()