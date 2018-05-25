#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 12:12:20 2018

@author: maryam
"""
import SIFpreprocessing
import SentenceExtraction
import Classification_SVM
#import PostEvaluationProfile


pathGTtrain = 'example1/PDF_JSON/MunicipalitFiltered.txt' #locality names in each row
pathRtrain = 'example1/StoryFiltered.txt' #News story in each row

pathGTtest = 'example2/PDF_JSON/MunicipalitFiltered.txt' #locality names in each row
pathRtest = 'example2/StoryFiltered.txt' #News story in each row

'''
you should set the path of NER in "SentenceExtraction.py" file
and set the path of word2vec or fastVec in "SIFpreprocessing.py" file
'''

lang = 'es'
NER = 'Mitie' #Stanford or Mitie  

SentenceListTrain, LblListTrain, DocTrain, LocTrain = SentenceExtraction.main(pathGTtrain, pathRtrain, NER, lang)
embTrain, lblTrian = SIFpreprocessing.main(0.01, lang, SentenceListTrain, LblListTrain)


SentenceListTest, LblListTest, DocTest, LocTest = SentenceExtraction.main(pathGTtest, pathRtest, NER, lang)
embTest, lblTest = SIFpreprocessing.main(0.01, lang, SentenceListTest, LblListTest)


model = Classification_SVM.trainModel(embTrain, lblTrian)
predictedResult = Classification_SVM.evaluateModel(embTest, lblTest, model)

print predictedResult


accuracy = PostEvaluationProfile.integrateSentences(predictedResult, DocTest, LocTest, pathGTtest)
print accuracy
