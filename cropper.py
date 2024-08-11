#!"C:\Program Files\Python310"

# Import libraries that are used for the initial cropping of the data window.
import csv
import os
from pathlib import Path

# Global variables for the start and end time of the crop window, 
# and the new directory  to create and save the aligned files to.
MAX_WINDOW_SIZE = 2000

startTime = 0
endTime = 0
saveLocation = 'croppedFiles'

#=====================================================
#CHAPTER: Functions implemented for aligning the values correctly.
#=====================================================
# Get the dictionary representation of a CSV file.
#
# filename:     The name of the file to read and return.
def getCSVDict(filename):
    csvFile = open(filename)
    csvreader = csv.DictReader(csvFile)
    return[row for row in csvreader]

#=====================================================
# Get the global start and end values within the current participant files.
#
# fileDict:     The dictionary containing data from an IMU file.
def getValues(fileDict):

    #Using global variables for processing.
    global startTime
    global endTime
    startTime = 0
    endTime = 0

    #Setting up a counter for the maximum size window, and a boolean check to evaluate whether we have found the final peak.
    finalPeakCounter = 0
    check = False

    try:
        #Looping through the entire dictionary of y-axis values.
        for x in range(0, len(fileDict)):
            yCurrent = float(fileDict[x]['ay_m/s/s'])

            #If we are checking for the final peak, keep incrementing our counter.
            if check:
                finalPeakCounter += 1

            #If the startTime has not been overwritten yet, and we have met our threshold...
            if startTime == 0 and yCurrent < -50:

                #Set the new start time and enable final peak check
                startTime = x
                check = True

            #Otherwise if the start time has been located, we have found another peak before the final peak.
            #Therefore, we overwrite endTime to the current peak and reset our window counter.
            elif yCurrent < -50:
                endTime = x
                finalPeakCounter = 0

            #If the window counter has reached the maximum window counter, break the loop as we have found our crop window.
            if finalPeakCounter == MAX_WINDOW_SIZE:
                check = False
                break
        
        #Using the written start and end times, set the +- window size timestamps.
        startTime = int(fileDict[startTime - MAX_WINDOW_SIZE]['unix_timestamp_microsec'])
        endTime = int(fileDict[endTime + MAX_WINDOW_SIZE]['unix_timestamp_microsec'])
    
    except Exception as e:
        print(e)

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
# Write a new CSV file based on the new start and end index values.
#
# filename:         The current file we are looking to crop and maintain the same name.
# newDict:          The newly cropped dictionary of the same file to now be written to the new directory.
def writeNewCSV(filename, newDict):
    
    #Setting variables depending on whether the file is an accelerometer or gyroscope data file.
    accelerometer = True
    if filename.endswith("lowg.csv"):
        accelerometer = False

    #Alter the header item depending if we need accelerometer or gyroscope headers.
    if accelerometer:
        headerItem = ['unix_timestamp_microsec', 'ax_m/s/s', 'ay_m/s/s', 'az_m/s/s']
    else:
        headerItem = ['unix_timestamp_microsec', 'gx_deg/s', 'gy_deg/s', 'gz_deg/s']

    #Create new file object with relevant header.
    newfile = open(saveLocation + '\\' + filename, mode = 'w', newline = '')
    csvwriter = csv.DictWriter(newfile, fieldnames = headerItem)
    csvwriter.writeheader()

    #For every value in the new aligned dictionary, write the current row to the new file using required index labels.
    for x in range(0, len(newDict)):
        if accelerometer:
            currentRow = {'unix_timestamp_microsec':newDict[x]['unix_timestamp_microsec'], 'ax_m/s/s':newDict[x]['ax_m/s/s'], 'ay_m/s/s':newDict[x]['ay_m/s/s'], 'az_m/s/s':newDict[x]['az_m/s/s']}
        else:
            currentRow = {'unix_timestamp_microsec':newDict[x]['unix_timestamp_microsec'], 'gx_deg/s':newDict[x]['gx_deg/s'], 'gy_deg/s':newDict[x]['gy_deg/s'], 'gz_deg/s':newDict[x]['gz_deg/s']}
        csvwriter.writerow(currentRow)

#=====================================================
# Required functionality for cropping an entire set of participant data, including all three sensors, and both the accelerometer and gyroscopes as well.
#
# group:            The initialised array of files for one jump occurence in a consistent order.
def runGroupCrop(group):

    #Using the global start and end time values that will be manipulated by getValues().
    global startTime
    global endTime

    #Using the filename at the 1st index of the group array (left ankle accelerometer).
    filename = str(group[1])

    #Get the dictionary of the file, and get the start and end timestamps for cropping from this file.
    fileDict = getCSVDict(filename)
    getValues(fileDict)

    #Loop through all the six files in the group.
    for x in range(1, 7):
        #Convert the filename to a string and get the relevant dictionary.
        filename = str(group[x])
        fileDict = getCSVDict(filename)

        #Get the closest timestamp in this specific file to the located start and end times.
        beginningIndex = getClosestTimestampIndex(fileDict, startTime)
        endingIndex = getClosestTimestampIndex(fileDict, endTime)

        #Slice the original file dictionary with the new index, and write a new cropped file using this slice.
        newDict = fileDict[beginningIndex:endingIndex]
        writeNewCSV(filename, newDict)

#=====================================================
#CHAPTER: Main Running Function of the Crop.
#=====================================================
print("Data Cropper for IMU LESS Data")
print("------------------------------")

#Get current working directory for path
currentDirectory = Path.cwd()

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

        #Make a new folder so the names of the file can stay the same without overwrite.
        exists = os.path.exists(saveLocation)
        if not exists:
            os.makedirs(saveLocation)
            print("The new directory is created!")
        break
    except Exception as e:
        print(e)

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
cropEnabled = False
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
        #Get the filename and only crop with the correct .csv files.
        filename = os.fsdecode(file)
        if filename.endswith("highg.csv") or filename.endswith("lowg.csv"):
        
            print("Cropping: " + filename)
            try:
                #Split filename to get ID of the current jump.
                id = filename.split("_")
                 
                #If the crop is not enabled yet, establish this file as the starting participant for the crop process.
                if (not cropEnabled):
                    currentPerson[0] = id[0]

                #If we get to a file with a new ID, apply cropping to current person then make a new person/group to focus on.
                if (id[0] != currentPerson[0]):
                    runGroupCrop(currentPerson)
                    currentPerson = [0] * 7
                    currentPerson[0] = id[0]
                    pelvisIndex = 0
                    rightAnkleIndex = 0
                    leftAnkleIndex = 0
                
                #Logic for implementing the filenames into the correct positions of the array.
                if (id[1] == leftAnkleId):
                    currentPerson[1 + leftAnkleIndex] = filename
                    leftAnkleIndex += 1

                elif (id[1] == rightAnkleId):
                    currentPerson[3 + rightAnkleIndex] = filename
                    rightAnkleIndex += 1

                elif (id[1] == pelvisId):
                    currentPerson[5 + pelvisIndex] = filename
                    pelvisIndex += 1
                else:
                    print("ERROR: THIS PARTICIPANT ID DOES NOT MATCH EXPECTED VARIABLES: " + id[1])
               
                #Once we are here, we must have a jump to crop.
                cropEnabled = True

            except Exception as e:
                print(e)
                break

#Once the loop finishes, call crop with the last remaining current person.
runGroupCrop(currentPerson)
#=====================================================