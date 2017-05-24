import os
import sys

import django


DJANGO_PROJECT_PATH = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), 'xing_django')
DJANGO_SETTINGS_MODULE = 'xing_django.settings'

sys.path.insert(0, DJANGO_PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE

django.setup()

BOT_NAME = 'search_employees'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['search_employees.spiders']
NEWSPIDER_MODULE = 'search_employees.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = {
    'search_employees.pipelines.SearchEmployeesPipeline': 1000,
}

MAX_ITEMS_COUNT = 10000
