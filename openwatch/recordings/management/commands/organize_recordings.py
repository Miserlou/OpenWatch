from django.core.management.base import BaseCommand
from optparse import make_option
from recordings.models import Recording
import re

import recording_tags


class Command(BaseCommand):
    args = 'none'
    option_list = BaseCommand.option_list + (
        make_option('--execute',
            action='store_true',
            help='save changes to database'),
    )
    help = 'Identify organizational Recordings by filename suffixes. Pass --execute to perform tagging.'

    def handle(self, *args, **options):
        do_execute = options.get('execute')
        if do_execute:
            action = "tagged"
        else:
            action = "should be tagged"

        modified_count = 0
        total = len(Recording.objects.all())

        # Look for ACLU-NJ recordings:
        tag = recording_tags.ACLU_NJ
        for recording in Recording.objects.all():
            #print 'checking ' + str(recording.rec_file)
            if "_aclunj" in str(recording.rec_file):
                if do_execute:
                    # If this recording is all ready tagged to an organization,
                    # assume it has been processed properly
                    print recording.tags
                    if tag not in recording.tags:
                        self.stdout.write('Recording %d (%s) %s with %s \n' % (recording.pk, recording.name, action, tag))
                        recording.add_tag(tag)  # saves recording
                        modified_count += 1
                        # Check for Police Tape embedded email
                        # Police Tape appends email to existing privDesc:
                        # privDesc = privDesc + "[" + email + "]";
                        try:
                            potential_email = recording.private_description.rsplit("[", 1)[1].rsplit("]", 1)[0]
                            if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", potential_email):
                                recording.email = potential_email
                            recording.private_description = recording.private_description.rsplit("[", 1)[0]
                            recording.save()
                        except:
                            # If we couldn't parse the email from private description, assume it didn't exist
                            pass
                else:
                    # If not do_execute, only indicate recordings
                    if tag not in recording.tags:
                        modified_count += 1
                        self.stdout.write('Recording %d (%s) %s with %s \n' % (recording.pk, recording.name, action, tag))


        self.stdout.write('%d/%d Recordings %s \n' % (modified_count, total, action))
