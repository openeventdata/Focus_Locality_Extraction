#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Download and run Mordecai from following link: 
    
    "https://github.com/mitmedialab/CLIFF-up"
    
    To change the corpus, just change the name in main function.
    
"""

import xml.etree.ElementTree as et
import requests
import json, sys

#reload(sys)
#sys.setdefaultencoding("utf-8")

def ClavinCliff(text):
    
    place=list()

    
    try:
        data = {'q': text.replace("'","")}  
    except:
        data = {'q': text}  
        
    out = requests.post('http://10.176.148.123:8999/cliff-2.3.0/parse/text', data=data)
    parsed_json = json.loads(out.text)
    try:
        for e in parsed_json["results"]["places"]["mentions"]:
            ind = e['source']['charIndex']
            place.append(e["name"]+ ",," + e['source']['string']+ ",," + str(e['lat']) + ",," + str(e['lon']) + ",,"+ str(ind) +',,'+ str(ind +len(e['source']['string'].strip()) ))
            
            #print place
    except:
        print "error"
    
    return place


if __name__ == '__main__':
      
    f = open('./data/wiki_Cliff.txt' , 'w') #change it if your data is lgl.xml
    
    tree = et.parse('./WikToR(SciPaper).xml') #change it if your data is lgl.xml
    root = tree.getroot()
    c = 0
    correct = 0
    for child in root:
        c +=1
        print c

        text = child.find('text').text
        place = ClavinCliff(text)
        
        if (place): 
            for t in place:
                f.write(t + "||")
        f.write("\n")
        f.flush()