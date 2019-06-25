#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: maryam
"""

from __future__ import division
from nltk.tag import StanfordNERTagger
import sys, os
import json
sys.path.append("/home/ahalt/MITIE/mitielib")
from mitie import *
from polyglot.text import Text


#reload(sys)
#sys.setdefaultencoding("utf-8")


def get_JSONfile(JSONfileName):
    with open(JSONfileName) as f:
        content = json.load(f)
    
    content= dict((k.lower().strip(), v) for k,v in content.iteritems())
    return content


# polyglot function to extract location names
def polyglotNER(textNews):
    locDic = {}
 #   print textNews
    text = Text(textNews)
    entities = text.entities
    for entity in entities: 
        if entity.tag == 'I-LOC':
            ent=''
            ent = ' '.join(entity)
#            ent = ent.decode('utf-16')
#            print(ent)
            if ent not in locDic:
                locDic[ent] = 1
            else:
                locDic[ent] +=locDic[ent]
#    print (locDic)    
    return locDic


# Mitie function to extract location names
def MitieNER(tokens, ner_model):
    
    entities = ner_model.extract_entities(tokens)
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
                
                lname= loc_part.strip().decode('utf-16').replace('\n', '')
                if (locDic.has_key(lname)):
                    locDic[lname]= locDic[lname]+1
                else:
                    locDic[lname]= 1
                #print loc_part
        else:
            i= i+1
    return locDic


def main(textTest, ner_model, NER, lang):
    Sent = list()
    Loc = list()
    
    # load the country names in different languages
    if lang == 'en': 
        JSONfileName = './data/english_country_names.json'
    elif lang == 'es': 
        JSONfileName = './data/spanish_country_names.json'
    elif lang == 'ar': 
        JSONfileName = './data/arabic_country_names.json'
    
    try:
        countries = get_JSONfile(JSONfileName).keys()
    except: 
        countries = list()
    
        
    textTest = textTest[textTest.find("-")+1:]
    text = Text(textTest, hint_language_code= lang)

    sentNum = 0
    
    if NER == 'Stanford': 
        loc_stan= stanfordNER(text, st)
    elif NER == 'Mitie':   
        tokens = tokenize(str(text))
        loc_stan= MitieNER(tokens, ner_model)
    else:
        loc_stan = polyglotNER(texttt)
    
    
    sent_list = text.sentences
    
    #focus_locs= focus_locs.strip()
    for sent in sent_list:
        
        sent = sent.string
        sentNum +=1
        
        if (sentNum > 7):
            break
        
        for loc in loc_stan:
            
            if(loc in countries):
                continue
            
            if  (loc in sent.lower()):
                Sent.append(sent)
                Loc.append(loc)
                                               
                break
    
    return Sent, Loc

    
if __name__ == '__main__':
    
    text = sys.argv[1] #path to text file (each line has is a news story)
    NER = sys.argv[2]   # specify the NER tool (Stanford or Mitie)
    lang = sys.argv[3]
    
#    text = '''105 words 4 July 2014 03:44 All Africa AFNWS English Mogadishu, Jul 04, 2014 (Tunis Afrique Presse/All Africa Global Media via COMTEX) -- A member of the Somali Federal Parliament has been shot dead by unknown gunmen on Thursday morning in Mogadishu, officials said. Ahmed Mohamud Hayd was killed in a drive-by shooting after he left his hotel in a heavily policed area, witnesses said. His bodyguard was also killed and a parliamentary secretary wounded in the shooting. Al-Shabab spokesman Abdulaziz Abu Musab said the group had carried out the "targeted assassination". At least five members of the Parliament have been shot since the beginning of the year.  '''
#    lang = 'en'
#    NER = 'Mitie'
    
    Sent, Loc = main( text, NER, lang)
