# -*- coding: utf-8 -*-
"""Untitled14.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ewvykNPD_YVZ3Kyr3gM9bVWc61BfWt3v

Importing necessary **libraries**
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats

df = pd.read_csv('/content/creditcard.csv')

df.shape

df.head(5)

df.info()

pd.set_option('precision',2)
df.loc[:,['Time','Amount']].describe()

"""Around 67 dollars is the mean of all credit card transactions.

The biggest transaction had a amount of around 29031 dollars.

Visualization of time
"""

plt.figure(figsize=(8,6))
plt.title('Distribution of Time Feature')
sns.distplot(df.Time)

"""Visualization of amount"""

plt.figure(figsize=(8,6))
plt.title('Distribution of Amount')
sns.distplot(df.Amount)

"""Fraud vs. Normal transactions"""

counts=df.Class.value_counts()
normal=counts[0]
fraud=counts[1]
percent_normal = (normal/(normal+fraud))*100
percent_fraud = (fraud/(normal+fraud))*100
print(normal,' ',fraud) 
print('%.2f' % percent_normal)
print('%.2f' % percent_fraud)

"""There were 17836 non-fraud transactions (99.55%) and 81 fraud transactions (0.45%)."""

plt.figure(figsize=(8,6))
sns.barplot(x=counts.index, y=counts)
plt.title('Count of Fraud vs. Non-Fraud Transactions')
plt.ylabel('Count')
plt.xlabel('Class (0:Non-Fraud, 1:Fraud)')

"""Correlation plot Heatmap

"""

corr = df.corr()
plt.figure(figsize=(12,10))
heat = sns.heatmap(data=corr)
plt.title('Heatmap of Correlation')

"""Checking for Skewness"""

df.skew()

"""Scaling Amount and Time"""

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler2 = StandardScaler()
#scaling time
scaled_time = scaler.fit_transform(df[['Time']])
flat_list1 = [item for sublist in scaled_time.tolist() for item in sublist]
scaled_time = pd.Series(flat_list1)

#scaling the amount
scaled_amount = scaler2.fit_transform(df[['Amount']])
flat_list2 = [item for sublist in scaled_amount.tolist() for item in sublist]
scaled_amount = pd.Series(flat_list2)

#concatenating newly created columns original df
df = pd.concat([df, scaled_amount.rename('scaled_amount'), scaled_time.rename('scaled_time')], axis=1)
df.head(5)

#dropping old amount and time columns
df.drop(['Amount', 'Time'], axis=1, inplace=True)

"""Splitting Data into Train and Test"""

#manual train test split using numpy's random.rand
mask = np.random.rand(len(df)) < 0.9
train = df[mask]
test = df[~mask]
print('Train Shape: {}\nTest Shape: {}'.format(train.shape, test.shape))

train.reset_index(drop=True, inplace=True)
test.reset_index(drop=True, inplace=True)

"""Creating a subsample data set with balanced class distributions"""

#how many random samples from normal transactions do we need?
no_of_frauds = train.Class.value_counts()[1]
print('There are {} fraud transactions in the train set'.format(no_of_frauds))

#randomly selecting 77 random non-fraud transactions
non_fraud = train[train['Class'] == 0]
fraud = train[train['Class'] == 1]

selected = non_fraud.sample(no_of_frauds)
selected.head(5)

#concatenating both into a subsample data set with equal class distribution
selected.reset_index(drop=True, inplace=True)
fraud.reset_index(drop=True, inplace=True)

subsample = pd.concat([selected, fraud])
len(subsample)

#shuffling our data set
subsample = subsample.sample(frac=1).reset_index(drop=True)
subsample.head(5)

new_counts = subsample.Class.value_counts()
plt.figure(figsize=(8,6))
sns.barplot(x=new_counts.index, y=new_counts)
plt.title('Count of Fraudulent vs. Non-Fraudulent Transactions In Subsample')
plt.ylabel('Count')
plt.xlabel('Class (0:Non-Fraudulent, 1:Fraudulent)')

#taking a look at correlations again
corr = subsample.corr()
corr = corr[['Class']]
corr

#negative correlations smaller than -0.5
corr[corr.Class < -0.5]

#positive correlations greater than 0.5
corr[corr.Class > 0.5]

#visualizing the features high negative correlation
f, axes = plt.subplots(nrows=2, ncols=4, figsize=(26,16))

f.suptitle('Features With High Negative Correlation', size=35)
sns.boxplot(x="Class", y="V3", data=subsample, ax=axes[0,0])
sns.boxplot(x="Class", y="V9", data=subsample, ax=axes[0,1])
sns.boxplot(x="Class", y="V10", data=subsample, ax=axes[0,2])
sns.boxplot(x="Class", y="V12", data=subsample, ax=axes[0,3])
sns.boxplot(x="Class", y="V14", data=subsample, ax=axes[1,0])
sns.boxplot(x="Class", y="V16", data=subsample, ax=axes[1,1])
sns.boxplot(x="Class", y="V17", data=subsample, ax=axes[1,2])
f.delaxes(axes[1,3])

#visualizing the features high positive correlation
f, axes = plt.subplots(nrows=1, ncols=2, figsize=(18,9))

f.suptitle('Features With High Positive Correlation', size=20)
sns.boxplot(x="Class", y="V4", data=subsample, ax=axes[0])
sns.boxplot(x="Class", y="V11", data=subsample, ax=axes[1])

"""Outlier Removal"""

#Only removing extreme outliers
Q1 = subsample.quantile(0.25)
Q3 = subsample.quantile(0.75)
IQR = Q3 - Q1

df2 = subsample[~((subsample < (Q1 - 2.5 * IQR)) |(subsample > (Q3 + 2.5 * IQR))).any(axis=1)]

len_after = len(df2)
len_before = len(subsample)
len_difference = len(subsample) - len(df2)
print('We reduced our data size from {} transactions by {} transactions to {} transactions.'.format(len_before, len_difference, len_after))

"""Dimensionality Reduction"""

from sklearn.manifold import TSNE

X = df2.drop('Class', axis=1)
y = df2['Class']

X_reduced_tsne = TSNE(n_components=2, random_state=42).fit_transform(X.values)

"""Classification Algorithms"""

# train test split
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = X_train.values
X_validation = X_test.values
y_train = y_train.values
y_validation = y_test.values

print('X_shapes:\n', 'X_train:', 'X_validation:\n', X_train.shape, X_validation.shape, '\n')
print('Y_shapes:\n', 'Y_train:', 'Y_validation:\n', y_train.shape, y_validation.shape)

from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

##Spot-Checking Algorithms

models = []

models.append(('LR', LogisticRegression()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('SVM', SVC()))
models.append(('RF', RandomForestClassifier()))

#testing models

results = []
names = []

for name, model in models:
    kfold = KFold(n_splits=10, random_state=42,shuffle=True)
    cv_results = cross_val_score(model, X_train, y_train, cv=kfold, scoring='roc_auc')
    results.append(cv_results)
    names.append(name)
    msg = '%s: %f (%f)' % (name, cv_results.mean(), cv_results.std())
    print(msg)

from sklearn import tree
import matplotlib.pyplot as plt
#visualizing RF
model = RandomForestClassifier(n_estimators=10)

# Train
model.fit(X_train, y_train)
# Extract single tree
estimator = model.estimators_[5]
plt.figure(figsize=(15,10))
tree.plot_tree(estimator,filled=True)