# -*- coding: utf-8 -*-
import json

from scrapy import Spider
from scrapy.http import Request
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.selector import Selector

from search_employees.items import XingSpiderItem

from xingapp.models import XingSearch

LETTERS_LIST = ["A", "B", "C", "D", "E", "F", "G", "H", "I",
                "J", "K", "L", "M", "N", "O", "P", "Q", "R",
                "S", "T", "U", "V", "W", "X", "Y", "Z"]


class XingByCompanySpider(Spider):
    name = 'xing_by_company'
    allowed_domains = ['https://www.xing.com']
    start_urls = ['https://www.xing.com']
    company_urls_list = [
        'https://www.xing.com/companies/{company}',
        'https://www.xing.com/company/{company}',
    ]
    company_name = None
    company_location = None
    company_url_part = 'companies'
    search_url = 'https://www.xing.com/{company_url_part}/{company}/' \
        'employees.json?filter=all&letter={letter}&limit=50&offset={offset}'

    def __init__(self, search_term='nextlevelgmbh', *args, **kwargs):
        super(XingByCompanySpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.search_term = search_term

    def spider_closed(self, spider):
        self.xing_search.status = 2
        self.xing_search.save()

    def parse(self, response):
        self.xing_search = XingSearch(
            search_term=self.search_term, search_type=1)
        self.xing_search.save()

        for company_url in self.company_urls_list:
            print 'self.company_name:', self.company_name
            if self.company_name:
                break

            url = company_url.format(company=self.search_term)
            print '=============', url
            if 'company' in url:
                self.company_url_part = 'company'

            yield Request(
                url, callback=self._parse_company_url, dont_filter=True)

    def _parse_company_url(self, response):
        self.company_name = self._get_company_name_from_page(response)

        city = self._get_company_city_from_page(response)
        country = self._get_company_country_from_page(response)
        self.company_location = '%s, %s' % (city, country)

        if self.company_name:
            for letter in LETTERS_LIST:
                items_url = self.search_url.format(
                    company_url_part=self.company_url_part,
                    company=self.search_term, letter=letter, offset=0)
                yield Request(
                    items_url, callback=self._parse_employees_items,
                    meta={"letter": letter}, dont_filter=True)

    def _get_company_name_from_page(self, response):
        company_name = response.xpath(
            '//h1[contains(@class, "organization-name")]/text()'
        ).extract_first()

        if company_name:
            return company_name
        return None

    def _get_company_city_from_page(self, response):
        city = response.xpath(
            '//span[contains(@itemprop, "addressLocality")]/text()'
        ).extract_first()

        if city:
            return city
        return None

    def _get_company_country_from_page(self, response):
        country = response.xpath(
            '//div[contains(@itemprop, "addressCountry")]/span/text()'
        ).extract_first()

        if country:
            return country
        return None

    def _parse_employees_items(self, response):
        letter = response.meta['letter']

        try:
            data = json.loads(response.body)
            employees_list = data['contacts'][letter]['html']
            for employee in employees_list:
                text = employee.decode('unicode-escape').encode('utf-8')

                xhs = Selector(text=text)

                item = XingSpiderItem()
                item['current_company'] = self.company_name
                item['location'] = self.company_location
                item['search'] = self.xing_search

                name = self._get_name(xhs)
                if name:
                    name_parts = name.split(' ')
                    item['first_name'] = name_parts[0]
                    item['last_name'] = name_parts[1]

                item['employee_link'] = self._get_employee_link(xhs)
                item['current_position'] = self._get_current_position(xhs)
                yield item

            total = data['contacts'][letter]["total"]
            offset = data['contacts'][letter]["offset"]
            if total == 50:
                items_url = self.search_url.format(
                    company_url_part=self.company_url_part,
                    company=self.search_term, letter=letter, offset=offset+50)
                yield Request(
                    items_url, callback=self._parse_employees_items,
                    meta={"letter": letter}, dont_filter=True)
        except Exception as e:
            print e

    def _get_name(self, employee):
        name = employee.xpath(
            '//div/div/ul/li/div/p[contains(@class, "user-name")]/a/text()'
        ).extract_first()
        if name:
            return name
        return None

    def _get_employee_link(self, employee):
        employee_link = employee.xpath(
            '//div/div/ul/li/div/p[contains(@class, "user-name")]/a/@href'
        ).extract_first()
        if employee_link:
            return employee_link
        return None

    def _get_current_position(self, employee):
        current_position = employee.xpath(
            '//div/div/ul/li[3]/text()'
        ).extract_first()
        if current_position:
            return current_position
        return None
