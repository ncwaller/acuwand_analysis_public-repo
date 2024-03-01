# AcuWand Analysis

AcuWand Data Analysis is a Python-based software designed to be used with an acupressure application device ("AcuWand"). This device is currently used for research purposes and has not been released for widespread therapuetic use. Acupressure is a complementary treatment that uses fingers and hands to stimulate acupoints and has been shown to be effective for relieving a variety of pains in different populations (Chen & Wang, 2014). This software allows for quick, flexible data analysis of raw AcuWand device output.

## Installation

The code in this repository was designed to function as a stand-alone executable file that installs all relevant Python dependencies on the user's local machine. It is used internally and among collaborators and is designed to be "no-code" in its accessibility. All user interaction is performed via a simple GUI. While the executable file and other finalized distribution elements are not present in this public repository, the scripts can function independently.

## Usage

## AcuWand Analysis

Provides data cleaning and descriptive statistic generation for AcuWand device data.

AcuWand Analysis aggregates .csv files produced by AcuWand devices, merges data along single days, removes pressure values under a defined minimum, removes pressure values over a defined maximum, removes consecutive exact value repeats equal to or greater than  1 minute in length, and generates a variety of descriptive statistics for pressure and treatment time data, both by date and by averaged whole subject, including: (for pressure) maximum, mean, median, skewness, kurtosis, standard deviation, and interquartile range, and (for treatment time) total time in seconds and minutes, and total number of treatment days. Results are output in log .txt and result .csv files.

Comments in script instruct path setting.

Check Output Directory for result output:

AcuWand_analysis_log.txt: This is a .txt file that contains notes about unique analysis cases. It lists the subjects included in each "T*" analysis (ex. T2), the lower and upper cutoffs for pressure values, and the range of values for removal of consecutive cases (ex. -0.1/+0.1). It then lists any unique cases when the data files were merged/cleaned (ex. if there is missing data, if analysis required merging multiple parts for a given participant in a single day). Finally, it lists any cases of repeated consecutive values exceeding 60 seconds, what the offending value was, and if it was removed from total treatment time.
 
AcuWand_T*_resultsbydate and bysubj...csv: These files show the desired metrics by date and by subject. For bydate files, this shows each subject in a given T folder, with each of that subject's treatment files by date. For bysubj files, this shows each subject in a given T folder with the overall statistics. These include max, mean, median, standard deviation, skewness, kurtosis, and interquartile range of pressure values, and the treatment total times in seconds and minutes (organized by individual date in the bydate files and averaged across subject in the bysubj files).

## AcuWand Validator

Provides file naming format validation for user-defined AcuWand data filenames.

AcuWand Validator scans available .csv AcuWand device data files to check if the filenames align with the required naming convention
used by 'AcuWand Analysis.' A log .txt file is produced that flags .csv files that do not align with convention requirements.

## AcuWand GUI

Provides a graphical user interface (GUI) to house the 'Acuwand Analysis' and 'AcuWand Validator' programs.

AcuWand GUI generates a pop-up window with buttons to define input and output directories, define absolute lower and upper cutoffs, define range for consecutive value deletions, run file naming format validation, and analyze the AcuWand data store.

This code shell will not have full functionality without inserting the AcuWand_Analysis and AcuWand_Validator scripts in defined sections below.

## Contributing

Please contact ncwaller@med.umich.edu for change requests. Please make note of errors/issues and send them along. I am working to make consistent improvements and additions to the program. Updated full distributions are kept internal but the open code in this repository will be updated simultaneously.

## Author

Noah C Waller
University of Michigan, Ann Arbor, MI 48109
ncwaller@med.umich.edu
