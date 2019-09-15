#!/usr/bin/env python3
# *-* coding: utf8 *-*

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv
import os
import sys

class PromofarmaFetcher():

    DATA_SOURCE = 'https://www.promofarma.com/es/search?q=protectores+solares&page='
    IMAGES_PATH = 'data/promofarma/'
    CSV_PATH = 'data/promofarma.csv'

    def __init__(self):
        self.data = []
        self.global_counter = 0
        self.global_counter_page = 1

    def export_csv(self):
        with open(self.CSV_PATH, mode='w+', encoding='utf8') as csv_file:

            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            csv_writer.writerow(['title', 'provider_value', 'actually_discount' , 'link' , \
                'rate_value', 'image_one','description','data_professional_advice', \
                'coupon_info', 'volume', 'tags', 'content_description', 'content_instructions', 'content_composition', 'provider'])

            for row in self.data:
                csv_writer.writerow([row['title'], row['provider_value'],row['data_discount_web'], row['link'], \
                     row['rate_value'],row['image_one'], row['description'], row['data_professional_advice'], \
                     row['coupon_info'], row['volume'], row['tags'], \
                     row['content_description'], row['content_instructions'], row['content_composition'], row['provider']
                     ])

    def fetch(self, page_link = None):

        if not page_link:
            page_link = self.DATA_SOURCE + str(self.global_counter_page)

        page = requests.get(page_link)

        if page.status_code == 200:

            if not page.encoding.lower() in 'utf-8':
                print('Warning: Content page encoding is not in utf8-format', page.encoding )
                sys.exit(1)

            self.global_counter_page += 1
            soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), 'html.parser')

            listing = soup.find('section', attrs={'class' : 'search-list'})

            if listing:
                elements = listing.find_all('div', attrs={'class' : 'item-container'})

                if elements:
                    for counter, element in enumerate(elements):
                        self.global_counter += 1
                        print('Global: ' + str(self.global_counter) + ' Element in page ' + str(counter) + ' found:')

                        (data_link, data_title) = self.fetch_title_link(element)

                        data_provider_value = self.fetch_provider_value(element)

                        data_discount_web = self.fetch_actually_discount(element)

                        rate_value = self.fetch_rate_value(element)

                        (image_one, description, data_professional_advice) = self.fetch_inside_page(data_link)

                        (coupon_info, volume, tags, content_description, content_instructions, content_composition) = self.get_item_page(data_link)

                        self.data.append(
                            {
                                'title': data_title,
                                'link': data_link,
                                'data_url': data_link,
                                'provider_value': data_provider_value,
                                'data_discount_web': data_discount_web,
                                'rate_value': rate_value,
                                'image_one': image_one,
                                'description': description,
                                'data_professional_advice': data_professional_advice,
                                'coupon_info': coupon_info,
                                'volume': volume,
                                'tags': tags,
                                'content_description': content_description,
                                'content_instructions': content_instructions,
                                'content_composition': content_composition,
                                'provider': 'promofarma'
                            })

                        print

                self.check_next_page(soup)

    def get_item_page(self, url):
        page = requests.get(url)

        coupon_info = None
        volume = None
        tags = None
        content_description = None
        content_instructions = None
        content_composition = None

        if page.status_code == 200:

            if not page.encoding.lower() in 'utf-8':
                print('Warning: Content page encoding is not in utf8-format')
                sys.exit(1)

            soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), 'html.parser')

            product_info = soup.find('div', attrs={'class' : 'product-info'})

            if product_info:
                coupon_info = product_info.find('p', attrs={'data-qa-ta' : 'couponInfo'}).text
                volume = product_info.find('p', attrs={'class' : 'volume'}).text
                tags = product_info.find('li', attrs={'class' : 'list-inline-item'}).text

            wrapper_description = soup.find('div', attrs={'class' : 'wrapper-description'})

            if wrapper_description:
                content_description = wrapper_description.find('div', attrs={'id' : 'content-description'}).text
                content_instructions = wrapper_description.find('div', attrs={'id' : 'content-instructions'}).text
                content_composition = wrapper_description.find('div', attrs={'id' : 'content-composition'}).text


        return (coupon_info, volume, tags, content_description, content_instructions, content_composition)


    def fetch_title_link(self, element):
        title = element.find('div', attrs={'class' : 'flex-column'})

        if title:
            data_title = title.find('a').text.strip()
            data_link = title.find('a').get('href')
            print('Link: ' + data_link)
            print('Title: ' + data_title)
            return (data_link, data_title)
        else:
            print('No title')
            return (None, None)

    def fetch_provider_value(self, element):
        provider_value = element.find('span', attrs={'class' : 'normal-price'})

        if provider_value:
            data_provider_value = provider_value.text.strip()
            print('Provider value: ' + data_provider_value)

        return data_provider_value

    def fetch_actually_discount(self,element):
        discount_web_value = element.find('div',attrs={'class':'tagimg_text'})

        if discount_web_value:
            data_discount_web = discount_web_value.text
            print('Actually discount web: '+ data_discount_web)
        else:
            data_discount_web = 'without discount'
        return data_discount_web

    def fetch_rate_value(self,element):

        rating_value = element.find('div',attrs={'class':'rating-box'})
        rate_value='' # No rating yet
        if rating_value:
            spec_rating = rating_value.find_all('meta')
            if spec_rating:
                rate_value = spec_rating[2].attrs['content']
        return rate_value

    def download_file_image(self, image_url):
        page_image = requests.get(image_url, stream=True)
        if page_image.status_code == 200:
            print(Path(image_url).stem)

            if not os.path.exists(self.IMAGES_PATH):
                Path(self.IMAGES_PATH).mkdir(parents=True, exist_ok=True)

            with open(self.IMAGES_PATH + Path(image_url).stem + '.jpg', 'wb') as image_file:
                for chunk in page_image:
                    image_file.write(chunk)

    def fetch_inside_page(self, inside_link):
        if inside_link:
            page = requests.get(inside_link)

        if page.status_code == 200:

            # @TODO REFACTOR ME HERE in functions - codigo chapuza rapido
            soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), 'html.parser')

            description = soup.find('div', attrs={'id' : 'content-description'})
            data_description = ''
            if description:
                data_description = description.text.strip()
                print('Description: ' + data_description)


            data_professional_advice = ''
            professional_advice = soup.find('div', attrs={'id' : 'professional-advice'})
            if professional_advice:
                data_professional_advice = professional_advice.text.strip()
                print('Professional advice: ' + data_professional_advice)

            image_one=""
            images__box = soup.find('div', attrs={'class':'boximg'})
            if images__box:
                image_one=images__box.find('img', attrs={'class' : 'img-fluid'})
                if image_one:
                    image_one = image_one.get('src')
                    print('Image first: ' + image_one)
                    self.download_file_image(image_one)

        return (image_one, data_description,data_professional_advice)

    def check_next_page(self, soup):

        next_page = self.DATA_SOURCE + str(self.global_counter_page)

        pages = requests.get(next_page)

        if pages.status_code == 200:
            next_page_link = self.DATA_SOURCE + str(self.global_counter_page)
            print('Processing next page: ' + next_page_link)
            self.fetch(next_page_link)
        else:
            print('No new pages found')

    def run(self):
        if sys.version_info[0] < 3:
            raise Exception("You need use Python 3 to execute this script. You have: Python" + str(sys.version_info[0]))

        print('Running Promofarma Fetcher')
        self.fetch(None)

        print('Data to store')
        print(self.data)

        print('Exporting to CSV')
        self.export_csv()
        print('Done')


PromofarmaFetcher().run()