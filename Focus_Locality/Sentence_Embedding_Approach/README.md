# Sentence Embedding 

The idea of the code is proposed in the paper "A Simple but Tough-to-Beat Baseline for Sentence Embeddings".

The customized code is written in python and requires numpy, nltk, sklearn, and gensim. 

To run the code and extract the feature vector for each sentence, you need training and testing files and their labels' file.
Each training or testing file contains a sentence per line and its relevant lable in the seperate label file. 

```
python SIF_Processing.py <alpha> <path/to/word2vec_model> <trainFile> <testFile> <trainLabelFile> <testLabelFile>
```

Then you can use any classifier to train a model based on training data, and evaluate it on test data. 

To apply bias correction, you can use main in the Bias Correction folder. 

# References


```
@article{arora2016asimple, 
	author = {Sanjeev Arora and Yingyu Liang and Tengyu Ma}, 
	title = {A Simple but Tough-to-Beat Baseline for Sentence Embeddings}, 
	year = {2016}
}
```
```
@article{gretton2009covariate,
  title={Covariate shift by kernel mean matching},
  author={Gretton, Arthur and Smola, Alexander J and Huang, Jiayuan and Schmittfull, Marcel and Borgwardt, Karsten M and Sch{\"o}lkopf, Bernhard},
  year={2009},
  publisher={MIT press}
}
```
