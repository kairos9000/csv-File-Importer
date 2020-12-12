import tkinter as tk
import pandas as pd
import io
import csv
import re
from tkinter import ttk 
from pandastable import Table
from tkinter.messagebox import showwarning, showinfo, showerror
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from PyPDF2 import PdfFileWriter, PdfFileReader
from pathlib import Path
from chardet import detect
from math import log, ceil, floor 
import csv_xml_importer as cxi

class csv_importer():
    def __init__(self):
        self.opened_csv_files_list : list =  []
        self.settings_dict : dict = {"hasHeader":None,"wantHeader":False,"Encoding":None,"Delimiter": None, "QuoteChar":None,"skipInitSpace":None,"lineTerminator":None}
        self.multiple_files_counter : int = 0
        self.main_dataframe = pd.DataFrame()
        self.default_header : list = []
        self.column_amount : int = 0
        self.__main_dataframe_has_header:bool = False
        self.main_dataframe_has_default_header:bool = False
        self.importer = cxi.model()
        
    def getDataframeFunctionality(self):
        return self.main_dataframe

    def AddtoList(self, filename:str):
        if filename.endswith('.csv'):
            if filename in self.opened_csv_files_list:
                self.opened_csv_files_list.append(filename+"_"+str(self.multiple_files_counter))
                self.multiple_files_counter += 1
            else:
                self.opened_csv_files_list.append(filename)
        else:
            print("Only CSV Files are allowed!")
            raise ValueError
        return self.opened_csv_files_list
    
    def csvSniffer(self, filename: str):
        with open(filename, "r") as sniffing_file:
            read_sniffing_file = sniffing_file.read()
            has_header = csv.Sniffer().has_header(read_sniffing_file)
            dialect = csv.Sniffer().sniff(read_sniffing_file)
            return has_header, dialect
    
    def import_with_init_settings(self, filename:str, lineTerminator:str = None, notReset:bool=True):
        
        hasSniffHeader, dialect = self.csvSniffer(filename)
        self.settings_dict["hasHeader"] = hasSniffHeader
        enc = detect(Path(filename).read_bytes())
        self.settings_dict["Encoding"] = enc["encoding"]      
        self.settings_dict["Delimiter"] = dialect.delimiter
        self.settings_dict["QuoteChar"] = dialect.quotechar
        self.settings_dict["skipInitSpace"] = dialect.skipinitialspace
        self.settings_dict["lineTerminator"] = lineTerminator
        if notReset:
            self.AddtoList(filename)
        self.OpenCSVFile(filename)
    
    def update_with_personal_settings(self, wantHeader:bool=None, encoding:str=None, Delimiter:str=None, Quotechar:str=None, skipInitSpace:bool=None,lineTerminator:str=None):
        self.reset()
        
        for filename in self.opened_csv_files_list:
            if filename.endswith("_", -2, -1):
                filename = filename[:-2:]
            if wantHeader is not None:
                self.settings_dict["wantHeader"] = wantHeader
            if encoding is not None and encoding in self.importer.encodings_list:
                self.settings_dict["Encoding"] = encoding
            if Delimiter is not None:
                self.settings_dict["Delimiter"] = Delimiter
            if Quotechar is not None:
                self.settings_dict["QuoteChar"] = Quotechar
            if skipInitSpace is not None:
                self.settings_dict["skipInitSpace"] = skipInitSpace
            if lineTerminator is not None:
                self.settings_dict["lineTerminator"] = lineTerminator
                
            self.OpenCSVFile(filename)
            
    def update_header(self, wantHeader:bool=None):
        if wantHeader:
            print(self.main_dataframe)
            return self.main_dataframe
        self.reset()
        for filename in self.opened_csv_files_list:
            if filename.endswith("_", -2, -1):
                filename = filename[:-2:]
            _,dialect = self.csvSniffer(filename)
            new_dataframe = pd.read_csv(filename, header = None, dialect = dialect)
            self.main_dataframe = self.main_dataframe.append(new_dataframe)
        if wantHeader is not None:
            self.settings_dict["wantHeader"] = wantHeader
            
        if not self.settings_dict["wantHeader"]:
            self.default_header = self.importer.find_header_formats(self.main_dataframe)
            main_dataframe_columns = list(self.main_dataframe.columns)
            default_cols = {x: y for x, y in zip(main_dataframe_columns, self.default_header)}
            self.main_dataframe = self.main_dataframe.rename(columns=default_cols)
            
        print(self.main_dataframe)
        return self.main_dataframe
    
    def OpenCSVFile(self, filename:str):    
        
        if self.settings_dict["hasHeader"]:
            header = "infer"             
        else:
            header = None
        
        try:
            new_dataframe = pd.read_csv(filename, encoding=self.settings_dict["Encoding"], header=header, sep=self.settings_dict["Delimiter"], quotechar= self.settings_dict["QuoteChar"],
                                        skipinitialspace=self.settings_dict["skipInitSpace"], lineterminator=self.settings_dict["lineTerminator"])
            column_amount = len(new_dataframe.columns)
        
        except OSError as e:
            self.opened_csv_files_list.pop(filename)
            raise OSError(e)
        
        self.main_dataframe = self.importer.ImportFile(new_dataframe, column_amount,self.settings_dict["hasHeader"])
        print(self.main_dataframe)
        return self.main_dataframe
        
                
    def reset(self):
        self.main_dataframe = pd.DataFrame()
        self.__main_dataframe_has_header = False
        self.column_amount = 0
        self.default_header = []            
               
    
    def RemoveFilesFunctionality(self, elem_name:str):
        self.opened_csv_files_list.remove(elem_name)
        return self

    def ClearAllFilesFunctionality(self):
        self.opened_csv_files_list.clear()
        return self

    def ExportFilesFunctionality(self):
        if len(self.opened_csv_files_list) == 0:
            showwarning("Warning", "No CSV Files to import selected!")
            return
        return self