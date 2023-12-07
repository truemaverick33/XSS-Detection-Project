# -*- coding: utf-8 -*-
"""XSS-Detector.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1e7otLC81UN06ANtmwpYYKA6hIb0dxcBL

## Import Modules
"""

import requests
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

"""## Upload Dataset

Dataset taken from: https://www.kaggle.com/datasets/syedsaqlainhussain/cross-site-scripting-xss-dataset-for-deep-learning
"""

data = pd.read_csv('XSS_dataset.csv')

"""## Separate Dataset:

* X = Predictor Variable (Here: "Sentence" the script snippet of HTML or Javascript)
* Y = Prediction Variable (Here: "Label" the classification label that if the script is XSS or Not)
"""

X = data['Sentence']
y = data['Label']

"""## Tokenize and Padding:

Tokenize the dataset to change text data into numerical data and pad them with 0s to make all of them of same length.
"""

tokenizer = Tokenizer()
tokenizer.fit_on_texts(X)
X = tokenizer.texts_to_sequences(X)
max_sequence_length = max(len(seq) for seq in X)
X = pad_sequences(X, maxlen=max_sequence_length)
print(X)

"""## Encode the Label:"""

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

"""## Split dataset into train and test
75 % Training
25 % Testing
"""

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.25)

"""## Create Deep Learning Model:
Using Sequential, LSTM, Dense and activation:"RelU"
"""

model = Sequential()
model.add(Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=128, input_length=max_sequence_length))
model.add(LSTM(100))
model.add(Dense(1, activation='relu'))

"""## Compile the Model:"""

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

"""## Fit Dataset into the Model:"""

model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))

"""## Load The Model (Optional)
if you saved an high accuracy fitted model you can load that instead of re-training the model again and again.
"""

model = load_model('model61223.h5')

"""## Take In Live Data And Pre-Process:

takes URL from user and gets source code of the page associated with the url to scan line by line for XSS scripts
"""

def getSourceCode(url):
  r = requests.get(url)
  return r.text
sc = getSourceCode(str(input("Enter a URL to scan: ")))
sclines = sc.split("\n")
cleaned = [item for item in sclines if item and item.strip()]
#cleaned.append("<script>while(1){alert('attack')}</script>") //Demo XSS-appended
#cleaned.append("<tt onmouseover='alert(1)>test</tt>") //Demo XSS-appended

"""## Predict Outputs:"""

tokenized = tokenizer.texts_to_sequences(cleaned)
padded = pad_sequences(tokenized, maxlen=max_sequence_length)
predictions = model.predict(padded)
binary_predictions = (predictions > 2.05).astype(int)
decoded_predictions = label_encoder.inverse_transform(binary_predictions.flatten())
highly_likely = []
for sentence, prediction, decoded in zip(cleaned,predictions,decoded_predictions,):
  if(decoded == 1):
    highly_likely.append({"Script":sentence.strip(),"Score":prediction,"Prediction":decoded})
highly_likely = sorted(highly_likely, key=lambda x: x["Score"], reverse=True)
for i in highly_likely:
    print(f"Script: {i['Script']}\nScore: {i['Score']}\nPrediction: {i['Prediction']}")

"""## Save Trained Model(Optional):

save the trained model if you want to re-use it instead of re-training several times.
"""

model.save('model61223.h5')