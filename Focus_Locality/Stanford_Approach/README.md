# Focus_Locality_Extraction

This code is developed to extract focus locality from the news stories. 

In order to run this program, you need to instal "nltk" at first. 
```
sudo pip install -U nltk
```
As an example to run the program, you can input the following command: 

```
python FocusLocality.py "92 words 20 De cember 2013 00:25 Agence France Presse AFPR English Four people including the mayor of a southern Philippine town were killed Friday in an ambush at Manila airport, its general manager said. "The mayor and his family and some security escorts were attacked," Manila airport general manager Angel Honrado told reporters, adding one of the dead was the mayor of Labangan town. Ukol Talumpa, a member of the political opposition, won a hotly contested electoral contest for mayor of Labangan in last May's elections."
```

# How do we develop this approach?

This approach is based on Conditional random field (CRF) model. We retrained CRF model in Stanford NER with our dataset and its new entity type. 
