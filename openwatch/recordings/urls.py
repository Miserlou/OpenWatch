from django.conf.urls.defaults import *
from openwatch.recordings.models import Recording 

info_dict = {
  'queryset': Recording.objects.all(),
}

urlpatterns = patterns('',
    (r'^upload$', 'openwatch.recordings.views.upload'),
    (r'^uploadnocaptcha$', 'openwatch.recordings.views.upload_no_captcha'),
    (r'^victory$', 'openwatch.recordings.views.victory'),
)
