# -*- coding: utf-8 -*-
#TODO: mit csv-Sniffer auseinandersetzen
#TODO: Parameter von csv-Dateien ändern können
#TODO: XML-Dateien einlesen können über xsl-Stylsheet
#TODO: verschiedene Ausgaben realisieren

import tkinter as tk
import pandas as pd
import io
from tkinter import ttk 
from pandastable import Table
from tkinter.messagebox import showwarning, showinfo, showerror
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from PyPDF2 import PdfFileWriter, PdfFileReader


class model():
    """This class provides the functionality of the project according to the 
    model-view-separation principle"""

    def __init__(self):
        self.opened_files_arr = []
        
        self.multiple_files_counter = 0
        self.encodings_list = ["UTF-8", "UTF-16", "UTF-32", "ASCII",
                               "ISO-8859-1", "ISO-8859-2", "ISO-8859-5", "ISO-8859-7", "ISO-8859-8", "ISO-2022-CN", "ISO-2022-KR", "ISO-2022-JP",
                               "windows-1251",  "windows-1250", "windows-1251",  "windows-1252", "windows-1253",  "windows-1255", 
                               "GB2312", "GB18030", 
                               "Big5",
                               "EUC-KR", "EUC-TW", "EUC-JP",
                               "HZ-GB-2312",
                               "SHIFT_JIS",  
                               "KOI8-R",
                               "MacCyrillic",
                               "IBM855", "IBM866",
                               "TIS-620"
                                ]
        self.csv_file = pd.DataFrame()
                
    def getEncodingsListFunctionality(self):
        return self.encodings_list
    
    def getDataframeFunctionality(self):
        return self.csv_file

    def ShowFilesFunctionality(self, filename):
        if filename.endswith('.csv'):
            if filename in self.opened_files_arr:
                self.opened_files_arr.append(
                    filename+"_"+str(self.multiple_files_counter))
                self.multiple_files_counter += 1
            else:
                self.opened_files_arr.append(filename)
        else:
            print("Only CSV Files are allowed!")
            raise ValueError
        return self.opened_files_arr
    
    def OpenFilesFunctionality(self, encoding="UTF-8"):
        if encoding not in self.encodings_list:
            print("""Encoding could not be identified;
                  call .getEncodingsListFunctionality() to see a list of possible encodings.""")
            return
        
        for filename in self.opened_files_arr:
            if filename.endswith("_", -2, -1):
                filename = filename[:-2:]
            try:
                new_csv_file = pd.read_csv(filename, encoding=encoding, header=None)
                self.csv_file = pd.concat([self.csv_file, new_csv_file])
                
            
            except OSError as e:
                self.opened_files_arr.remove(filename)
                raise OSError(e)
        return self.csv_file               
            
            

    def RemoveFilesFunctionality(self, elem_name):
        self.opened_files_arr.remove(elem_name)
        return self

    def ClearAllFilesFunctionality(self):
        self.opened_files_arr.clear()
        return self

    def MergeFilesFunctionality(self):
        if len(self.opened_files_arr) == 0:
            showwarning("Warning", "No CSV Files to import selected!")
            return
        # save_file = asksaveasfilename(defaultextension=".csv",
        #                               filetypes=[("CSV file", "*.csv")],
        #                               initialfile="import.csv")
        # pdfWriter = PdfFileWriter()

        # for filename in self.__opened_files_arr:
        #     if filename.endswith("_", -2, -1):
        #         filename = filename[:-2:]

        #     pdfFileObj = open(filename, 'rb')
        #     pdfReader = PdfFileReader(pdfFileObj)

        #     for pageNum in range(pdfReader.numPages):
        #         pageObj = pdfReader.getPage(pageNum)
        #         pdfWriter.addPage(pageObj)

        # if save_file == "":
        #     return
        # pdfOutput = open(save_file, 'wb')
        # pdfWriter.write(pdfOutput)
        # pdfOutput.close()
        return self