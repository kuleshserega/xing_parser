# -*- coding: utf-8 -*-
from scrapy_djangoitem import DjangoItem
from xingapp.models import XingSearchResult


class XingSpiderItem(DjangoItem):
    django_model = XingSearchResult
