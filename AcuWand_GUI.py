#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provides a graphical user interface (GUI) to house the 'Acuwand Analysis' and 'AcuWand Validator' programs.

AcuWand GUI generates a pop-up window with buttons to define input and output directories, define absolute lower and upper cutoffs,
define range for consecutive value deletions, run file naming format validation, and analyze the AcuWand data store.

This code shell will not have full functionality without inserting the AcuWand_Analysis and AcuWand_Validator scripts in defined sections below.
"""

##### IMPORT #####
from tkinter import filedialog
import tkinter as tk
import os
from os.path import join as pathjoin
from glob import glob
import pandas as pd
import datetime
import numpy as np
from decimal import Decimal
import statistics
import math
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

##### GUI #####
# root window
root = tk.Tk()
root.geometry("700x600")
root.title('AcuWand Data Analysis')
root.resizable(0, 0)

# configure the grid
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)

#canvas = tk.Canvas(root, width =400, height = 600)
#canvas.grid(columnspan = 2, rowspan = 8)

## LOGO ##
#logo = Image.open('umlogo.png')
#logo = ImageTk.PhotoImage(logo)
#logo_label = tk.Label(image = logo)
#logo_label.image = logo
#logo_label.grid(column=1, row=0)
 
## FUNCTIONS ##        
def input_dir():
    global in_folder
    in_folder = filedialog.askdirectory()
    if in_folder:
        in_folder_path = os.path.abspath(in_folder)
        input_dir_text.set('Input Dir')
        
        tk.Label(root, text=in_folder_path).grid(row=1, column=1)
        
def output_dir():
    global out_folder
    out_folder = filedialog.askdirectory()
    if out_folder:
        out_folder_path = os.path.abspath(out_folder)
        output_dir_text.set('Output Dir')
        tk.Label(root, text=out_folder_path).grid(row=2, column=1)
        
def define_low():
    global low_cutoff
    low_cutoff = float(e1.get())
    if low_cutoff:
        lower_cut_text.set('Lower Cutoff')
        
def define_up():
    global up_cutoff
    up_cutoff = float(e2.get())
    if up_cutoff:
        upper_cut_text.set('Upper Cutoff')
        
def low_range_del():
    global low_range_val
    low_range_val = float(e3.get())
    if low_range_val:
        low_range_text.set('Range Neg Value')
        
def up_range_del():
    global up_range_val
    up_range_val = float(e4.get())
    if up_range_val:
        up_range_text.set('Range Pos Value')

def validate_acu():
    ##### INSERT AcuWand_Validator CODE HERE ####
            
    ##### END #####
            tk.Label(root, text='Done').grid(column=1, row=7)

def analyze_acu():
    ##### INSERT AcuWand_Analysis CODE HERE ####

    ##### END #####
    tk.Label(root, text='Done').grid(column=1, row=8)


## INSTRUCTIONS ##
instructions = tk.Label(root, text = 'Set All Parameters Before Pressing Analyze\n'+
                        'Set Input Dir and Output Dir Before Pressing Validate',
                       font = 'Raleway')
instructions.grid(columnspan = 3, column = 0, row = 0)

instructions_full = tk.Label(root, text = 'Please use README.txt file included in software folder for instructions',
                       font = 'Raleway')
instructions_full.grid(columnspan = 3, column = 0, row = 9)

version_sig = tk.Label(root, text = __email__+' --- ver '+__version__+' --- '+__year__,
                       font = 'Raleway')
version_sig.grid(columnspan = 3, column = 0, row = 10)
#canvas = tk.Canvas(root, width = 600, height = 250)
#canvas.grid(columnspan = 3)


## BUTTONS/INPUT ##
input_dir_text = tk.StringVar() #input directory
input_dir_btn = tk.Button(root, textvariable = input_dir_text, command=lambda:input_dir(),
                          fg='black', bg='gray', font='Raleway', height=2, width=15)
input_dir_text.set('Set Input Dir*')
input_dir_btn.grid(column=0, row=1, pady=5)

output_dir_text = tk.StringVar() #output directory
output_dir_btn = tk.Button(root, textvariable = output_dir_text, command=lambda:output_dir(),
                          fg='black', bg='gray', font='Raleway',height=2, width=15)
output_dir_text.set('Set Output Dir*')
output_dir_btn.grid(column=0, row=2, pady=5)

lower_cut_text = tk.StringVar() #output directory
lower_cut_btn = tk.Button(root, textvariable = lower_cut_text, command=lambda:define_low(),
                          fg='black', bg='gray', font='Raleway',height=2, width=15)
lower_cut_text.set('Set Lower Cutoff*')
lower_cut_btn.grid(column=0, row=3, pady=5)

upper_cut_text = tk.StringVar() #output directory
upper_cut_btn = tk.Button(root, textvariable = upper_cut_text, command=lambda:define_up(),
                          fg='black', bg='gray', font='Raleway',height=2, width=15)
upper_cut_text.set('Set Upper Cutoff*')
upper_cut_btn.grid(column=0, row=4, pady=5)

e1 = tk.Entry(root, width=10)
e2 = tk.Entry(root, width=10)

e1.grid(row=3, column=1)
e2.grid(row=4, column=1)


low_range_text = tk.StringVar() #output directory
low_range_btn = tk.Button(root, textvariable = low_range_text, command=lambda:low_range_del(),
                          fg='black', bg='gray', font='Raleway',height=2, width=15)
low_range_text.set('Set Range Neg Val*')
low_range_btn.grid(column=0, row=5, pady=5)

up_range_text = tk.StringVar() #output directory
up_range_btn = tk.Button(root, textvariable = up_range_text, command=lambda:up_range_del(),
                          fg='black', bg='gray', font='Raleway',height=2, width=15)
up_range_text.set('Set Range Pos Val*')
up_range_btn.grid(column=0, row=6, pady=5)

e3 = tk.Entry(root, width=10)
e4 = tk.Entry(root, width=10)

e3.grid(row=5, column=1)
e4.grid(row=6, column=1)

validate_text = tk.StringVar() #validate
validate_btn = tk.Button(root, textvariable = validate_text, command=lambda:validate_acu(),
                          fg='black', bg='gray', font='Raleway', height=2, width=15)
validate_text.set('Validate Format')
validate_btn.grid(column=0, row=7, pady=5)

analyze_text = tk.StringVar() #analyze
analyze_btn = tk.Button(root, textvariable = analyze_text, command=lambda:analyze_acu(),
                          fg='black', bg='gray', font='Raleway', height=2, width=15)
analyze_text.set('Analyze Data')
analyze_btn.grid(column=0, row=8, pady=5)


root.mainloop()
##### END GUI CREATION #####

