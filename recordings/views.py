from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from datetime import datetime
from openwatch.recordings.models import Recording, RecordingForm 

def root(request):
    default = {'date': 'Nov 16, 2010', 'body': 'Welcome to OpenWatch, a project to house citizen media of recordings of power use and abuse from around the world. OpenWatch is currently the web counterpart to the Cop Recorder application for Android, though it will be expanding greatly in the coming weeks. More soon. ', 'name': 'Welcome to OpenWatch'}
    print default
    return render_to_response('index.html', {'content': [default]})

def upload(request):
    if request.method == 'POST': # If the form has been submitted...
        form = RecordingForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # XXX: Check filetypes, etc

            form.save()
            return HttpResponseRedirect('/openwatch/victory') # Redirect after POST
        else:
            print "Shiiiiit"
    else:
        form = RecordingForm() # An unbound form

    return render_to_response('upload.html', {
        'form': form,
    })

def victory(request):
    return render_to_response('victory.html')
