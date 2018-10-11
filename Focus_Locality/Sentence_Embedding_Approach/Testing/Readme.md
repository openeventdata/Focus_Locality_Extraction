# Profile 

You can run the following code to use Profile for the real news articles (which their primary focus location are not provided). 


```Python 
from fastText_multilingual.fasttext import FastVector
import pickle
import Profile


# define the news language 
lang = en

if lang =='es': 
    word2vec_model = '/UserPath/wiki.es.vec'
    word2vec_Dictionary = FastVector(vector_file= word2vec_model)
    word2vec_Dictionary.apply_transform('./fastText_multilingual/alignment_matrices/es.txt')
elif lang =='en':
    word2vec_model = '/UserPath/wiki.en.vec'
    word2vec_Dictionary = FastVector(vector_file= word2vec_model)
    word2vec_Dictionary.apply_transform('./fastText_multilingual/alignment_matrices/en.txt')
elif lang == 'ar':
    word2vec_model = '/UserPath/wiki.ar.vec'
    word2vec_Dictionary = FastVector(vector_file= word2vec_model)
    word2vec_Dictionary.apply_transform('./fastText_multilingual/alignment_matrices/ar.txt')

# load model 
model = "model_"+lang+".sav"
loaded_model = pickle.load(open(model, 'rb'))

print( Profile.main(lang, TextTest, word2vec_Dictionary, loaded_model) ) 

```


## Dependencies: 

- fastText_mulilingual: https://github.com/Babylonpartners/fastText_multilingual
- fastText pretrained-vectors: https://github.com/facebookresearch/fastText/blob/master/pretrained-vectors.md
- Mitie Named Entity Extractor: https://github.com/mit-nlp/MITIE
