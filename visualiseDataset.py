#!"C:\Program Files\Python310"

# Import libraries that are used for the visualising an IMU file.
import csv
import os
import matplotlib.pyplot as plt
from pathlib import Path

# Global variables for the files we may want to visualise, whether we want to save a figure,
# where these figures would be saved, and which axis of data to visualise.
#Can be either highg.csv, lowg.csv, acc.csv, or gyro.csv
specifiedFile = "acc.csv"
saveFile = True
saveLocation = "imageFiles"
#Can be either l, r, or p for different positions.
combinedAxis = 'r'

#=====================================================
#Function for visualising any of the data files we have manipulated throughout processing.
#
# filename:         The name of the file to visualise.
def visualiseData(filename):
    try:
        #Open the file and set the reader object.
        csvfile = open(filename)
        csvreader = csv.DictReader(csvfile)

        #Initialise three lists for appending.
        x = []
        y = []
        z = []

        #If we are focused on original data files (i.e., highg or lowg files)...
        if filename.endswith("highg.csv") and specifiedFile == "highg.csv":
            for data in csvreader:
                x.append(float(data['ax_m/s/s']))
                y.append(float(data['ay_m/s/s']))
                z.append(float(data['az_m/s/s']))
        
        elif filename.endswith("lowg.csv") and specifiedFile == "lowg.csv":
            for data in csvreader:
                x.append(float(data['gx_deg/s']))
                y.append(float(data['gy_deg/s']))
                z.append(float(data['gz_deg/s']))
        
        #Otherwise, we may want to focus on some of our processed datasets (i.e., after segmentation)
        elif filename.endswith("acc-combined.csv") and specifiedFile == 'acc.csv':
            for data in csvreader:
                x.append(float(data[combinedAxis + 'ax_m/s/s']))
                y.append(float(data[combinedAxis + 'ay_m/s/s']))
                z.append(float(data[combinedAxis + 'az_m/s/s']))
        
        elif filename.endswith("gyro-combined.csv") and specifiedFile == 'gyro.csv':
            for data in csvreader:
                x.append(float(data[combinedAxis + 'gx_deg/s']))
                y.append(float(data[combinedAxis + 'gy_deg/s']))
                z.append(float(data[combinedAxis + 'gz_deg/s']))
        else:
            return
        
        #Set up plot correctly.
        plt.figure(figsize = (14, 6))
        plt.title(filename)
        plt.grid(axis = "y")

        #Plot all of the axes with respective colours.
        plt.plot(x, color = "blue")
        plt.plot(y, color = "red")
        plt.plot(z, color = "green")

        #If we want to, save the figure. Otherwise, show the figure. 
        if saveFile:
            plt.savefig(saveLocation + "/" + filename + ".png")
        else:
            plt.show()
        plt.close()

    except Exception as e:
        print(e)

#=====================================================
#CHAPTER: Main Running Function of the Visualiser
#=====================================================
print("Data Visualiser for IMU LESS Data")
print("---------------------------------")

#Get current working directory for path
currentDirectory = Path.cwd()

#While folder input is invalid...
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

#For every file in the current directory...
for file in os.listdir(directory):
     
     #Get the filename and only visualise .csv files.
     filename = os.fsdecode(file)
     if filename.endswith('.csv'):
        print("Visualising..." + filename)
        visualiseData(filename)
        
     else:
         continue
#=====================================================