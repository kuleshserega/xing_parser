from django.contrib import admin

from xingapp.models import XingSearch, XingSearchResult, \
    XingUser

admin.site.register(XingSearch)
admin.site.register(XingSearchResult)
admin.site.register(XingUser)
