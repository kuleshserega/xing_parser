# -*- coding: utf-8 -*-
class SearchEmployeesPipeline(object):
    def process_item(self, item, spider):
        item.save()
        return item
