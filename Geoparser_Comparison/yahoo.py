#!/usr/bin/python

import urllib
import xml.etree.ElementTree as ET
import sys


def yahoo_resolve(q):
    """
    This simple script calls the API of Yahoo PlaceMaker to find and ground toponyms in text.
    You can use it in a Unix command line or integrate it into a python project for instance.

    Command line usage: ./path/to/yahoo.py "TEXT to be processed (not a filename)"
    :param q: TEXT to be processed (not a filename)
    :return: A list of toponyms - format: [geoname, matched name, lat, long, start index, end index]
    """
    q = q.replace("\"", "\'")  # Yahoo API does not like double quotes so we remove them
    base_url = 'https://query.yahooapis.com/v1/public/yql?'
    query = {'q': 'SELECT * FROM geo.placemaker WHERE documentContent=\"'
            + q + '\" AND documentType=\"text/plain\"', 'format': 'xml'}
    response = urllib.urlopen(base_url + urllib.urlencode(query))  # contact Yahoo servers
    out = []  # list of tuples as output
    ns = "{http://wherein.yahooapis.com/v1/schema}"  # namespace to avoid repetition
    root = ET.fromstring(response.read())
    matches = root.findall("./results/matches/match")
    if response.code != 200:
        print "Error Response Code =", response.code, " query=", q
        print response.info()
        return
    for match in matches:
        refs = match.findall("./" + ns + "reference")
        place = match.find("./" + ns + "place")
        for ref in refs:
            name = place.find(ns + 'name').text if place.find(ns + 'name').text is not None else "None"
            lat = place.find('./' + ns + 'centroid/' + ns + 'latitude').text
            lon = place.find('./' + ns + 'centroid/' + ns + 'longitude').text
            start = ref.find(ns + 'start').text
            end = ref.find(ns + 'end').text
            string = ref.find(ns + 'text').text
            out.append(name + ",," + string + ",," + lat + ",," + lon + ",," + start + ",," + end)
    return out


# This is how to use it inside the editor.
# q = ""
# print yahoo_resolve(q)

if len(sys.argv) > 1:
    print "Your query:", sys.argv[1]
    results = "No toponyms found..."
    for t in yahoo_resolve(sys.argv[1]):
        results = "Finished..."
        print "Toponym:", t
    print results
