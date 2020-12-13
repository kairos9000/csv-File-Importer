# -*- coding: utf-8 -*-#
#TODO: verschiedene Ausgaben realisieren

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


class model():
    """This class provides the functionality of the project according to the 
    model-view-separation principle"""

    def __init__(self):
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
        self.types_dict : dict = {
                        "Integer": re.compile(
                            r"^\d+$"
                        ),
                        "Float": re.compile(
                            r"^\d+(\.|\,)\d+$"
                        ),
                        "Coordinate": re.compile(
                            r"^(N|S)?0*\d{1,2}°0*\d{1,2}(′|')0*\d{1,2}\.\d*(″|\")(?(1)|(N|S)) (E|W)?0*\d{1,2}°0*\d{1,2}(′|')0*\d{1,2}\.\d*(″|\")(?(5)|(E|W))$"
                        ),
                        "Email": re.compile(
                            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                        ),                       
                        "Time": re.compile(
                            r"^([0-1]\d|2[0-3]):[0-5]\d(:[0-5]\d)*$"
                        ),
                        "Date": re.compile(
                            r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$"
                        ),
                        "Datetime": re.compile(
                            r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2}).([0-1]\d|2[0-3]):[0-5]\d(:[0-5]\d)*$"
                        ),
                        "Web-URL": re.compile(
                            r"^((ftp|http|https):\/\/)?(www\.)?(ftp|http|https|www\.)?([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-]+)+((\/)([\w].*)+(#|\?)*)*((\/)*\w+\?[a-zA-Z0-9_]+=\w+(&[a-zA-Z0-9_]+=\w+)*)?$"
                        ),               
                        "Bool": re.compile(
                            r"^(True|true|TRUE|Wahr|wahr|WAHR|False|false|FALSE|Falsch|falsch|FALSCH)$"
                        )      
                    }
        self.main_dataframe = pd.DataFrame()
        self.default_header : list = []
        self.column_amount : int = 0
        self.__main_dataframe_has_header:bool = False
        self.main_dataframe_has_default_header:bool = False
                
    def getEncodingsListFunctionality(self):
        return self.encodings_list
    
    
    
    def ImportFile(self, new_dataframe:pd.DataFrame, column_amount:int, hasHeader:bool):    
            
        if self.main_dataframe.empty:
            self.main_dataframe = new_dataframe
            self.column_amount = column_amount
        else:
            if self.column_amount is not column_amount:
                raise ValueError("The Files have different column amounts")
            
            type_list_new_dataframe = list(new_dataframe.iloc[1])
            type_list_main_dataframe = list(self.main_dataframe.iloc[1])
            regex_types_new_dataframe = []
            regex_types_main_dataframe = []
            compare_list_new_dataframe = []
            compare_list_main_dataframe = []
            regex_types_new_dataframe = self.regex_list_filler(regex_types_new_dataframe, type_list_new_dataframe)
            regex_types_main_dataframe = self.regex_list_filler(regex_types_main_dataframe, type_list_main_dataframe)
            splice_len = 1
            string_splice_len = splice_len + 1
            for item_new, item_main in zip(regex_types_new_dataframe,regex_types_main_dataframe):
                item_new = item_new[string_splice_len:]
                item_main = item_main[string_splice_len:]
                splice_len += 1
                string_splice_len = ceil(log(splice_len, 10)+1)
                compare_list_new_dataframe.append(item_new)
                compare_list_main_dataframe.append(item_main)
            if sorted(compare_list_new_dataframe) != sorted(compare_list_main_dataframe):
                raise ValueError("The Types of the Dataframes are not compatible")
                
                

            if not self.__main_dataframe_has_header and hasHeader:
                new_cols = {x: y for x, y in zip(self.main_dataframe, new_dataframe)}
                self.main_dataframe = self.main_dataframe.rename(columns=new_cols)
                

            if self.__main_dataframe_has_header and not hasHeader:
                new_cols = {x: y for x, y in zip(new_dataframe, self.main_dataframe)}
                new_dataframe = new_dataframe.rename(columns=new_cols)

            self.main_dataframe = self.main_dataframe.append(new_dataframe)
            
        
            
            
        if not self.__main_dataframe_has_header:
            self.default_header = self.find_header_formats(self.main_dataframe)
            main_dataframe_columns = list(self.main_dataframe.columns)
            default_cols = {x: y for x, y in zip(main_dataframe_columns, self.default_header)}
            self.main_dataframe = self.main_dataframe.rename(columns=default_cols)
        
        self.__main_dataframe_has_header = True
                   
        return self.main_dataframe               
            
    def reset(self):
        self.main_dataframe = pd.DataFrame()
        self.__main_dataframe_has_header = False
        self.column_amount = 0
        self.default_header = []
    
    def find_header_formats(self, dataframe):
        row_counter = 0
        first_row = True
        type_lists_dict = {"first_row":[],"second_row":[],"third_row":[],"fourth_row":[],"fifth_row":[]}
        iter_type_lists_dict = iter(type_lists_dict)
        key = next(iter_type_lists_dict)
        for _, row in self.main_dataframe.iterrows():
            if not self.__main_dataframe_has_header and first_row:
                first_row = False
                continue
            
            row_list = list(row)
            type_lists_dict[key] = self.regex_list_filler(type_lists_dict[key], row_list)
            if row_counter >= 4:
                break  
            key = next(iter_type_lists_dict) 
                  
            row_counter += 1
            
        key_list = type_lists_dict["first_row"]
        for key in type_lists_dict.keys():
            if key_list != type_lists_dict[key]:
                raise ImportError("The column formats are not consistent")
                
        return key_list
    
    
    def regex_list_filler(self, regex_list, row):
        column_counter = 0
        for elem in row:
            elem = str(elem).strip()
            regex_type = self.regex_tester(elem)
            regex_list.append(str(column_counter)+"_"+ regex_type)
            column_counter += 1
        
        return regex_list
    
    def regex_tester(self, elem):
        for key in self.types_dict.keys():
            match = self.types_dict[key].fullmatch(elem)
            if match:
                return key
        return "String"

    
