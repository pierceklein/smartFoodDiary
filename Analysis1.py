#!/usr/bin/env python
# coding: utf-8

# In[108]:


## Authors: Henry Feild, Pierce Klein

import pandas as pd
from sklearn.linear_model import LogisticRegression

get_ipython().system(u'pip install dateparser')
get_ipython().system(u'pip install tabulate')

import dateparser
import random
from datetime import datetime, timedelta
from math import isnan
from sklearn import metrics # For evaluation
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from tabulate import tabulate

get_ipython().system(u'pip install xlrd==1.2.0')

## Take a time and the symptom data => a series of max symptom values + a binary "had symptoms"
def getSymptomsInInterval(startDateTime, endDateTime, symptomsDF):
  ## Find the rows.
  matches = symptomsDF[(symptomsDF['datetime'] >= startDateTime) & (symptomsDF['datetime'] <= endDateTime)]
  ## Find the max for each of the symptoms. Add these to a new series.
  symptoms = pd.Series({
      'Appetite': matches['Appetite'].min(),
      'Stomach Ache': matches['Stomach Ache'].max(),
      'Distension': matches['Distension'].max(),
      'Gas': matches['Gas'].max(),
      'Belching': matches['Belching'].max(),
      'Heartburn': matches['Heartburn'].max(),
      'has_symptoms': 0
  })

  if(isnan(symptoms[0])):
    symptoms = pd.Series({
      'Appetite': 3,
      'Stomach Ache': 0,
      'Distension': 0,
      'Gas': 0,
      'Belching': 0,
      'Heartburn': 0,
      'has_symptoms': 0
    })

  if(symptoms['Appetite'] <= 1):
      symptoms['has_symptoms'] = 1

  for symptom in symptoms.index:
    if(symptom != 'Appetite' and symptoms[symptom] >= 1):
      symptoms['has_symptoms'] = 1
      break

  return symptoms
  ## Add a column to the series called 'has_symptoms'
  ## Set to true if any of the max symptoms are above 0
  ## Return new series



## Takes an observation (a food item) and generates `hours`/`step` series, where
## each series corresponds to a time frame and consists of the symptoms 
## experienced in that timeframe. 
##
## Ex. 
## Input (as a Series):
##  observation = "breakfast, Gluten Free delicious soft white sandwi..., 	130, 	21g, ..."
##  nextObservation = the following observation; used to determine night time
##  symptoms = (symptoms data frame)
##  hours = 6
##  step = 1
##
## Output:
##  observation \union {hour1_Appetite: ..., hour2_Stomach Ache: ..., ..., hour2_Appetite: ..., ...}
##
def generateDVs(observations, observation, symptoms, timeframes, observations_ignored, hours, step=1) :


  # Grab the next observation if one exists.
  nextObservation = None
  if observation[observation.index[0]]+1 < len(observations):
    nextObservation = observations.iloc[observation[observation.index[0]]+1]

  # Check if this observation and the next are on different days so we can block out sleep 
  # (2 hours after last meal of a day through 1 hour before breakfast the following morning).
  if(not nextObservation is None and observation['datetime'].date() != nextObservation['datetime'].date()):
    for hour in range(0, hours):
      startTime = observation['datetime'] + timedelta(hours=hour)
      endTime = observation['datetime'] + timedelta(hours=hour+step)

      # Skip over intervals that are entirely contained within sleep time. 
      if startTime < observation['datetime'] + timedelta(hours=2) or endTime > nextObservation['datetime']-timedelta(hours=1):
        # store row index of current observation in observations_ignored
        curr_key = f'{hour}-{hour+step}'
        if curr_key not in observations_ignored:
            observations_ignored[curr_key] = [] 
        observations_ignored[curr_key].append(observation[observation.index[0]])
        continue

      key = f'{hour}-{hour+step}'
      data = getSymptomsInInterval(startTime, endTime, symptoms)
      if key not in timeframes:
        timeframes[key] = pd.DataFrame(columns=data.index)

      timeframes[key] = timeframes[key].append(data, ignore_index=True)

  else:
    for hour in range(0, hours):
      startTime = observation['datetime'] + timedelta(hours=hour)
      endTime = observation['datetime'] + timedelta(hours=hour+step)
      key = f'{hour}-{hour+step}'
      data = getSymptomsInInterval(startTime, endTime, symptoms)
      if key not in timeframes:
        timeframes[key] = pd.DataFrame(columns=data.index)

      timeframes[key] = timeframes[key].append(data, ignore_index=True)

  


# Balances labels so that there is a roughly 50/50 split of 1's (has symptoms) and 0's (no symptoms)
def balance(labels):
    numNegs = len(labels[labels == 0])
    numPos = len(labels[labels == 1])
    print(f'numNegs: {numNegs} numPos: {numPos}')
    numTotal = len(labels)
    return labels[labels.map(lambda x: x == 1 or random.randint(1,numNegs) > (numNegs-numPos))].copy()


# Runs KNN, Decision Tree, and Logistic Regression .
# Prints out results in table format using tabulate.
def runAndEval(hours, features, timeframes):
    
    ## Extract the labels we care about.
    labels = timeframes[hours]['has_symptoms'].astype('int')

    ## Split the data into training and test.
    (train_features, test_features, train_labels, test_labels) = train_test_split(features, labels, test_size=0.4, shuffle=False)

    ## Balance
    train_labels = balance(train_labels)
    test_labels = balance(test_labels)

    ## Scale
    continuous_feature_names = ['Calories', 'Carbs (g)', 'Fat(g)', 'Protein (g)', 'Cholest (mg)', 'Sodium (mg)',
                                'Sugars (g)', 'Fiber (g)']
    scaler = MinMaxScaler()
    scaler.fit(train_features[continuous_feature_names])
    scaled_train_features = train_features.copy()
    scaled_train_features[continuous_feature_names] = scaler.transform(train_features[continuous_feature_names])

    scaled_test_features = test_features.copy()
    scaled_test_features[continuous_feature_names] = scaler.transform(test_features[continuous_feature_names])

    ## Find the distribution of labels over the training set.
    
    left_col = f'Sizes: {train_labels.value_counts()}'
    left_col = left_col + '\n' + 'Training set label distribution'
    left_col = left_col + '\n' + str(train_labels.value_counts() / train_labels.shape[0])

    left_col = left_col + '\n' + f'Sizes: {test_labels.value_counts()}'
    left_col = left_col + '\n' + 'Testing set label distribution'
    ## Find the distribution of labels over the development set.
    left_col = left_col + '\n' + str(test_labels.value_counts() / test_labels.shape[0])

    temp_list = []
    curr_data = []
    test_columns = ['Accuracy', 'F1', 'Prec', 'Recall', 'AuROC']
    test_list = {0:'KNN', 1:'Log Reg', 2:'Decision Tree'}

    ## KNN
    knn_model = KNeighborsClassifier(n_neighbors=5)
    knn_model.fit(scaled_train_features.iloc[train_labels.index], train_labels)
    knn_test_predictions = knn_model.predict(scaled_test_features.loc[test_labels.index])

    curr_data.append(metrics.accuracy_score(test_labels, knn_test_predictions))
    curr_data.append(metrics.f1_score(test_labels, knn_test_predictions))
    curr_data.append(metrics.precision_score(test_labels, knn_test_predictions))
    curr_data.append(metrics.recall_score(test_labels, knn_test_predictions))

    ## Area under the Receiver Operator Curve
    auc = metrics.roc_auc_score(test_labels, knn_test_predictions)
    curr_data.append(auc)
    temp_list.append(curr_data)
    curr_data = []

    ## Logistic regression
    logreg_model = LogisticRegression()
    logreg_model.fit(scaled_train_features.iloc[train_labels.index], train_labels) 

    logreg_model_predictions = logreg_model.predict(scaled_test_features.loc[test_labels.index])

    curr_data.append(metrics.accuracy_score(test_labels, logreg_model_predictions))
    curr_data.append(metrics.f1_score(test_labels, logreg_model_predictions))
    curr_data.append(metrics.precision_score(test_labels, logreg_model_predictions))
    curr_data.append(metrics.recall_score(test_labels, logreg_model_predictions))

    ## Area under the Receiver Operator Curve
    auc = metrics.roc_auc_score(test_labels, logreg_model_predictions)
    curr_data.append(auc)
    temp_list.append(curr_data)
    curr_data = []

    ## Decision Tree
    tree_model = DecisionTreeClassifier()
    tree_model.fit(scaled_train_features.iloc[train_labels.index], train_labels) 

    tree_model_predictions = tree_model.predict(scaled_test_features.loc[test_labels.index])

    curr_data.append(metrics.accuracy_score(test_labels, tree_model_predictions))
    curr_data.append(metrics.f1_score(test_labels, tree_model_predictions))
    curr_data.append(metrics.precision_score(test_labels, tree_model_predictions))
    curr_data.append(metrics.recall_score(test_labels, tree_model_predictions))

    ## Area under the Receiver Operator Curve
    auc = metrics.roc_auc_score(test_labels, tree_model_predictions)
    curr_data.append(auc)
    temp_list.append(curr_data)

    # Put results into dataframe to make printing easier
    results_df = pd.DataFrame(data=temp_list, columns=test_columns)
    results_df = results_df.rename(test_list)
    
    # Print results in tabulated format
    l = [[left_col, results_df]]
    table = tabulate(l, tablefmt='orgtbl')
    print(f'================================= Models/evaluation for hour {hours} =================================\n')
    print(table)
    print('\n\n\n')


# # Target format
# 
# 
# An observation is one food item.
# 
# ## non-feature attributes
# 
#   * timestamp
# 
# ## features
# 
#   * each of nutrtional info (fats, etc.)
#   * ingredients
# 
# ## independent variables, each at 1 hour increments for X hours
# 
# Values: 0-5
#   * Appetite
#   * Stomach Ache
#   * Distension
#   * Gas
#   * Belching
#   * Heartburn
# 
# Binary
#   * has_symptoms (1 if any of the above are > 0)
#   
# 

# In[2]:


meals = pd.read_excel('clean_data.xlsx')
meals.tail()


# In[3]:


columns = meals.columns
columns


# In[4]:


meals.rename(columns={meals.columns[0]: "id"})
meals.columns


# In[5]:


## Removing the amount of food item (e.g., ", 37g")
meals['Food-clean'] = meals['Food'].map(lambda x: x[0:x.index(',')])


# In[6]:


foodList = pd.read_excel('master_food_list.xlsx')
foodList.tail()


# In[42]:


## Extend each meal food entry with details about that food (ingredients)
observations = meals.merge(foodList, how='left', left_on='Food-clean', right_on='food')


# In[8]:


symptomsDF = pd.read_excel('symptoms.xlsx', sheet_name='Symptoms')
#symptomsDF.head()


# In[9]:


## Merge date and time into one cell
symptomsDF['datetime']  = symptomsDF[['Date', 'Time']].apply(
    lambda row: dateparser.parse(row['Date'].strftime('%Y-%m-%d') +' '+ str(row['Time']),
                                 date_formats=['Y-%m-%d %H:%M:%S']), 
    axis=1)
print(symptomsDF.head())


# In[44]:


# concatenate date and time into one cell
observations['datetime']  = observations[['Date', 'Time']].apply(
    lambda row: dateparser.parse(row['Date'].strftime('%Y-%m-%d') +' '+ str(row['Time']),
                                 date_formats=['Y-%m-%d %H:%M:%S']), 
    axis=1)
observations.head()


# In[68]:


# timeframes <- dict of data frames
# for each observation:
#   generateDVs
# now for each key (timeframe) in timeframes, we have a list of symptom values that correspond to each
# observation

timeframes = {}
observations_ignored = {}
observations.apply(lambda row: generateDVs(observations, row, symptomsDF, timeframes, observations_ignored, 12, 4), axis=1)


# In[70]:


total_length = sum(len(row) for row in observations_ignored)
print(total_length)
print(len(observations_ignored))
print(observations_ignored)
# show what timeframes we generated DV's over
timeframes.keys()
print(len(observations_ignored['0-4']))


# In[13]:


print(timeframes['0-4'].head(20))


# In[41]:


## remove unnecessary columns from featureNames
featureNames = observations.columns.to_list()
featureNames.remove("Date")
featureNames.remove("Time")
featureNames.remove("Meal")
featureNames.remove("datetime")
featureNames.remove("Unnamed: 0_x")
featureNames.remove("Unnamed: 0_y")
featureNames.remove("Food")
featureNames.remove("food")
featureNames.remove("Food-clean")
featureNames.remove("id")

## Some ingredients were not properly set to 0; fix that
features = observations[featureNames].applymap(lambda x: 0 if isnan(x) or type(x) == type("") else x)
features.head()


# In[109]:


## Train and test the models.

for timeBlock in timeframes.keys():
    feature_subset = features.drop(features.index[observations_ignored[timeBlock]])
    feature_subset = feature_subset.reset_index()
    runAndEval(timeBlock, feature_subset, timeframes)


# # Concluding CSC333 Fall 2020 
# 
# ## Future directions
# * eleminating all timeframes that are fully enveloped during non-awake hours
#   - currently, this is only done for dinner observations (a.k.a. last meal of the day observations)
#   - to do this, we would need to determine, for any given observation, when the last meal of that day occurs
#     and when the first meal of the next day occurs
#     * maybe use a precomputed lookup table that has each day's first and last meal timestamps
#   - use 2 hours after last meal -- 1 hour before breakfast as "sleep"
# 
# * look at feature weight -- what are the important features
# * look at regression or classification models that predict symptoms or symptom levels (right now now, we're only predicting "has any symptoms")
# * experiment with different timeBlock sizes
