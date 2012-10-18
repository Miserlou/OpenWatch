# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from tagging.models import Tag, TaggedItem
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404
from django.db.models import Q
import json

from openwatch.recordings.models import Recording
from openwatch import recording_tags


@login_required
def moderate(request):
    '''  Split  map/table recording moderation.
         Requires user is a superuser or has an org tag and can_moderate=True
    '''

    response_values = {}

    org_tag = request.user.get_profile().org_tag
    # If the user isn't a superuser or doesn't have an org tag w/ moderation privilege, bounce 'em
    #print 'can_moderate: ' + str(request.user.get_profile().can_moderate) + ' org_tag: ' + str(org_tag)
    if not request.user.is_superuser and (not request.user.get_profile().can_moderate or org_tag == ''):
        raise Http404

    if recording_tags.ACLU_NJ in org_tag:
        # Center on New Jersey
        location = {}
        location['lat'] = 40.167274
        location['lon'] = -74.616338
        response_values['location'] = location

    response_values['total'] = 'lots!'

    return render_to_response('moderate.html', response_values, context_instance=RequestContext(request))



def map(request):
    #featureset = Recording.objects.filter(~Q(lat=None), ~Q(lon=None), ~Q(jtype='organic')).order_by('-date')
    #total = len(featureset)
    total = "lots!"
    return render_to_response('map.html', {'total': total}, context_instance=RequestContext(request))

# def map_zipcode(request, zipcode):
#     #featureset = Recording.objects.filter(~Q(lat=None), ~Q(lon=None), ~Q(jtype='organic')).order_by('-date')
#     #total = len(featureset)
#     total = ">40000"
#     try:
#         location = Location.objects.get(zipcode=zipcode)
#     except:
#         return HttpResponseRedirect('/')
#     return render_to_response('map.html', {'total': total, 'location': location, 'zipcode': zipcode}, context_instance=RequestContext(request)) 

def size(request):
    featureset = Recording.objects.filter(~Q(lat=None), ~Q(lon=None), ~Q(jtype='organic')).exclude(location__exact='No description available').exclude(location__exact='0.0, 0.0').order_by('-date')
    total = len(featureset)
    return render_to_response('map.html', {'total': total}, context_instance=RequestContext(request)) 

def redir(self):
    return HttpResponseRedirect('/')

# def map_tag(request, tag=None):

#     #0 Responses
#     try:
#         query_tag = Tag.objects.get(name=tag)
#     except Exception, e:
#         return render_to_response('map.html', {'jobs': [], 'numcareers': 0, 'tag': tag}, context_instance=RequestContext(request)) 

#     entries = TaggedItem.objects.get_by_model(Recording, query_tag)
#     featureset = entries.filter(~Q(lat=None), ~Q(lon=None),).order_by('-date')


#     return render_to_response('map.html', {'jobs': featureset, 'numcareers': len(featureset), 'tag': tag}, context_instance=RequestContext(request))

def map_json(request, moderate=0):
    #featureset = Recording.objects.filter(~Q(lat=None), ~Q(lon=None), ~Q(jtype='organic')).order_by('-date')[:1000]
    featureset = Recording.objects.all().order_by('-date').filter(~Q(location='')).exclude(location__isnull=True).exclude(location__exact='')[:750]
    resp = encode_queryset(featureset)
    return HttpResponse(resp, mimetype="application/json")


@login_required
def map_json_moderate(request):
    # If moderating, only return recordings that are not org-approved
    # And that are tagged with the user's organization tag
    org_tag = request.user.get_profile().org_tag
    if org_tag != '':
        #print 'Org tag: ' + org_tag
        featureset = Recording.objects.filter(org_approved=False, org_flagged=False, tags__contains=org_tag)
    else:
        featureset = Recording.objects.all()

    #featureset = Recording.objects.filter(~Q(lat=None), ~Q(lon=None), ~Q(jtype='organic')).order_by('-date')[:1000]
    featureset = featureset.order_by('-date').filter(~Q(location='')).exclude(location__isnull=True).exclude(location__exact='')
    resp = encode_queryset(featureset)
    return HttpResponse(resp, mimetype="application/json")

# def map_tag_json(request, tag):

#     #0 Responses
#     try:
#         query_tag = Tag.objects.get(name=tag)
#     except Exception, e:
#         return HttpResponse("{\"objects\":[]}", mimetype="application/json")

#     entries = TaggedItem.objects.get_by_model(Recording, query_tag)
#     #featureset = entries.filter(~Q(lat=None), ~Q(lon=None),).order_by('-date')
#     featureset = entries.filter().order_by('-date')
#     resp = encode_queryset(featureset)
#     return HttpResponse(resp, mimetype="application/json")


# def map_tag_location(request, tag=None, ne_lat=0, ne_lon=0, sw_lat=0, sw_lon=0):

#     ne_lat = float(ne_lat)
#     ne_lon = float(ne_lon)
#     sw_lat = float(sw_lat)
#     sw_lon = float(sw_lon)

#     #0 Responses
#     try:
#         query_tag = Tag.objects.get(name=tag)
#     except Exception, e:
#         return render_to_response('map.html', {'jobs': [], 'numcareers': 0, 'tag': tag}, context_instance=RequestContext(request)) 

#     entries = TaggedItem.objects.get_by_model(Recording, query_tag)
#     #featureset = entries.filter(lat__lt=ne_lat, lat__gt=sw_lat,lon__lt=ne_lon, lon__gt=sw_lon).order_by('-date')
#     featureset = Recording.objects.order_by('-date')
    
#     return render_to_response('map.html', {'jobs': featureset, 'numcareers': len(featureset), 'tag': tag}, context_instance=RequestContext(request))

def map_location_json(request, ne_lat=0, ne_lon=0, sw_lat=0, sw_lon=0):

    ne_lat = float(ne_lat)
    ne_lon = float(ne_lon)
    sw_lat = float(sw_lat)
    sw_lon = float(sw_lon)

    featureset = Recording.objects.filter(lat__lt=ne_lat, lat__gt=sw_lat,lon__lt=ne_lon, lon__gt=sw_lon).order_by('-date').exclude(location__isnull=True).exclude(location__exact='').exclude(location__exact='No description available').exclude(location__exact='0.0, 0.0')[:750]
    #featureset = Recording.objects.order_by('-date').exclude(location__isnull=True).exclude(location__exact='').exclude(location__exact='No description available').exclude(location__exact='0.0, 0.0')[:750]

    if len(featureset) < 1:
        return HttpResponse("{\"objects\":[]}", mimetype="application/json")
    
    resp = encode_queryset(featureset)
    return HttpResponse(resp, mimetype="application/json")

# def about(request):
#     return render_to_response('about.html', {}, context_instance=RequestContext(request))

# Encoders

def encode_queryset(featureset):
    resp = '{"objects":['
    for obj in featureset:
        resp = resp + json.dumps(obj.to_dict()) + ','
    resp = resp[:-1] + ']}'

    return resp