#Sentence Embedding 

The idea of the code is proposed in the paper "A Simple but Tough-to-Beat Baseline for Sentence Embeddings".

The customized code is written in python and requires numpy, nltk, sklearn, and gensim. 

To run the code and extract the feature vector for each sentence, you need training and testing files and their labels' file.
Each training or testing file contains a sentence per line and its relevant lable in the seperate label file. 

```
python SIF_Processing.py <alpha> <path/to/word2vec_model> <trainFile> <testFile> <trainLabelFile> <testLabelFile>
```

# References


```
@article{arora2016asimple, 
	author = {Sanjeev Arora and Yingyu Liang and Tengyu Ma}, 
	title = {A Simple but Tough-to-Beat Baseline for Sentence Embeddings}, 
	year = {2016}
}
```
