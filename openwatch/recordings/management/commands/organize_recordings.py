from django.core.management.base import BaseCommand
from optparse import make_option
from recordings.models import Recording
import re
import sys

import recording_tags


class Command(BaseCommand):
    args = 'none'
    option_list = BaseCommand.option_list + (
        make_option('--execute',
            action='store_true',
            help='save changes to database'),
    )
    help = 'Identify organizational Recordings by filename suffixes. Pass --execute to perform tagging.'

    def write(self, string):
        ''' A wrapper for self.stdout.write to avoid problems with unicode:
            A bug in Python 2.6 results in self.stdout.write using
            'default' unicode encoding, which can be ascii. This breaks
            when the module encounters unicode characters.
            Thus we've got to wrap the call :(
            see http://stackoverflow.com/questions/8016236/python-unicode-handling-differences-between-print-and-sys-stdout-write
        '''
        if isinstance(string, unicode):
            string = string.encode(sys.__stdout__.encoding)
        sys.__stdout__.write(string)

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
                        self.write('Recording %d (%s) %s with %s \n' % (recording.pk, recording.name, action, tag))
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
                        self.write('Recording %d (%s) %s with %s \n' % (recording.pk, recording.name, action, tag))

        self.write('%d/%d Recordings %s \n' % (modified_count, total, action))
