#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  1 13:40:15 2017

@author: maryam
"""

from __future__ import division
from nltk.tag import StanfordNERTagger
import nltk.data
from itertools import izip
import sys, os
import json
from mitie import *


reload(sys)
sys.setdefaultencoding("utf-8")


def get_JSONfile(JSONfileName):
        
    with open(JSONfileName) as f:
        content = json.load(f)
    
    content= dict((k.lower().strip(), v) for k,v in content.iteritems())
    return content


# Mitie function to extract location names
def MitieNER(tokens, ner):
    
    entities = ner.extract_entities(tokens)
    locDic = {}
        
    for e in entities:
        range = e[0]
        tag = e[1]
        
        if tag == 'LOCATION':
            entity_text = " ".join(tokens[i] for i in range)
            
            ent = entity_text.lower().strip()
            if ent not in locDic:
                locDic[ent] = 1
            else:
                locDic[ent] +=locDic[ent]
            
    return locDic


# Stanford function to extract location names
def stanfordNER(text, st):    
    loc=[]
    locDic={}
    
    tagg=st.tag(text.split())
    length= len(tagg)
    k=0
    i=0
    if (length == 0):
        print('error')
        return []
    while (i<length):
        loc_part=''
        if (tagg[i][1]== 'LUG' or tagg[i][1]=='LOCATION'):
            for j in range(i, length):
                if (tagg[j][1]== 'LUG' or tagg[i][1]=='LOCATION'):
                    loc_part += " "+ tagg[j][0].strip().replace('.','').replace('\n', '')
                    k=j+1
                else:
                    break
            i=k
            if (loc_part !=''):
                if (loc_part.replace('\n', '') not in loc):
                    loc.append(loc_part.strip().replace('\n', ''))
                
                lname= loc_part.strip().encode('utf8').replace('\n', '')
                if (locDic.has_key(lname)):
                    locDic[lname]= locDic[lname]+1
                else:
                    locDic[lname]= 1
                #print loc_part
        else:
            i= i+1
    return locDic


def main(pathGT, pathR, NER, lang):

    
    Sent = list()
    Lbl = list()
    Doc = list()
    Loc = list()
    
    
#    pathGT = '/data/maryam/Documents/Geolocation11272017/Spanish_PDF/PDF_JSON/MunicipalitFiltered.txt'
#    pathR = '/data/maryam/Documents/Geolocation11272017/Spanish_PDF/PDF_JSON/StoryFiltered.txt'
    
    print("loading NER model...")
    if NER == 'Stanford': 
        # Stanford setup
        os.environ['CLASSPATH'] = '/data/maryam/Documents/Geolocation11272017/Spanish_protest/stanford/stanford-ner.jar'  
        if lang == 'es':
            st = StanfordNERTagger('/data/maryam/Documents/Geolocation11272017/Spanish_protest/stanford/stanford-spanish-corenlp-models-current/edu/stanford/nlp/models/ner/spanish.ancora.distsim.s512.crf.ser.gz')
        elif lang == 'en': 
            st = StanfordNERTagger('/data/maryam/Documents/Geolocation11272017/Spanish_protest/stanford/stanford-spanish-corenlp-models-current/edu/stanford/nlp/models/ner/spanish.ancora.distsim.s512.crf.ser.gz')
    
    else:
        sys.path.append('/data/maryam/Documents/Tools/Libs/MITIE-master/mitielib')
        if lang == 'es':
            ner = named_entity_extractor('/data/maryam/Documents/Tools/Libs/MITIE-models/spanish/ner_model.dat')
        elif lang == 'en': 
            ner = named_entity_extractor('/data/maryam/Documents/Tools/Libs/MITIE-models/english/ner_model.dat')
    
    
    # load the country names in different languages
    if lang == 'en': 
        JSONfileName = './data/english_country_names.json'
    if lang == 'es': 
        JSONfileName = './data/spanish_country_names.json'
    
    try:
        countries = get_JSONfile(JSONfileName).keys()
    except: 
        countries = list()
    
    
    docCount=0 
    
    with open(pathR) as fileR, open(pathGT) as fileGT:
        for text, focus_locs in izip(fileR, fileGT):
            
            docCount = docCount +1
            
            if docCount % 100 == 0:
                print str(docCount) + ' news have been processed'
            sentNum = 0
            
            
            if NER == 'Stanford': 
                loc_stan= stanfordNER(text, st)
            else:   
                tokens = tokenize(text)
                loc_stan= MitieNER(tokens, ner)
            
            
            sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
            sent_list= sent_detector.tokenize(text.encode('utf-8').strip())
            
            #focus_locs= focus_locs.strip()
            for sent in sent_list:
                
                flagFocus= False
                sentNum +=1
                
                if (sentNum > 7):
                    break
                
                for focus_loc in focus_locs.split(','):
                    focus_loc = focus_loc.strip()
                    
                    if ( focus_loc.lower() in sent.lower() and flagFocus == False):
                        
                        Sent.append(sent.encode('utf-8'))
                        Lbl.append(1)
                        Doc.append( str(docCount))
                        Loc.append(focus_loc.encode('utf-8'))
                        
                        
                        flagFocus = True
                
                if flagFocus == False:
                    
                    for loc in loc_stan:
                        
                        if(loc in countries):
                            continue
                        
                        if  (loc.lower() in sent.lower()):
                            
                            Sent.append(sent.encode('utf-8'))
                            Lbl.append(0)
                            Doc.append( str(docCount))
                            Loc.append(loc.encode('utf-8'))
                                                      
                            
                            break
    
    return Sent, Lbl, Doc, Loc

    
if __name__ == '__main__':
    
    pathGT = sys.argv[1] #path to locations in ground truth 
    pathR = sys.argv[2] #path to text file (each line has is a news story)
    NER = sys.argv[3]   # specify the NER tool (Stanford or Mitie)
    lang = sys.argv[4]
    
    Sent, Lbl, Doc, Loc = main(pathGT, pathR, NER, lang)