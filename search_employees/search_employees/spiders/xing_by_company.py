# -*- coding: utf-8 -*-
import json

from scrapy import Spider
from scrapy.http import Request, FormRequest
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.selector import Selector

from search_employees.items import XingSpiderItem

from xingapp.models import XingSearch, XingUser

LETTERS_LIST = ["A", "B", "C", "D", "E", "F", "G", "H", "I",
                "J", "K", "L", "M", "N", "O", "P", "Q", "R",
                "S", "T", "U", "V", "W", "X", "Y", "Z"]


class XingByCompanySpider(Spider):
    name = 'xing_by_company'
    allowed_domains = ['https://www.xing.com']
    start_urls = ['https://login.xing.com/login']
    company_urls_list = [
        'https://www.xing.com/companies/{company}',
        'https://www.xing.com/company/{company}',
    ]
    search_employees_url_part = 'employees.json?' \
        'filter=all&letter={letter}&limit=50'
    company_location = None

    def __init__(self, search_term='upwork', *args, **kwargs):
        super(XingByCompanySpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.search_term = search_term

        self.xing_search = XingSearch(
            search_term=self.search_term, search_type=1)
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
            callback=self._parse_company_urls_list, dont_filter=True)

    def _parse_company_urls_list(self, response):
        loged_in = response.xpath('//a[contains(@class, "header-personal")]')
        attempt = 2
        for i in xrange(attempt):
            if not loged_in:
                self.parse(response)
            else:
                break

        for company_url in self.company_urls_list:
            url = company_url.format(company=self.search_term)
            yield Request(
                url, callback=self._parse_company_url,
                meta={'dont_redirect': True}, dont_filter=True)

    def _parse_company_url(self, response):
        company_name = self._get_company_name_from_page(response)

        city = self._get_company_city_from_page(response)
        country = self._get_company_country_from_page(response)
        company_location = '%s, %s' % (city, country)

        base_company_url = response.url
        if company_name:
            for letter in LETTERS_LIST:
                search_url_part = self.search_employees_url_part.format(
                    letter=letter, offset=0)
                items_url = '%s/%s' % (base_company_url, search_url_part)

                company_name = company_name.strip() if company_name else None
                meta = {
                    'letter': letter,
                    'items_url': items_url,
                    'company_name': company_name,
                    'company_location': company_location}

                yield Request(
                    items_url, callback=self._parse_employees_items,
                    meta=meta, dont_filter=True)

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
        meta = response.meta
        try:
            data = json.loads(response.body)
            employees_list = data['contacts'][meta['letter']]['html']
            total = data['contacts'][meta['letter']]["total"]
            offset = data['contacts'][meta['letter']]["offset"]
            if total == 50:
                offset_row_param = 'offset=%d' % (offset+50)
                url = '%s&%s' % (meta['items_url'], offset_row_param)
                yield Request(
                    url, callback=self._parse_employees_items,
                    meta=meta, dont_filter=True)

            for employee in employees_list:
                text = employee.encode("utf-8")
                xhs = Selector(text=text)

                item = XingSpiderItem()
                item['current_company'] = meta['company_name']
                item['location'] = meta['company_location']
                item['search'] = self.xing_search

                name = self._get_name(xhs)
                if name:
                    name_parts = name.rsplit(' ', 1)
                    item['first_name'] = name_parts[0]
                    item['last_name'] = name_parts[1]

                item['employee_link'] = self._get_employee_link(xhs)
                item['current_position'] = self._get_current_position(xhs)
                yield item
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
