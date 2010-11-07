from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from datetime import datetime
from MassSous.recordings.models import Recording, RecordingForm 

def upload(request):
    if request.method == 'POST': # If the form has been submitted...
        form = RecordingForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # XXX: Check filetypes, etc

            form.save()
            return HttpResponseRedirect('/MassSous/victory') # Redirect after POST
        else:
            print "Shiiiiit"
    else:
        form = RecordingForm() # An unbound form

    return render_to_response('upload.html', {
        'form': form,
    })

def victory(request):
    return render_to_response('victory.html')
