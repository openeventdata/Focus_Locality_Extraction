#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 12:14:05 2018

@author: maryam
"""
import sys 
from itertools import izip



def evaluate(locDict, countDoc, locations):
    
    sortedLocDic = sorted(locDict.iterkeys())
    
    try:
        foc = locations[countDoc-1].lower().replace('\n','').strip()
    except: 
        return 0
    
    if len(sortedLocDic)!=0 and foc in sortedLocDic[0]:
        #print countDoc
        return 1
        
    else:
        
        print countDoc
        print "foc:" + foc 
        print sortedLocDic
        return 0
    

def integrateSentences(predictedResult, docList, locList):
    
    countDoc = 1
    locDict = dict()
    score = 0
    allLoc = list()
       
    for res, doc, loc in izip(predictedResult, docList, locList): 
        
        loc = loc.replace('\n','')
        doc = int(doc.replace('\n',''))
        if countDoc != doc: 
            
            if len(locDict) != 0:
                score += evaluate(locDict, countDoc, locList)
            else: 
                
                try:
                    
                    score += evaluate(allLoc, countDoc, locList)
                except:
                    pass
            
            allLoc = list()
            allLoc.append(loc)
            locDict = dict()
            countDoc = doc
            
                        
            if int(res) == 1:
                locDict[loc.lower()] = 1
            
        
        else:
            allLoc.append(loc)
            
            if int(res) == 0:
                continue
                
            if loc.lower() not in locDict:
                locDict[loc.lower()] = 0
            locDict[loc.lower()] += 1
                  
            return score / float(doc)

