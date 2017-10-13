#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Download and run Mordecai from following link: 
    
    "https://github.com/openeventdata/mordecai"
    
    To change the corpus, just change the name in main function.
"""

import xml.etree.ElementTree as et
import re
import json, sys
import requests

#reload(sys)
#sys.setdefaultencoding("utf-8")


def Mordecai(text):

    headers = {'Content-Type': 'application/json'}
    place=list()
        
    data = {'text': text}
        
    data = json.dumps(data)    
    out = requests.post('http://localhost:5000/places', data=data, headers=headers)
    parsed_json = json.loads(out.text)
    try:
        for e in parsed_json:
            #print e
            index = [m.start() for m in re.finditer(e['placename'].strip(), text)]
            for ind in index:                 
                place.append(e['searchterm'] + ",," + e['placename'] + ",," + str(e['lat']) + ",," + str(e['lon']) + ",,"+ str(ind) +',,'+ str(ind +len(e['placename'].strip()) ))
            
    except:
        pass     
    
    return place



if __name__ == '__main__':
      
    f = open('./data/wiki_mordecai_Original.txt' , 'w')
    
    tree = et.parse('./WikToR(SciPaper).xml')   #change it if your data is lgl.xml
    root = tree.getroot()
    c = 0
    for child in root:
        c +=1
        print c

        
        text = child.find('text').text
        place = Mordecai(text)
        
        if (place): 
            for t in place:
                f.write(t + "||")
        f.write("\n")
        f.flush()
