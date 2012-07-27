from django.core.management.base import BaseCommand
from optparse import make_option
from recordings.models import Recording, ACLUNJRecording


class Command(BaseCommand):
    args = 'none'
    option_list = BaseCommand.option_list + (
        make_option('--execute',
            action='store_true',
            help='save changes to database'),
    )
    help = 'Move Recording objects to appropriate child object based on filename'

    def handle(self, *args, **options):
        do_execute = options.get('execute')
        if do_execute:
            action = "moved"
        else:
            action = "should be moved"

        modified_count = 0
        total = len(Recording.objects.all())
        for recording in Recording.objects.all():
            if "_aclunj." in recording.rec_file:
                if do_execute:
                    aclunj_recording = ACLUNJRecording.objects.create()
                    aclunj_recording.__dict__.update(recording.__dict__)
                    recording.delete()

                self.stdout.write('Recording %d (%s) %s to type %s \n' % (recording.pk, recording.name, action, "ACLUNJRecording"))
            modified_count += 1

        self.stdout.write('%d/%d Recordings %s \n' % (modified_count, total, action))
