#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: maryam
"""
import SIFpreprocessing_test
import SentenceExtraction_test
from itertools import izip


def main(lang, TextTest, word2vec_Dictionary, loaded_model):

#    lang = 'en'
#    TextTest = sys.argv[1]
#    TextTest = '''105 words 4 July 2014 03:44 All Africa AFNWS English Mogadishu, Jul 04, 2014 (Tunis Afrique Presse/All Africa Global Media via COMTEX) -- A member of the Somali Federal Parliament has been shot dead by unknown gunmen on Thursday morning in Mogadishu, officials said. Ahmed Mohamud Hayd was killed in a drive-by shooting after he left his hotel in a heavily policed area, witnesses said. His bodyguard was also killed and a parliamentary secretary wounded in the shooting. Al-Shabab spokesman Abdulaziz Abu Musab said the group had carried out the "targeted assassination". At least five members of the Parliament have been shot since the beginning of the year.  '''

    NER = 'Mitie' #Stanford or Mitie or other
        
    # test
    SentenceListTest, LocTest = SentenceExtraction_test.main(TextTest, NER, lang)
    embTest = SIFpreprocessing_test.main(0.01, lang, TextTest, word2vec_Dictionary)
    
    predictedResult = loaded_model.predict(embTest)
    
    locDic = dict()
    resDic = dict()
    for res, loc in izip(predictedResult, LocTest):
        loc = loc.lower().strip()
        if res==1:
            if loc not in resDic:
                resDic[loc] = 0
            resDic[loc] +=1
        
        if loc not in locDic:
            locDic[loc] = 0
        locDic[loc] +=1
    
    if resDic: 
        sorted_loc = sorted(resDic, key=resDic.__getitem__, reverse=True)
    else: 
        sorted_loc = sorted(locDic, key=locDic.__getitem__, reverse=True)
    
    return sorted_loc[0]
