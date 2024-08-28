# Automation-of-the-Landing-Error-Scoring-System-using-Inertial-Measurement-Units
![implementationPipeline](https://github.com/user-attachments/assets/df102332-8ec8-4ee3-8ab0-d6a9d4bd5242)

Repository containing the Python code used to process and integrate IMU movement datum with machine learning for automation of Landing Error Scoring System scores.

The following files are available, with algorithms as specified in the thesis integrated throughout:

**cropper.py:**                The algorithms as required for detecting threshold values, and cropping the movement window down for processing.

**aligner.py:**                Direct manipulation of the dataset to align the axes of the sensor to one consistent axis.

**filter.py:**                 Application of a Fourth-order Butterworth Filter to all axes of datum.

**segmentation.py:**            Includes the segmentation using key events, dividing the data into groups, and outputting new files.

**subsetter.py:**               The first step of merging and subsetting, by creating new directories with the correct subsets of the data.

**merger.py:**                  The second step required for merging the subsets by combining LESS scores with the subsets of data.

**classification.py:**          Evaluation of multiple models and extraction of performance metrics for this evaluation.

**featureImportance.py:**       Use the best performing model for a scoring item and extract the top performing features.


Extra available file available for visualisation of the data:

**visualiser.py:**             Used throughout the thesis to visualise the dataset or subsets as processing occurred.
