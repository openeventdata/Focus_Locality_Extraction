#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 11:34:46 2017

@author: maryam
"""
import nltk
import numpy as np
import sys
from nltk.corpus import stopwords
from sklearn.decomposition import TruncatedSVD

#reload(sys)
#sys.setdefaultencoding("utf-8")

stop = set(stopwords.words('english'))

to_filter = [',', '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', "'s",'``', '"', "'", '.' , "''"]


def parse_files(trainlist):
    
    corpus= ''
    for trainl in trainlist:
        text = trainl.lower().replace('\n', ' ')    
        #text = unicode(text, errors='ignore')
        corpus += text.replace('\n', ' ') +'\n'
   
    vocabDic = nltk.FreqDist(w.lower() for w in nltk.tokenize.word_tokenize(corpus))
   
    vocabDic1 = [(w,v) for (w,v) in vocabDic.items() if (w not in to_filter and not w.isdigit())]
    vocabulary = [w for (w,v) in vocabDic1] 
    vocabFreq = [v for (w,v) in vocabDic1] 
    
    return corpus, vocabulary, vocabFreq



def index_vector(trainTextList, vocabulary, vocabFreq, corpus, alpha):
    
#    alpha= 0.001
    summ = sum(vocabFreq)
    
    lines1 = [line.strip().replace('_',' ') for line in trainTextList]

    X_index= []
    weight= []
    for line in lines1:
        if line == '':
            continue
        word1 = nltk.tokenize.word_tokenize(line)
        word = [w for w in word1 if (w not in to_filter and not w.isdigit())]
        x = [0] * len(word)
        w = [1] * len(word)
        for i in range(len(word)):
            try:
                x[i] = vocabulary.index(word[i].lower())
            except Exception as excep:
                print (excep)
                continue
            try:
                w[i] = alpha / (alpha + 1.0* vocabFreq[x[i]] / summ)  #main formula
            except Exception as excep:
                print (excep)
                continue
        X_index.append(x)
        weight.append(w)
        
    return X_index , weight


def word2vec(word2vec_Dictionary, vocabulary, lang):
    
   
    word2vec2= []
       
    for word in vocabulary:
        try:
            #print (word)
            word2vec = word2vec_Dictionary[word.encode('utf-8')]
            
        except Exception:
            #print 'error'
            word2vec = [0.0000001] * 300
        
        word2vec2.append(word2vec)
    
    return word2vec2

def get_weighted_average(We, x, w):
    """
    Compute the weighted average vectors
    :param We: We[i,:] is the vector for word i
    :param x: x[i, :] are the indices of the words in sentence i
    :param w: w[i, :] are the weights for the words in sentence i
    :return: emb[i, :] are the weighted average vector for sentence i
    """
    
    WeArr=np.asarray(We)
    
    n_samples = len(x)
    emb = np.zeros((n_samples, 300))
    for i in xrange(n_samples):
        emb[i,:] = np.asarray(w[i]).dot(WeArr[[np.asarray(x[i])],:]) / np.count_nonzero(np.asarray(w[i]))
    
    return emb

def compute_pc(X,npc):
    """
    Compute the principal components
    :param X: X[i,:] is a data point
    :param npc: number of principal components to remove
    :return: component_[i,:] is the i-th pc
    """
    svd = TruncatedSVD(n_components=npc, n_iter=7, random_state=0)
    svd.fit(X)
    return svd.components_

def remove_pc(X, npc):
    """
    Remove the projection on the principal components
    :param X: X[i,:] is a data point
    :param npc: number of principal components to remove
    :return: XX[i, :] is the data point after removing its projection
    """
    pc = compute_pc(X, npc)
    if npc==2:
        XX = X - X.dot(pc.transpose()) * pc
    else:
        XX = X - X.dot(pc.transpose()).dot(pc)
    return XX


def SIF_embedding(We, x, w, npc):
    """
    Compute the scores between pairs of sentences using weighted average + removing the projection on the first principal component
    :param We: We[i,:] is the vector for word i
    :param x: x[i, :] are the indices of the words in the i-th sentence
    :param w: w[i, :] are the weights for the words in the i-th sentence
    :param params.rmpc: if >0, remove the projections of the sentence embeddings to their first principal component
    :return: emb, emb[i, :] is the embedding for sentence i
    """
    emb = get_weighted_average(We, x, w)
    if  npc > 0:
        emb = remove_pc(emb, npc)
    return emb

def makingfile(trainTextList, vocabulary, vocabFreq, corpus, alpha, We):
    
    x , w= index_vector(trainTextList, vocabulary, vocabFreq, corpus, alpha)
    emb = get_weighted_average(We, x, w)
    embList = emb.tolist()
           
    newemb= []
    x, y = emb.shape
    for i in range (x):
        if (not np.isnan(emb[i,0]) and not np.isinf(emb[i,0]) ):
            newemb.append(embList[i])
       
    emb = np.asarray(newemb)
    emb = remove_pc(emb, npc=1)
    
    return emb


def main(alpha, lang, trainTextList, word2vec_Dictionary):
    

    corpus , vocabulary, vocabFreq = parse_files(trainTextList)
    We= word2vec(word2vec_Dictionary, vocabulary, lang)
    emb = makingfile(trainTextList, vocabulary, vocabFreq, corpus, alpha, We)
    
    return emb
    
if __name__ == '__main__':
    
    if len(sys.argv) <3:
        sys.exit()
    else:  
        alpha = float(sys.argv[1])
        lang= sys.argv[2]
        SentenceListTest= sys.argv[3]
    emb= main(alpha, lang, SentenceListTest)
    
#    SentenceListTest= ['''A member of the Somali Federal Parliament has been shot dead by unknown gunmen on Thursday morning in Mogadishu, officials said. Ahmed Mohamud Hayd was killed in a drive-by shooting after he left his hotel in a heavily policed area, witnesses said.''',''' His bodyguard was also killed and a parliamentary secretary wounded in the shooting.''']
#    emb = main(0.01, 'en', SentenceListTest)
#    print emb
