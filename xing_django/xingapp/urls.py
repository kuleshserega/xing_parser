from django.conf.urls import url
from xingapp import views


urlpatterns = [
    url(r'^$', views.XingSearchView.as_view(), name='search'),
    url(r'^login/$', views.LoginFormView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^search-details/(?P<pk>[0-9]+)/$',
        views.SearchDetailsView.as_view(), name='search-details'),
    url(r'^get_employees/(?P<pk>[0-9]+)/$',
        views.get_xing_employees_csv, name='get-employees'),
    url(r'^get_search_list/$',
        views.get_search_list, name='get-search-list'),
]
