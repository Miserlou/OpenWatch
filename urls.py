from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
     (r'^openwatch/', include('openwatch.recordings.urls')),
     (r'^upload/', 'openwatch.recordings.views.upload'),
     (r'^uploadnocaptcha/', 'openwatch.recordings.views.upload_no_captcha'),
     (r'^all/', 'openwatch.recordings.views.listall'),
     (r'^about/', 'openwatch.recordings.views.about'),
     (r'^view/(?P<media_id>\d+)$', 'openwatch.recordings.views.view'),  
     (r'^tags/$', 'recordings.views.tags'),
     (r'^tag/(?P<tag>[^/]+)/$','recordings.views.with_tag'), 
     (r'^captcha/', include('captcha.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
     (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
     (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'static'}),
     (r'^$', 'openwatch.recordings.views.root')
)
