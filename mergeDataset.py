#!"C:\Program Files\Python310"

# Import libraries that are used in the merging process.
import csv
import os
import numpy as np
from pathlib import Path
import pandas as pd

# Global variable for the directory to be created, and the list of flattened values.
saveLocation = 'merged'
flattenedDataset = []
subsetInput = ""

#=====================================================
#CHAPTER: Functions implemented for aligning the values correctly.
#=====================================================
# Get the dictionary representation of a CSV file.
#
# filename: The name of the file to read and return.
def getCSVDict(filename):
    csvFile = open(filename)
    csvreader = csv.DictReader(csvFile)
    return[row for row in csvreader]

#=====================================================

def runMerge():
    #Setting up method-scope values for getting the maximum lengths of both the accelerometer, and gyroscope datum.
    maxAcc = 0
    maxGyro = 0

    #Open the CSV file containing the scores as given by the user, and store this in a dictionary.
    scoreCSV = open('scores_subject.csv', mode='r', newline='')
    featureRows = getCSVDict('feature_list.csv')

    #Create a new file for writing the entire dataset to.
    newCombinedFile = open(saveLocation + '\\f' + subsetInput + '.csv', mode = 'w', newline = '')

    #Hard-coded header item.
    headerItem = ['Name','ID','Mass','Height','BMI','Age','Sex','Foot','Injury','Past_Injury','JUMP', 'SCORE1', 'SCORE2', 'SCORE3', 'SCORE4', 'SCORE5', 'SCORE6', 'SCORE7', 'SCORE8', 'SCORE9', 'SCORE10', 'SCORE11', 'SCORE12', 'SCORE13', 'SCORE14', 'SCORE15', 'SCORE16', 'SCORE17', 'TOTAL']
    first = True

    #For each specified header we want to include, write this to the first row of the new CSV file.
    for header in headerItem:
        #If it's the first value (Name), write without a comma.
        if first:
            newCombinedFile.write(header)
            first = False
        else:
            newCombinedFile.write(',' + header)

    #Loop through the entirety of the flattened dataset, and find the maximum length of both accelerometer and gyroscope flattened datasets.
    for x in range(0, len(flattenedDataset)):
        
        #Accelerometer data is on every even row, while gyroscope datum is on the odd rows.
        if x % 2 == 0:
            if len(flattenedDataset[x]) > maxAcc:
                maxAcc = len(flattenedDataset[x])
        else:
            if len(flattenedDataset[x]) > maxGyro:
                maxGyro = len(flattenedDataset[x])
    
    #Now with the maximum accelerometer and gyroscope values found, fill all other rows with -1 to make all rows of balanced length.
    for x in range(0, len(flattenedDataset)):

        #Depending on the datum type, create -1 values to be inserted altogether.
        if x % 2 == 0:
            insertArray = [-1] * (maxAcc - len(flattenedDataset[x]))
        else:
            insertArray = [-1] * (maxGyro - len(flattenedDataset[x]))
        
        #Append the inserted array to each row.
        flattenedDataset[x] = np.append(flattenedDataset[x], insertArray)

    # For all the header items (features) in this dataset, write this to the header as well.
    for item in featureRows[0]:
        newCombinedFile.write(',' + str(item))

    #For both the accelerometer and gyroscope data, write a number of header items.
    for x in range(0, maxAcc):
        newCombinedFile.write(',' + 'acc-point-' + str(x))
    for y in range(0, maxGyro):
        newCombinedFile.write(',' + 'gyro-point-' + str(y))
    newCombinedFile.write('\n')

    #Move to the next row of the CSV file of all participant LESS scores.
    next(scoreCSV, None)

    #Initialise variables for correct output logic to avoid multiple nested loops.
    #dataCounter is for tracking the rows in the flattened dataset (2 rows per participant, 1 for accelerometer, 1 for gyroscope).
    #featureCounter is for tracking the current row in the rows of features.
    dataCounter = 0
    featureCounter = 0

    #For all the data in the scoring CSV file (ordered the same as our dataset)...
    for data in scoreCSV:
        #Strip the newline and return carriage characters out.
        outputRow = data.strip('\r\n')

        #For every feature item for this dataset, write this to the current row.
        for item in featureRows[featureCounter]:
            outputRow += ',' + str(featureRows[featureCounter][item])

        #Using dataCounter, add both the accelerometer and gyroscope data to the output row.
        for x in range(0, len(flattenedDataset[dataCounter])):
            outputRow += ',' + str(flattenedDataset[dataCounter][x])
        
        #Gyroscope datum is on the next row, so add one to the dataCounter to index this.
        dataCounter += 1
        for x in range(0, len(flattenedDataset[dataCounter])):
            outputRow += ',' + str(flattenedDataset[dataCounter][x])

        #Write the new output row to the new file, update the counters and write a newline.
        newCombinedFile.write(outputRow)
        dataCounter += 1
        featureCounter += 1
        newCombinedFile.write('\n')

    newCombinedFile.close()

#=====================================================
#CHAPTER: Main Running Function for Merging.
#=====================================================
print("Merging of the IMU Data and Scoring Items")
print("-----------------------------------------")

#Get current working directory for path.
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
        
        #Get subset to save the full dataset under the name of the current subset.
        subsetInput = str(directory).split('/')[-1].strip("'")
        break
    except Exception as e:
        print(e)

#For every file in the current directory...
for file in os.listdir(directory):
        #Get the current filename in a directory.
        filename = os.fsdecode(file)

        #If we find a filename with the correct identifier, flatten out the dataset. 
        if filename.endswith("gyro-combined.csv") or filename.endswith("acc-combined.csv"):
                print("Merging: " + filename)
                df = pd.read_csv(filename, header=0)
                values = df.values

                #Flatten ID 'C': Row-major order.
                val = values.flatten('C')
                flattenedDataset.append(val)

#Run the merge functionality with the program-scope variables.
runMerge()
#=====================================================