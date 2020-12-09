# -*- coding: utf-8 -*-
#TODO: regex-Ausdrücke benutzen, um Spalten zu benennen
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
        self.opened_files_dict : dict =  {}
        
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
        self.main_dataframe = pd.DataFrame()
        self.column_amount : int = 0
        self.__headerSeen:bool = False
                
    def getEncodingsListFunctionality(self):
        return self.encodings_list
    
    def getDataframeFunctionality(self):
        return self.main_dataframe

    def AddtoDict(self, filename:str, encoding:str, dialect):
        if filename.endswith('.csv'):
            if filename in self.opened_files_dict:
                self.opened_files_dict[filename+"_"+str(self.multiple_files_counter)] = [encoding, dialect.delimiter, dialect.quotechar, dialect.skipinitialspace]
                self.multiple_files_counter += 1
            else:
                self.opened_files_dict[filename] = [encoding, dialect.delimiter, dialect.quotechar, dialect.skipinitialspace]
        else:
            print("Only CSV Files are allowed!")
            raise ValueError
        return self.opened_files_dict
    
    def csvSniffer(self, filename: str):
        with open(filename, "r") as sniffing_file:
            read_sniffing_file = sniffing_file.read()
            has_header = csv.Sniffer().has_header(read_sniffing_file)
            dialect = csv.Sniffer().sniff(read_sniffing_file)
            return has_header, dialect
    
    def OpenCSVFiles(self, filename:str, encoding:str = None, delimiter:str = None, quoteChar:str = None, skipInitSpace:bool=None):    
        if filename.endswith("_", -2, -1):
            filename = filename[:-2:]
        if encoding not in self.encodings_list or encoding == None:
            enc = detect(Path(filename).read_bytes())
            encoding = enc["encoding"]
        
        hasSniffHeader, dialect = self.csvSniffer(filename)
        self.AddtoDict(filename, encoding, dialect)
        if delimiter == None:
            delimiter = dialect.delimiter
        if quoteChar == None:
            quoteChar = dialect.quotechar
        if skipInitSpace == None:
            skipInitSpace = dialect.skipinitialspace
        
        if hasSniffHeader:
            header = "infer"             
        else:
            header = None
        
        try:
            new_dataframe = pd.read_csv(filename, encoding=encoding, header=header, sep=delimiter, quotechar=quoteChar, skipinitialspace=skipInitSpace)
            column_amount = len(new_dataframe.columns)
            
            if self.main_dataframe.empty:
                self.main_dataframe = new_dataframe
                self.column_amount = column_amount
            else:
                if self.column_amount is not column_amount:
                    raise ValueError("The csv-Files have different column amounts")
                
                

                if not self.__headerSeen and hasSniffHeader:
                    new_cols = {x: y for x, y in zip(self.main_dataframe, new_dataframe)}
                    self.main_dataframe = self.main_dataframe.rename(columns=new_cols)
                    
                    
                    
                    #TODO: testen, ob bei gleicher spaltenanzahl die typen der spalten unterschiedlich sind
                if self.__headerSeen and not hasSniffHeader:
                    new_cols = {x: y for x, y in zip(new_dataframe, self.main_dataframe)}
                    new_dataframe = new_dataframe.rename(columns=new_cols)
                
                self.main_dataframe = self.main_dataframe.append(new_dataframe)
                
            if not self.__headerSeen and hasSniffHeader: 
                self.__headerSeen = True    
            
        
        except OSError as e:
            self.opened_files_dict.pop(filename)
            raise OSError(e)
        print(self.main_dataframe)
        return self.main_dataframe               
            
    def reset(self):
        self.main_dataframe = pd.DataFrame()
        self.__headerSeen = False
        self.column_amount = 0
        
    def update(self):
        for filename in self.opened_files_dict.keys():
            self.OpenCSVFiles(filename)
                

    def RemoveFilesFunctionality(self, elem_name:str):
        self.opened_files_dict.pop(elem_name)
        return self

    def ClearAllFilesFunctionality(self):
        self.opened_files_dict.clear()
        return self

    def MergeFilesFunctionality(self):
        if len(self.opened_files_dict) == 0:
            showwarning("Warning", "No CSV Files to import selected!")
            return
        return self
    
