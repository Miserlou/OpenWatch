from django.db import models
from django.db.models.signals import post_save
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

from recordings.models import Recording

class FeatureSet(models.Model):

    rec = models.ForeignKey(Recording, null=False, editable=False)

    num_minutes = models.FloatField(null=True, blank=True)
    file_size = models.FloatField(null=True, blank=True)

    has_location = models.BooleanField(default=False, blank=True)

    # Number of words, number of actually english words
    title_word_count = models.FloatField(null=True, blank=True)
    title_actual_word_count = models.FloatField(null=True, blank=True)

    desc_word_count = models.FloatField(null=True, blank=True)
    desc_actual_word_count = models.FloatField(null=True, blank=True)

    private_word_count = models.FloatField(null=True, blank=True)
    private_actual_word_count = models.FloatField(null=True, blank=True)

    title = models.CharField(max_length='200', blank=True)
    description = models.CharField(max_length='200', blank=True)
    private = models.CharField(max_length='200', blank=True)

    is_test = models.BooleanField(default=False, blank=True)

    file_type = models.CharField(max_length='200', blank=True)

    verified = models.BooleanField(default=False, blank=True)
    legit = models.BooleanField(default=False, blank=True)

class SciPickle(models.Model):

    pickle = models.TextField()