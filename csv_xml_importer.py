# -*- coding: utf-8 -*-
#TODO: Parameter von csv-Dateien ändern können
#TODO: XML-Dateien einlesen können über xsl-Stylsheet
#TODO: verschiedene Ausgaben realisieren

import tkinter as tk
import pandas as pd
import io
import csv
from tkinter import ttk 
from pandastable import Table
from tkinter.messagebox import showwarning, showinfo, showerror
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from PyPDF2 import PdfFileWriter, PdfFileReader
from pathlib import Path
from chardet import detect


class model():
    """This class provides the functionality of the project according to the 
    model-view-separation principle"""

    def __init__(self):
        self.opened_files_arr : list =  []
        
        self.multiple_files_counter : int = 0
        self.encodings_list : list = ["UTF-8", "UTF-16", "UTF-32", "ASCII",
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
        self.csv_file : pd.DataFrame()
        self.column_amount : int = 0
                
    def getEncodingsListFunctionality(self):
        return self.encodings_list
    
    def getDataframeFunctionality(self):
        return self.csv_file

    def ImportCSVFiles(self, filename:str):
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
    
    def csvSniffer(self, filename: str):
        with open(filename, "r") as sniffing_file:
            header_line = sniffing_file.readline()
            has_header = csv.Sniffer().has_header(header_line)
            dialect = csv.Sniffer().sniff(sniffing_file.read(1024))
            return has_header, dialect
    
    def OpenCSVFiles(self, encoding:str = None, hasHeader:bool = None):
        self.csv_file = None
        for filename in self.opened_files_arr:
            if encoding not in self.encodings_list or encoding == None:
                print("No encoding or not available encoding chosen; encoding will be guessed from File")
                enc = detect(Path(filename).read_bytes())
                encoding = enc["encoding"]
            hasSniffHeader, dialect = self.csvSniffer(filename)
            print(dialect.delimiter)
            if not hasHeader:
                header = None
            elif hasSniffHeader or hasHeader:
                header = "infer"
            else:
                header = None

            if filename.endswith("_", -2, -1):
                filename = filename[:-2:]
            try:
                new_csv_file = pd.read_csv(filename, encoding=encoding, header=header, dialect=dialect)
                column_amount = len(new_csv_file.columns)
                
                if self.csv_file == None:
                    self.csv_file = new_csv_file
                    self.column_amount = column_amount
                else:
                    if self.column_amount is not column_amount:
                        raise ValueError("The csv-Files have different column amounts")
                    else:
                        self.csv_file = self.csv_file.append(new_csv_file)
                
            
            except OSError as e:
                self.opened_files_arr.remove(filename)
                raise OSError(e)
        return self.csv_file               
            
            

    def RemoveFilesFunctionality(self, elem_name:str):
        self.opened_files_arr.remove(elem_name)
        return self

    def ClearAllFilesFunctionality(self):
        self.opened_files_arr.clear()
        return self

    def MergeFilesFunctionality(self):
        if len(self.opened_files_arr) == 0:
            showwarning("Warning", "No CSV Files to import selected!")
            return
        return self
    
