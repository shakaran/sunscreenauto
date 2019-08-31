#!/usr/bin/env python
# *-* coding: utf8 *-*

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv
import os
import sys

class OcuFetcher():

    DATA_SOURCE = 'https://www.ocu.org/salud/cuidado-piel/test/cremas-solares/results'
    IMAGES_PATH = 'data/ocu/'
    CSV_PATH = 'data/ocu.csv'

    def __init__(self):
        self.data = []
        self.global_counter = 0

    def export_csv(self):
        with open(self.CSV_PATH, mode='a+', encoding='utf8') as csv_file:

            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            csv_writer.writerow(['title', 'quality_overall', 'quality_overall_info', 'spec_content',
                         'spec_spf', 'spec_container', 'provider_value',
                         'picture_image', 'laboratory', 'users', 'tagging'])

            for row in self.data:
                csv_writer.writerow([row['title'], row['quality_overall'], row['quality_overall_info'], row['spec_content'], \
                                     row['spec_spf'], row['spec_container'], row['provider_value'], row['picture_image'],    \
                                     row['laboratory'], row['users'], row['tagging']])

    def fetch(self, page_link = None):

        if not page_link:
            page_link = self.DATA_SOURCE

        page = requests.get(page_link)

        if page.status_code == 200:

            if not page.encoding in 'utf-8':
                print('Warning: Content page enconding is not in utf8-format')
                sys.exit(1)

            soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), 'html.parser')

            listing = soup.find('div', attrs={'data-type' : 'PsfProductListController'})

            if listing:
                elements = listing.find_all('div', attrs={'class' : 'recommended__listing__item'})

                if elements:
                    for counter, element in enumerate(elements):
                        self.global_counter += 1
                        print('Global: ' + str(self.global_counter) + ' Element in page ' + str(counter) + ' found:')

                        (data_link, data_title) = self.fetch_title_link(element)

                        data_quality_overall = self.fetch_quality_overall(element)

                        data_quality_overall_info = self.fetch_quality_overall_info(element)

                        (data_spec_content, data_spec_spf, data_spec_container) = self.fetch_specs(element)

                        data_provider_value = self.fetch_provider_value(element)

                        data_picture_image = self.fetch_picture_image(element)

                        (laboratory, users, tagging) = self.fetch_quality_badge_info(element)

                        # @TODO Improve me please!
                        self.fetch_inside_page(data_link)

                        self.data.append(
                            {
                                'title': data_title,
                                'link': data_link,
                                'quality_overall': data_quality_overall,
                                'quality_overall_info': data_quality_overall_info,
                                'spec_content': data_spec_content,
                                'spec_spf': data_spec_spf,
                                'spec_container': data_spec_container,
                                'provider_value': data_provider_value,
                                'picture_image': data_picture_image,
                                'laboratory': laboratory,
                                'users': users,
                                'tagging': tagging,
                            })

                        print

                self.check_next_page(soup)

    def fetch_inside_page(self, inside_link):
        if inside_link:
            page = requests.get('https://www.ocu.org' + inside_link)

        if page.status_code == 200:

            # @TODO REFACTOR ME HERE in functions
            soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), 'html.parser')

            location = soup.find('div', attrs={'class' : 'recommended-detail__floating__wtb align-central'})

            print('Location: ' + location.text.strip().replace('Localización ', ''))

            item_images = soup.find_all('div', attrs={'class' : 'owl-detail-item__picture'})

            for image in item_images:
                print('Item image: ' + image.find('img').get('src'))

                """ @TODO Challenge
                ul              split split--striped split--padded

                <strong data-selector="PC_FeatureValue" class="split__value split__narrow deci">
                Sí
                </strong>

                <h3 data-selector="PC_GroupLabel" class="epsilon">Ingredientes</h3>
                """


    def fetch_title_link(self, element):
        title = element.find('div', attrs={'class' : 'recommended__listing__item__title'})

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
        quality_overall = element.find('span', attrs={'class' : 'quality-badge__value'})

        if quality_overall:
            data_quality_overall = quality_overall.text.strip()
            print('Quality Overall: ' + data_quality_overall)

        return data_quality_overall

    def fetch_quality_overall_info(self, element):
        quality_overall_info = element.find('span', attrs={'class' : 'quality-badge__info'})

        if quality_overall_info:
            data_quality_overall_info = quality_overall_info.text.strip().replace('CALIDAD', '')
            print('Quality Overall Info: ' + data_quality_overall_info)

        return data_quality_overall_info

    def fetch_specs(self, element):
        specs = element.find('div', attrs={'class' : 'recommended__listing__item__specs'})

        if specs:
            data_specs = specs.find_all('p')

            if data_specs[0]:
                data_spec_content = data_specs[0].text.replace('Contenido: ', '').strip()
                print('Content: ' + data_spec_content)

            if data_specs[1]:
                data_spec_spf = data_specs[1].text.replace('SPF: ', '').strip()
                print('SPF: ' + data_spec_spf)

            data_spec_container = ''
            if len(data_specs) > 2:
                data_spec_container = data_specs[2].text.replace('Precio por envase: ', '').strip()
                print('Price by container: ' + data_spec_container)

        return (data_spec_content, data_spec_spf, data_spec_container)

    def fetch_provider_value(self, element):
        provider_value = element.find('div', attrs={'class' : 'recommended__calltoaction__provider-value'})

        if provider_value:
            data_provider_value = provider_value.text.strip()

            print('Provider value: ' + data_provider_value)

        return data_provider_value

    def download_file_image(self, image_url):
        page_image = requests.get(image_url, stream=True)
        if page_image.status_code == 200:
            print(Path(image_url).stem)

            if not os.path.exists(self.IMAGES_PATH):
                os.mkdir(self.IMAGES_PATH)

            with open(self.IMAGES_PATH + Path(image_url).stem + '.jpg', 'wb') as image_file:
                for chunk in page_image:
                    image_file.write(chunk)

    def fetch_picture_image(self, element):
        picture_image = element.find('a', attrs={'class' : 'recommended__picture-image'})

        if picture_image:
            data_picture_image = 'https:' + picture_image.find('img').get('src').strip()
            print('Picture Image: ' + data_picture_image)

            self.download_file_image(data_picture_image)


        return data_picture_image

    def fetch_quality_badge_info(self, element):
        quality_badge = element.find('div', attrs={'class' : 'quality-badge'})

        if quality_badge:
            product_id =  quality_badge.get('data-selector').replace('open-quality-box-', '')
            print('Selector: ' + product_id)

            ajax_page = requests.post('https://www.ocu.org/ProductSelectorsAPI/PsfQualityBoxes/RenderQualityBox/084056b0-d25d-4df8-8036-210e53b06fe8',
                         data = {'productId': product_id, 'mainPageId': '43ee393ea9394a7f8d7d442d663fe29f', 'isModel': 'false' },
                         headers = {'x-requested-with': 'XMLHttpRequest'})

            if ajax_page.status_code == 200:
                ajax_content = ajax_page.json()
                ajax_content_soup = ajax_content['Updates'][0]['Html']

                ajax_soup = BeautifulSoup(ajax_content_soup, 'html.parser')

                boxes = ajax_soup.find_all('span', attrs={'class' : 'quality-boxes__indicators__item-bar-value'})

                if boxes:
                    laboratory = boxes[0].text
                    users = boxes[1].text
                    tagging = boxes[2].text

                    print('Laboratory: ' + laboratory)
                    print('Users: ' + users)
                    print('Tagging: ' + tagging)

        return (laboratory, users, tagging)


    def check_next_page(self, soup):
        next_page =soup.find('li', attrs={'class' : 'pagination__item--next'})

        if next_page:
            next_page_link = 'https://www.ocu.org/' + next_page.a.get('href')
            print('Processing next page: ' + next_page_link)
            self.fetch(next_page_link)

    def run(self):
        if sys.version_info[0] < 3:
            raise Exception("You need use Python 3 to execute this script. You have: Python" + str(sys.version_info[0]))

        print('Running Ocu Fetcher')
        self.fetch(None)

        print('Data to store')
        print(self.data)

        print('Exporting to CSV')
        self.export_csv()
        print('Done')


OcuFetcher().run()