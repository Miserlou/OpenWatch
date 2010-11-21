#!/usr/bin/python2
#
# Youtube-upload is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Youtube-upload is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Youtube-upload. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Arnau Sanchez <tokland@gmail.com>
# Website: http://code.google.com/p/tokland/
# Website: http://code.google.com/p/youtube-upload

"""
Upload videos to youtube from the command-line (splitting the video if necessary).

$ youtube-upload myemail@gmail.com mypassword anne_sophie_mutter.flv \
  "A.S. Mutter" "Anne Sophie Mutter plays Beethoven" Music "mutter, beethoven"
www.youtube.com/watch?v=pxzZ-fYjeYs
"""

import os
import re
import sys
import time
import locale
import urllib
import optparse
import itertools
import subprocess
# python >= 2.6
from xml.etree import ElementTree 

# python-gdata (>= 1.2.4)
import gdata.media
import gdata.geo
import gdata.youtube
import gdata.youtube.service

VERSION = "0.5"
DEVELOPER_KEY = "AI39si7iJ5TSVP3U_j4g3GGNZeI6uJl6oPLMxiyMst24zo1FEgnLzcG4i" + \
                "SE0t2pLvi-O03cW918xz9JFaf_Hn-XwRTTK7i1Img"

def debug(obj):
    """Write obj to standard error."""
    string = str(obj.encode(get_encoding(), "backslashreplace") 
                 if isinstance(obj, unicode) else obj)
    sys.stderr.write("--- " + string + "\n")

def get_encoding():
    """Guess terminal encoding.""" 
    return sys.stdout.encoding or locale.getpreferredencoding()

def compact(it):
    """Filter false (in the truth sense) elements in iterator."""
    return filter(bool, it)
  
def run(command, inputdata=None, **kwargs):
    """Run a command and return standard output/error"""
    debug("run: %s" % " ".join(command))
    popen = subprocess.Popen(command, **kwargs)
    outputdata, errdata = popen.communicate(inputdata)
    return outputdata, errdata

def ffmpeg(*args, **kwargs):
    """Run ffmpeg command and return standard error output."""
    kwargs2 = {}
    if "show_stderr" not in kwargs:
        kwargs2["stderr"] = subprocess.PIPE
    outputdata, errdata = run(["ffmpeg"] + list(args), **kwargs2)
    return errdata

def get_video_duration(video_path):
    """Return video duration in seconds."""
    errdata = ffmpeg("-i", video_path)
    match = re.search(r"Duration:\s*(.*?),", errdata)
    if not match:
        return
    strduration = match.group(1)
    return sum(factor*float(value) for (factor, value) in 
               zip((60*60, 60, 1), strduration.split(":")))

def split_video(video_path, max_duration, max_size=None, split_rewind=0):
    """Split video in chunks and yield path of splitted videos."""
    if not os.path.isfile(video_path):
        raise ValueError, "Video path not found: %s" % video_path
    total_duration = get_video_duration(video_path)
    assert total_duration
    if total_duration <= max_duration and os.path.getsize(video_path) <= max_size:
        yield video_path
        return
    base, extension = os.path.splitext(os.path.basename(video_path))
    
    debug("split_video: %s, total_duration=%02.f" % (video_path, total_duration))
    offset = 0
    for index in itertools.count(1): 
        debug("split_video: index=%d, offset=%d (total=%d)" % 
            (index, offset, total_duration))
        output_path = "%s-%d.%s" % (base, index, "mkv")
        temp_output_path = "%s-%d.%s" % (base, index, "partial.mkv")
        if os.path.isfile(output_path) and get_video_duration(output_path):
            debug("skipping existing file: %s" % output_path)
        else:
            args = ["-y", "-i", video_path]
            if max_size:
                args += ["-fs", str(int(max_size))]
            args += ["-vcodec", "copy", "-acodec", "copy", "-ss", str(offset), 
                     "-t", str(max_duration), temp_output_path]
            err = ffmpeg(*args, **dict(show_stderr= True))
            os.rename(temp_output_path, output_path)
        yield output_path
        size = os.path.getsize(output_path)
        assert size
        duration = get_video_duration(output_path)
        assert duration
        debug("chunk file size: %d (max: %d)" % (size, max_size))  
        debug("chunk duration: %d (max: %d)" % (duration, max_duration))
        if size < max_size and duration < max_duration:
            debug("end of video reached: %d chunks created" % index)
            break 
        offset += duration - split_rewind

def split_youtube_video(video_path, split_rewind=5):
    """Split video to match Youtube restrictions (<2Gb and <15minutes)."""
    return split_video(video_path, 60*15, max_size=int(2e9), split_rewind=split_rewind)

def get_entry_info(entry):      
    """Return pair (url, id) for video entry."""
    url = entry.GetHtmlLink().href.replace("&feature=youtube_gdata", "")
    video_id = re.search("=(.*)$", url).group(1)
    return url, video_id

class Youtube:
    """Interface the Youtube API."""        
    CATEGORIES_SCHEME = "http://gdata.youtube.com/schemas/2007/categories.cat"
    
    def __init__(self, developer_key, email, password, source="tokland-youtube_upload", 
                 client_id="tokland-youtube_upload"):
        """Login and preload available categories."""
        service = gdata.youtube.service.YouTubeService()
        service.ssl = False # SSL is not yet supported by Youtube API
        service.email = email
        service.password = password
        service.source = source
        service.developer_key = developer_key
        service.client_id = client_id
        service.ProgrammaticLogin()
        self.service = service
        self.categories = self.get_categories()

    def get_upload_form_data(self, path, *args, **kwargs):
        """Return dict with keys 'post_url' and 'token' with upload info."""
        video_entry = self._create_video_entry(*args, **kwargs)
        post_url, token = self.service.GetFormUploadToken(video_entry)
        debug("post url='%s', token='%s'" % (post_url, token))
        return dict(post_url=post_url, token=token)

    def upload_video(self, path, *args, **kwargs):
        """Upload a video."""
        video_entry = self._create_video_entry(*args, **kwargs)
        return self.service.InsertVideoEntry(video_entry, path)

    def add_video_to_playlist(self, video_id, playlist_uri, title=None, description=None):
        """Add video to playlist."""
        playlist_video_entry = self.service.AddPlaylistVideoEntryToPlaylist(
            playlist_uri, video_id, title, description)
        return playlist_video_entry
      
    def check_upload_status(self, video_entry):
        """
        Check upload status of video entry.
        
        Return None if video is processed, and a pair (status, message) otherwise.
        """
        url, video_id = get_entry_info(video_entry)
        return self.service.CheckUploadStatus(video_id=video_id)
           
    def _create_video_entry(self, title, description, category, keywords=None, 
            location=None, private=False):
        assert self.service, "Youtube service object is not set"
        if category not in self.categories:
            valid = " ".join(self.categories.keys())
            raise ValueError("Invalid category '%s' (valid: %s)" % (category, valid))
        media_group = gdata.media.Group(
            title=gdata.media.Title(text=title),
            description=gdata.media.Description(description_type='plain', text=description),
            keywords=gdata.media.Keywords(text=keywords),
            category=gdata.media.Category(
                text=category,
                label=self.categories[category],
                scheme=self.CATEGORIES_SCHEME),
            private=(gdata.media.Private() if private else None),
            player=None)
        if location:            
            where = gdata.geo.Where()
            where.set_location(location)
        else: 
            where = None
        return gdata.youtube.YouTubeVideoEntry(media=media_group, geo=where)
                
    @classmethod
    def get_categories(cls):
        """Return categories dictionary with pairs (term, label)."""
        def get_pair(element):
            """Return pair (term, label) for a (non-deprecated) XML element."""
            if all(not(str(x.tag).endswith("deprecated")) for x in element.getchildren()):
                return (element.get("term"), element.get("label"))            
        xmldata = urllib.urlopen(cls.CATEGORIES_SCHEME).read()
        xml = ElementTree.XML(xmldata)
        return dict(compact(map(get_pair, xml)))

def parse_location(string):
    """Return tuple (long, latitude) from string with coordinates."""
    if string and string.strip():
        return map(float, string.split(",", 1))

def wait_processing(yt, entry):
    debug("waiting until video is processed")
    while 1:
        try:
          response = yt.check_upload_status(entry)
        except socket.gaierror, msg:
          debug("network error (will retry): %s" % msg)
          continue                      
        if not response:
            debug("video processed")
            break
        status, message = response
        debug("check_upload_status: %s" % " - ".join(compact(response)))
        if status != "processing":
            break 
        time.sleep(5)
    
def main_upload(filename, title, description):
    """Upload video to Youtube."""
    usage = """Usage: %prog [OPTIONS] EMAIL PASSWORD FILE TITLE DESCRIPTION CATEGORY KEYWORDS

    Upload a video to youtube spliting it if necessary (uses ffmpeg)."""

    email = 'XXXXYOUREMAIL'
    password = 'XXXXYOURPASSWORD'

    print arguments

    parser = optparse.OptionParser(usage, version=VERSION)
    parser.add_option('-t', '--time-rewind', dest='split_rewind', type="int", 
        default=5, metavar="SECONDS", 
        help='Time to rewind between videos on split (default: 5 seconds)')
    parser.add_option('-c', '--get-categories', dest='get_categories',
        action="store_true", default=False, help='Show video categories')
    parser.add_option('-s', '--split-only', dest='split_only',
        action="store_true", default=False, help='Split videos without uploading')
    parser.add_option('-n', '--no-split', dest='no_split',
        action="store_true", default=False, help='Skip video split')
    parser.add_option('-u', '--get-upload-form-info', dest='get_upload_form_data',
        action="store_true", default=False, help="Don't upload, just get the form info")
    parser.add_option('', '--private', dest='private',
        action="store_true", default=False, help='Set uploaded video as private')
    parser.add_option('', '--location', dest='location', type="string", default=None,
        metavar="COORDINATES", help='Video location (lat, lon). example: "37.0,-122.0"')
    parser.add_option('', '--playlist-uri', dest='playlist_uri', type="string", default=None,
        metavar="URI", help='Upload video to playlist')
    parser.add_option('', '--wait-processing', dest='wait_processing', action="store_true", 
        default=False, help='Wait until the video has processed')
    options, args = parser.parse_args(arguments)
    
    if options.get_categories:
        print " ".join(Youtube.get_categories().keys())
        return
    elif options.split_only:
        video_path, = args
        for path in split_youtube_video(video_path, options.split_rewind):
            print path
        return
    elif len(args) != 7:
        parser.print_usage()
        return 1
    
    encoding = get_encoding()
    email, password0, video_path, title, description, category, skeywords = \
        [unicode(s, encoding) for s in args]
    password = (sys.stdin.readline().strip() if password0 == "-" else password0)
    videos = ([video_path] if options.no_split else 
              list(split_youtube_video(video_path, options.split_rewind)))
    debug("connecting to Youtube API")
    yt = Youtube(DEVELOPER_KEY, email, password)
    
    for index, splitted_video_path in enumerate(videos):
        complete_title = ("%s [%d/%d]" % (title, index+1, len(videos)) 
                          if len(videos) > 1 else title)
        args = [splitted_video_path, complete_title, description, category, skeywords]
        kwargs = dict(private=options.private, location=parse_location(options.location))
        if options.get_upload_form_data:
            data = yt.get_upload_form_data(*args, **kwargs)
            print "\n".join([splitted_video_path, data["token"], data["post_url"]])
            if options.playlist_uri:
                debug("--playlist-uri is ignored on form upload")        
        else:
            debug("start upload: %s (%s)" % (splitted_video_path, complete_title)) 
            entry = yt.upload_video(*args, **kwargs)                
            url, video_id = get_entry_info(entry)                     
            if options.wait_processing:
                wait_processing(yt, entry)
            print url
            if options.playlist_uri:
                debug("adding video (%s) to playlist: %s" % (video_id, options.playlist_uri))
                yt.add_video_to_playlist(video_id, options.playlist_uri)
   
if __name__ == '__main__':
    sys.exit(main_upload(sys.argv[1:]))
