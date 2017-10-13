# Geoparsers comparision 

Here we compare different geoparsers on two datasets: WikToR(SciPaper).xml and LGL.xml dataset.

These geoparsers include: Yahoo, Clavin, Cliff, TopoCluster, GeoTxt, Edinburgh, and Mordecai. 

## Summary

We use some data and code from "What's missing in geographical parsing?" in the journal [Language Resources and Evaluation](http://link.springer.com/journal/10579) (link coming soon after publication). 

We also add two other geoparsers to the previous work. In near future, we will use these geoparser on Spanish dataset and evaluate their performance on them. 


## How to replicate

You should have some basic Python libraries like Numpy, NLTK, Matplotlib (if you want graphics), ... to start with.
- methods.py is the main python script for running the experiments (requires the yahoo.py script)
- Please install [GeoPy](https://pypi.python.org/pypi/geopy/1.11.0) to calculate the distances between coordinates.
- Also install [Wikipedia](https://pypi.python.org/pypi/wikipedia/) for Python, nice API wrapper :+1:


## How to start

All data are provided in "data" folder. You need just run "method.py" in python to get the evaluations. 

In order to rerun geoparsers, you neead just to run its code from the main folder or in "method.py" 