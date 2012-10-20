from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from datetime import datetime
from tagging.models import Tag, TaggedItem
from django.views.decorators.csrf import csrf_exempt

from openwatch.recordings.models import Recording, RecordingForm, RecordingNoCaptchaForm

def root(request):

    #featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('coming_soon.html')

def about(request):
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('about.html', {'featured': list(featureset)[0:5], 'cat': 'about' })

def apps(request):
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('apps.html', {'featured': list(featureset)[0:5], 'cat': 'apps' })

def contact(request):
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('contact.html', {'featured': list(featureset)[0:5], 'cat': 'contact' })

def join(request):
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('join.html', {'featured': list(featureset)[0:5], 'cat': 'join' })

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

    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('upload.html', {
        'form': form,
        'featured': list(featureset)[0:5],
        'cat': 'upload' 
    })

@csrf_exempt
def upload_no_captcha(request):
    if request.method == 'POST': # If the form has been submitted...
        recording = Recording()
        recording.public_description = request.POST.get('public_description', 'No description available')
        recording.private_description = request.POST.get('private_description', 'No description available')
        recording.name = request.POST.get('name', 'No description available')
        recording.public_description = request.POST.get('public_description', 'No description available')
        recording.location = request.POST.get('location', 'No description available')
        recording.rec_file = request.FILES['rec_file']
        recording.date = datetime.now()
        recording.save()
        return HttpResponseRedirect('/openwatch/victory') # Redirect after POST
    else:
        form = RecordingNoCaptchaForm() # An unbound form

    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('upload_nocaptcha.html', {
        'form': form,
        'featured': list(featureset)[0:5],
        'cat': 'upload' 
    })

def victory(request):
    return render_to_response('victory.html')

def listall(request):
    queryset = Recording.objects.filter(approved=True).all().order_by('-date')
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('listall.html', {'list': list(queryset), 'featured': list(featureset)[0:5], 'cat': 'media'})

def view(request, media_id):
    recording = get_object_or_404(Recording, pk=media_id)
    queryset = Recording.objects.filter(approved=True).all().order_by('-date')
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    if not recording.approved:
       return HttpResponseNotFound('<h1>No Page Here</h1>')
    return render_to_response('view.html', {'recording': recording, 'featured': list(featureset)[0:5], 'cat': 'media'})

def tags(request):
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response("tags.html", {'featured': list(featureset)[0:5], 'cat': 'media'})

def with_tag(request, tag, object_id=None, page=1):
    query_tag = Tag.objects.get(name=tag)
    entries = TaggedItem.objects.get_by_model(Recording, query_tag)
    entries = entries.order_by('-date')
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response("with_tag.html", {'tag': tag, 'entries': entries, 'featured': list(featureset)[0:5], 'cat': 'media'})

