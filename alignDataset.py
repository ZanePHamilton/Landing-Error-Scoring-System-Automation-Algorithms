#!"C:\Program Files\Python310"

# Import libraries that are used in the alignment process.
import copy
import csv
import os
from pathlib import Path

# Global variables for the IDs of the sensors, and the new directory 
# to create and save the aligned files to.
leftId = 'TS-04223'
rightId = 'TS-04204'
pelvisId = 'TS-04205'
saveLocation = 'alignedData'

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
# Write the aligned dictionary to a new CSV file based 
# on the consistent alignment axis selected.
# 
# filename:     The name of the file for saving the new file with.
# alignedDict:  The dictionary of newly aligned values.
# lowgFile:     Boolean value depicting the correct formatting for the header and writing rows.
def writeNewCSV(filename, alignedDict, lowgFile):
    #Create new file object
    newfile = open(saveLocation + '\\' + filename, mode='w', newline='')

    #Alter the header item depending if we need gyroscope values as well and write this to the new file.
    if lowgFile:
        header_item = ['unix_timestamp_microsec', 'ax_m/s/s', 'ay_m/s/s', 'az_m/s/s', 'gx_deg/s', 'gy_deg/s', 'gz_deg/s']
    else:
        header_item = ['unix_timestamp_microsec', 'ax_m/s/s', 'ay_m/s/s', 'az_m/s/s']
    csvwriter = csv.DictWriter(newfile, fieldnames=header_item)
    csvwriter.writeheader()

    #For every value in the new aligned dictionary, print the current row with required variables.
    for x in range(0, len(alignedDict)):
        if lowgFile:
            current_row = {'unix_timestamp_microsec':alignedDict[x]['unix_timestamp_microsec'],
                           'gx_deg/s':alignedDict[x]['gx_deg/s'], 'gy_deg/s':alignedDict[x]['gy_deg/s'], 'gz_deg/s':alignedDict[x]['gz_deg/s']}
        else:
            current_row = {'unix_timestamp_microsec':alignedDict[x]['unix_timestamp_microsec'], 'ax_m/s/s':alignedDict[x]['ax_m/s/s'], 'ay_m/s/s':alignedDict[x]['ay_m/s/s'], 'az_m/s/s':alignedDict[x]['az_m/s/s']}
        csvwriter.writerow(current_row)

#=====================================================
# A function for applying the logic required for correctly aligning the axes to a consistent axis.
#
# filename:     The name of the file currently being aligned.
def runAlignment(filename):
    
    #Return a dictionary of the CSV file datum.
    data = getCSVDict(filename)
    aligned = copy.deepcopy(data)

    #Evaluate whether the current file is a HighG or LowG file.
    split_file = filename.split("_")
    gyroscopeInc = split_file[3] == 'lowg.csv'

    #Following code alters the old dictionary to new alignment.
    #If it is the left ankle, perform the following:
    # X = Z inversed
    # Y = Y
    # Z = X inversed
    if (split_file[1] == leftId):
        for x in range(0, len(aligned)):
            if gyroscopeInc:
                current = float(data[x]['gz_deg/s'])
                current = current * -1
                aligned[x]['gx_deg/s'] = current

                current = float(data[x]['gx_deg/s'])
                current = current * -1
                aligned[x]['gz_deg/s'] = current
            else:
                current = float(data[x]['az_m/s/s'])
                current = current * -1
                aligned[x]['ax_m/s/s'] = current

                current = float(data[x]['ax_m/s/s'])
                current = current * -1
                aligned[x]['az_m/s/s'] = current

    #If it is the right ankle, perform the following:
    # X = Z
    # Y = Y
    # Z = X
    elif (split_file[1] == rightId):
        for x in range(0, len(aligned)):
            if gyroscopeInc:
                current = float(data[x]['gz_deg/s'])
                aligned[x]['gx_deg/s'] = current

                current = float(data[x]['gx_deg/s'])
                aligned[x]['gz_deg/s'] = current
            else:
                current = float(data[x]['az_m/s/s'])
                aligned[x]['ax_m/s/s'] = current

                current = float(data[x]['ax_m/s/s'])
                aligned[x]['az_m/s/s'] = current

    #If it is the left ankle, perform the following:
    # X = Y inversed
    # Y = X inversed
    # Z = Z inversed
    elif (split_file[1] == pelvisId):
        for x in range(0, len(aligned)):
            if gyroscopeInc:
                current = float(data[x]['gy_deg/s'])
                current = current * -1
                aligned[x]['gx_deg/s'] = current

                current = float(data[x]['gx_deg/s'])
                current = current * -1
                aligned[x]['gy_deg/s'] = current

                current = float(data[x]['gz_deg/s'])
                current = current * -1
                aligned[x]['gz_deg/s'] = current

            else:
                current = float(data[x]['ay_m/s/s'])
                current = current * -1
                aligned[x]['ax_m/s/s'] = current

                current = float(data[x]['ax_m/s/s'])
                current = current * -1
                aligned[x]['ay_m/s/s'] = current

                current = float(data[x]['az_m/s/s'])
                current = current * -1
                aligned[x]['az_m/s/s'] = current
               
    #If it is another file that has reached here, return out of the function.
    else:
        return
    
    #Write the new CSV file with the newly aligned dictionary.
    writeNewCSV(filename, aligned, gyroscopeInc)

#=====================================================
#CHAPTER: Main Running Function of the Alignment.
#=====================================================
print("Axes Alignment for IMU Data")
print("------------------------------")

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
        break
    except Exception as e:
        print(e)

#For every file in the current directory...
for file in os.listdir(directory):
        #Get the current filename in a directory.
        filename = os.fsdecode(file)

        #If the current file is a HighG or LowG file, run the alignment.
        if filename.endswith("highg.csv") or filename.endswith("lowg.csv"):
            runAlignment(filename)
            print("Aligning: " + filename)
#=====================================================