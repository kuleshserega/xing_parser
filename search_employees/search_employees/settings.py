from settings_local import *


BOT_NAME = 'search_employees'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['search_employees.spiders']
NEWSPIDER_MODULE = 'search_employees.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = {
    'search_employees.pipelines.SearchEmployeesPipeline': 1000,
}

MAX_ITEMS_COUNT = 10000
