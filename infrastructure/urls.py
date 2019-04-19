from django.conf.urls import patterns, include, url
from infrastructure.cip.views import *
from django.contrib import admin
from django.http import HttpResponseRedirect
from rest_framework import routers
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'projects', ProjectViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'infrastructure.views.home', name='home'),
    # url(r'^infrastructure/', include('infrastructure.foo.urls')),
    url(r'^$',DashboardView.as_view(), name='index'), 
    url(r'^projects$',ProjectList.as_view(), name='projects'),
    url(r'^projects/(?P<phase>(design|planning|bid|construction|post-construction|completed))$',ProjectList.as_view(), name='phase_projects'),
    url(r'^projects/(?P<asset_type>(airports|buildings|storm-water-drainage|parks|transportation|sewer|water))$',ProjectList.as_view(), name='asset_type_projects'),
    url(r'^projects/district/(?P<district>([1-9]))$',ProjectList.as_view(), name='district_projects'),

    url(r'^projects/(?P<show>(all|current))$',ProjectList.as_view(), name='projects'),
    url(r'^projects/(?P<filter>\w+([\w_])*)/(?P<value>\w+([\/\w \.-?%?&]*))$', ProjectList.as_view(), name='projects_filter_list'),
    url(r'^projects/(?P<filter>\w+)/(?P<value>\w+(\s+\w+)*)/(?P<show>(all|current))$', ProjectList.as_view(), name='projects_list'),
    url(r'^projects/filter$', ProjectList.as_view(), name='filter_projects'),
    url(r'^projects_list$', ProjectsListListView.as_view(), name='projects_list'),

    url(r'^project/(?P<pk>\d+)$', ProjectDetailView.as_view(),name='project_detail'),
    url(r'^project/(?P<slug>([A-Z0-9]*))$', ProjectDetailView.as_view(),name='project_detail'),
    url(r'^project/(?P<pk>\d+)/timetable.json$', ProjectDetailJSONView.as_view(),name='project_timetable'),
    url(r'^search/', include('haystack.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls))
)
