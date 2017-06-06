import os
import sys

import django

from twisted.python import log

log.startLogging(sys.stdout)

DJANGO_PROJECT_PATH = os.environ['XING_PROJECT_PATH']
sys.path.insert(0, DJANGO_PROJECT_PATH)

log.msg(DJANGO_PROJECT_PATH)
log.msg(os.environ['DJANGO_SETTINGS_MODULE'])

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
