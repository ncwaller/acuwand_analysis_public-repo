#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provides file naming format validation for user-defined AcuWand data filenames.

AcuWand Validator scans available .csv AcuWand device data files to check if the filenames align with the required naming convention
used by 'AcuWand Analysis.' A log .txt file is produced that flags .csv files that do not align with convention requirements.
"""

##### IMPORT BELOW #####
from os.path import join as pathjoin
from os.path import sep
from glob import glob
import datetime
import re

__author__ = "Noah C Waller"
__copyright__ = "Copyright Pending"
__credits__ = ["Noah C Waller"]
__license__ = "PSF License Agreement"
__version__ = "2.1"
__year__ = "2023"
__maintainer__ = "Noah C Waller"
__email__ = "ncwaller@med.umich.edu"
__status__ = "Production"

##### INITIALIZE BELOW #####
study_name='study_name' #specify study name
dateandtime = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')) #initializes date and time here
logfilename = study_name+'_validator_log_'+dateandtime+'.txt' #name log file here

##### DIRECTORIES BELOW #####
data_dir = pathjoin(sep) #define input data directory
log_dir = pathjoin(data_dir) #define output directory to save log file output

##### PROGRAM BODY BELOW #####
logfile = open(pathjoin(log_dir,logfilename),'x') #create a log file for output
logfile.close()
logfile = open(pathjoin(log_dir,logfilename),'a') 
logfile.write('\n'+'\n'+'##############################'+"\n"+
              study_name+' Validator Notes'+"\n"+
              'Script Ran at '+dateandtime+"\n"+
              'Please Contact Noah Waller at ncwaller@umich.edu for Errors/Issues'+'\n'+
              '##############################'+'\n'+'\n'+
              'AcuWands Have 3 Naming Formats (Pre- and Post-2019 Update, and older manually named format):'+'\n'+
              'Naming Format 1: wand#_instance#_date#_timeofday#_lengthoffile(rows)#.csv'+'\n'+
              'Example Format 1: 00001_0005_18-01-2079_01-22-33_03679.csv'+'\n'+
              'Naming Format 2: wand#_instance#___date#___timeofday#___lengthoffile(mins)#_mins.csv'+'\n'+
              'Example Format 2: 00001_0005___01-18-79___01-22___7.0_mins.csv'+'\n'
              'Naming Format 3: STUDYNAME03-####-subject#_T#_date#-date#-date#_part#.csv'+'\n'+
              'Example Format 3: STUDYNAME03-0512-001_T7_1-18-79.csv or STUDYNAME03-0512-001_T7_1-18-79.csv_part1.csv'+'\n'+'\n'
              'Important Notes: File names must not include a space character. By default, naming formats should be correct.'+
              ' Data analysis results will be incorrect is the naming format of each file is not correctly formatted. This validator'+
              ' is meant to catch most mistakes in naming format but is not comprehensive. Please take care to format file names'+
              ' consistently.'+'\n'+'\n')
logfile.close()


T_list = glob(pathjoin(data_dir, 'T*')) #grab list of all T# directories
for folder in T_list:
    T_ID = folder.split('/')[-1]
    subjects_list = glob(pathjoin(data_dir, T_ID, 'BPCR01*')) #create subject list
    subjects_list.sort()
    for subject_dir in subjects_list:
        day_list_total = glob(pathjoin(subject_dir, '*.csv'))
        ###
        day_list_format1_check = glob(pathjoin(subject_dir, '*'+'_'+'*'+'_'+'*'+'-'+'*'+'-'+'*'+'_'+'*'+'_'+'*.csv')) #reads .csv file in Format 1
        day_list_format2_check = glob(pathjoin(subject_dir, '*'+'_'+'*'+'___'+'*'+'-'+'*'+'-'+'*'+'___'+'*'+'___'+'*'+'_'+'*.csv')) #reads .csv file in Format 2
        day_list_format3_check = glob(pathjoin(subject_dir, '*'+T_ID+'_'+'*'+'-'+'*'+'-'+'*.csv')) #reads .csv file in Format 3
        
        if len(day_list_format3_check) != 0: #as Format 3 is most stringent, start here: if there is data for given subject, assign Format 3
            format_style = 3 #assign Format 3
            logfile = open(pathjoin(log_dir,logfilename),'a')
            logfile.write(subject_dir+' data is in Format Style: 3'+ "\n"+ "\n")
            logfile.close()
        elif len(day_list_format2_check) != 0: #if there is data for given subject not in Format 3, assign Format 2
            format_style = 2 #assign Format 2
            logfile = open(pathjoin(log_dir,logfilename),'a')
            logfile.write(subject_dir+' data is in Format Style: 2'+ "\n"+ "\n")
            logfile.close()
        elif len(day_list_format1_check) != 0: #if there is data for given subject not in Format 2, assign Format 1
            format_style = 1 #assign Format 1
            logfile = open(pathjoin(log_dir,logfilename),'a')
            logfile.write(subject_dir+' data is in Format Style: 1'+ "\n"+ "\n")
            logfile.close()
        else: #if neither of the above are true, there is no readable data for the given subject
            logfile = open(pathjoin(log_dir,logfilename),'a') 
            logfile.write('\n'+'No Readable Data for '+subject_dir+' ... check to ensure this is correct and rename if not.'+'\n'+'\n')
            logfile.close()
            continue #jump back to loop
        ###
        day_list_nofull = [x for x in day_list_total if not x.endswith('_full.csv')]
        for day_check in day_list_nofull:
             day_check_name = day_check.split('/')[-1]   
             fullstring = day_check_name
             substring_1 = 'DataSheet'
             substring_2 = 'Datasheet'
             substring_3 = 'datasheet'
             substring_4 = 'Data Sheet'
             substring_5 = ' '
             substring_6 = '-part'
             if substring_1 in fullstring:
                 continue
             if substring_2 in fullstring:
                 continue
             if substring_3 in fullstring:
                 continue
             if substring_4 in fullstring:
                 continue
             if substring_5 in fullstring:
                 logfile = open(pathjoin(log_dir,logfilename),'a') 
                 logfile.write('\n'+'Naming Error in File: '+day_check_name+' ... improper formatting (space included) in name.'+'\n'+'\n')
                 logfile.close()
                 continue
             if substring_6 in fullstring:
                 logfile = open(pathjoin(log_dir,logfilename),'a') 
                 logfile.write('\n'+'Naming Error in File: '+day_check_name+' ... improper formatting (-part) in name.'+'\n'+'\n')
                 logfile.close()
                 continue
             if format_style == 1:
                matched = re.match('[0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]_*-*-*_*-*-*_*', day_check_name)
                is_match= bool(matched)
                if is_match == 1:
                    continue
                if is_match == 0:
                    logfile = open(pathjoin(log_dir,logfilename),'a') 
                    logfile.write('\n'+'Naming Error in File: '+day_check_name+' ... improper formatting in name.'+'\n'+'\n')
                    logfile.close()
             if format_style == 2:
                matched = re.match('[0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]___*-*-*', day_check_name) #this is as close as I can get it to Format 2
                is_match= bool(matched)
                if is_match == 1:
                    continue
                if is_match == 0:
                    logfile = open(pathjoin(log_dir,logfilename),'a') 
                    logfile.write('\n'+'Naming Error in File: '+day_check_name+' ... improper formatting in name.'+'\n'+'\n')
                    logfile.close()
             if format_style == 3:
                matched = re.match('BPCR01-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9]_'+T_ID+'_*-*-*', day_check_name)
                is_match= bool(matched)
                if is_match == 1:
                    continue
                if is_match == 0:
                    logfile = open(pathjoin(log_dir,logfilename),'a') 
                    logfile.write('\n'+'Naming Error in File: '+day_check_name+' ... improper formatting in name.'+'\n'+'\n')
                    logfile.close()