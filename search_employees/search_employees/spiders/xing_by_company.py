# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from search_employees.items import XingSpiderItem

from xingapp.models import XingSearch


class XingByCompanySpider(Spider):
    name = 'xing_by_company'
    allowed_domains = ['xing.com']
    start_urls = ['http://xing.com/']
    search_url = 'https://www.xing.com/companies/{company}/employees.json?' \
        'filter=all&letter={letter}&limit=50&offset={offset}'

    def __init__(self, search_term='siemensag', *args, **kwargs):
        super(XingByCompanySpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.search_term = search_term

    def spider_closed(self, spider):
        self.xing_search.status = 2
        self.xing_search.save()

    def parse(self, response):
        self.xing_search = XingSearch(
            search_term=self.search_term, search_type=2, search_geo=self.city)
        self.xing_search.save()

        letter = 'A'
        offset = 0
        url = self.search_url.format(
            company=self.search_term, letter=letter, offset=offset)

        return Request(url, callback=self._parse_details, dont_filter=True)

    def _parse_details(self, response):
        print response

        # for employee in employees_info:
        #     item = XingSpiderItem()
        #     name = employee.xpath(
        #         './div/a[contains(@class, "name-page-link")]/text()'
        #     ).extract_first()
        #     if name:
        #         name_parts = name.split(' ')
        #         item['first_name'] = name_parts[0]
        #         item['last_name'] = name_parts[1]

        #     company = employee.xpath(
        #         './div[contains(@class, "company-name")]/a/text()'
        #     ).extract_first()
        #     if company:
        #         item['current_company'] = company

        #     current_position = employee.xpath(
        #         './div[contains(@class, "occupation-title")]/text()'
        #     ).extract_first()
        #     if current_position:
        #         item['current_position'] = current_position.strip()

        #     employee_link = employee.xpath(
        #         './div/a[contains(@class, "name-page-link")]/@href'
        #     ).extract_first()
        #     item['employee_link'] = employee_link

        #     item['search'] = self.xing_search

        #     next_page = response.urljoin(employee_link)
        #     request = Request(
        #         next_page,
        #         callback=self._parse_location,
        #         meta={'item': item}, dont_filter=True)
        #     request.meta['item'] = item
        #     yield request

    def _parse_location(self, response):
        item = response.meta['item']
        location = response.xpath(
            '//span[contains(@class, "company-location")]/text()'
        ).extract_first()
        if location:
            item['location'] = location.strip()

        yield item
