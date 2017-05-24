from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from templatetags.base_extra import status_icons

STATE_IN_PROCESS = 1
STATE_FINISHED = 2
STATE_ERROR = 3


STATUS_CHOICES = (
    (STATE_IN_PROCESS, _('Search in process')),
    (STATE_FINISHED, _('Search is finished')),
    (STATE_ERROR, _('Search has errors')),
)

SEARCH_BY_COMPANY = 1
SEARCH_BY_GEO = 2

SEARCH_TYPE_CHOICES = (
    (SEARCH_BY_COMPANY, _('Search by company')),
    (SEARCH_BY_GEO, _('Search by Geo'))
)


class XingSearch(models.Model):
    search_term = models.CharField(
        default=None, null=True, blank=True,
        max_length=120, verbose_name=_('Search term'))
    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Date created'))
    status = models.SmallIntegerField(
        default=1, choices=STATUS_CHOICES, verbose_name=_('Status of search'))
    search_type = models.SmallIntegerField(
        default=1, choices=SEARCH_TYPE_CHOICES, verbose_name=_('Search type'))
    search_geo = models.CharField(
        default=None, null=True, blank=True,
        max_length=120, verbose_name=_('Search geo location'))
    last_scraped_page = models.IntegerField(
        default=None, null=True, blank=True,
        verbose_name=_('Last scraped employees page'))

    def as_dict(self):
        date_created = self.date_created.strftime("%Y-%m-%d %H:%M:%S")
        result = {
            'id': self.id,
            'search_term': self.search_term,
            'date_created': date_created,
            'search_geo': self.search_geo,
            'search_type': self.get_search_type_display(),
            'status': self.status,
            'status_text': self.get_status_display(),
            'status_icon': status_icons(self.status),
            'search_details_url': reverse(
                'xingapp:search-details', kwargs={'pk': self.id}),
            'employees_to_csv': reverse(
                'xingapp:get-employees', kwargs={'pk': self.id}),
        }
        return result

    def __str__(self):
        return self.search_term


class XingSearchResult(models.Model):
    first_name = models.CharField(
        default=None, null=True, blank=True,
        max_length=120, verbose_name=_('First name'))
    last_name = models.CharField(
        default=None, null=True, blank=True,
        max_length=120, verbose_name=_('Last name'))
    employee_link = models.CharField(
        default=None, null=True, blank=True,
        max_length=250, verbose_name=_('Employee link'))
    current_company = models.CharField(
        default=None, null=True, blank=True,
        max_length=250, verbose_name=_('Current company'))
    current_position = models.CharField(
        default=None, null=True, blank=True,
        max_length=250, verbose_name=_('Current position'))
    location = models.CharField(
        default=None, null=True, blank=True,
        max_length=250, verbose_name=_('Location'))
    search = models.ForeignKey(
        'XingSearch', verbose_name=_('Xing Search instance'))

    def __str__(self):
        last_name = self.last_name
        if not self.last_name:
            last_name = ''
        return "%s %s" % (self.first_name, last_name)

    def __unicode__(self):
        return unicode(self.id)


class XingUser(models.Model):
    email = models.CharField(
        max_length=120, verbose_name=_('Xing email'))
    password = models.CharField(
        max_length=120, verbose_name=_('Xing password'))

    def __str__(self):
        return self.email
