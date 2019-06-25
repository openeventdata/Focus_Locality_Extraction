# Profile 

You can run the following code to use Profile for the real news articles (in which the primary focus locations are not provided). 


```Python 
from fastText_multilingual.fasttext import FastVector
import pickle
import Profile


# define the news language 
lang = 'en'
NER = 'Mitie' #Stanford or Mitie or other

if lang =='es': 
    word2vec_model = '/UserPath/wiki.es.vec'
    word2vec_Dictionary = FastVector(vector_file= word2vec_model)
    word2vec_Dictionary.apply_transform('./fastText_multilingual/alignment_matrices/es.txt')
elif lang =='en':
    word2vec_model = '/home/ahalt/wiki.en.vec'
    word2vec_Dictionary = FastVector(vector_file= word2vec_model)
    word2vec_Dictionary.apply_transform('./fastText_multilingual/alignment_matrices/en.txt')
elif lang == 'ar':
    word2vec_model = '/UserPath/wiki.ar.vec'
    word2vec_Dictionary = FastVector(vector_file= word2vec_model)
    word2vec_Dictionary.apply_transform('./fastText_multilingual/alignment_matrices/ar.txt')

# load model 
model = "./model/model_"+lang+".sav"
loaded_model = pickle.load(open(model, 'rb'))

TextTest = ['A sentence about nowhere', 'After a week of calm in Boston, violence broke out in Amherst and Williamstown.']
print( Profile.main(lang, NER, TextTest, word2vec_Dictionary, loaded_model) ) 

```


## Other information

- You need to change NER path in ```SentenceExtraction_test.py``` if you want to work with Mitie or Stanford. 
- You must use Python 2! The pickled model can only be loaded from Python 2. Loading with Python 3 gives a Unicode error.
- You'll need to uncompress the English model in `models/` (currently only English is available)
- Make sure to upgrade `sklearn` to 0.20
- Make sure to download the nltk models, too:  
    >>> import nltk
    >>> nltk.download('punkt')

## Dependencies: 

- fastText_mulilingual: https://github.com/Babylonpartners/fastText_multilingual
- fastText pretrained-vectors: https://github.com/facebookresearch/fastText/blob/master/pretrained-vectors.md
- Mitie Named Entity Extraction: https://github.com/mit-nlp/MITIE
- Polyglot Named Entity Extraction: https://polyglot.readthedocs.io/en/latest/NamedEntityRecognition.html 
  (It supports most of the languages such as Arabic) 
