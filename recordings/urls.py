from django.conf.urls.defaults import *
from MassSous.recordings.models import Recording 

info_dict = {
  'queryset': Recording.objects.all(),
}

urlpatterns = patterns('',
      (r'^upload$', 'MassSous.recordings.views.upload'),
      (r'^victory$', 'MassSous.recordings.views.victory'),
)
