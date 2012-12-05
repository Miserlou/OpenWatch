from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from openwatch.recordings.models import Recording
import settings
from datetime import *
import time
import envoy
import enchant

import os 

from learning.models import FeatureSet
from recordings.models import Recording

class Command(BaseCommand):
    args = '<path>'
    help = 'Extract features of all Recordings in the Database'

    # Set up dictionary
    # Note about installation, requires dicts to be installed too
    # brew install aspell --lang=en
    d = enchant.Dict('en_US')

    def handle(self, *args, **options):


        # example: /Users/tuttle/Projects/OpenWatch/uploads/
        path = None
        for a in args:
            path = a
        print path


        recordings = Recording.objects.all().defer('rec_file')

        for recording in recordings:

            try:
                print "Recording: " + str(recording.name)

                f_path = path + str(recording.rec_file)
                print "Size: " + str(os.stat(f_path).st_size)

                duration = envoy.run('ffmpeg -i ' + f_path)
                duration = [line.strip() for line in duration.std_err.split('\n') if "Duration" in line][0]
                length = duration.split('Duration: ')[1].split(', ')[0]
                print "Length: " + str(length)
                minutes = int(length.split(':')[0]) * 60 + int(length.split(':')[1])
                print "Minutes: " + str(minutes)

                has_location = False
                if recording.location and recording.location is not 'No description available' and recording.location != '0.0, 0.0':
                    has_location = True

                print "Has Location: " + str(has_location)

                title_words = recording.name.replace(',', '').replace('.', '').split()
                title_word_count = len(title_words)
                title_actual_word_count = self.get_actual_word_count(title_words)

                print "Title Words: " + str(len(title_words))
                print "Actual Title Words: " + str(title_actual_word_count)

                desc_words = recording.public_description.replace(',', '').replace('.', '').split()
                desc_word_count = len(desc_words)
                desc_actual_word_count = self.get_actual_word_count(desc_words)

                print "Desc Words: " + str(len(desc_words))
                print "Actual Desc Words: " + str(desc_actual_word_count)

                priv_words = recording.private_description.replace(',', '').replace('.', '').split()
                priv_word_count = len(priv_words)
                priv_actual_word_count = self.get_actual_word_count(priv_words)

                print "Private Words: " + str(len(priv_words))
                print "Actual Private Words: " + str(priv_actual_word_count)

                file_type = str(recording.rec_file).split('.')[-1:]
                print "File Type: " + file_type[0]

                is_test = 'test' in recording.name or 'test' in recording.public_description or 'test' in recording.private_description
                print "Is test: " + str(is_test)

                print '\n'

                f = FeatureSet()
                f.rec = recording
                f.num_minutes = minutes
                f.has_location = has_location
                f.title_word_count = title_word_count
                f.title_actual_word_count = title_actual_word_count
                f.desc_word_count = desc_word_count
                f.desc_actual_word_count = desc_actual_word_count
                f.private_word_count = priv_word_count
                f.private_actual_word_count = priv_actual_word_count
                f.title = recording.name
                f.description = recording.public_description[:199]
                f.private = recording.private_description[:199]
                f.file_type = file_type[0]
                f.is_test = is_test
                f.verified = False
                f.legit = False

                f.save()
            except Exception, e:
                print 'Crap.\n'
                print e
                continue

    def get_actual_word_count(self, inwords):
            
        actual_words = 0
        for t in inwords:
            if self.d.check(t):
                actual_words = actual_words + 1

        return actual_words

