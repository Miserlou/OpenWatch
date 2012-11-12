from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from openwatch.recordings.models import Recording
import settings
from datetime import *
import time

class Command(BaseCommand):
    args = ''
    help = 'Re-geocode old Recordings'

    def handle(self, *args, **options):
        recordings = Recording.objects.all().defer('rec_file')

        for recording in recordings:
            try:
                if ',' in recording.location:
                    print "Regeocoding.."
                    print recording.name
                    latlon = recording.location.split(',')
                    recording.lat = latlon[0].strip()
                    recording.lon = latlon[1].strip()
                    recording.save()
                    recording.rec_file.close()
            except Exception, e:
                print e
                continue