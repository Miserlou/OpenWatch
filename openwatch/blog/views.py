from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from datetime import datetime
from tagging.models import Tag, TaggedItem
from django.views.decorators.csrf import csrf_exempt

from openwatch.blog.models import Post 
from openwatch.recordings.models import Recording, RecordingForm, RecordingNoCaptchaForm

def view(request, media_id):
    post = get_object_or_404(Post, pk=media_id)
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    if not post.approved:
       return HttpResponseNotFound('<h1>No Page Here</h1>')
    return render_to_response('viewblog.html', {'post': post, 'featured': list(featureset)[0:5], 'cat': 'blog'})

def listall(request):
    queryset = Post.objects.filter(approved=True).all().order_by('-date')
    featureset = Recording.objects.filter(featured=True).all().order_by('-date')
    return render_to_response('listallblog.html', {'list': list(queryset), 'featured': list(featureset)[0:5], 'cat': 'blog'})
