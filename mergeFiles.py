#!"C:\Program Files\Python310"

# Import libraries that are used in the dividing process.
import csv
import os
from pathlib import Path

# Global variables for the save location.
saveLocation = 'S2-Pelvis'
identifier = saveLocation.split('-')
segmentSubset = identifier[0]
sensorSubset = identifier[1]

#=====================================================
# Get the dictionary representation of a CSV file.
#
# filename:             The name of the file to read and return.
def getCSVDict(filename):
    csvFile = open(filename)
    csvReader = csv.DictReader(csvFile)
    return[row for row in csvReader]

#=====================================================
# Merge the two segments into one dictionary.
#
# segment1:         The dictionary with movement datum related to segment 1.
# segment2:         The dictionary with movement datum related to segment 2.
def mergeSegmentDicts(segment1, segment2):
    fullDataset = segment1 + segment2
    return fullDataset

#=====================================================
# Function for writing the new combined files of accelerometer and gyroscope datum between segment 1 and 2.
#
# participant:      The unique identifier of a jump.
# fileDict:         The dictionary containing sensor datum for both segments.
# accelerometer:    The Boolean value depicting whether the current file is an accelerometer or gyroscope.
def writerLoop(participant, fileDict, accelerometer):
    #Get the correct header items and write these to the new file.
    if accelerometer:
        newFile = open(saveLocation + '\\' + participant +'-acc-combined.csv' , mode = 'w', newline = '')
        if sensorSubset == 'Pelvis':
            headerItem = ['pax_m/s/s', 'pay_m/s/s', 'paz_m/s/s']
        elif sensorSubset == 'Ankles':
            headerItem = ['lax_m/s/s', 'lay_m/s/s', 'laz_m/s/s', 'rax_m/s/s', 'ray_m/s/s', 'raz_m/s/s']
        else:
            headerItem = ['lax_m/s/s', 'lay_m/s/s', 'laz_m/s/s', 'rax_m/s/s', 'ray_m/s/s', 'raz_m/s/s', 'pax_m/s/s', 'pay_m/s/s', 'paz_m/s/s']
    else:
        newFile = open(saveLocation + '\\' + participant +'-gyro-combined.csv' , mode = 'w', newline = '')
        if sensorSubset == 'Pelvis':
            headerItem = ['pgx_deg/s', 'pgy_deg/s', 'pgz_deg/s']
        elif sensorSubset == 'Ankles':
            headerItem = ['lgx_deg/s', 'lgy_deg/s', 'lgz_deg/s', 'rgx_deg/s', 'rgy_deg/s', 'rgz_deg/s']
        else:
            headerItem = ['lgx_deg/s', 'lgy_deg/s', 'lgz_deg/s', 'rgx_deg/s', 'rgy_deg/s', 'rgz_deg/s', 'pgx_deg/s', 'pgy_deg/s', 'pgz_deg/s']

    csvWriter = csv.DictWriter(newFile, fieldnames = headerItem)
    csvWriter.writeheader()
 
    #Set a list for storing the columns of data.
    columns = []

    #For each item within the headerItem...
    for item in headerItem:
        #Set up variables for correctly adding all the items to a list.
        currColumn = [item]
        rowIndex = 0

        #While the row index is less than the length of the current file...
        while rowIndex < len(fileDict):
            #Get the value from the file dictionary.
            currentValue = fileDict[rowIndex][item]

            #If the value is not an integer representation of -1. append to the current column list.
            if currentValue != '-1':
                currColumn.append(currentValue)
            
            #Add 1 to the row index.
            rowIndex += 1
        #Append the final column to our columns list.
        columns.append(currColumn)

    #Get the maximum index from the columns (between left and right ankle, and pelvis)
    if sensorSubset == 'Pelvis':
        max_index = len(columns[0])
    elif sensorSubset == 'Ankles':
        max_index = max([len(columns[0]), len(columns[3])])
    else:
        max_index = max([len(columns[0]), len(columns[3]), len(columns[6])])

    #For all the columns, now we fill the new merged segments with -1 as the dataset must still be the same length.
    for column in columns:
        for x in range(len(column), max_index):
            column.append('-1')
    
    #Now with additional rows, use a list to store dictionary entries of an entire row of data.
    rows = []
    for x in range(1, max_index):
        currentRow = {}
        for column in columns:
            currentRow[column[0]] = column[x]
        rows.append(currentRow)

    #For each row in the found rows, write this to the new file.
    for row in rows:
        csvWriter.writerow(row)

#=====================================================
# A function purely for the S1A2 merging and organising in a new directory.
#
# accS1:                A list of the filenames relevant to accelerometer data in segment 1.
# accS2:                A list of the filenames relevant to accelerometer data in segment 2.
# gyroS1:               A list of the filenames relevant to gyroscope data in segment 1.
# gyroS2:               A list of the filenames relevant to gyroscope data in segment 2.
def runFinalSegmentMerge(accS1, accS2, gyroS1, gyroS2):
    #For all of the filenames we have in accData...
    for accData in range(0, len(accS1)):
        #Get the file dictionaries from the filenames found.
        fileDictS1 = getCSVDict(accS1[accData])
        fileDictS2 = getCSVDict(accS2[accData])

        #Merge the two dictionaries using the correct logic.
        merged = mergeSegmentDicts(fileDictS1, fileDictS2)

        #Split the filename by a dash.
        data = accS1[accData].split('-')
        
        #Write the new accelerometer file with correct participant ID.
        writerLoop(data[0] + '-' + data[1], merged, True)

    #Replicate the same process as the Accelerometer datum, but now with the gyroscope.
    for gyroData in range(0, len(gyroS1)):
        fileDictS1 = getCSVDict(gyroS1[gyroData])
        fileDictS2 = getCSVDict(gyroS2[gyroData])
        merged = mergeSegmentDicts(fileDictS1, fileDictS2)
        data = gyroS1[gyroData].split('-')
        writerLoop(data[0] + '-' + data[1], merged, False)

#=====================================================
# A function used for subsetting the raw datum into subsets, primarily involving the sensor subset and called when the current subset is S2. 
#
# filename:                 Current filename we are focused on.
# accelerometer:            Boolean value depicting whether the current file is an accelerometer or not.
def subsetRawData(filename, accelerometer):
    #Get the dictionary and open a new file to write to.
    fileDict = getCSVDict(filename)
    newfile = open(saveLocation + '\\' + filename, mode='w', newline='')

    #Logic required using the sensor subset for the correct headers.
    if accelerometer:
        if sensorSubset == 'Pelvis':
            headerItem = ['pax_m/s/s', 'pay_m/s/s', 'paz_m/s/s']
        elif sensorSubset == 'Ankles':
            headerItem = ['lax_m/s/s', 'lay_m/s/s', 'laz_m/s/s', 'rax_m/s/s', 'ray_m/s/s', 'raz_m/s/s']
        else:
            headerItem = ['lax_m/s/s', 'lay_m/s/s', 'laz_m/s/s', 'rax_m/s/s', 'ray_m/s/s', 'raz_m/s/s', 'pax_m/s/s', 'pay_m/s/s', 'paz_m/s/s']
    else:
        if sensorSubset == 'Pelvis':
            headerItem = ['pgx_deg/s', 'pgy_deg/s', 'pgz_deg/s']
        elif sensorSubset == 'Ankles':
            headerItem = ['lgx_deg/s', 'lgy_deg/s', 'lgz_deg/s', 'rgx_deg/s', 'rgy_deg/s', 'rgz_deg/s']
        else:
            headerItem = ['lgx_deg/s', 'lgy_deg/s', 'lgz_deg/s', 'rgx_deg/s', 'rgy_deg/s', 'rgz_deg/s', 'pgx_deg/s', 'pgy_deg/s', 'pgz_deg/s']
    
    #Write the correct header to the new file.
    csvwriter = csv.DictWriter(newfile, fieldnames = headerItem)
    csvwriter.writeheader()

    #With similar logic to the previous loop, write the correct rows to the new file.
    for x in range(0, len(fileDict)):
        if accelerometer:
            if sensorSubset == 'Pelvis':
                if fileDict[x]['pax_m/s/s'] == '-1' and fileDict[x]['pay_m/s/s'] == '-1' and fileDict[x]['paz_m/s/s'] == '-1':
                    break
                else:
                    currentRow = {'pax_m/s/s':fileDict[x]['pax_m/s/s'], 'pay_m/s/s':fileDict[x]['pay_m/s/s'], 'paz_m/s/s':fileDict[x]['paz_m/s/s']}
            elif sensorSubset == 'Ankles':
                if fileDict[x]['lax_m/s/s'] == '-1' and fileDict[x]['lay_m/s/s'] == '-1' and fileDict[x]['laz_m/s/s'] == '-1' and fileDict[x]['rax_m/s/s'] == '-1' and fileDict[x]['ray_m/s/s'] == '-1' and fileDict[x]['raz_m/s/s'] == '-1':
                    break
                else:
                    currentRow = {'lax_m/s/s':fileDict[x]['lax_m/s/s'], 'lay_m/s/s':fileDict[x]['lay_m/s/s'], 'laz_m/s/s':fileDict[x]['laz_m/s/s'], 'rax_m/s/s':fileDict[x]['rax_m/s/s'], 'ray_m/s/s':fileDict[x]['ray_m/s/s'], 'raz_m/s/s':fileDict[x]['raz_m/s/s']}
            else:
                currentRow = {'lax_m/s/s':fileDict[x]['lax_m/s/s'], 'lay_m/s/s':fileDict[x]['lay_m/s/s'], 'laz_m/s/s':fileDict[x]['laz_m/s/s'], 'rax_m/s/s':fileDict[x]['rax_m/s/s'], 'ray_m/s/s':fileDict[x]['ray_m/s/s'], 'raz_m/s/s':fileDict[x]['raz_m/s/s'], 'pax_m/s/s':fileDict[x]['pax_m/s/s'], 'pay_m/s/s':fileDict[x]['pay_m/s/s'], 'paz_m/s/s':fileDict[x]['paz_m/s/s']}

        else:
            if sensorSubset == 'Pelvis':
                if fileDict[x]['pgx_deg/s'] == '-1' and fileDict[x]['pgy_deg/s'] == '-1' and fileDict[x]['pgz_deg/s'] == '-1':
                    break
                else:
                    currentRow = {'pgx_deg/s':fileDict[x]['pgx_deg/s'], 'pgy_deg/s':fileDict[x]['pgy_deg/s'], 'pgz_deg/s':fileDict[x]['pgz_deg/s']}
            elif sensorSubset == 'Ankles':
                if fileDict[x]['lgx_deg/s'] == '-1' and fileDict[x]['lgy_deg/s'] == '-1' and fileDict[x]['lgz_deg/s'] == '-1' and fileDict[x]['rgx_deg/s'] == '-1' and fileDict[x]['rgy_deg/s'] == '-1' and fileDict[x]['rgz_deg/s'] == '-1':
                    break
                else:
                    currentRow = {'lgx_deg/s':fileDict[x]['lgx_deg/s'], 'lgy_deg/s':fileDict[x]['lgy_deg/s'], 'lgz_deg/s':fileDict[x]['lgz_deg/s'], 'rgx_deg/s':fileDict[x]['rgx_deg/s'], 'rgy_deg/s':fileDict[x]['rgy_deg/s'], 'rgz_deg/s':fileDict[x]['rgz_deg/s']}
            else:
                currentRow = {'lgx_deg/s':fileDict[x]['lgx_deg/s'], 'lgy_deg/s':fileDict[x]['lgy_deg/s'], 'lgz_deg/s':fileDict[x]['lgz_deg/s'], 'rgx_deg/s':fileDict[x]['rgx_deg/s'], 'rgy_deg/s':fileDict[x]['rgy_deg/s'], 'rgz_deg/s':fileDict[x]['rgz_deg/s'], 'pgx_deg/s':fileDict[x]['pgx_deg/s'], 'pgy_deg/s':fileDict[x]['pgy_deg/s'], 'pgz_deg/s':fileDict[x]['pgz_deg/s']}

        csvwriter.writerow(currentRow)
    newfile.close()

#=====================================================
# Function for taking the entire dataset with All segments of data, and subsetting it depending on which subset we are focused on.
#
# filename:             The name of the file to read and return.
def subsetFeatureData(filename):
    #Get the dictionary of the filename and create a new file of the subsetted information.
    fileDict = getCSVDict(filename)
    newFile = open(saveLocation + '\\' + filename, mode = 'w', newline = '')
    headerItem = []

    #Using the save location naming conventions, find the current subset.
    identifier = saveLocation.split('-')
    segmentSubset = identifier[0]
    sensorSubset = identifier[1]

    #Depending on which line is uncommented, gives us a different subset of feature data.
    for value in fileDict[0]:
        if (sensorSubset == 'Ankles'):
            if segmentSubset == 'S1A2':
                if 'time' in value or 'S1_LANK' in value or 'S2_LANK' in value or 'S1_RANK' in value or 'S2_RANK' in value:
                    headerItem.append(value)
            else:
                if 'time' in value or 'S2_LANK' in value or 'S2_RANK' in value:
                    headerItem.append(value)
        elif (sensorSubset == 'Pelvis'):
            if segmentSubset == 'S1A2':
                if 'time' in value or 'S1_PELV' in value or 'S2_PELV' in value:
                    headerItem.append(value)
            else:
                if 'time' in value or 'S2_PELV' in value:
                    headerItem.append(value)
        elif (sensorSubset == 'All'):
            if segmentSubset == 'S1A2':
                if 'time' in value or 'S1_LANK' in value or 'S2_LANK' in value or 'S1_RANK' in value or 'S2_RANK' in value or 'S1_PELV' in value or 'S2_PELV' in value:
                    headerItem.append(value)
            else:
                if 'time' in value or 'S2_LANK' in value or 'S2_RANK' in value or 'S2_PELV' in value:
                    headerItem.append(value)
        
    csvWriter = csv.DictWriter(newFile, fieldnames = headerItem)
    csvWriter.writeheader()

    #Replicating the same logic as the header, write the relevant features to the new file.
    for x in range(0, len(fileDict)):
        currentRow = {}
        for value in fileDict[x]:
            if (sensorSubset == 'Ankles'):
                if segmentSubset == 'S1A2':
                    if 'time' in value or 'S1_LANK' in value or 'S2_LANK' in value or 'S1_RANK' in value or 'S2_RANK' in value:
                        currentRow[value] = fileDict[x][value]
                else:
                    if 'time' in value or 'S2_LANK' in value or 'S2_RANK' in value:
                        currentRow[value] = fileDict[x][value]
            elif (sensorSubset == 'Pelvis'):
                if segmentSubset == 'S1A2':
                    if 'time' in value or 'S1_PELV' in value or 'S2_PELV' in value:
                        currentRow[value] = fileDict[x][value]
                else:
                    if 'time' in value or 'S2_PELV' in value:
                        currentRow[value] = fileDict[x][value]
            elif (sensorSubset == 'All'):
                if segmentSubset == 'S1A2':
                    if 'time' in value or 'S1_LANK' in value or 'S2_LANK' in value or 'S1_RANK' in value or 'S2_RANK' in value or 'S1_PELV' in value or 'S2_PELV' in value:
                        currentRow[value] = fileDict[x][value]
                else:
                    if 'time' in value or 'S2_LANK' in value or 'S2_RANK' in value or 'S2_PELV' in value:
                        currentRow[value] = fileDict[x][value]
        #Write the correct row to the new file.
        csvWriter.writerow(currentRow)

#=====================================================
#CHAPTER: Main Running Function for Dividing of the Full Dataset.
#=====================================================
print("Dividing Segments of IMU LESS Data")
print("----------------------------------")

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
# Variables required for adding the segments into a list to be merged.
accS1 = []
accS2 = []
gyroS1 = []
gyroS2 = []

#For every file in the current directory...
for file in os.listdir(directory):
    #Get the filename and only crop with the correct data files.
    filename = os.fsdecode(file)
    if filename.endswith('feature_list.csv'):
        subsetFeatureData(filename)
    elif segmentSubset == 'S1A2':
        if filename.endswith('S1-acc-combined.csv'):
            accS1.append(filename)
        elif filename.endswith('S1-gyro-combined.csv'):
            gyroS1.append(filename)
        elif filename.endswith('S2-acc-combined.csv'):
            accS2.append(filename)
        elif filename.endswith('S2-gyro-combined.csv'):
            gyroS2.append(filename)

    elif segmentSubset == 'S2':
        if filename.endswith('S2-acc-combined.csv'):
            subsetRawData(filename, True)
        elif filename.endswith('S2-gyro-combined.csv'):
            subsetRawData(filename, False)
    else:
        continue

if segmentSubset == 'S1A2':
    runFinalSegmentMerge(accS1, accS2, gyroS1, gyroS2)
#=====================================================