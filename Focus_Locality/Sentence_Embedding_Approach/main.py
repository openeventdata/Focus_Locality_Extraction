#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 12:12:20 2018

@author: maryam
"""
import SIFpreprocessing
import SentenceExtraction
import Classification_SVM
import PostEvaluationProfile


pathGT = '/data/maryam/Documents/Geolocation11272017/Spanish_PDF/PDF_JSON/MunicipalitFiltered.txt'
pathR = '/data/maryam/Documents/Geolocation11272017/Spanish_PDF/PDF_JSON/StoryFiltered.txt'

lang = 'es'
NER = 'Mitie' #Stanford or Mitie 

SentenceListTrain, LblListTrain, DocTrain, LocTrain = SentenceExtraction.main(pathGT, pathR, NER, lang)
embTrain, lblTrian = SIFpreprocessing.main(0.01, lang, SentenceListTrain, LblListTrain)


SentenceListTest, LblListTest, DocTest, LocTest = SentenceExtraction.main(pathGT, pathR, NER, lang)
embTest, lblTest = SIFpreprocessing.main(0.01, lang, SentenceListTest, LblListTest)


model = Classification_SVM.trainModel(embTrain, lblTrian)
predictedResult = Classification_SVM.evaluateModel(embTest, lblTest, model)

print predictedResult


accuracy = PostEvaluationProfile.integrateSentences(predictedResult, DocTest, LocTest)
print accuracy