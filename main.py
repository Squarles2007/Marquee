# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from datetime import datetime
import os
import re
import tkinter as tk
from tkinter import filedialog
import tmdbsimple as tmdb
import PTN
import pprint
from urllib import request
from fuzzywuzzy import fuzz
from wand.image import Image

#add code here
def mkv_img_resize(filename: str):
    # resize poster image to meet matroska spec smallest side 600px
    with Image(filename=filename) as img:
        w = img.width
        h = img.height
        if w <= h:
            resize_ratio = 600 / w
        else:
            resize_ratio = 600 / h
        img.resize(int(w * resize_ratio), int(h * resize_ratio))
        img.save(filename=filename)
        img.close()

from pymkv import MKVAttachment, MKVFile

# Setup Section

# TMDP APIv3 Key
tmdb.API_KEY = '7538fbf0a0d48d0fcd68f16c06fe3674'
search = tmdb.Search()

# get TMDB configuration
tmdbConf = tmdb.Configuration()
tmdbConf.info()

# tkinter setup
root = tk.Tk()
root.withdraw()
# pretty print setup
pp = pprint.PrettyPrinter()

# Ask user for directory we are going to be looking in
dir = filedialog.askdirectory(initialdir='/media/fquarles')

# regex setup looking for filename extensions *.mp4 or *.mkv
regexp = r'\.mkv$|\.mp4$'
regexp = re.compile(regexp)

regex_mkv = r'\.mkv$'
regex_mkv = re.compile(regex_mkv)

missing = []

# Walk directories below userprovided dir
for dirpath, dnames, fnames in os.walk(dir):
    # iterate filenames
    for f in fnames:
        # check for desired file extensions
        m = regexp.search(f)
        if m:
            # parse torrent title info
            info = PTN.parse(f)
            # search TMDB for found title name
            search.movie(query=info['title'])
            # iterate search results
            found = False
            for s in search.results:
                # find an exact match
                if fuzz.ratio(s['title'], info['title']) > 92:
                    found = True
                    movie = tmdb.Movies(s['id'])
                    # get movie info from TMDB
                    response = movie.info()
                    if response['poster_path'] is None:
                        break
                    # concat poster url
                    poster_url = tmdbConf.images['secure_base_url'] + tmdbConf.images['poster_sizes'][-1] + \
                                 response['poster_path']
                    # Download poster
                    poster_file = request.urlretrieve(poster_url, dirpath + response['poster_path'])
                    mkv_img_resize(poster_file[0])
                    if(regex_mkv.search(f)):
                        # add poster file to mkv
                        command = 'mkvpropedit \'' + os.path.join(dirpath, f) + '\' --attachment-name "cover.jpg" ' \
                                                                             '--attachment-mime-type "image/jpeg" ' \
                                                                             '--add-attachment \'' + poster_file[0] + '\''
                        print("Running command: " + command)
                        os.system(command)
                        # delete no longer needed poster file
                        os.remove(poster_file[0])
                    else:
                        command = 'AtomicParsley \'' + os.path.join(dirpath, f) + '\' --artwork \'' + poster_file[0] \
                                  + '\' --overWrite'
                        print("Running command: " + command)
                        os.system(command)
                        # delete no longer needed poster file
                        os.remove(poster_file[0])
            if not found:
                missing.append(f)
print("Could Not Find")
for file in missing:
    print(file)




