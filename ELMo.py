#!/usr/bin/env python
# coding: utf-8

# The code used here was taken and adapted from https://www.analyticsvidhya.com/blog/2019/03/learn-to-use-elmo-to-extract-features-from-text/


import pandas as pd
import numpy as np
import spacy
from tqdm import tqdm
import re
import time
import pickle
import tensorflow_hub as hub
import tensorflow.compat.v1 as tf
from sklearn.model_selection import train_test_split
tf.compat.v1.disable_eager_execution()
tf.disable_v2_behavior()

elmo = hub.Module("https://tfhub.dev/google/elmo/2", trainable=True)
pd.set_option('display.max_colwidth', 200)





# read data
reviews = pd.read_csv("sentances_classified_archive.csv")





def elmo_vectors(x):
  embeddings = elmo(x.tolist(), signature="default", as_dict=True)["elmo"]

  with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    sess.run(tf.tables_initializer())
    # return average of ELMo features
    return sess.run(tf.reduce_mean(embeddings,1))





y=reviews.Category
x=reviews.drop('Category',axis=1)

x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2)
x_train.head()





train = pd.concat([y_train, x_train], axis = 1)
test = pd.concat([y_test, x_test], axis = 1)




punctuation = '!"#$%&()*+-/:;<=>?@[\\]^_`{|}~'

train['Review'] = train['Review'].apply(lambda x: ''.join(ch for ch in x if ch not in set(punctuation)))
test['Review'] = test['Review'].apply(lambda x: ''.join(ch for ch in x if ch not in set(punctuation)))

# convert text to lowercase
train['Review'] = train['Review'].str.lower()
test['Review'] = test['Review'].str.lower()

# remove numbers
train['Review'] = train['Review'].str.replace("[0-9]", " ")
test['Review'] = test['Review'].str.replace("[0-9]", " ")

# remove whitespaces
train['Review'] = train['Review'].apply(lambda x:' '.join(x.split()))
test['Review'] = test['Review'].apply(lambda x: ' '.join(x.split()))

# remove stopwords
import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
stop = stopwords.words('english')
train['Review'] = train['Review'].apply(lambda x: " ".join(x for x in x.split() if x not in stop))
train['Review'].head()
test['Review'] = test['Review'].apply(lambda x: " ".join(x for x in x.split() if x not in stop))
test['Review'].head()

# encode the response variable
train["Category"] = LabelEncoder().fit_transform(train["Category"])
test["Category"] = LabelEncoder().fit_transform(test["Category"])






# import spaCy's language model
nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])

# function to lemmatize text
def lemmatization(texts):
    output = []
    for i in texts:
        s = [token.lemma_ for token in nlp(i)]
        output.append(' '.join(s))
    return output





train['Review'] = lemmatization(train['Review'])
test['Review'] = lemmatization(test['Review'])





train.head()





train.shape, test.shape





list_train = [train[i:i+100] for i in range(0,train.shape[0],100)]
list_test = [test[i:i+100] for i in range(0,test.shape[0],100)]





elmo_train = [elmo_vectors(x['Review']) for x in list_train]
elmo_test = [elmo_vectors(x['Review']) for x in list_test]





elmo_train_new = np.concatenate(elmo_train, axis = 0)
elmo_test_new = np.concatenate(elmo_test, axis = 0)





xtrain, xvalid, ytrain, yvalid = train_test_split(elmo_train_new, 
                                                  train['Category'],  
                                                  random_state=42, 
                                                  test_size=0.2)





train.head()






from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

lreg = LogisticRegression(max_iter=1000)
lreg.fit(xtrain, ytrain)




preds_valid = lreg.predict(xvalid)




f1_score(yvalid, preds_valid, average = 'micro')




preds_test = lreg.predict(elmo_test_new)





preds_test




from sklearn import metrics

print(metrics.confusion_matrix(y_test, preds_test))

print(metrics.classification_report(y_test, preds_test))

from sklearn.metrics import accuracy_score

print("Accuracy of ELMO is:",accuracy_score(y_test,preds_test))






