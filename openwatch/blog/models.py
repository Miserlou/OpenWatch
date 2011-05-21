from django.db import models
from datetime import datetime
from tagging.fields import TagField
from tagging.models import Tag

class Post(models.Model):
    title = models.CharField(max_length='200')
    body = models.TextField()
    approved = models.BooleanField(default=False, blank=True)
    
    date = models.DateTimeField('date', blank=True, default=datetime.now())
    tags = TagField()

    def get_tags(self):
        return Tag.objects.get_for_object(self)

    def __unicode__(self):
        return self.title 
