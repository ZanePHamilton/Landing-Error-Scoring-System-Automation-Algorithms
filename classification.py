#!"C:\Program Files\Python310"

# Import libraries that are used for the classification results.
import os
import numpy as np
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

# Global variables for the row header, the overall scores to keep track of
# additional rows for three-class classification, and the consistent random
# state used for replicating the best performing models (where random state exists)
rowHeader = 'Dummy, KNN, GNB, SVC, GBC, SGD, RFC, DFF\n'
overallScoreRows = ['Accuracy', 'Precision_0', 'Recall_0', 'F1_0', 'Precision_1', 'Recall_1', 'F1_1']
multiClassRows = ['Precision_2', 'Recall_2', 'F1_2']
randomState = 1513595
weightedScoreRows = ['Accuracy', 'Precision', 'Recall', 'F1']

#=====================================================
# The function used for writing the results to a CSV file for easier analysis and comparison between other models.
#
# currentScore:             The current scoring item for the label writing.
# dummyResults:            The performance metrics of the ZeroR or Dummy Classifier.
# knnResults:              The performance metrics for the KNN Classifier.
# gnbResults:              The performance metrics for the GNB Classifier.
# svcResults:              The performance metrics for the SVC Classifier.
# gbcResults:              The performance metrics for the GBC Classifier.
# sgdResults:              The performance metrics for the SGD Classifier.
# rfcResults:              The performance metrics for the RFC Classifier.
# dffResults:              The performance metrics for the DFF Classifier.
def writeResults(currentScore, dummyResults, knnResults, gnbResults, svcResults, gbcResults, sgdResults, rfcResults, dffResults):
    #Write the required score headers.
    fullScoreWriter.write('SCORE' + str(currentScore) + ',' +  rowHeader)
    weightedScoreWriter.write('SCORE' + str(currentScore) + ',' +  rowHeader)

    #Write the seven metrics to the new file.
    for counter in range(0, 7):
        fullScoreWriter.write(overallScoreRows[counter] + ',' + str(dummyResults[counter]) + ',' + str(knnResults[counter]) + ',' + str(gnbResults[counter]) + ',' + str(svcResults[counter]) + ',' + str(gbcResults[counter]) + ',' + str(sgdResults[counter]) + ',' + str(rfcResults[counter]) + ',' + str(dffResults[counter]))
        fullScoreWriter.write('\n')

    #If the score is a multi-class classification, we need an additional loop for the metrics of a third class.
    if currentScore > 15:
        for counter in range(10, 13):
            fullScoreWriter.write(multiClassRows[counter - 10] + ',' + str(dummyResults[counter]) + ',' + str(knnResults[counter]) + ',' + str(gnbResults[counter]) + ',' + str(svcResults[counter]) + ',' + str(gbcResults[counter]) + ',' + str(sgdResults[counter]) + ',' + str(rfcResults[counter]) + ',' + str(dffResults[counter]))
            fullScoreWriter.write('\n')

    #In the weighted result CSV file, also write these results.
    weightedScoreWriter.write(weightedScoreRows[0] + ',' + str(dummyResults[0]) + ',' + str(knnResults[0]) + ',' + str(gnbResults[0]) + ',' + str(svcResults[0]) + ',' + str(gbcResults[0]) + ',' + str(sgdResults[0]) + ',' + str(rfcResults[0]) + ',' + str(dffResults[0]))
    weightedScoreWriter.write('\n')
    for counter in range(7, 10):
        weightedScoreWriter.write(weightedScoreRows[counter - 6] + ',' + str(dummyResults[counter]) + ',' + str(knnResults[counter]) + ',' + str(gnbResults[counter]) + ',' + str(svcResults[counter]) + ',' + str(gbcResults[counter]) + ',' + str(sgdResults[counter]) + ',' + str(rfcResults[counter]) + ',' + str(dffResults[counter]))
        weightedScoreWriter.write('\n')
    fullScoreWriter.write('\n')
    weightedScoreWriter.write('\n')

#=====================================================
# A function for specifically writing the results of the total score, as there are more labels and metrics to keep track of.
# Only the weighted metrics were output in the final product.
#
# currentScore:               The current scoring item for the label writing.
# dummyResults:            The performance metrics of the ZeroR or Dummy Classifier.
# knnResults:              The performance metrics for the KNN Classifier.
# gnbResults:              The performance metrics for the GNB Classifier.
# svcResults:              The performance metrics for the SVC Classifier.
# gbcResults:              The performance metrics for the GBC Classifier.
# sgdResults:              The performance metrics for the SGD Classifier.
# rfcResults:              The performance metrics for the RFC Classifier.
# dffResults:              The performance metrics for the DFF Classifier.
def totalScoreOutput(currentScore, dummyResults, knnResults, gnbResults, svcResults, gbcResults, sgdResults, rfcResults, dffResults):
    #Replicate the other writer logic, but writing just the weighted values instead.
    weightedScoreWriter.write('SCORE' + str(currentScore) + ',' +  rowHeader)
    weightedScoreWriter.write(weightedScoreRows[0] + ',' + str(dummyResults[0]) + ',' + str(knnResults[0]) + ',' + str(gnbResults[0]) + ',' + str(svcResults[0]) + ',' + str(gbcResults[0]) + ',' + str(sgdResults[0]) + ',' + str(rfcResults[0]) + ',' + str(dffResults[0]))
    weightedScoreWriter.write('\n')
    for counter in range(1, 4):
        weightedScoreWriter.write(weightedScoreRows[counter] + ',' + str(dummyResults[counter]) + ',' + str(knnResults[counter]) + ',' + str(gnbResults[counter]) + ',' + str(svcResults[counter]) + ',' + str(gbcResults[counter]) + ',' + str(sgdResults[counter]) + ',' + str(rfcResults[counter]) + ',' + str(dffResults[counter]))
        weightedScoreWriter.write('\n')
    weightedScoreWriter.write('\n')

#=====================================================
# A general function for outputting errors to the console, in addition to the actual files too.
#
# error:                    The error message for the console window.
def classExceptionMessage(error):
    print(error)
    weightedScoreWriter.write('ERROR,')
    fullScoreWriter.write('ERROR,ERROR,ERROR,')

#=====================================================
# Function used for validaitng one model using cross-fold validation, with 5 total folds.
#
# score:                    Keeping track of the current scoring item so the logic can be altered if it is multi-class.
# cv:                       The cross validation object passed through from the original loop.
# classifier:               The current classifier being validated.
# XSet:                    The input data, or current subset of data to be validated.
# ySet:                    The LESS scores to be predicted.
def validateCurrentModel(score, cv, classifier, XSet, ySet):
    #Set variables to be used.
    multiClassCheck = False
    accuraciesList = []
    
    #Create required lists to keep track of various metrics.
    weightedPrecisionList = []
    weightedRecallList = []
    weightedF1List = []

    if score != 18:
        #All '0' classes.
        absentPrecisionList = []
        absentRecallList = []
        absentF1List = []

        #All '1' classes.
        presentPrecisionList = []
        presentRecallList = []
        presentF1List = []

        #Class names to be used in the classification report.
        classNames = ['absent', 'present']
        
        #If the score is greater than 15, we need an additional set of lists for the '2' classes.
        if score > 15:
            classNames.append('poor')
            multiClassCheck = True
            poorPrecisionList = []
            poorRecallList = []
            poorF1List = []
        
        #Clone the original classifier so we aren't training the same classifier on every fold.
        rawClassifier = sklearn.base.clone(classifier)

        #Using the five splits, get the train and test sets and clone the original classifier.
        for trainIndex, testIndex in cv.split(XSet, ySet):
            XTrain, XTest = XSet.iloc[trainIndex], XSet.iloc[testIndex]
            yTrain, yTest = ySet.iloc[trainIndex], ySet.iloc[testIndex]
            classifier = sklearn.base.clone(rawClassifier)
            
            #Using the data extracted, fit and predict.
            try:
                classifier.fit(XTrain, yTrain)
                predictions = classifier.predict(XTest)
                
                #Show the classification report in the console, in addition to the CSV file.
                print(classification_report(yTest, predictions, target_names = classNames))
                fullReport = classification_report(yTest, predictions, target_names = classNames, output_dict = True)

            except Exception as e:
                print(e)
                return -1
            
            #Append all of the data from the classification report to the lists for averaging.
            accuraciesList.append(fullReport['accuracy'])

            absentPrecisionList.append(fullReport['absent']['precision'])
            absentRecallList.append(fullReport['absent']['recall'])
            absentF1List.append(fullReport['absent']['f1-score'])

            presentPrecisionList.append(fullReport['present']['precision'])
            presentRecallList.append(fullReport['present']['recall'])
            presentF1List.append(fullReport['present']['f1-score'])

            weightedPrecisionList.append(fullReport['weighted avg']['precision'])
            weightedRecallList.append(fullReport['weighted avg']['recall'])
            weightedF1List.append(fullReport['weighted avg']['f1-score'])

            #If we have a multi-class scoring item, append to the additional lists too.
            if multiClassCheck:
                poorPrecisionList.append(fullReport['poor']['precision'])
                poorRecallList.append(fullReport['poor']['recall'])
                poorF1List.append(fullReport['poor']['f1-score'])

        #Average all of the lists to get an average metric for 5 folds.
        performanceMeasures = [statistics.mean(accuraciesList), 
                                statistics.mean(absentPrecisionList), statistics.mean(absentRecallList), statistics.mean(absentF1List),
                                statistics.mean(presentPrecisionList), statistics.mean(presentRecallList), statistics.mean(presentF1List),
                                statistics.mean(weightedPrecisionList), statistics.mean(weightedRecallList), statistics.mean(weightedF1List)]
        
        #Add in the additional class if it is multi-class.
        if multiClassCheck:
            performanceMeasures.append(statistics.mean(poorPrecisionList))
            performanceMeasures.append(statistics.mean(poorRecallList))
            performanceMeasures.append(statistics.mean(poorF1List))
    
    #Otherwise, if it is the total score, we only extract the weighted measures.
    else:
        for trainIndex, testIndex in cv.split(XSet, ySet):
            XTrain, XTest = XSet.iloc[trainIndex], XSet.iloc[testIndex]
            yTrain, yTest = ySet.iloc[trainIndex], ySet.iloc[testIndex]

            try:
                classifier.fit(XTrain, yTrain)
                predictions = classifier.predict(XTest)

                print(classification_report(yTest, predictions))
                fullReport = classification_report(yTest, predictions, output_dict = True)
            except Exception as e:
                print(e)
                return -1
            
            accuraciesList.append(fullReport['accuracy'])

            weightedPrecisionList.append(fullReport['weighted avg']['precision'])
            weightedRecallList.append(fullReport['weighted avg']['recall'])
            weightedF1List.append(fullReport['weighted avg']['f1-score'])

        performanceMeasures = [statistics.mean(accuraciesList), 
                                statistics.mean(weightedPrecisionList), statistics.mean(weightedRecallList), statistics.mean(weightedF1List)]

    #Return the final instance of performance measures for output to CSV file.
    return performanceMeasures

#=====================================================
# The primary function for applying all of the selected models to each scoring item accordingly.
#
# X:                        The set of input data to use for training each model/
# y:                        The LESS scores to attempt to predict.
# crossFolds:              The consistent folds to use for the entire selection of models.
def crossFoldClassification(X, y, crossFolds):
    #In our dataset, 0 corresponds to scoring item 1, and 18 is the total score. The scores are in order.
    for item in range(0, 18):
        yZoom = y.iloc[:, item]
        scoreStr = item + 1
        print("SCORE" + str(scoreStr))
        
        #For each classifier, try to validate all of the models one after the other.
        #ZeroR
        try:
            print(" ")
            print("Dummy Classifier")
            dummy = DummyClassifier(strategy="most_frequent")
            dummyResults = validateCurrentModel(scoreStr, crossFolds, dummy, X, yZoom)
        except Exception as e:
            classExceptionMessage(e)
        
        #KNN
        try:
            print(" ")
            print("K-Nearest Neighbours Classifier")
            knn = KNeighborsClassifier()
            knnResults = validateCurrentModel(scoreStr, crossFolds, knn, X, yZoom)
        except Exception as e:
            classExceptionMessage(e)
        
        #Gaussian Naive-Bayes
        try:
            print(" ")
            print("Gaussian Classifier")
            gnb = GaussianNB()
            gnbResults = validateCurrentModel(scoreStr, crossFolds, gnb, X, yZoom)
        except Exception as e:
            classExceptionMessage(e)

        #Support-Vector
        try:
            print(" ")
            print("Support Vector Classifier")
            svc_clf = SVC(random_state = randomState)
            svcResults = validateCurrentModel(scoreStr, crossFolds, svc_clf, X, yZoom)
        except Exception as e:
            classExceptionMessage(e)
        
        #Gradient Boosting
        try:
            print(" ")
            print("Gradient Boosting Classifier")
            gbc = GradientBoostingClassifier(random_state = randomState)
            gbcResults = validateCurrentModel(scoreStr, crossFolds, gbc, X, yZoom)
        except Exception as e:
            classExceptionMessage(e)
        
        #Stochastic Gradient Descent
        try:
            print(" ")
            print("SGD Classifier")
            sgd = SGDClassifier(random_state = randomState)
            sgdResults = validateCurrentModel(scoreStr, crossFolds, sgd, X, yZoom)
        except Exception as e:
            classExceptionMessage(e)

        #Random Forest
        try:
            print(" ")
            print("Random Forest Classifier")
            rfc = RandomForestClassifier(random_state = randomState)
            rfcResults = validateCurrentModel(scoreStr, crossFolds, rfc, X, yZoom)
        except Exception as e:
            classExceptionMessage(e)
        
        #Multi-Layer Perception (DFF)
        try:
            print(" ")
            print("Deep Feed-forward Neural Network Classification")
            dff = MLPClassifier(random_state = randomState)
            dffResults = validateCurrentModel(scoreStr, crossFolds, dff, X, yZoom)
        except Exception as e:
            classExceptionMessage(e)
        
        #Depending on the current scoring item, call the correct writer.
        if item != 17:
            if dummyResults != -1: 
                print("Writing to output now.")
                writeResults(scoreStr, dummyResults, knnResults, gnbResults, svcResults, gbcResults, sgdResults, rfcResults, dffResults)
        else:
            if dummyResults != -1:
                totalScoreOutput(scoreStr, dummyResults, knnResults, gnbResults, svcResults, gbcResults, sgdResults, rfcResults, dffResults)

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
#CHAPTER: Main Running Function for Classifying all of the Subsets
#=====================================================
#Get current working directory for path
currentDirectory = Path.cwd()
foldersToCreate = ['weighted', 'full']

#=====================================================
# Process for creating a new directory using the specified save location.
# While folder input is invalid...
while(True):
    try:
        #Get the folder from the user, create the string using current directory and change to it.
        folder = input("Please input the directory name you want to process: ")
        processFolderName = str(currentDirectory) + "\\" + folder.strip()
        directory = os.fsencode(processFolderName)
        os.chdir(processFolderName)

        for folders in foldersToCreate:
            exists = os.path.exists(folders)
            if not exists:
                os.makedirs(folders)
                print("The new directory is created!")
        break
        #Make a new folder so the names of the file can stay the same without overwrite.
    except Exception as e:
        print(e)

#A list of the files and subsets to run through the classification.
availableFiles = ['fS1A2-All', 'fS1A2-Ankles', 'fS1A2-Pelvis', 'fS2-All', 'fS2-Ankles', 'fS2-Pelvis']
availableSubsets = ['Full', 'Raw', 'Stats']

#Create the stratified k fold object, with n = 5 for a 80/20% split.
crossFolds = StratifiedKFold(n_splits = 5)

#For each of the files and the available subsets...
for currentFile in availableFiles:
    for currentSubset in availableSubsets:
        
        #Open the full dataset from the specified path and the two new files to write to.
        scoreDataframe = pd.read_csv(currentFile + '.csv', header = 0)
        fullScoreWriter = open('full\\full_' + currentSubset + '_' + currentFile + '.csv', mode = 'w', newline = '')
        weightedScoreWriter = open('weighted\\weighted_' + currentSubset + '_' + currentFile + '.csv', mode = 'w', newline = '')

        #Call the helper function to get the correct subset from the full X set, and get the scores.
        X = getCurrXSet(scoreDataframe, currentFile, currentSubset)
        y = scoreDataframe.iloc[:, 11:29]

        #Call the classification method on the current dataset.
        crossFoldClassification(X, y, crossFolds)

        #Close the current files for this specific subset.
        fullScoreWriter.close()
        weightedScoreWriter.close()
    
        #Use the console window to track the current subset.
        print(currentSubset + " is done")
    
    #Use the console window to keep track of the current file.
    print(currentFile + " is done")

#=====================================================