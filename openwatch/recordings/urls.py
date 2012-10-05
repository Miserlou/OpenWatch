from django.conf.urls.defaults import *
from django.conf.urls import patterns, url
from openwatch.recordings.models import Recording

info_dict = {
  'queryset': Recording.objects.all(),
}

urlpatterns = patterns('',
	  # These are all ready specified in the project urls.py
      #url(r'^upload$', 'openwatch.recordings.views.upload', name='upload'),
      #url(r'^uploadnocaptcha$', 'openwatch.recordings.views.upload_no_captcha', name='upload_no_captcha'),
      
      #url(r'^victory$', 'openwatch.recordings.views.victory', name='victory'),

      # Ajax API:
      #url(r'^approve$', 'openwatch.recordings.views.approve', name='approve'),
)
