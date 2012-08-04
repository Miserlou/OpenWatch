from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.forms import ModelForm
from datetime import datetime
from django import forms
from django.conf import settings
from tagging.fields import TagField
from tagging.models import Tag
from captcha.fields import CaptchaField

ulpath = 'openwatch/uploads/recordings/'
attachment_file_storage = FileSystemStorage(location=settings.UPLOAD_ROOT, base_url='recordings')


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    can_moderate = models.BooleanField(default=False)

# Create your models here.
class Recording(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, blank=True)
    date = models.DateTimeField('date uploaded', blank=True, default=datetime.now())
    location = models.CharField(max_length='200')
    vimeo = models.CharField(max_length='200', blank=True)
    vimeo_dl = models.CharField(max_length='200', blank=True)
    liveleak = models.CharField(max_length='200', blank=True)
    youtube = models.CharField(max_length='200', blank=True)
    local = models.CharField(max_length='200', blank=True)
    rec_file = models.FileField(upload_to='recordings', storage=attachment_file_storage)
    file_loc = models.CharField(max_length='200', blank=True)
    mimetype = models.CharField(max_length='200', blank=True)
    approved = models.BooleanField(default=False, blank=True)
    featured = models.BooleanField(default=False, blank=True)
    tags = TagField()

    public_description = models.TextField()
    private_description = models.TextField(blank=True)

    def save(self):
        super(Recording, self).save()

        # New recording, let me know about it
        #if not self.approved and int(self.rec_file.file.size) > 204800:
        #    send_mail('New recording: ' + self.name, 'Public: \n ' + self.public_description + 'Private: \n' + self.private_description + '\nSize:\n:' + str(self.rec_file.file.size) + '\nFile: ' + str(self.rec_file) + ' ' + str(self.file_loc) + "\nMIME: " + str(self.mimetype), 'openwatchnotifier@gmail.com', ['rich@anomos.info'], fail_silently=False)

        #XXX: Move the shit to static if approved!
        if len(self.vimeo) == 0 and self.approved and "video" in self.mimetype:
            pass
            #XXX: Vimeo upload https://github.com/dkm/python-vimeo


    def to_dict(self):
        if ',' in self.location:
            lat, lon = self.location.split(",",1)
        else:
            lat = 0.0
            lon = 0.0
        return {'id':self.pk, 'rec_file': str(self.rec_file), 'title' :self.name, 'tags': self.tags, 'url': 'http://openwatch.net/view/' + str(self.pk), 'about': self.public_description, 'lat': lat, 'lon': lon, 'location': self.location} 

    def get_tags(self):
        return Tag.objects.get_for_object(self)


    def __unicode__(self):
        return self.name + ': ' + self.public_description 


class RecordingNoCaptchaForm(ModelForm):
    class Meta:
        model = Recording

    #def __init__(self, bound_object=None, *args, **kwargs):
    #    super(RecordingForm, self).__init__(*args, **kwargs)
    #    self.bound_object = bound_object
    #    self.is_updating = False
    #    if self.bound_object:
    #        self.is_updating = True

    def clean(self):
        rec = self.cleaned_data.get('rec_file',None)
        if rec is None:
            raise forms.ValidationError("No file attached")
        if self.cleaned_data.get('rec_file',None).size > 209715200:
            raise forms.ValidationError("File too big, son")
        return self.cleaned_data

    def save(self):
        self.bound_object = Recording()
        uploaded_file = self.cleaned_data['rec_file']
        import re
        stored_name = re.sub(r'[^a-zA-Z0-9._]+', '-', uploaded_file.name)
        self.bound_object.rec_file.save(stored_name, uploaded_file)
        self.bound_object.mimetype = uploaded_file.content_type
        self.bound_object.name = self.cleaned_data['name']
        self.bound_object.public_description = self.cleaned_data['public_description']
        self.bound_object.private_description = self.cleaned_data['private_description']
        self.bound_object.location = self.cleaned_data['location']
        self.bound_object.date = datetime.now()
        self.bound_object.file_loc = ulpath + stored_name
        self.bound_object.save() 

class RecordingForm(ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = Recording

    #def __init__(self, bound_object=None, *args, **kwargs):
    #    super(RecordingForm, self).__init__(*args, **kwargs)
    #    self.bound_object = bound_object
    #    self.is_updating = False
    #    if self.bound_object:
    #        self.is_updating = True

    def clean(self):
        rec = self.cleaned_data.get('rec_file',None)
        if rec is None:
            raise forms.ValidationError("No file attached")
        if self.cleaned_data.get('rec_file',None).size > 209715200:
            raise forms.ValidationError("File too big, son")
        return self.cleaned_data

    def save(self):
        self.bound_object = Recording()
        uploaded_file = self.cleaned_data['rec_file']
        import re
        stored_name = re.sub(r'[^a-zA-Z0-9._]+', '-', uploaded_file.name)
        self.bound_object.rec_file.save(stored_name, uploaded_file)
        self.bound_object.mimetype = uploaded_file.content_type
        self.bound_object.name = self.cleaned_data['name']
        self.bound_object.public_description = self.cleaned_data['public_description']
        self.bound_object.private_description = self.cleaned_data['private_description']
        self.bound_object.location = self.cleaned_data['location']
        self.bound_object.date = datetime.now()
        self.bound_object.file_loc = settings.UPLOAD_ROOT + stored_name
        self.bound_object.save() 
