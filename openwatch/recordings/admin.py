from django.contrib import admin
from openwatch.recordings.models import Recording, ACLUNJRecording

admin.site.register(Recording)
admin.site.register(ACLUNJRecording)
