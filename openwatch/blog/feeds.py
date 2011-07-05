from django.contrib.syndication.views import Feed

from openwatch.blog.models import Post 
from openwatch.recordings.models import Recording, RecordingForm, RecordingNoCaptchaForm

class LatestEntriesFeed(Feed):
    title = "OpenWatch Blog"
    link = "/blog/"
    description = "News and Reports from OpenWatch.net"

    def items(self):
        return Post.objects.all().order_by('-date')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body
