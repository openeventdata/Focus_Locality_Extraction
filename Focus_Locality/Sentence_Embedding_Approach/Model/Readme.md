## load the model from disk

To work directly with the trained model, you can use the following code to load it by using sklearn library: 

```
from sklearn.externals import joblib

filename = "finalized_model.sav"
loaded_model = joblib.load(filename)
```
