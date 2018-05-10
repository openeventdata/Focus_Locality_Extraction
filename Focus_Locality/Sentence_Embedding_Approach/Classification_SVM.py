# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 11:19:39 2016

@author: maryam
"""

from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn import svm
import random


def trainModel(trainDataset, trainLabel):
  
    #trainDataset = trainDataset[0:200,:]
    #trainLabel = trainLabel[0:200]
    
    #model = svm.SVC(gamma=0.01, C=100., kernel='poly')
    model = svm.SVC(gamma=0.01, C=100.)
    model.fit(trainDataset, trainLabel)
      
    #model = RandomForestClassifier(n_estimators=100, random_state=12)
    #model.fit(trainDataset, trainLabel)

    return model

def evaluateModel(testDataset, testLabel, model):

    result= model.predict(testDataset)
    np.savetxt('/data/maryam/Documents/Geolocation11272017/Spanish_protest/PredictedLoc.txt', result, delimiter=',', fmt='%i')
    #np.save('./Word2vec/PredictedLoc', result)
    
    summ=0
    TP=0
    FP=0
    FN=0
    TN= 0
    
    for i in range(0, len(result)):
        if (result[i]== testLabel[i]):
            summ += 1
            if (result[i]==1):
                TP +=1
            else: 
                TN +=1
        elif (result[i]== 1):
            FP +=1
        elif (result[i]==0):
            FN +=1
    
    print ('TP: '+ str (TP))
    print ('FP: '+ str (FP))
    print ('FN: '+ str (FN))
    print ('TN: '+ str (TN))
    
    print ('TPR: '+ str (float(TP*100) / float (TP+FN)))
    print ('FPR: '+ str (float(FP*100) / float (FP+TN)))
    print ('FNR: '+ str (float(FN*100) / float (TP+FN)))
    
    accuracy = accuracy_score(testLabel, result)
    print ('Accuracy: '+ str (accuracy*100) )
    precision = precision_score(testLabel, result, average='binary')
    recall= recall_score(testLabel, result, average='binary')
    print ('Precision: '+ str (precision)+ '\nRecall: '+ str (recall) )
    print ('F1: '+ str ( 100*(2*precision* recall)/(precision+recall)) )
    
    
    return result

