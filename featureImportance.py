#!"C:\Program Files\Python310"

# Import libraries that are used for the classification results.
import os
import numpy as np
import matplotlib as plt
import pandas as pd
from pathlib import Path
import statistics

# Import sklearn key libraries required.
from sklearn.dummy import DummyClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

# Import the metrics required for assessing performance.
import sklearn.base
from sklearn.feature_selection import SelectPercentile
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_validate
from sklearn.model_selection import StratifiedKFold

# Turn off the warnings (issues with current version)
import warnings
warnings.filterwarnings('ignore') 

import shap
# shap.initjs()
from sklearn.feature_selection import SelectPercentile

#=====================================================
# The function for returning the correct subset of input data, based on the specified subset.
def getCurrXSet(scoreDataframe, file, subset):
    #General set up using the entire dataset.
    X1 = scoreDataframe.iloc[:, 2:10]
    X2 = scoreDataframe.iloc[:, 29:]

    #Correctly indexing the data to get either raw, statistical or both feature types together.
    if 'S1A2' in file:
        if 'All' in file:
            if 'Stats' in subset:
                X2 = scoreDataframe.iloc[:, 29:254]

            elif 'Raw' in subset:
                X2 = scoreDataframe.iloc[:, 254:]

        elif 'Ankles' in file:
            if 'Stats' in subset:
                X2 = scoreDataframe.iloc[:, 29:182]
            elif 'Raw' in subset:
                X2 = scoreDataframe.iloc[:, 182:]

        elif 'Pelvis' in file:
            if 'Stats' in subset:
                X2 = scoreDataframe.iloc[:, 29:110]
            elif 'Raw' in subset:
                X2 = scoreDataframe.iloc[:, 110:]
    
    elif 'S2' in file:
        if 'All' in file:
            if 'Stats' in subset:
                X2 = scoreDataframe.iloc[:, 29:146]

            elif 'Raw' in subset:
                X2 = scoreDataframe.iloc[:, 146:]

        elif 'Ankles' in file:
            if 'Stats' in subset:
                X2 = scoreDataframe.iloc[:, 29:110]
            elif 'Raw' in subset:
                X2 = scoreDataframe.iloc[:, 110:]

        elif 'Pelvis' in file:
            if 'Stats' in subset:
                X2 = scoreDataframe.iloc[:, 29:74]
            elif 'Raw' in subset:
                X2 = scoreDataframe.iloc[:, 74:]

    #Concatenate the subject characteristics with the other sliced data.
    X = pd.concat([X1, X2], axis = 1)

    #Output the subset to the console for validation.
    print("X FOR SUBSET " + subset)
    print(X)
    print('')
    return X

#=====================================================
# A general function for outputting errors to the console, in addition to the actual files too.
#
# error:                    The error message for the console window.
def classExceptionMessage(error):
    print(error)

#=====================================================
#CHAPTER: Main Running Function for Extracting Features
#=====================================================
#Get current working directory for path
currentDirectory = Path.cwd()

#Variables required for extracting information.
#Depending on the best subset, these will be changed manually to extract the correct features.
fileToUse = 'fS2-All'
subsetToUse = 'Raw'
score = 1
item = score - 1

#Extract the relevant data, the same process as classification.
scoreDataframe = pd.read_csv(fileToUse + '.csv' +  fileToUse + '.csv', header = 0)
X = getCurrXSet(scoreDataframe, fileToUse, subsetToUse)
y = scoreDataframe.iloc[:, 11:29]
yZoom = y.iloc[:, item]

#All the options of classifiers to use.
print("Classifiers")
#classifier = KNeighborsClassifier()
#classifier = GaussianNB()
#classifier = GradientBoostingClassifier(random_state = 1513595)
#classifier = SGDClassifier(random_state = 1513595)
#classifier = RandomForestClassifier(random_state = 1513595)
classifier = MLPClassifier(random_state = 1513595)

#Output the current scoring item that is being used.
print("SCORE" + str(score))

#In larger subsets, we need to limit the number of features due to SHAP limitations.
#Therefore, SelectPercentile is used to pick the top 1% of thousands of features.
if subsetToUse == 'DRaw' or subsetToUse == 'DFull':
    kBest = sklearn.feature_selection.SelectPercentile(percentile = 1)
    kBest = kBest.set_output(transform = 'pandas')
    X = kBest.fit_transform(X, yZoom)

    #Output the percentile of X values.
    print("REPLACED X VALUES")
    print(X)
    print('')


#Fit the classifier to the entire dataset.
classifier.fit(X, yZoom)

#Create lists of class names for graph output.
if item == 17:
    classNames = ['excellent', 'average', 'poor']
elif item == 16:
    classNames = ['soft', 'average', 'stiff']
else:
    classNames = ['absent', 'present']

#Create an explainer and explain the probability of prediction for the entire dataset.
explainer = shap.KernelExplainer(classifier.predict_proba, X)
SHAPValues = explainer.SHAPValues(X)

#For the amount of classes we have (length of SHAP values).
for x in range(0, len(SHAPValues)):
    shap.summary_plot(SHAPValues[x], X, plot_type = "dot", classNames = classNames[x], show = False)
    plt.savefig("score" + str(item) + "_labelsummary" + str(x) + "_bee.png")
    plt.show()

    shap.summary_plot(SHAPValues[x], X, plot_type = "bar", classNames = classNames[x], show = False)
    plt.savefig("score" + str(item) + "_labelsummary" + str(x) + "_bar.png")
    plt.show()

    shap.summary_plot(SHAPValues[x], X, plot_type = "violin", classNames = classNames[x], show = False)
    plt.savefig("score" + str(item) + "_labelsummary" + str(x) + "_violin.png")
    plt.show()

#Also, provide the summary plot of the entire group of classes.
try:
    shap.summary_plot(SHAPValues, X, plot_type = "bar", max_display = 5, classNames = classNames, show = False)
    plt.savefig("score" + str(item) + "_summary_bar.png")
    plt.show()

except Exception as e:
    print(e)

#Output final message.
print("Feature Importance has been extracted.")
print(" ")

#=====================================================