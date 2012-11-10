import json
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, Http404, HttpResponse
from recordings.utils import validate_email
from datetime import datetime
from tagging.models import Tag, TaggedItem
from django.views.decorators.csrf import csrf_exempt

import recording_tags

from openwatch.recordings.models import Recording, RecordingForm, RecordingNoCaptchaForm

def root(request):
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('home.html', {'featured': list(featureset)[0:5], 'cat': 'main' })

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
            return HttpResponseRedirect('/victory') # Redirect after POST
        else:
            pass
            #print "Shiiiiit"
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
    if request.method == 'POST':  # If the form has been submitted...
        recording = Recording()
        # Check if recording submitted by ACLU-NJ Police Tape 
        # These recording filenames are of form XXXX_aclunj.XXX
        #print 'checking ' + str(request.FILES['rec_file'].name)

        tag = recording_tags.ACLU_NJ
        if "_aclunj." in str(request.FILES['rec_file'].name):
            #print str(request.FILES['rec_file'].name) + ' will be tagged with ' + tag
            recording.add_tag(tag)
            # Police Tape appends email to existing privDesc:
            # privDesc = privDesc + "[" + email + "]";

            #recording.email = request.POST.get('private_description', '').rsplit("[", 1)[1].rsplit("]", 1)[0]
            potential_email = request.POST.get('private_description', '').rsplit("[", 1)[1].rsplit("]", 1)[0]
            if validate_email(potential_email):
                recording.email = potential_email
                recording.private_description = request.POST.get('private_description', 'No description available').rsplit("[", 1)[0]
            else:
                recording.private_description = request.POST.get('private_description', 'No description available')
        else:
            recording.private_description = request.POST.get('private_description', 'No description available')

        recording.public_description = request.POST.get('public_description', 'No description available')
        recording.name = request.POST.get('name', 'No description available')
        recording.public_description = request.POST.get('public_description', 'No description available')
        recording.location = request.POST.get('location', 'No description available')
        recording.rec_file = request.FILES['rec_file']
        recording.date = datetime.now()
        recording.save()
        return HttpResponseRedirect('/victory')  # Redirect after POST
    else:
        form = RecordingNoCaptchaForm()  # An unbound form

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
    #queryset = Recording.objects.filter(approved=True).all().order_by('-date')
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    #print request.user.get_profile().can_moderate
    if not recording.approved and not request.user.is_superuser:
        raise Http404
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


''' AJAX API
'''


@login_required
def approve(request, media_id):
    ''' Approve a recording at the top-level

        Once Approved, it will appear on OpenWatch.net

        To Approve, user.is_superuser == True

        Args:
            media_id : a Recording pk
    '''

    if request.user.is_superuser:
        recording = get_object_or_404(Recording, pk=media_id)
        recording.approved = True
        recording.save()
        return HttpResponse(json.dumps({'status': 'success'}), mimetype="application/json")
    else:
        return HttpResponse(json.dumps({'status': 'failure'}), mimetype="application/json")


@login_required
def org_moderate(request, media_id):
    ''' Approve or Flag a recording at the organizational level

        Org approval should be considered by admins
        Before top-level approval for display on OpenWatch.net
        with organizational affiliation

        Flagging should be considered by admins
        in their decision to delete recordings of no significance
        Flagged recordings will not appear in the organizations
        map moderation panel

        To Approve, a user must have can_moderate true and
        an organizational tag matching a tag held by the Recording with pk=media_id
        Or have .issup

        Args:
            media_id : a Recording pk
            [POST] value: 1 = Approve, -1 = Flag

    '''
    org_tag = request.user.get_profile().org_tag
    recording = get_object_or_404(Recording, pk=media_id)
    if 'value' not in request.POST:
        raise Http404

    value = int(request.POST.get('value', 0))
    #print 'POST moderate value: ' + str(value)

    if request.user.is_superuser or (org_tag in recording.tags and request.user.get_profile().can_moderate):
        recording = get_object_or_404(Recording, pk=media_id)
        if value == 1:
            recording.org_approved = True
        elif value == -1:
            recording.org_flagged = True
        else:
            return HttpResponse(json.dumps({'status': 'failure'}), mimetype="application/json")

        recording.save()
        return HttpResponse(json.dumps({'status': 'success'}), mimetype="application/json")
    else:
        return HttpResponse(json.dumps({'status': 'failure'}), mimetype="application/json")
