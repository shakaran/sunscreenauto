#!/usr/bin/env python
# *-* coding: utf8 *-*

import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import sys
import os

class MifarmaFetcher():

    DATA_SOURCE = 'https://www.mifarma.es/cosmetica-y-belleza/sol/protectores-solares/'
    IMAGES_PATH = 'data/mifarma/'
    CSV_PATH = 'data/mifarma.csv'

    def __init__(self):
        self.data = []
        self.global_counter = 0

    def export_csv(self):
        with open('self.CSV_PATH', mode='a+', encoding='utf8') as csv_file:

            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            csv_writer.writerow(['title', 'quality_overall',
                         'price', 'picture_image', 'laboratory', 'laboratory_logo'])

            for row in self.data:
                csv_writer.writerow([row['title'], row['quality_overall'], row['price'], row['picture_image'],
                                     row['laboratory'], row['laboratory_logo']])

    def fetch(self, page_link = None):

        if not page_link:
            page_link = self.DATA_SOURCE

        page = requests.get(page_link)

        if page.status_code == 200:

            if not page.encoding.lower() in 'utf-8':
                print('Warning: Content page encoding is not in utf8-format')
                sys.exit(1)

            soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), 'html.parser')

            listing = soup.find('div', attrs={'class' : 'listado-completo'})

            if listing:
                elements = listing.find_all('li', attrs={'class' : 'item'})

                if elements:
                    for counter, element in enumerate(elements):
                        self.global_counter += 1
                        print('Global: ' + str(self.global_counter) + ' Element in page ' + str(counter) + ' found:')

                        (data_link, data_title) = self.fetch_title_link(element)

                        data_quality_overall = self.fetch_quality_overall(element)

                        price = self.fetch_specs(element)

                        data_picture_image = self.fetch_picture_image(element)

                        (laboratory_name, logo) = self.fetch_laboratory(element)

                        self.data.append(
                            {
                                'title': data_title,
                                'link': data_link,
                                'quality_overall': data_quality_overall,
                                'price': price,
                                'picture_image': data_picture_image,
                                'laboratory': laboratory_name,
                                'laboratory_logo': logo

                            })

                        print

                self.check_next_page(soup)

    def fetch_title_link(self, element):
        title = element.find('h2', attrs={'class' : 'product-name'})

        if title:
            data_title = title.find('a').text
            data_link = title.find('a').get('href')
            print('Link: ' + data_link)
            print('Title: ' + data_title)
            return (data_link, data_title)
        else:
            print('No title')
            return (None, None)

    def fetch_quality_overall(self, element):
        quality_overall = element.find('div', attrs={'class' : 'rating'})
        data_quality_overall = None

        if quality_overall:
            data_quality_overall = quality_overall.attrs["style"].replace('width:', '')

            print('Quality Overall: ' + data_quality_overall)


        return data_quality_overall

    def fetch_specs(self, element):
        specs = element.find('span', attrs={'class' : 'price'})
        price = None
        if specs:
            price = specs.text.strip()
            print('Price: ' + price)
        return price

    def fetch_picture_image(self, element):
        picture_image = element.find('a', attrs={'class' : 'product-image'})

        data_picture_image = None
        if picture_image:
            data_picture_image = picture_image.find('img').get('src').strip()
            print('Picture Image: ' + data_picture_image)

            self.download_file_image(data_picture_image)

        return data_picture_image


    def download_file_image(self, image_url):
        page_image = requests.get(image_url, stream=True)
        if page_image.status_code == 200:
            #print(Path(image_url).stem)

            if not os.path.exists(self.IMAGES_PATH):
                Path(self.IMAGES_PATH).mkdir(parents=True, exist_ok=True)

            with open(self.IMAGES_PATH + Path(image_url).stem + '.jpg', 'wb') as image_file:
                for chunk in page_image:
                    image_file.write(chunk)


    def fetch_laboratory(self, element):
        laboratory = element.find('div', attrs={'class' : 'amshopby-link'})

        laboratory_name = ''
        logo = ''

        if laboratory:
            logo = laboratory.find('img').get('src').strip()
            print('Laboratory Logo Link: ' + logo)
            laboratory_name = laboratory.find('img').get('title')
            print('Laboratory Name: ' + laboratory_name)

        return (laboratory_name, logo)

    def check_next_page(self, soup):
        next_page =soup.find('div', attrs={'class' : 'pages'})

        if next_page:
            next_page_link = next_page.find('a', attrs={'class' : 'i-next'})

            if next_page_link:
                next_page_link_final = next_page_link.get('href')
                print('Processing next page: ' + next_page_link_final)
                self.fetch(next_page_link_final)


    def run(self):
        if sys.version_info[0] < 3:
            raise Exception("You need use Python 3 to execute this script. You have: Python" + str(sys.version_info[0]))

        print('Running MiFarma Fetcher')
        self.fetch(None)

        print('Data to store')
        print(self.data)

        print('Exporting to CSV')
        self.export_csv()
        print('Done')


MifarmaFetcher().run()
