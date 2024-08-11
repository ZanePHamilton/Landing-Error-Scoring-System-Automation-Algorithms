#!"C:\Program Files\Python310"

# Import libraries that are used in the filtering process.
import csv
import os
from pathlib import Path
from scipy import signal

# Global variable for the directory to be created.
saveLocation = 'filtered'
    
#=====================================================
#CHAPTER: Functions implemented for filtering the files.
#=====================================================
# Write the filtered values of an accelerometer or gyroscope to a new CSV file.
#
# filename:         The name of the file to create and write new values to.
# accelerometer:    Boolean value, true when the current file is an accelerometer.
# timestamps:       The list of timestamps from the original file.
# xFiltered:        List of filtered acceleration datum from the x-axis.
# yFiltered:        List of filtered acceleration datum from the y-axis.
# zFiltered:        List of filtered acceleration datum from the z-axis.
def writeFilteredCSV(filename, accelerometer, timestamps, xFiltered, yFiltered, zFiltered):
    #Create a new file in the specified writer location.
    newfile = open(saveLocation + '\\' + filename , mode='w', newline='')

    #Evaluate the correct header format to write.
    if (accelerometer):
        header_item = ['unix_timestamp_microsec', 'ax_m/s/s', 'ay_m/s/s', 'az_m/s/s']
    else:
        header_item = ['unix_timestamp_microsec', 'gx_deg/s', 'gy_deg/s', 'gz_deg/s']
    
    csvwriter = csv.DictWriter(newfile, fieldnames=header_item)
    csvwriter.writeheader()

    #Write all of the updated rows to the new file.
    for x in range(0, len(timestamps)):
        newfile.write(str(timestamps[x]) + ',' + str(xFiltered[x]) + ',' + str(yFiltered[x]) + ',' + str(zFiltered[x]) + '\n')
    newfile.close()

#=====================================================
# A function for applying the logic required for using the Butterworth filter library on all axes of a file.
#
# filename:         The name of the file with sensor datum to be filtered.
def runFilter(filename):
    try:
        #Open the file in a reader object.
        csvfile = open(filename)
        csvreader = csv.DictReader(csvfile)
        
        #Setting up a default Butterworth filter for the accelerometer file (1600 Hz).
        sos = signal.butter(4, 100, 'lp', fs = 1600, output='sos')
        
        #Variables created for storing values from the files.
        timestamps = []
        x = []
        y = []
        z = []
        
        #Evaluating whether current filename is an accelerometer...
        if filename.endswith("highg.csv"):
            accelerometer = True
            #Read in all of the information from the file to the lists.
            for data in csvreader:
                timestamps.append(int(data['unix_timestamp_microsec']))
                x.append(float(data['ax_m/s/s']))
                y.append(float(data['ay_m/s/s']))
                z.append(float(data['az_m/s/s']))

        #Otherwise, the only other type of file it can be is a gyroscope file.
        else:
            accelerometer = False

            #Replicate behaviour, but with different index labels.
            for data in csvreader:
                timestamps.append(int(data['unix_timestamp_microsec']))
                x.append(float(data['gx_deg/s']))
                y.append(float(data['gy_deg/s']))
                z.append(float(data['gz_deg/s']))

            #Overwriting the Butterworth Filter variable with the correct sample rate for a gyroscope (1125 Hz).
            sos = signal.butter(4, 100, 'lp', fs = 1125, output='sos')
        
        #Apply the filter to every value in all axes lists.
        filteredx = signal.sosfilt(sos, x)
        filteredy = signal.sosfilt(sos, y)
        filteredz = signal.sosfilt(sos, z)

        # Write the newly filtered values to a new CSV file.
        writeFilteredCSV(filename, accelerometer, timestamps, filteredx, filteredy, filteredz)

    except Exception as e:
        print(e)

#=====================================================
#CHAPTER: Main Running Function of the Filtering.
#=====================================================
print("Filtering Process for IMU Data")
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

#For every file in the current directory...
for file in os.listdir(directory):
        #Get the current filename in a directory.
        filename = os.fsdecode(file)
        
        #Only when the filename is a HighG or LowG file, run the filter.
        if filename.endswith("highg.csv") or filename.endswith("lowg.csv"):
            print("Filtering: " + filename)
            try:
                runFilter(filename)
            except Exception as e:
                print(e)

#=====================================================