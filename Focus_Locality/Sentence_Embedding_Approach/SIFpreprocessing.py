#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 11:34:46 2017

@author: maryam
"""
import gensim, nltk
import numpy as np
import sys
from gensim.models.keyedvectors import KeyedVectors
from nltk.corpus import stopwords
from sklearn.decomposition import TruncatedSVD
from fastText_multilingual.fasttext import FastVector

reload(sys)
sys.setdefaultencoding("utf-8")

stop = set(stopwords.words('english'))

to_filter = [',', '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', "'s",'``', '"', "'", '.' , "''"]


def parse_files(trainlist):
    
    corpus= ''
    for trainl in trainlist:
        text = trainl.lower().replace('\n', ' ')    
        text = unicode(text, errors='ignore')
        corpus += text.replace('\n', ' ') +'\n'

#    with open (testFile, 'r') as f: 
#        text = f.read().lower().replace('\n', ' ')
#        text = unicode(text, errors='ignore')
#        corpus += text.replace('\n', ' ') +'\n'
    
    vocabDic = nltk.FreqDist(w.lower() for w in nltk.tokenize.word_tokenize(corpus))
   # vocabDic = word_features.keys()
    
    vocabDic1 = [(w,v) for (w,v) in vocabDic.items() if (w not in to_filter and not w.isdigit())]
#    vocabulary = [w for w in vocabDic if (w not in to_filter and not w.isdigit())]
    
    vocabulary = [w for (w,v) in vocabDic1] 
    vocabFreq = [v for (w,v) in vocabDic1] 

#    f= open ('vocab.txt','w')
#    f.write("\n".join(map(lambda x: str(x), vocabulary)) )
    
    return corpus, vocabulary, vocabFreq



def index_vector(trainTextList, vocabulary, vocabFreq, corpus, alpha):
    
#    alpha= 0.001
    summ = sum(vocabFreq)
    
    lines1 = [line.decode('utf-8').strip().replace('_',' ') for line in trainTextList]
#    posLbl = [1]* len(lines1)
#    
#    with open('./Testingnegsentences.neg', 'r') as f: 
#        lines2 = [line.decode('utf-8').strip() for line in f.readlines()]
#    negLbl = [0]* len(lines2)
    
#    posLbl.extend(negLbl)
#    lines1.extend(lines2)

#    f= open ('testLabel1.txt','w')
#    f.write("\n".join(map(lambda x: str(x), posLbl)) + "\n")
    

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
                #w[i] = 10.0 * vocabFreq[x[i]] / summ
            except Exception as excep:
                print (excep)
                continue
        X_index.append(x)
        weight.append(w)
        
    return X_index , weight


def word2vec(word2vec_model, vocabulary, lang):
    
#    f= open ('word2vec.txt','w')
    
    word2vec2= []
    
    fr_model = FastVector(vector_file= word2vec_model)
    
    if lang == 'es':
        fr_model.apply_transform('./fastText_multilingual/alignment_matrices/es.txt')
    else: 
        fr_model.apply_transform('./fastText_multilingual/alignment_matrices/en.txt')
    
    for word in vocabulary:
        try:
            word2vec = fr_model[word]
        except Exception:
            word2vec = [0.0000001] * 300
#        f.write(",".join(map(lambda x: str(x), word2vec)) + "\n")
        
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

def makingfile(trainTextList, trainLblList, vocabulary, vocabFreq, corpus, alpha, We):
    
    x , w= index_vector(trainTextList, vocabulary, vocabFreq, corpus, alpha)
    emb = get_weighted_average(We, x, w)
    embList = emb.tolist()
           
    newemb= []
    newlbl=[]
    x, y = emb.shape
    for i in range (x):
        if (not np.isnan(emb[i,0]) and not np.isinf(emb[i,0]) ):
            newlbl.append(trainLblList[i])
            newemb.append(embList[i])
    
    
#    f= open (name+'Label.txt','w')
#    f.write("\n".join(map(lambda x: str(int(x)), newlbl)) + "\n")
#    f.flush()
    
    emb = np.asarray(newemb)
    emb = remove_pc(emb, npc=1)
    
#    np.savetxt(name+'emb.txt', emb, delimiter=",")
    
    
    return emb, newlbl


def main(alpha, lang, trainTextList, trainLblList):
    
#    trainFile = '/data/maryam/Documents/Geolocation11272017/Spanish_protest/Spanish_feature_viveca/Mitie7/ProtestSpanishSentences7.txt'
#    testFile = 'PDFSpanishSentencesTest.txt'
#    trainLblFile = '/data/maryam/Documents/Geolocation11272017/Spanish_protest/Spanish_feature_viveca/Mitie7/ProtestSpanishlabels7.txt'
#    testLblFile = 'PDFSpanishlabelsTest.txt'
#    alpha=0.01
    #word2vec_model = '/home/maryam/Data/Documents/Geolocation26092016/Word2Vec/GoogleNews-vectors-negative300.bin.gz'
    
    if lang =='es': 
        word2vec_model = '/usr/src/data/wiki.es.vec'
    else: 
        word2vec_model = '/usr/src/data/wiki.en.vec'
    
    
    corpus , vocabulary, vocabFreq = parse_files(trainTextList)
    We= word2vec(word2vec_model, vocabulary, lang)
    
    emb, newlbl = makingfile(trainTextList, trainLblList, vocabulary, vocabFreq, corpus, alpha, We)
    #makingfile(testFile, testLblFile, vocabulary, vocabFreq, corpus, alpha, name='TestPDFSpanish7')
    
    return emb, newlbl
    
if __name__ == '__main__':
    
    if len(sys.argv) <5:
        sys.exit()
    else:  
        alpha = float(sys.argv[1])
        lang= sys.argv[2]
        trainFile= sys.argv[3]
        trainLblFile= sys.argv[4]
        
    emb, newlbl= main(alpha, lang, trainFile, trainLblFile)
