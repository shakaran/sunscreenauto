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

            soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), 'html.parser')

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

                        quality_overall = element.find('span', attrs={'class' : 'quality-badge__value'})

                        if quality_overall:
                            data_quality_overall = quality_overall.text.strip()
                            print('Quality Overall: ' + data_quality_overall)

                        quality_overall_info = element.find('span', attrs={'class' : 'quality-badge__info'})

                        if quality_overall_info:
                            data_quality_overall_info = quality_overall_info.text.strip().replace('CALIDAD', '')
                            print('Quality Overall Info: ' + data_quality_overall_info)

                        specs = element.find('div', attrs={'class' : 'recommended__listing__item__specs'})

                        if specs:
                            data_specs = specs.find_all('p')

                            if data_specs[0]:
                                data_spec_content = data_specs[0].text.replace('Contenido: ', '').strip()
                                print('Content: ' + data_spec_content)

                            if data_specs[1]:
                                data_spec_spf = data_specs[1].text.replace('SPF: ', '').strip()
                                print('SPF: ' + data_spec_spf)

                            if len(data_specs) > 2:
                                data_spec_container = data_specs[2].text.replace('Precio por envase: ', '').strip()
                                print('Price by container: ' + data_spec_container)


                        provider_value = element.find('div', attrs={'class' : 'recommended__calltoaction__provider-value'})

                        if specs:
                            data_provider_value = provider_value.text

                            print('Provider value: ' + str(data_provider_value.encode('utf-8').strip()))

                        picture_image = element.find('a', attrs={'class' : 'recommended__picture-image'})

                        if picture_image:
                            data_picture_image = picture_image.find('img').get('src').strip()
                            print('Picture Image: ' + data_picture_image)



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
                            })

                        print

            print('Data to store')
            print(self.data)

    def run(self):
        print('Running Ocu Fetcher')
        self.fetch()


OcuFetcher().run()