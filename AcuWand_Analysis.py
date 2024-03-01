#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provides data cleaning and descriptive statistic generation for AcuWand device data.

AcuWand Analysis aggregates .csv files produced by AcuWand devices, merges data along single days, removes pressure values under
a defined minimum, removes pressure values over a defined maximum, removes consecutive exact value repeats equal to or greater than 
1 minute in length, and generates a variety of descriptive statistics for pressure and treatment time data, both by date and by 
averaged whole subject, including: (for pressure) maximum, mean, median, skewness, kurtosis, standard deviation, and interquartile 
range, and (for treatment time) total time in seconds and minutes, and total number of treatment days. 
Results are output in log .txt and result .csv files.
"""

##### IMPORT BELOW #####
import os
from os.path import join as pathjoin
from os.path import sep
from glob import glob
import pandas as pd
import datetime
import numpy as np
from decimal import Decimal
import statistics
import math

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
calcpressurestats = 1 #use 1 to calculate the min, max, and mean pressure per day
calctotaltreatment = 1 #use 1 to calculate the total treatment time per day
lower_cutoff = -10 #define lower floor cutoff for pressure calculations
upper_cutoff = 10 #define upper ceiling cutoff for pressure calculations
lower_range_fordel = -0.1 #define lower end of range of values to remove consecutive appearances
upper_range_fordel = 0.1 #define upper end of range of values to remove consecutive appearances
dateandtime = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')) #initializes date and time here
logfilename = study_name+'_analysis_log_'+dateandtime+'.txt' #name log file here

##### DIRECTORIES BELOW #####
data_dir = pathjoin(sep) #define input data directory
log_dir = pathjoin(data_dir) #define output directory to save log file output


##### PROGRAM BODY BELOW #####
logfile = open(pathjoin(log_dir,logfilename),'x') #create a log file for output
logfile.close()
logfile = open(pathjoin(log_dir,logfilename),'a') 
logfile.write('\n'+'\n'+'##############################'+"\n"+
              study_name+' Data Log Notes'+"\n"+
              'Script Ran at '+dateandtime+"\n"+
              'Please Contact Noah Waller at ncwaller@umich.edu for Errors/Issues'+'\n'+
              '##############################'+'\n'+'\n')
logfile.close()

T_list = glob(pathjoin(data_dir, 'T*')) #grab list of all T# directories
for folder in T_list:
    T_ID = folder.split('/')[-1]
    subjects_list = glob(pathjoin(data_dir, T_ID, 'BPCR01*')) #create subject list
    subjects_list.sort()
    subjects = []
    outfilename_pressure_bydate = study_name+'_'+T_ID+'_pressure_resultsbydate_'+dateandtime+'.csv' #name output file here
    outfilename_pressure_bysubj = study_name+'_'+T_ID+'_pressure_resultsbysubj_'+dateandtime+'.csv' #name output file here
    outfilename_txtime_bydate = study_name+'_'+T_ID+'_txtime_resultsbydate_'+dateandtime+'.csv' #name output file here
    outfilename_txtime_bysubj = study_name+'_'+T_ID+'_txtime_resultsbysubj_'+dateandtime+'.csv' #name output file here
    outfilename_final_bydate = study_name+'_'+T_ID+'_resultsbydate_'+dateandtime+'.csv' #name output file here
    outfilename_final_bysubj = study_name+'_'+T_ID+'_resultsbysubj_'+dateandtime+'.csv' #name output file here
    for subj in subjects_list:
        subjects.append(subj.split('/')[-1])
    subjects = str(subjects)
    lower_cutoff_str = str(lower_cutoff)
    upper_cutoff_str = str(upper_cutoff)
    lower_range_fordel_str = str(lower_range_fordel)
    upper_range_fordel_str = str(upper_range_fordel)
    logfile = open(pathjoin(log_dir,logfilename),'a') #creates header in log file
    logfile.write('\n'+'Subjects Included in AcuWand '+T_ID+' Analysis: '+'\n'+
                  subjects+'\n'+
                  'Lower Cutoff for Pressure Values: '+lower_cutoff_str+'\n'+
                  'Upper Cutoff for Pressure Values: '+upper_cutoff_str+'\n'+
                  'Range for Consecutive Pressure Value Removal Around Zero: '+lower_range_fordel_str+
                  '/+'+upper_range_fordel_str+'\n'+'\n')
    logfile.close()


### PREPARE .CSV FILES (MERGE)
    logfile = open(pathjoin(log_dir,logfilename),'a') 
    logfile.write('\n'+'File Preparation Unique Cases (Merge & Clean):'+'\n'+'\n')
    logfile.close()
    for subject_dir in subjects_list:
        remove_list = glob(pathjoin(subject_dir, '*_full.csv')) #removes current _full.csv files (important for re-running script)
        for file in remove_list:
            os.remove(file)
        subj_name = 'subject: '+subject_dir.split('/')[-1]

        ### Examples below have been altered to protect individual privacy

        ### FORMAT 1 ####
        # "00001_0005_18-01-2079_01-22-33_03679.csv"
        # "wand#_instance#_date#_timeofday#_lengthoffile#.csv"

        #### FORMAT 2 ####
        # "00001_0005___01-18-79___01-22___7.0_mins.csv"
        # "wand#_instance#___date#___timeofday#___lengthoffile#_mins.csv"

        #### FORMAT 3 ####
        # "STUDYNAME03-0512-001_T7_1-18-79.csv" or "STUDYNAME03-0512-001_T7_1-18-79_part1.csv"
        # "STUDYNAME03-####-subject#_T#_date#-date#-date#_part#.csv"

        day_list_format1 = glob(pathjoin(subject_dir, '*'+'_'+'*'+'_'+'*'+'-'+'*'+'-'+'*'+'_'+'*'+'_'+'*.csv')) #reads .csv file in Format 1..
        day_list_format2 = glob(pathjoin(subject_dir, '*'+'_'+'*'+'___'+'*'+'-'+'*'+'-'+'*'+'___'+'*'+'___'+'*'+'_'+'*.csv')) #reads .csv file in Format 2
        day_list_format3 = glob(pathjoin(subject_dir, '*'+T_ID+'_'+'*'+'-'+'*'+'-'+'*.csv')) #reads .csv file in Format 3

        if len(day_list_format3) != 0: #Format 3 is the most stringent, start here: if there is data for a given subject, assign Format 3
            format_style = 3 #assign Format 3
            day_list = day_list_format3 #assign day_list variable as _format3
            logfile = open(pathjoin(log_dir,logfilename),'a')
            logfile.write(subj_name+' data is in Format Style: 3'+ "\n"+ "\n")
            logfile.close()
        elif len(day_list_format2) != 0: #as Format 2 is the next most stringent: if there is data for given subject, assign Format 2
            format_style = 2 #assign Format 2
            day_list = day_list_format2 #assign day_list variable as _format2
            logfile = open(pathjoin(log_dir,logfilename),'a')
            logfile.write(subj_name+' data is in Format Style: 2'+ "\n"+ "\n")
            logfile.close()
        elif len(day_list_format1) != 0: #if there is data for given subject not in Format 2, assign Format 1
            format_style = 1 #assign Format 1
            day_list = day_list_format1 #assign day_list variable as _format1
            logfile = open(pathjoin(log_dir,logfilename),'a')
            logfile.write(subj_name+' data is in Format Style: 1'+ "\n"+ "\n")
            logfile.close()
        else: #if neither of the above are true, there is no readable data for the given subject
            logfile = open(pathjoin(log_dir,logfilename),'a')
            logfile.write('No Readable Data for '+subj_name+'... skipping subject for .csv preparation.'+ "\n"+ "\n")
            logfile.close()
            continue #jump back to loop

        if format_style == 2 or format_style == 1: #if files are named in the more raw formats, they need special help sorting by date
        
            day_list_noinstance = [] #make new list object for days with instance part removed (SORTING BY DATE)

            for day in day_list:
                day_name = day.split('/')[-1].replace(".csv","")
                wand_instance_label = "{}".format(day_name[0:10]) #takes first 10 characters from string (wand and isntance label)
                revised_day_name = day.replace(wand_instance_label,"") #rename the day name without the wand and instance labels
                day_list_noinstance.append(revised_day_name) #add to the new list

            day_list_noinstance.sort() #new sorted list (essentially sorted by date, but has nonexistent paths)

            day_list = [] #create new day_list empty list
            for revised_day in day_list_noinstance: #iterates through revised sorted list
                day_name = revised_day.split('/')[-1] #revised day name
                if format_style == 2:
                    day_list_original = day_list_format2 #takes list of original path names for days
                elif format_style == 1:
                    day_list_original = day_list_format1 #takes list of original path names for days
                for original_day in day_list_original: #iterates through original day list
                    if original_day.endswith(day_name) == True: #if the day matches the ending of the revised day
                        day_list.append(original_day) #this is added to the day_list, in the correct order this time
                    elif original_day.endswith(day_name) == False:
                        continue

        elif format_style == 3: #running with older, manually named Format 3
            day_list.sort() #easier to sort by date

# The newly sorted day_list has been created, essentially grouped by date, and has been re-named day_list
# From this point on, DO NOT re-sort day_list. Use day_list, never use day_list_noinstance again
        list0 = [] #defines the number of lists needed for a given subject (i.e. a list for each *_part*.csv)
        for day in day_list:
            day_name = day.split('/')[-1].replace(".csv","")
            if format_style == 1:
                date_split = day_name.split('_')[2] #Format 1
            elif format_style == 2:
                date_split = day_name.split('_')[4] #Format 2
            elif format_style == 3:   
                date_split = day_name.split('_')[2] #Format 3
            list0.append(date_split)
            df_list_dates = pd.DataFrame(list0, columns = ['date'])
            df_grouped = df_list_dates.groupby('date')
            n_groups = df_grouped.ngroups #number of .csv files per date
            list_oflists = [] #list of lists (determined by how many .csv files per date)
        if n_groups < len(df_list_dates):
            logfile = open(pathjoin(log_dir,logfilename),'a')
            logfile.write('Multiple parts for at least 1 date for '+subj_name+'... check participant log to ensure files are not '
                          + 'multiple hours apart.'
                          + "\n"+ "\n")
            logfile.close()
        
        for i in range(n_groups):
            list_oflists.append([]) 
        i = 0
        for day in day_list: #iterate through lists, adding .csv files with identical dates to the same list
            list_v = list_oflists[i]
            day_name = day.split('/')[-1].replace(".csv","")
            if format_style == 1:
                date_split = day_name.split('_')[2] #Format 1
            elif format_style == 2:
                date_split = day_name.split('_')[4] #Format 2
            elif format_style == 3:   
                date_split = day_name.split('_')[2] #Format 3
            if len(list_v) == 0:
                list_v.append(day)
                continue
            elif len(list_v) != 0:
                day_currlist = list_v[0]
                day_name_currlist = day_currlist.split('/')[-1].replace(".csv","")
                if format_style == 1:
                    date_split_currlist = day_name_currlist.split('_')[2] #Format 1
                elif format_style == 2:
                    date_split_currlist = day_name_currlist.split('_')[4] #Format 2 
                elif format_style == 3:   
                    date_split_currlist = day_name_currlist.split('_')[2] #Format 3
                if date_split == date_split_currlist:
                    list_v.append(day)
                elif date_split != date_split_currlist: #adding .csv files with new date to next list
                    i = i + 1
                    list_v = list_oflists[i]
                    list_v.append(day)
                    continue
        for list_v in list_oflists: #merge .csv files within each list (within the same date)
            merge_day_name = list_v[0].split('/')[-1].replace(".csv","")
            if merge_day_name.endswith("_part1"):
                merge_day_name = merge_day_name.replace("_part1","")
            if merge_day_name.endswith("_part 1"):
                merge_day_name = merge_day_name.replace("_part 1","")
            if merge_day_name.endswith("_part1_graph"):
                merge_day_name = merge_day_name.replace("_part1_graph","")
            if merge_day_name.endswith("_Part1"):
                merge_day_name = merge_day_name.replace("_Part1","") #interesting way to handle this
            merge_df = pd.DataFrame() #creates DF for .csv files to be merged
            for f in list_v:
                df = pd.read_csv(f)
                df = df[df.columns[0]] #takes first column from the frame (some .csv files have multiple empty columns)
                df.columns=[0] #changes index to zero (results in slightly changed data, minimal impact)
                merge_df = pd.concat([merge_df, df]) 
            os.chdir(subject_dir)
            merge_df.to_csv(merge_day_name+"_full.csv", index=False, encoding='utf-8-sig')
            #NOTE: this outputs a .csv file to the given subject directory for each date; this will be output 
            #even if there were not multiple parts - it will just consist of the original .csv file for the date


### MIN, MAX, MEAN PRESSURE
    if calcpressurestats == 1:
        #logfile = open(pathjoin(log_dir,logfilename),'a') 
        #logfile.write('\n'+'Pressure Descriptive Statistics:'+'\n'+'\n'+'\n')
        #logfile.close()
        df_full = pd.DataFrame()
        df_overall = pd.DataFrame()
        for subject_dir in subjects_list:
            day_list = glob(pathjoin(subject_dir, '*_full.csv'))
            day_list.sort()
            subj_name = 'subject: '+subject_dir.split('/')[-1]
            subj_name_strip = subject_dir.split('/')[-1]
            list_subj = []
            list_overallmean = []
            list_overallsd = []
            list_subjday = [] #create empty list for each measure of interest for given subject
            list_subjmax = []
            list_subjmean = []
            list_subjmedian = []
            list_subjskew = []
            list_subjkurtosis = []
            list_subjsd = []
            list_subjIQR = []
            list_m_mean = []
            list_m_sd = []
            for day in day_list:
                day_name = day.split('/')[-1].replace("_full.csv","") #get subj/day name
                full_name = subj_name_strip+'_'+day_name
                list_subjday.append(full_name)
                column_list = [0]
                df = pd.read_csv(day, usecols=column_list)
                df.columns = ["Pressure"] #read in .csv file, take only the first column, rename it to "Pressure"
                df_chopmin = df[df.Pressure > lower_cutoff] #remove lower values
                df_chopboth = df_chopmin[df_chopmin.Pressure < upper_cutoff] #remove upper values
                day_min = df_chopboth.min() #calculate min pressure value
                day_max = df_chopboth.max() #calculate max pressure value
                day_mean = df_chopboth.mean() #calculate mean pressure value
                day_median = df_chopboth.median() #calculation median pressure value
                day_skew = df_chopboth.skew() #calculate skewness
                day_kurtosis = df_chopboth.kurtosis() - 3 #calculate kurtosis
                day_sd = df_chopboth.std() #calculate standard deviation   
                day_min_str = str(day_min)
                day_max_str = str(day_max)
                day_mean_str = str(day_mean)
                day_median_str = str(day_median)
                day_skew_str = str(day_skew)
                day_kurtosis_str = str(day_kurtosis)
                day_sd_str = str(day_sd)
                if math.isnan(day_mean) == False:
                    list_m_mean.append(day_mean)
                if math.isnan(day_sd) == False:
                    list_m_sd.append(day_sd)
                if df_chopboth.empty:
                    day_IQR = str('NaN') #if dataframe is empty, needs special intervention
                elif not df_chopboth.empty:
                    day_Q3 = np.quantile(df_chopboth, 0.75) #calculate third quartile cutoff
                    day_Q1 = np.quantile(df_chopboth, 0.25) #calculate first quartile cufoff
                    day_IQR = day_Q3 - day_Q1 #calculate interquartile range
                day_IQR_str = str(day_IQR)
                #logfile = open(pathjoin(log_dir,logfilename),'a') #report pressure statistics for subject date in log file
                #logfile.write(day_name+':'+ "\n"
                #              +'Minimum '+day_min_str+"\n"+'Maximum '+day_max_str+"\n"
                #              +'Mean '+day_mean_str+"\n"+'Median '+day_median_str+"\n"+'Skewness '+day_skew_str+"\n"+
                #              'Kurtosis (Fisher) '+day_kurtosis_str+"\n"+'Standard Deviation '+day_sd_str+"\n"+
                #              'IQR '+day_IQR_str+"\n"+"\n")
                #logfile.close()

                list_subjmax.append(day_max_str) #append calculated values to lists
                list_subjmean.append(day_mean_str)
                list_subjmedian.append(day_median_str)
                list_subjskew.append(day_skew_str)
                list_subjkurtosis.append(day_kurtosis_str)
                list_subjsd.append(day_sd_str)
                list_subjIQR.append(day_IQR_str)           
                ### 
            if len(day_list) != 0:
                df_subjday = pd.DataFrame(list(zip(list_subjday))) #dataframe of subject and days  
                df_max = pd.DataFrame(list(zip(list_subjmax))) #dataframe of maxes
                df_max = df_max[0].str.replace("Pressure","")
                df_max = df_max.str.replace("\ndtype:","")
                df_max = df_max.str.replace("float64","")
                df_mean = pd.DataFrame(list(zip(list_subjmean))) #dataframe of means
                df_mean = df_mean[0].str.replace("Pressure","")
                df_mean = df_mean.str.replace("\ndtype:","")
                df_mean = df_mean.str.replace("float64","")
                df_median = pd.DataFrame(list(zip(list_subjmedian))) #dataframe of medians
                df_median = df_median[0].str.replace("Pressure","")
                df_median = df_median.str.replace("\ndtype:","")
                df_median = df_median.str.replace("float64","")
                df_skew = pd.DataFrame(list(zip(list_subjskew))) #dataframe of skewness
                df_skew = df_skew[0].str.replace("Pressure","")
                df_skew = df_skew.str.replace("\ndtype:","")
                df_skew = df_skew.str.replace("float64","")
                df_kurtosis = pd.DataFrame(list(zip(list_subjkurtosis))) #dataframe of kurtosis 
                df_kurtosis = df_kurtosis[0].str.replace("Pressure","")
                df_kurtosis = df_kurtosis.str.replace("\ndtype:","")
                df_kurtosis = df_kurtosis.str.replace("float64","")
                df_sd = pd.DataFrame(list(zip(list_subjsd))) #dataframe of standard deviations
                df_sd = df_sd[0].str.replace("Pressure","")
                df_sd = df_sd.str.replace("\ndtype:","")
                df_sd = df_sd.str.replace("float64","")
                df_IQR = pd.DataFrame(list(zip(list_subjIQR))) #dataframe of IQRs
                stat_frames = [df_subjday, df_max, df_mean, df_median, df_skew, df_kurtosis, df_sd, df_IQR]
                subj_result = pd.concat(stat_frames, axis=1).reindex(df_subjday.index)
            elif len(day_list) == 0:
                continue
            df_frames = [df_full, subj_result]
            df_full = pd.concat(df_frames)
            ###
            if len(list_m_mean) == 0:
                subj_mean_pressure = 'NaN'
            elif len(list_m_mean) != 0:
                subj_mean_pressure = statistics.fmean(list_m_mean)
            if len(list_m_sd) == 0:
                subj_sd_pressure = 'NaN'
            elif len(list_m_sd) != 0:
                subj_sd_pressure = statistics.fmean(list_m_sd)
            subj_mean_pressure_str = str(subj_mean_pressure)
            subj_sd_pressure_str = str(subj_sd_pressure)
            #logfile = open(pathjoin(log_dir,logfilename),'a') #report pressure statistics for whole subject in log file
            #logfile.write('Overall Statistics for '+subj_name+':'+ "\n"
            #              +'Mean Pressure '+subj_mean_pressure_str+"\n"+'SD Pressure '+subj_sd_pressure_str+"\n"+"\n")
            #logfile.close()
            list_subj.append(subj_name_strip) #add subject name to overall list
            list_overallmean.append(subj_mean_pressure_str) #append calculated values to lists
            list_overallsd.append(subj_sd_pressure_str)
            df_overallsubj = pd.DataFrame(list(zip(list_subj))) #dataframe of subjects
            df_overallmean = pd.DataFrame(list(zip(list_overallmean))) #dataframe of means
            df_overallsd = pd.DataFrame(list(zip(list_overallsd))) #dataframe of sds
            overall_frames = [df_overallsubj, df_overallmean, df_overallsd]
            overall_result = pd.concat(overall_frames, axis=1).reindex(df_overallsubj.index)
            df_overall_frames = [df_overall, overall_result]
            df_overall = pd.concat(df_overall_frames)
            ###
        #df_overall.columns = ['subj_name', 'overall_mean_p', 'overall_sd_p']
        #df_overall.to_csv(pathjoin(log_dir, outfilename_pressure_bysubj))
        #df_full.columns =['subj_name', 'max_p', 'mean_p', 'median_p', 'skew_p', 'kurtosis_p', 'sd_p', 'IQR_p']
        #df_full.to_csv(pathjoin(log_dir, outfilename_pressure_bydate))
        ###
        #logfile_old = open(pathjoin(log_dir,logfilename),'r') #clean unwanted lines from log file
        #lines = logfile_old.readlines()
        #logfile_old.close()     
        #logfile_clean = open(pathjoin(log_dir,logfilename), 'w')
        #for line in lines:
        #    if line.strip('\n') != 'dtype: float64':
        #        logfile_clean.write(line)
        #logfile_clean.close()


### TOTAL TREATMENT TIME
    if calctotaltreatment == 1:
        logfile = open(pathjoin(log_dir,logfilename),'a') 
        logfile.write('\n'+'Notes About Excessive Repeated Values in Total Treatment Time Calculations:'+'\n'+'\n')
        logfile.close()
        df_full_tx = pd.DataFrame()
        df_overall_tx = pd.DataFrame()
        for subject_dir in subjects_list: #iterate through each subject
            day_list = glob(pathjoin(subject_dir, '*_full.csv'))
            day_list.sort()
            totaltxdays = len(day_list)
            subj_name = 'subject: '+subject_dir.split('/')[-1]
            subj_name_strip = subject_dir.split('/')[-1]
            list_tx_min = []
            list_tx_sec = []
            list_subj_tx = []
            list_overallmeantx_sec = []
            list_overallmeantx_min = []
            list_subjday_tx = [] #create empty list for each measure of interest for given subject
            list_subjtotaltxtime_sec = []
            list_subjtotaltxtime_min = []
            list_totaltx_days = []
            for day in day_list: #iterate through each .csv file
                day_name = day.split('/')[-1].replace("_full.csv","") #get subject name and date
                full_name = subj_name_strip+'_'+day_name
                list_subjday_tx.append(full_name)
                day_name_str = str(day_name)
                column_list = [0]
                df = pd.read_csv(day, usecols=column_list)
                df.columns = ["Pressure"] #read in .csv file, take only the first column, rename it to "Pressure"
                df_boolean = df.Pressure.eq(df.Pressure.shift(-1)) #determine if consecutive pressure values match the previous value, label these as "True"
                df['Boolean'] = df_boolean
                boolean_list = df.Boolean.tolist()
                counter=0
                consec_list=[]
                pos = -1
                for idx, val in enumerate(boolean_list):
                    if val==True and pos == -1:
                        counter += 1
                        pos = idx
                    elif val == True:
                        counter += 1
                    elif pos != -1:
                        consec_list.append([pos,counter])
                        pos = -1
                        counter = 0
                if counter > 0:
                    consec_list.append([pos,counter])
                total_tx_rows = len(df.index)
                for pair in consec_list: #iterate through each instance of repeats
                    num_repeats = pair[1] #define number of consecutive repeats
                    if num_repeats > 600: #if > 60 seconds of consecutive repeats
                        row_num = pair[0] #define row number where this span of repeats began
                        row_val = df.iloc[row_num, 0] #define pressure value being repeated
                        row_val_str = str(row_val)
                        logfile = open(pathjoin(log_dir,logfilename),'a')
                        logfile.write('Case for '+subj_name+' '+day_name_str+':'+"\n"+"\n"
                                      +'Series of Consecutive Values of '+row_val_str+' Exceeded 60 seconds.'
                                      +"\n")
                        logfile.close()
                        if row_val == int(row_val): #if the repeated value is equal to a rounded version of itself (i.e. integar)
                            row_val_dec = row_val  #define value
                        else: #if the repeated value is not equal to the rounded version of itself (i.e. decimal)
                            row_val_dec = Decimal(row_val) #define value
                        if lower_range_fordel <= row_val_dec <= upper_range_fordel: #if this pressure value is in the range of +/- val of 0
                            total_tx_rows = total_tx_rows - num_repeats #subtract consecutive 0 rows from total df length
                            logfile = open(pathjoin(log_dir,logfilename),'a') #make note in log file about the break
                            logfile.write('Values Within '+lower_range_fordel_str+'/+'+upper_range_fordel_str+' of 0; '
                                          +'Time Removed from Total Tx Time.'+"\n"+"\n")
                            logfile.close()
                        elif not lower_range_fordel <= row_val_dec <= upper_range_fordel: #if this pressure value is not 0
                            logfile = open(pathjoin(log_dir,logfilename),'a') #make note in log file about the break
                            logfile.write('Values Not Within '+lower_range_fordel_str+'/+'+upper_range_fordel_str+' of 0; '
                                      +'Time Not Removed from Total Tx Time.'+"\n"+"\n")
                            logfile.close()
                            continue
                    else: #if !> 60 seconds of consecutive repeats
                         continue
                net_tx_rows = total_tx_rows
                total_tx_time_sec = net_tx_rows/10
                total_tx_time_min = total_tx_time_sec/60
                total_tx_time_sec_str = str(total_tx_time_sec)
                total_tx_time_min_str = str(total_tx_time_min)
                if math.isnan(total_tx_time_sec) == False:
                    list_tx_sec.append(total_tx_time_sec)
                if math.isnan(total_tx_time_min) == False:
                    list_tx_min.append(total_tx_time_min)
                #logfile = open(pathjoin(log_dir,logfilename),'a') #report tx time information per subject date in log file
                #logfile.write(day_name_str+':'+ "\n"
                #              +'Seconds: '+total_tx_time_sec_str+"\n"+'Minutes: '+total_tx_time_min_str+"\n"+"\n")
                #logfile.close()
                ###
                list_subjtotaltxtime_sec.append(total_tx_time_sec)
                list_subjtotaltxtime_min.append(total_tx_time_min) #append calculated values to lists
            if len(day_list) != 0:
                df_subjday_tx = pd.DataFrame(list(zip(list_subjday_tx))) #dataframe of subject and days  
                df_txtime_sec = pd.DataFrame(list(zip(list_subjtotaltxtime_sec))) #dataframe of seconds
                df_txtime_min = pd.DataFrame(list(zip(list_subjtotaltxtime_min))) #dataframe of minutes
                df_totaltx_days = pd.DataFrame(list(zip(list_totaltx_days))) #dataframe of total tx days
                time_frames = [df_subjday_tx, df_txtime_sec, df_txtime_min]
                time_result = pd.concat(time_frames, axis=1).reindex(df_subjday_tx.index)
            elif len(day_list) == 0:
                continue
            df_tx_frames = [df_full_tx, time_result]
            df_full_tx = pd.concat(df_tx_frames)
            ###
            if len(list_tx_min) <= 1:
                subj_mean_txtime_min = total_tx_time_min_str
            elif len(list_tx_min) > 1:
                subj_mean_txtime_min = statistics.mean(list_tx_min)
            if len(list_tx_sec) <= 1:
                subj_mean_txtime_sec = total_tx_time_sec_str
            elif len(list_tx_min) > 1:
                subj_mean_txtime_sec = statistics.mean(list_tx_sec)
            subj_totaltx_days = len(day_list)
            subj_mean_txtime_min_str = str(subj_mean_txtime_min)
            subj_mean_txtime_sec_str = str(subj_mean_txtime_sec)
            subj_totaltx_days_str = str(subj_totaltx_days)          
            list_subj_tx.append(subj_name_strip) #add subject name to overall list
            list_overallmeantx_sec.append(subj_mean_txtime_sec_str) #append calculated values to lists
            list_overallmeantx_min.append(subj_mean_txtime_min_str)
            list_totaltx_days.append(subj_totaltx_days_str)
            df_overallsubj_tx = pd.DataFrame(list(zip(list_subj_tx))) #dataframe of subjects
            df_overallmeantx_sec = pd.DataFrame(list(zip(list_overallmeantx_sec))) #dataframe of means
            df_overallmeantx_min = pd.DataFrame(list(zip(list_overallmeantx_min))) #dataframe of sds
            df_totaltx_days = pd.DataFrame(list(zip(list_totaltx_days))) #dataframe of total tx days
            overall_frames_tx = [df_overallsubj_tx, df_overallmeantx_sec, df_overallmeantx_min, df_totaltx_days]
            overall_result_tx = pd.concat(overall_frames_tx, axis=1).reindex(df_overallsubj_tx.index)
            df_overall_frames_tx = [df_overall_tx, overall_result_tx]
            df_overall_tx = pd.concat(df_overall_frames_tx)
            ###
        df_final_overall_frame = [df_overall, df_overall_tx]
        df_final_overall = pd.concat(df_final_overall_frame, axis=1)
        df_final_overall.columns = ['subj_name', 'overall_mean_p', 'overall_sd_p',
                                    'subj_name', 'mean_txtime_sec', 'mean_txtime_min', 'number_tx_days']
        df_final_overall.to_csv(pathjoin(log_dir, outfilename_final_bysubj))
        df_final_full_frame = [df_full, df_full_tx]
        df_final_full = pd.concat(df_final_full_frame, axis=1)
        df_final_full.columns = ['subj_name', 'max_p', 'mean_p', 'median_p', 'skew_p', 'kurtosis_p', 'sd_p', 'IQR_p',
                                    'subj_name', 'txtime_sec', 'txtime_min']
        df_final_full.to_csv(pathjoin(log_dir, outfilename_final_bydate))
        #df_overall_tx.columns = ['subj_name', 'mean_txtime_sec', 'mean_txtime_min']
        #df_overall_tx.to_csv(pathjoin(log_dir, outfilename_txtime_bysubj))
        #df_full_tx.columns =['subj_name', 'txtime_sec', 'txtime_min']
        #df_full_tx.to_csv(pathjoin(log_dir, outfilename_txtime_bydate))
        ###
            #if len(list_tx_min) <= 1:
             #   subj_mean_txtime = total_tx_time_min_str
              #  subj_sd_txtime = 'NaN'
            #elif len(list_tx_min) > 1:
             #   subj_mean_txtime = statistics.mean(list_tx_min)
              #  subj_sd_txtime = statistics.stdev(list_tx_min)
            #subj_mean_txtime_str = str(subj_mean_txtime)
            #subj_sd_txtime_str = str(subj_sd_txtime)
            #logfile = open(pathjoin(log_dir,logfilename),'a') #report txtime statistics for whole subject in log file
            #logfile.write('Overall Statistics for '+subj_name+':'+ "\n"
            #              +'Mean Tx Time '+subj_mean_txtime_str+"\n"+'SD Tx Time '+subj_sd_txtime_str+"\n"+"\n")
            #logfile.close()
            
### END ANALYSIS
logfile = open(pathjoin(log_dir,logfilename),'a') 
logfile.write('\n'+'##############################'+"\n"+
              'END LOG'+'\n'
              '##############################'+'\n')
logfile.close()
