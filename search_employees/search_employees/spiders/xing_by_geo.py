# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request, FormRequest
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from search_employees.items import XingSpiderItem

from xingapp.models import XingSearch, XingUser


class XingByGeoSpider(Spider):
    name = 'xing_by_geo'
    allowed_domains = ['https://www.xing.com']
    start_urls = ['https://login.xing.com/login']
    search_url = 'https://www.xing.com/search/members?advanced_form=true&' \
        'city={city}&keywords={search_term}&section=members&page={page}'

    def __init__(self, search_term='programmer', city='Kiev', *args, **kwargs):
        super(XingByGeoSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.search_term = search_term
        self.city = city

        self.xing_search = XingSearch(
            search_term=self.search_term, search_type=2, search_geo=self.city)
        self.xing_search.save()

        self.user = XingUser.objects.all()[0]

    def spider_closed(self, spider):
        self.xing_search.status = 2
        self.xing_search.save()

    def parse(self, response):
        return FormRequest.from_response(
            response,
            formdata={
                'login_form[username]': self.user.email,
                'login_form[password]': self.user.password},
            callback=self._parse_item, dont_filter=True)

    def _parse_item(self, response):
        loged_in = response.xpath('//a[contains(@class, "header-personal")]')
        attempt = 2
        for i in xrange(attempt):
            if not loged_in:
                self.parse(response)
            else:
                break

        # maximum search results pages that xing return with city param
        pages = 16
        for page in xrange(1, pages):
            url = self.search_url.format(
                city=self.city, search_term=self.search_term, page=page)
            yield Request(url, callback=self._parse_details, dont_filter=True)

    def _parse_details(self, response):
        employees_info = response.xpath(
            '//div[contains(@class, "search-result")]/'
            'div[contains(@class, "bd")]')

        for employee in employees_info:
            item = XingSpiderItem()
            name = employee.xpath(
                './div/a[contains(@class, "name-page-link")]/text()'
            ).extract_first()
            if name:
                name_parts = name.split(' ')
                item['first_name'] = name_parts[0]
                item['last_name'] = name_parts[1]

            company = employee.xpath(
                './div[contains(@class, "company-name")]/a/text()'
            ).extract_first()
            if company:
                item['current_company'] = company

            current_position = employee.xpath(
                './div[contains(@class, "occupation-title")]/text()'
            ).extract_first()
            if current_position:
                item['current_position'] = current_position.strip()

            employee_link = employee.xpath(
                './div/a[contains(@class, "name-page-link")]/@href'
            ).extract_first()
            item['employee_link'] = employee_link
            item['search'] = self.xing_search
            item['location'] = self.city
            yield item
