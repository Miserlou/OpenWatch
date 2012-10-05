from django.conf.urls.defaults import *
from django.conf import settings
from openwatch.blog.feeds import LatestEntriesFeed

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     url(r'^upload/', 'openwatch.recordings.views.upload', name='upload'),
     url(r'^uploadnocaptcha/', 'openwatch.recordings.views.upload_no_captcha', name='upload_no_captcha'),
     url(r'^victory$', 'openwatch.recordings.views.victory', name='victory'),
     # Ajax API:
     url(r'^approve$', 'openwatch.recordings.views.approve', name='approve'),  # For top-level approval
     url(r'^org-approve$', 'openwatch.recordings.views.org_approve', name='org_approve'),  # For organizational approval

     (r'^all/', 'openwatch.recordings.views.listall'),
     (r'^about/', 'openwatch.recordings.views.about'),
     (r'^contact/', 'openwatch.recordings.views.contact'),
     (r'^join/', 'openwatch.recordings.views.join'),
     (r'^apps/', 'openwatch.recordings.views.apps'),
     (r'^view/(?P<media_id>\d+)$', 'openwatch.recordings.views.view'),

     # There is no corresponding url in recordings.urls
     #(r'^recording/(?P<media_id>\d+)', include('openwatch.recordings.urls')),
     (r'^blog/(?P<media_id>\d+)$', 'openwatch.blog.views.view'),
     (r'^blog/', 'openwatch.blog.views.listall'),
     (r'^feed/', LatestEntriesFeed()),
     (r'^tags/$', 'recordings.views.tags'),
     (r'^tag/(?P<tag>[^/]+)/$', 'recordings.views.with_tag'),
     (r'^captcha/', include('captcha.urls')),
     (r'^map/', include('openwatch.map.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
     (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
     (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT}),
     (r'^$', 'openwatch.recordings.views.root')


)
