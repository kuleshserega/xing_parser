# -*- coding: UTF-8 -*-
import csv

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.http.response import JsonResponse
from django.contrib import messages
from django.conf import settings

from xingapp.models import XingSearch, XingSearchResult


class LoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        else:
            return super(LoginFormView, self).dispatch(
                request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginFormView, self).form_valid(form)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/login")


class XingSearchView(LoginRequiredMixin, ListView):
    model = XingSearch
    template_name = 'search.html'
    context_object_name = 'results'
    paginate_by = settings.ROWS_ON_PAGE

    def get_queryset(self):
        qs = super(XingSearchView, self).get_queryset().order_by(
            '-date_created')
        return qs


class SearchDetailsView(LoginRequiredMixin, ListView):
    model = XingSearchResult
    template_name = 'search-details.html'
    context_object_name = 'employees'
    paginate_by = settings.ROWS_ON_PAGE

    def get_queryset(self):
        return XingSearchResult.objects.filter(
            search_id=self.kwargs['pk']).order_by('last_name')

    def get_context_data(self, **kwargs):
        data = super(SearchDetailsView, self).get_context_data(**kwargs)
        try:
            data['search_info'] = XingSearch.objects.get(
                pk=self.kwargs['pk'])
        except XingSearch.DoesNotExist:
            data['search_info'] = []
            messages.error(
                self.request, 'Search details does not exists in database.')

        return data


def get_xing_employees_csv(request, pk):
    try:
        s = XingSearch.objects.get(pk=pk)
    except Exception:
        return HttpResponse('Xing search do not exists')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = \
        'attachment; filename="%s_employees.csv"' % s.search_term

    qs = XingSearchResult.objects.filter(search_id=s.id).order_by('last_name')

    writer = csv.writer(response)
    writer.writerow([
        'ID SEARCH RESULT', 'FIRST NAME', 'LAST NAME', 'LOCATION',
        'COMPANY', 'POSITION'])
    for row in qs:
        first_name = row.first_name.encode(
            'utf-8').replace(';', '.') if row.first_name else None
        last_name = row.last_name.encode(
            'utf-8').replace(';', '.') if row.last_name else None
        location = row.location.encode(
            'utf-8').replace(';', '.') if row.location else None
        current_company = row.current_company.encode(
            'utf-8').replace(';', '.') if row.current_company else None
        current_position = row.current_position.encode(
            'utf-8').replace(';', '.') if row.current_position else None
        writer.writerow([
            row.id, first_name, last_name, location,
            current_company, current_position])

    return response


def get_search_list(request):
    page = request.GET.get('page')
    page = int(page) if page else 1
    start = 0
    if page > 1:
        start = page*settings.ROWS_ON_PAGE - settings.ROWS_ON_PAGE
    end = page*settings.ROWS_ON_PAGE
    qs = XingSearch.objects.all().order_by(
            '-date_created')[start:end]

    result = []
    for line in qs:
        result.append(line.as_dict())

    return JsonResponse({'status': 'ok', 'content': result})
