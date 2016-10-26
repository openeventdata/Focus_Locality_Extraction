# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 17:12:34 2016

@author: maryam
"""

import sys, os
from nltk.tag import StanfordNERTagger

reload(sys)
sys.setdefaultencoding("utf-8")


def stanfordNER(text, st):    
    loc=[]
    
    tagg=st.tag(text.split())
    length= len(tagg)
    k=0
    i=0
    if (length == 0):
        print('error')
        return []
    while (i<length):
        loc_part=''
        if (tagg[i][1]== 'locality'):
            for j in range(i, length):
                if (tagg[j][1]== 'locality'):
                    loc_part += " "+ tagg[j][0].strip().replace('.','')
                    k=j+1
                else:
                    break
            i=k
            if (loc_part !=''):
                if (loc_part.encode('utf8') not in loc):
                    loc.append(loc_part.strip().encode('utf8'))
        else:
            i= i+1
    return loc

if __name__ == '__main__':
    
    inputText = sys.argv[1]
    
    # Stanford setup
    os.environ['CLASSPATH'] = './model/stanford-ner.jar'  
    st = StanfordNERTagger('./model/cus-stan-model-MitStan.ser.gz')
        
    Stanford_loc = stanfordNER(inputText, st)
    print Stanford_loc