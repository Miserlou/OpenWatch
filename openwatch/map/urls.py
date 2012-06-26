from django.conf.urls.defaults import *
from openwatch.recordings.models import Recording 

info_dict = {
  'queryset': Recording.objects.all(),
}

urlpatterns = patterns('',
    
    
    (r'^search/(?P<tag>[a-zA-Z0-9_. -]+)$', 'openwatch.map.views.map_tag'),
    (r'^search/(?P<tag>[a-zA-Z0-9_. -]+)/(?P<ne_lat>[0-9.]+)/$', 'openwatch.map.views.map_tag_location'),
    (r'^search/(?P<tag>[a-zA-Z0-9_. -]+)/(?P<ne_lat>[0-9.-]+)/(?P<ne_lon>[0-9.-]+)/(?P<sw_lat>[0-9.-]+)/(?P<sw_lon>[0-9.-]+)/$', 'openwatch.map.views.map_tag_location'),
    (r'^search/$', 'map.views.redir'),
    (r'^api/$', 'map.views.map_json'),
    (r'^api/(?P<tag>[a-zA-Z0-9_. -]+)/$', 'map.views.map_tag_json'),
    (r'^api/(?P<ne_lat>[0-9.-]+)/(?P<ne_lon>[0-9.-]+)/(?P<sw_lat>[0-9.-]+)/(?P<sw_lon>[0-9.-]+)/$', 'map.views.map_location_json'),
    (r'^about/$', 'map.views.about'),
    (r'^size/$','map.views.size'),

    (r'^recordings/(?P<zipcode>[a-zA-Z0-9_. -]+)/', 'map.views.map_zipcode'),
    (r'^$','openwatch.map.views.map'),


)