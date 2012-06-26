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
from django.db.models import Q
import json

from openwatch.recordings.models import Recording


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
    featureset = Recording.objects.filter(~Q(lat=None), ~Q(lon=None), ~Q(jtype='organic')).exclude(location__exact='No description available').order_by('-date')
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

def map_json(request):
    #featureset = Recording.objects.filter(~Q(lat=None), ~Q(lon=None), ~Q(jtype='organic')).order_by('-date')[:1000]
    featureset = Recording.objects.all().order_by('-date').filter(~Q(location='')).exclude(location__isnull=True).exclude(location__exact='')[:750]
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

    #featureset = Recording.objects.filter(lat__lt=ne_lat, lat__gt=sw_lat,lon__lt=ne_lon, lon__gt=sw_lon).order_by('-date')
    featureset = Recording.objects.order_by('-date').exclude(location__isnull=True).exclude(location__exact='').exclude(location__exact='No description available')[:750]

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