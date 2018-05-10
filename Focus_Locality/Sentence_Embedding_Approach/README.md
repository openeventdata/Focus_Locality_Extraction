# Sentence Embedding 

The idea of the code is proposed in the paper "A Simple but Tough-to-Beat Baseline for Sentence Embeddings".

The customized code is written in python and requires numpy, nltk, sklearn, and gensim. 

To run the code and extract the feature vector for each sentence, you need training and testing files and their labels' file.
Each training or testing file contains a sentence per line and its relevant lable in the seperate label file. Then you can use any classifier to train a model based on training data, and evaluate it on test data. 

You need to set some parameters in main.py file and related files. 

```
python main.py
```


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
```
@inproceedings{imani2017focus,
  title={Focus location extraction from political news reports with bias correction},
  author={Imani, Maryam Bahojb and Chandra, Swarup and Ma, Samuel and Khan, Latifur and Thuraisingham, Bhavani},
  booktitle={Big Data (Big Data), 2017 IEEE International Conference on},
  pages={1956--1964},
  year={2017},
  organization={IEEE}
}
```
