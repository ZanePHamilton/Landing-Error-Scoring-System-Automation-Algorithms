#!"C:\Program Files\Python310"

# Import libraries that are used in the segmentation process.
import copy
import csv
import os
import math
import numpy as np
from pathlib import Path
import statistics

# Global variables for the list of features derived from the segments and the save location.
# The save location has a naming convention depending on the subset we are currently segmenting.
featureList = []
saveLocation = "segments"

#=====================================================
#CHAPTER: Functions implemented for extracting and outputting information from the input CSV files.
#=====================================================
# Function for performing the slicing of the dictionaries using a start and end index point.
#
# fileDict:         The dictionary containing data from a CSV file to be sliced.
# initialIndex:     The index of the current dictionary that needs to be sliced from.
# finalIndex:       The index of the current dictionary that needs to be sliced to.
def cropFileDict(fileDict, initialIndex, finalIndex):
    return fileDict[initialIndex:finalIndex]

#=====================================================
# Return the index position of the closest timestamp in a file dictionary.
#
# fileDict:         The dictionary of IMU datum with timestamps to use.
# timestamp:        The timestamp value from an IMU sensor that we want to get an event from.
def getClosestTimestampIndex(fileDict, timestamp):
    #Create a list for all the timestamps in a file dictionary.
    timestampList = []

    #Store all of the timestamps into the timestamp list.
    for x in range(0, len(fileDict)):
        timestampList.append(int(fileDict[x]['unix_timestamp_microsec']))
    
    #Using a lambda expression, find the closest absolute timestamp to the parameter timestamp and return it's index.
    translatedTimestamp = timestampList[min(range(len(timestampList)), key = lambda i: abs(timestampList[i] - timestamp))]
    return timestampList.index(translatedTimestamp)

#=====================================================
# Get the dictionary representation of a CSV file.
#
# filename:     The name of the file to read and return.
def getCSVDict(filename):
    csvFile = open(filename)
    csvreader = csv.DictReader(csvFile)
    return[row for row in csvreader]

#=====================================================
# Function for writing the entirety of the three different sensors to a new file.
#
# csvWriter:        The writer currently being used to write to a new file.
# accelerometer:    Boolean value corresponding to whether the current file is an accelerometer or gyroscope.
# leftAnkle:        The dictionary containing the left ankle sensor datum to be written.
# rightAnkle:       The dictionary containing the right ankle sensor datum to be written.
# pelvis:           The dictionary containing the pelvis sensor datum to be written.
# maxIndex:         The length of the largest dictionary in the current file group.
def getCSVRows(csvWriter, accelerometer, leftAnkle, rightAnkle, pelvis, maxIndex):
    if accelerometer:
        for x in range(0, maxIndex):
            current =  {'lax_m/s/s':leftAnkle[x]['ax_m/s/s'], 'lay_m/s/s':leftAnkle[x]['ay_m/s/s'], 'laz_m/s/s':leftAnkle[x]['az_m/s/s'],
                        'rax_m/s/s':rightAnkle[x]['ax_m/s/s'], 'ray_m/s/s':rightAnkle[x]['ay_m/s/s'], 'raz_m/s/s':rightAnkle[x]['az_m/s/s'],
                        'pax_m/s/s':pelvis[x]['ax_m/s/s'], 'pay_m/s/s':pelvis[x]['ay_m/s/s'], 'paz_m/s/s':pelvis[x]['az_m/s/s']}
            csvWriter.writerow(current)
    else:
        for x in range(0, maxIndex):
            current =  {'lgx_deg/s':leftAnkle[x]['gx_deg/s'], 'lgy_deg/s':leftAnkle[x]['gy_deg/s'], 'lgz_deg/s':leftAnkle[x]['gz_deg/s'],
                        'rgx_deg/s':rightAnkle[x]['gx_deg/s'], 'rgy_deg/s':rightAnkle[x]['gy_deg/s'], 'rgz_deg/s':rightAnkle[x]['gz_deg/s'],
                        'pgx_deg/s':pelvis[x]['gx_deg/s'], 'pgy_deg/s':pelvis[x]['gy_deg/s'], 'pgz_deg/s':pelvis[x]['gz_deg/s']}
            csvWriter.writerow(current)

#=====================================================
# Function aimed at filling the smaller files with -1 values to ensure the segmented data is of the same length.
#
# accelerometer:    Boolean value corresponding to whether the current file is an accelerometer or gyroscope.
# leftAnkle:        The dictionary containing the left ankle sensor datum to be filled.
# rightAnkle:       The dictionary containing the right ankle sensor datum to be filled.
# pelvis:           The dictionary containing the pelvis sensor datum to be filled.
# maxIndex:         The length of the largest dictionary in the current file group.
def fillEmptyDict(accelerometer, leftAnkle, rightAnkle, pelvis, maxIndex):
    #Make deep copies of the original lists to not make any changes to the original data.
    lAnkle = copy.deepcopy(leftAnkle)
    rAnkle = copy.deepcopy(rightAnkle)
    pelv = copy.deepcopy(pelvis)

    #Change the format of the output dependent on the current file type.
    if accelerometer:
        fillerDict = {'ax_m/s/s': -1, 'ay_m/s/s': -1, 'az_m/s/s': -1}
    else:
        fillerDict = {'gx_deg/s': -1, 'gy_deg/s': -1, 'gz_deg/s': -1}

    #Using the max index, fill all the dictionaries up until they are the same length.
    for x in range(len(lAnkle), maxIndex + 1):
        lAnkle.append(fillerDict)
    for y in range(len(rAnkle), maxIndex + 1):
        rAnkle.append(fillerDict)
    for z in range(len(pelv), maxIndex + 1):
        pelv.append(fillerDict)

    #Return the new dictionaries in a list that can be indexed.
    return [lAnkle, rAnkle, pelv]
        
#=====================================================
# Function used for writing the segmented data to a new 'combined' file with all three sensors included.
#
# accelerometer:        Boolean value on whether the current file is an accelerometer or not.
# leftAnkle:            The dictionary containing the left ankle sensor datum to be written.
# rightAnkle:           The dictionary containing the right ankle sensor datum to be written.
# pelvis:               The dictionary containing the pelvis sensor datum to be written.
# participant:          The unique identifier for each jump so the output file can be ordered correctly.
def writeNewCSV(accelerometer, leftAnkle, rightAnkle, pelvis, participant):
    #Determine the maximum index required between all three files.
    maximalLimit = max([len(leftAnkle), len(rightAnkle), len(pelvis)])

    #If it is an accelerometer, write the correct formatted file using m/s/s labels.
    if accelerometer:
        newFile = open(saveLocation + '\\' + participant +'-acc-combined.csv' , mode = 'w', newline = '')
        headerItem = ['lax_m/s/s', 'lay_m/s/s', 'laz_m/s/s','rax_m/s/s', 'ray_m/s/s', 'raz_m/s/s', 'pax_m/s/s', 'pay_m/s/s', 'paz_m/s/s']
        csvWriter = csv.DictWriter(newFile, fieldnames=headerItem)
        csvWriter.writeheader()

        updatedDicts = fillEmptyDict(True, leftAnkle, rightAnkle, pelvis, maximalLimit)
        leftAnkleUpdated = updatedDicts[0]
        rightAnkleUpdated = updatedDicts[1]
        pelvisUpdated = updatedDicts[2]

        getCSVRows(csvWriter, accelerometer, leftAnkleUpdated, rightAnkleUpdated, pelvisUpdated, maximalLimit)
    
    #Otherwise, use the gyroscope formatting.
    else:
        newFile = open(saveLocation + '\\' + participant +'-gyro-combined.csv' , mode = 'w', newline = '')
        headerItem = ['lgx_deg/s', 'lgy_deg/s', 'lgz_deg/s','rgx_deg/s', 'rgy_deg/s', 'rgz_deg/s', 'pgx_deg/s', 'pgy_deg/s', 'pgz_deg/s']
        csvWriter = csv.DictWriter(newFile, fieldnames = headerItem)
        csvWriter.writeheader()

        updatedDicts = fillEmptyDict(False, leftAnkle, rightAnkle, pelvis, maximalLimit)
        leftAnkle = updatedDicts[0]
        rightAnkle = updatedDicts[1]
        pelvis = updatedDicts[2]
        
        getCSVRows(csvWriter, accelerometer, leftAnkle, rightAnkle, pelvis, maximalLimit)

#=====================================================
#CHAPTER: Functions implemented for extracting relevant movement datum related to the key phases/events of the movement.
#=====================================================
# A function implementing the selected logic for locating initial contact within the ankle datum.
#
# fileDict:         The current ankle file (left or right) that the function is using.
# startIndex:       The starting point within the dictionary to process from.
# sensitivity:      The threshold value or sensitivity to noise.
def getInitialContact(fileDict, startIndex, sensitivity):
        #Starting from the start index and working toward the end of the file.
        loopCounter = startIndex
        check = False
        maxIndex = len(fileDict)

        #While we are within the range of the dictionary...
        while loopCounter < maxIndex and loopCounter >= startIndex:
            
            #Extract the z-axis acceleration at the given index.
            current = float(fileDict[loopCounter]['az_m/s/s'])

            #If we have found the main peak, we now want to process backward to the start of the peak.
            #Therefore, the loop counter is incremented backward until a new threshold (15m/s/s) is surpassed.
            if check:
                current = float(fileDict[loopCounter]['az_m/s/s'])
                if current < 15:
                    #Return the index value, and the timestamp of initial contact.
                    return [loopCounter+1, int(fileDict[loopCounter+1]['unix_timestamp_microsec'])]
                loopCounter -= 1

            #Otherwise, keep looking for the peak and enable check when it is found.
            elif (current > sensitivity):
                check = True
            else:
                loopCounter += 1

#=====================================================
# The function implemented for processing a pelvis file to locate a take-off point.
#
# pelvisAccDict:               The dictionary containing pelvis-related sensor datum.
# initialContactTimestamp:  The timestamp found in the ankle datum where initial contact takes place.
#---------------------------------------------
def getInitialTakeOff(pelvisAccDict, initialContactTimestamp):
    #Find the ankle initial contact index within the pelvis data, and subtract 300 (to speed up processing)
    counter = getClosestTimestampIndex(pelvisAccDict, initialContactTimestamp) - 300
    currentMin = 0

    #While the counter has not reached the start of the dictionary...
    while counter != 0:
        #Check whether our current point is the new minimum.
        current = float(pelvisAccDict[counter]['ay_m/s/s'])
        if current < currentMin:
            currentMin = current
            currentMinIndex = counter
        counter -= 1

    #Once a minimum is found, use this as a starting point for finding the beginning point.
    counter = currentMinIndex
    current = float(pelvisAccDict[counter]['ay_m/s/s'])

    #Loop until the current y-axis acceleration surpasses a -10m/s/s threshold.
    while (current < -10):
        counter -= 1
        current = float(pelvisAccDict[counter]['ay_m/s/s'])

    #Return the index, and the relevant timestamp of the take-off point together.
    return [counter + 1, int(pelvisAccDict[counter+1]['unix_timestamp_microsec'])]

#=====================================================
# A helper function used for finding a minimum or maximum point in a selected axis for maximum knee flexion.
# A majority of the functionality is duplicated from initial take-off extraction, but maximum knee flexion requires a timeout.
#
# minimumCheck:         Boolean value on whether this function is checking for a maximum or minimum point.
# pelvisAccDict:           The dictionary containing relevant pelvis sensor datum.
# counter:              The counter value from the main function to use as a starting index.
# axis:                 The axis label from the pelvis dictionary that we want to evaluate.
def detectionMaxMin(minimumCheck, pelvisAccDict, counter, axis):
    #Set timeout to 0 and get starting values.
    timeoutCounter = 0
    detectedValue = float(pelvisAccDict[counter][axis])
    detectedValueIndex = counter

    #Loop through the pelvis dictionary from the passed in index until a minimum is found.
    #The loop will break once there has been no new detected value in 50 rows of data.
    while timeoutCounter != 50:
        curr = float(pelvisAccDict[counter][axis])
        
        #If the minimum or maximum is detected, set the new values.
        if (minimumCheck and curr < detectedValue) or (not minimumCheck and curr > detectedValue):
            detectedValue = curr
            detectedValueIndex = counter
            timeoutCounter = 0
        else:
            timeoutCounter += 1
        counter -= 1
    
    #Return the index back to the main function.
    return detectedValueIndex
        
#=====================================================
# Main function for extracting a relative maximum knee flexion point from the available datum.
#
# pelvisAccDict:           The dictionary containing relevant pelvis sensor datum.
# initialContactIndex:  The point of initial contact provided by an ankle sensor.
# finalContactIndex:    The final index point to stop the loop if nothing has been detected.
def getMaximumKneeFlexion(pelvisAccDict, initialContactIndex, finalContactIndex):
    #Set boolean values depending on which step of detection the function is in.
    detectionStep1 = False
    detectionStep2 = False
    detectionStep3 = False

    #Set up a counter from the initial contact index, but increased by 500 to step over the fluctuating movement datum upon landing.
    processCounter = initialContactIndex + 500

    #While our counter is within a feasible range...
    while processCounter >= initialContactIndex and processCounter <= finalContactIndex - 300:
        
        #Detection 3 relates to the final minimum in the y-axis of the pelvis.
        if detectionStep3:
            processCounter = detectionMaxMin(True, pelvisAccDict, processCounter, 'ay_m/s/s')
            detectionStep3 = False
            
            #Returning the relevant index point of maximum knee flexion, and it's corresponding timestamp.
            return [processCounter, pelvisAccDict[processCounter]['unix_timestamp_microsec']]
        
        #Detection 2 relates to the maximum 'spike' in the z-axis of the pelvis between first and last detection.
        elif detectionStep2:
            processCounter = detectionMaxMin(False, pelvisAccDict, processCounter, 'az_m/s/s')
            detectionStep2 = False
            detectionStep3 = True
        
        #Detection 1 relates to the minimum in the y-axis of the pelvis between first and last detection.
        elif detectionStep1:
            processCounter = detectionMaxMin(True, pelvisAccDict, processCounter, 'ay_m/s/s')
            detectionStep1 = False
            detectionStep2 = True

        #Otherwise, the first objective is to find a y-axis point past the selected threshold of 2m/s/s.
        else:
            curr = float(pelvisAccDict[processCounter]['ay_m/s/s'])
            if curr > 2 and not detectionStep1:
                detectionStep1 = True
            processCounter += 1
        
#=====================================================
#CHAPTER: Functions implemented for processing the outputs prior to writing them to a new file.
#=====================================================
# A function implemented purely for finding the initial contact timestamp that is the earlier timestamp for the pelvis segmentation.
#
# initialContactLeftAnkle:      The timestamp that was detected as initial contact from the left ankle datum.
# initialContactRightAnkle:     The timestamp that was detected as initial contact from the right ankle datum.
def getCorrectPelvisTimestamp(initialContactLeftAnkle, initialContactRightAnkle):
    if int(initialContactLeftAnkle[1]) > int(initialContactRightAnkle[1]):
        return int(initialContactRightAnkle[1])
    else:
        return int(initialContactLeftAnkle[1])

#=====================================================
# Function used for segmentaiton into the two relevant segments using the detected events from the pelvis.
#
# accelerometer:                Boolean value on whether the current file is an accelerometer or not.
# ankleDict:                    The current dictionary from an ankle to process for output.
# takeOff:                      The takeoff timestamp as detected from the pelvis datum.
# initialContact:               The initial contact timestamp detected individually for either the left or right ankle.
# kneeFlexion:                  The timestamp in relation to maximal knee flexion as detected from the pelvis datum.
def individualAnkleOutputs(accelerometer, ankleDict, takeOff, initialContact, kneeFlexion):
    #As the initial contact index is calculated from the accelerometer, we have to translate it if we have a gyroscope.
    if not accelerometer:
        initialContact = getClosestTimestampIndex(ankleDict, int(initialContact[1]))
    else:
        initialContact = int(initialContact[0])

    #Get the closest timestamp and index for slicing.
    takeOffTimestamp = getClosestTimestampIndex(ankleDict, int(takeOff))
    flexionTimestamp = getClosestTimestampIndex(ankleDict, int(kneeFlexion))
    #Slice the dictionaries to their relevant key phases.
    segment1 = cropFileDict(ankleDict, int(takeOffTimestamp), int(initialContact))
    segment2 = cropFileDict(ankleDict, int(initialContact), int(flexionTimestamp))

    #Return both segments.
    return [segment1, segment2]

#=====================================================
# Function used for processing all of the accelerometer or gyroscope files into their respective segments for output.
#
# accelerometer:                Boolean value on whether the current file is an accelerometer or not.
# participant:                  The unique identifier for each jump so the output file can be ordered correctly.
# leftAnkle:                    The full dictionary containing the movement datum of the left ankle sensor.
# rightAnkle:                   The full dictionary containing the movement datum of the right ankle sensor.
# pelvis:                       The full dictionary containing the movement datum of the pelvis sensor.
# takeOff:                      The take-off event detected from the pelvis datum.
# initialContactLeftAnkle:      The initial contact event detected in the left ankle datum.
# initialContactRightAnkle:     The initial contact event detected in the right ankle datum.
# kneeFlexion:                  The relative maximal knee flexion event detected from the pelvis datum.
def processSegmentsOutput(accelerometer, participant, leftAnkle, rightAnkle, pelvis, takeOff, initialContactLeftAnkle, initialContactRightAnkle, kneeFlexion):
    #Get the left and right ankle segments from the helper output function.
    leftSegments = individualAnkleOutputs(accelerometer, leftAnkle, takeOff[1], initialContactLeftAnkle, kneeFlexion[1])
    rightSegments = individualAnkleOutputs(accelerometer, rightAnkle, takeOff[1], initialContactRightAnkle, kneeFlexion[1])

    #For the pelvis datum, get the correct timestamps and get the closest index to this timestamp.
    closestPelvisStartTime = getCorrectPelvisTimestamp(initialContactLeftAnkle, initialContactRightAnkle)
    pelvisStartIndex = getClosestTimestampIndex(pelvis, closestPelvisStartTime)

    #Create two segments based on these detected indexes.
    pelvisSegment1 = cropFileDict(pelvis, int(takeOff[0]), pelvisStartIndex)
    pelvisSegment2 = cropFileDict(pelvis, pelvisStartIndex, int(kneeFlexion[0]))

    #Change the participant string to ensure no whitespace, based on the IMU naming conventions.
    participant = participant.replace(' ', '')

    #Write two new CSV files, one for segment1, and one for segment 2.
    if accelerometer:
        writeNewCSV(True, leftSegments[0], rightSegments[0], pelvisSegment1, participant + '-S1')
        writeNewCSV(True, leftSegments[1], rightSegments[1], pelvisSegment2, participant + '-S2')
    else:
        writeNewCSV(False, leftSegments[0], rightSegments[0], pelvisSegment1, participant + '-S1')
        writeNewCSV(False, leftSegments[1], rightSegments[1], pelvisSegment2, participant + '-S2')

    #Return these grouped segments back to the main function.
    return [leftSegments, rightSegments, [pelvisSegment1, pelvisSegment2]]

#=====================================================
#CHAPTER: Functions used for extracting or calculating statistical and temporal features.
#=====================================================
# Calculation of root mean square, related to a more weighted mean value of the data.
#
# fileDict:         The current dictionary being focused on.
# axis:             The axis of movement datum to be extracted from.
def rms(fileDict, axis):
    #Setting relevant starting variables.
    square = 0
    mean = 0.0
    root = 0.0
     
    #Calculate the square value of each value in the axis.
    for x in range(0, len(fileDict)):
        square += float(fileDict[x][axis]) ** 2
     
    #Calculate the mean of this square, based on the number of rows in the file.
    mean = square / (float) (len(fileDict))
     
    #Using the mean, get the square root value and return.
    root = math.sqrt(mean)
    return root

#=====================================================
# Function used for grouping together all the calculation or extraction of statistical features.
#
# featureStorage:           The dictionary of features to be added to.
# dictLabel:                The label of the dictionary to be used in the overall list for identification.
# fileDict:                 The current dictionary or sensor datum we want to extract features from.
# axis:                     The axis of movement datum to be extracted from.
#-----------------------------------------------
def statisticalFeatureList(featureStorage, dictLabel, fileDict, axis):
    #Extract all of the values into a list.
    values = []
    for x in range(0, len(fileDict)):
        values.append(float(fileDict[x][axis]))
    
    #Derive the selected features using a variety of libraries or functions and return.
    featureStorage[dictLabel + '_' + axis + '_rms'] = rms(fileDict, axis)
    featureStorage[dictLabel + '_' + axis + '_variance'] = np.var(values)
    featureStorage[dictLabel + '_' + axis + '_valueMean'] = statistics.mean(values)
    featureStorage[dictLabel + '_' + axis + '_stdDev'] = statistics.stdev(values)
    featureStorage[dictLabel + '_' + axis + '_maxima'] = max(values)
    featureStorage[dictLabel + '_' + axis + '_minima'] = min(values)
    return featureStorage

#=====================================================
# Function used for grouping together all the calculation and extraction of temporal features.
#
# featureStorage:               The dictionary of features to be added to.
# initialContactLeft:           The timestamp at which initial contact was detected in the left ankle.
# initialContactRight:          The timestamp at which initial contact was detected in the right ankle.
# takeOff:                      The timestamp at which take-off was detected in the pelvis.
# flexion:                      The timestamp at which maximal knee flexion was detected in the pelvis.
#-----------------------------------------------
def getTemporalFeatures(featureStorage, initialContactLeft, initialContactRight, takeOff, flexion):
    #Calculate the time taken between different events using microseconds and just subtracting the later event in the jump.
    featureStorage['takeOff_flight_time_left'] =    initialContactLeft - takeOff
    featureStorage['takeOff_flight_time_right'] =   initialContactRight - takeOff
    featureStorage['takeOff_time_to_flexion'] =     flexion - takeOff
    featureStorage['segment2_time_from_left'] =     flexion - initialContactLeft
    featureStorage['segment2_time_from_right'] =    flexion - initialContactRight
    return featureStorage

#=====================================================
#CHAPTER: Functions created for applying statistical and temporal feature extraction with relevant segments of data.
#=====================================================
# Process the entire list of features using the processed dictionaries for each sensor.
#
# segment:              The current segment ID that has called the function.
# lAnkleAcc             The left ankle accelerometer datum in a dictionary.
# rAnkleAcc             The right ankle accelerometer datum in a dictionary.
# pelvAcc               The pelvis accelerometer datum in a dictionary.
# lAnkleGyro            The left ankle gyroscope datum in a dictionary.
# rAnkleGyro            The right ankle gyroscope datum in a dictionary.
# pelvGyro              The pelvis gyroscope datum in a dictionary.
def processFeatureListFromDict(segment, lAnkleAcc, rAnkleAcc, pelvAcc, lAnkleGyro, rAnkleGyro, pelvGyro):
    #Set an empty dictionary.
    featureData = {}

    #All of these functions use featureData and add the statistical features to that dictionary.
    #These were stored in variables for error checking, but are unused throughout the main algorithm.
    leftAnkle = [statisticalFeatureList(featureData, segment + '_LANK', lAnkleAcc, 'ax_m/s/s')] + [statisticalFeatureList(featureData, segment + '_LANK', lAnkleAcc, 'ay_m/s/s')] + [statisticalFeatureList(featureData, segment + '_LANK', lAnkleAcc, 'az_m/s/s')] \
    + [statisticalFeatureList(featureData, segment + '_LANK', lAnkleGyro, 'gx_deg/s')] + [statisticalFeatureList(featureData, segment + '_LANK', lAnkleGyro, 'gy_deg/s')] + [statisticalFeatureList(featureData, segment + '_LANK', lAnkleGyro, 'gz_deg/s')]
    rightAnkle = [statisticalFeatureList(featureData, segment + '_RANK', rAnkleAcc, 'ax_m/s/s')] + [statisticalFeatureList(featureData, segment + '_RANK', rAnkleAcc, 'ay_m/s/s')] + [statisticalFeatureList(featureData, segment + '_RANK', rAnkleAcc, 'az_m/s/s')] \
    + [statisticalFeatureList(featureData, segment + '_RANK', rAnkleGyro, 'gx_deg/s')] + [statisticalFeatureList(featureData, segment + '_RANK', rAnkleGyro, 'gy_deg/s')] + [statisticalFeatureList(featureData, segment + '_RANK', rAnkleGyro, 'gz_deg/s')]
    pelvis = [statisticalFeatureList(featureData, segment + '_PELV', pelvAcc, 'ax_m/s/s')] + [statisticalFeatureList(featureData, segment + '_PELV', pelvAcc, 'ay_m/s/s')] + [statisticalFeatureList(featureData, segment + '_PELV', pelvAcc, 'az_m/s/s')] \
    + [statisticalFeatureList(featureData, segment + '_PELV', pelvGyro, 'gx_deg/s')] + [statisticalFeatureList(featureData, segment + '_PELV', pelvGyro, 'gy_deg/s')] + [statisticalFeatureList(featureData, segment + '_PELV', pelvGyro, 'gz_deg/s')]

    #Return the final featureData after adding all of the new statistical features.
    return featureData

#=====================================================
# Called when the output files are ready to be output to new CSV files.
#
# participant:                  The unique ID of the participant to be used for the output file names.
# leftAnkle:                    The list of left ankle sensor datum, [0] is the accelerometer, [1] is the gyroscope.
# rightAnkle:                   The list of right ankle sensor datum, [0] is the accelerometer, [1] is the gyroscope.
# pelvis                        The list of pelvis sensor datum, [0] is the accelerometer, [1] is the gyroscope.
# takeOff:                      The list of relevant data relating to the takeoff point in the pelvis, [0] is the index, [1] is the actual timestamp.
# initialContactLeftAnkle:      The list of relevant data relating to the initial contact in the left ankle, [0] is the index, [1] is the actual timestamp.
# initialContactRightAnkle:     The list of relevant data relating to the initial contact in the right ankle, [0] is the index, [1] is the actual timestamp.
# kneeFlexion:                  The list of relevant data relating to maximum knee flexion from the pelvis, [0] is the index, [1] is the actual timestamp.
def processOutputFiles(participant, leftAnkle, rightAnkle, pelvis, takeOff, initialContactLeftAnkle, initialContactRightAnkle, kneeFlexion):
    #Use the global scope featureList to add all features to.
    global featureList
    featureData = {}

    #Process the segments for both accelerometer and gyroscope files.
    segmentsAcc = processSegmentsOutput(True, participant, leftAnkle[0], rightAnkle[0], pelvis[0], takeOff, initialContactLeftAnkle, initialContactRightAnkle, kneeFlexion)
    segmentsGyro = processSegmentsOutput(False, participant, leftAnkle[1], rightAnkle[1], pelvis[1], takeOff, initialContactLeftAnkle, initialContactRightAnkle, kneeFlexion)
    
    #Extract and append the temporal features from the calculated timestamps in each key event to the feature list.
    temporalMeasures = getTemporalFeatures(featureData, initialContactLeftAnkle[1], initialContactRightAnkle[1], takeOff[1], int(kneeFlexion[1]))
    featureList.append(temporalMeasures)
    
    #Extract and append the statistical features from both segments one and two to the feature list.
    s1FeatureList = processFeatureListFromDict('S1', segmentsAcc[0][0], segmentsAcc[1][0], segmentsAcc[2][0], segmentsGyro[0][0], segmentsGyro[1][0], segmentsGyro[2][0])
    featureList.append(s1FeatureList)
    
    s2FeatureList = processFeatureListFromDict('S2', segmentsAcc[0][1], segmentsAcc[1][1], segmentsAcc[2][1], segmentsGyro[0][1], segmentsGyro[1][1], segmentsGyro[2][1])
    featureList.append(s2FeatureList)

#=====================================================
# The primary function for writing the entire feature list to a new CSV file that aligns with the same order as the written combined files.
def runFeatureListOutput():
    #Open a new file and create header items.
    featureCSV = open(saveLocation + '\\feature_list.csv', mode = 'w', newline = '')
    headerItem = []

    #Loop through the groups of features ([0] is temporal, [1] is S1 features, and [2] is S2 features)
    for x in range(0, 3):
        for value in featureList[x]:
            headerItem.append(value)
    
    csvWriter = csv.DictWriter(featureCSV, fieldnames = headerItem)
    csvWriter.writeheader()

    #Add the entire feature list into the created file.
    loopCounter = 0
    while loopCounter < len(featureList):
        outputRow = {}
        for x in range(0, 3):
            outputRow.update(featureList[loopCounter + x])
        loopCounter += 3
        csvWriter.writerow(outputRow)

#=====================================================
# The primary function for organising the calculation and extraction of key events from the IMU datum.
#
# person:               The array containing relevant CSV files related to one jump occurrence. The index of each filename is consistent between each group.
def runSegmentation(person):
    try:
        #In index 0, the participant ID string is stored for use in writing to the console and saving new updated segment files.
        participantId = str(person[0])
        print("")
        print("CURRENT PERSON: " + participantId)

        #Get the accelerometer filenames.
        leftAnkleFilename = str(person[1])
        rightAnkleFilename = str(person[3])
        pelvisFilename = str(person[5])

        #Convert these files into a dictionary.
        leftAccDict = getCSVDict(leftAnkleFilename)
        rightAccDict = getCSVDict(rightAnkleFilename)
        pelvisAccDict = getCSVDict(pelvisFilename)

        #Use these dictionaries to extract relevant key events using appropriate functions.
        initialContactLeftAnkle = getInitialContact(leftAccDict, 0, 60)
        initialContactRightAnkle = getInitialContact(rightAccDict, 0, 60)
        takeOff = getInitialTakeOff(pelvisAccDict, int(initialContactLeftAnkle[1]))
        #Since we aren't extracting final contact, use the cropped window size (which was 2000) and get a relative final index
        kneeFlexion = getMaximumKneeFlexion(pelvisAccDict, int(initialContactLeftAnkle[0]), len(pelvisAccDict) - 1500)

        #Replicate the same process for the gyroscope files.
        leftAnkleFilename = str(person[2])
        rightAnkleFilename = str(person[4])
        pelvisFilename = str(person[6])
        leftGyroDict = getCSVDict(leftAnkleFilename)
        rightGyroDict = getCSVDict(rightAnkleFilename)
        pelvisGyroDict = getCSVDict(pelvisFilename)

        #Process all of the key events and use the entire file dictionaries.
        processOutputFiles(participantId, [leftAccDict, leftGyroDict], [rightAccDict, rightGyroDict], [pelvisAccDict, pelvisGyroDict], takeOff, initialContactLeftAnkle, initialContactRightAnkle, kneeFlexion)
    
    except Exception as e:
        print(e)

#=====================================================
#CHAPTER: Main Running Function for Segmentation of the Movement Datum.
#=====================================================
print("Segmentation Process for IMU LESS Data")
print("--------------------------------------")

#Get current working directory for path
currentDirectory = Path.cwd()

#=====================================================
# Process for creating a new directory using the specified save location.
# While folder input is invalid...
while(True):
    try:
        #Get the folder from the user, create the string using current directory and change to it.
        folder = input("Please input the folder you want to search through: ")
        processFolderName = str(currentDirectory) + "\\" + folder.strip()
        directory = os.fsencode(processFolderName)
        os.chdir(processFolderName)

        #Make a new folder so the names of the file can stay the same.
        exists = os.path.exists(saveLocation)
        if not exists:
            os.makedirs(saveLocation)
            print("The new directory is created!")
        break
    except:
        print("Directory produced an error. Please try again.")

#=====================================================
# Initialising variables for correct set up of the array. Ordering of the following algorithm is done by the naming conventions of each IMU data file.
# Index values are as follows:
# Group[0]: Participant identifier.
# Group[1]: Left Ankle Accelerometer.
# Group[2]: Left Ankle Gyroscope.
# Group[3]: Right Ankle Accelerometer.
# Group[4]: Right Ankle Gyroscope.
# Group[5]: Pelvis Accelerometer.
# Group[6]: Pelvis Gyroscope.
enabledSegmentation = False
currentPerson = [0] * 7
currentPerson[0] = "null"
pelvisIndex = 0
rightAnkleIndex = 0
leftAnkleIndex= 0

leftAnkleId = "TS-04223"
rightAnkleId = "TS-04204"
pelvisId = "TS-04205"

#=====================================================
#For every file in the current directory...
for file in os.listdir(directory):
        #Get the filename and only segment with the correct .csv files
        filename = os.fsdecode(file)
        if filename.endswith("highg.csv") or filename.endswith("lowg.csv"):
            print("Segmentation using: " + filename)

            try:
                #Split filename to get ID of the current jump.
                id = filename.split("_")
                 
                #If the segmentation is not enabled yet, establish this file as the starting person using their ID.
                if (not enabledSegmentation):
                    currentPerson[0] = id[0]
                    
                #If we get to a file with a new ID, apply segmentation to current person then make a new person/group to focus on.
                if (id[0] != currentPerson[0]):
                    runSegmentation(currentPerson)
                    currentPerson = [0] * 7
                    currentPerson[0] = id[0]
                    pelvisIndex = 0
                    rightAnkleIndex = 0
                    leftAnkleIndex  = 0

                #Logic for implementing the filenames into the correct positions of the array.
                if (id[1] == leftAnkleId):
                    currentPerson[1 + leftAnkleIndex ] = filename
                    leftAnkleIndex += 1
                elif (id[1] == rightAnkleId):
                    currentPerson[3 + rightAnkleIndex] = filename
                    rightAnkleIndex += 1
                elif (id[1] == pelvisId):
                    currentPerson[5 + pelvisIndex] = filename
                    pelvisIndex += 1
                else:
                    print("ERROR: THIS PARTICIPANT ID DOES NOT MATCH EXPECTED VARIABLES: " + id[1])
                
                #Once we are here, we must have a jump to calculate with.
                enabledSegmentation = True
            except Exception as e:
                print(str(currentPerson[0]) + ': ' + str(e))
                break
        
runSegmentation(currentPerson)
runFeatureListOutput()
#=====================================================