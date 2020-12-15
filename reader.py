# -*- coding: utf-8 -*-#

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
import lxml.etree
from lxml import etree
import xml.etree.ElementTree as ET
#TODO: dict für die Dateien anlegen, da jede Datei ihre eigenen Parameter braucht
#TODO: verschiedene Ausgaben realisieren    

class reader():
    def __init__(self):
        self.opened_files_dict : dict = {}
        #self.opened_csv_files_list : list =  []
       #self.settings_csv_dict : dict = {"hasHeader":None,"wantHeader":False,"Encoding":None,"Delimiter": None, "QuoteChar":None,"skipInitSpace":None,"lineTerminator":None}        
        #self.opened_xml_files_list : list =  []
        #self.settings_xml_dict : dict = {}
        self.multiple_files_counter : int = 0
        self.main_dataframe = pd.DataFrame()
        self.default_header : list = []
        self.column_amount : int = 0
        self.__main_dataframe_has_header:bool = False
        self.main_dataframe_has_default_header:bool = False
        self.importer = cxi.model()
        #self.parameters_len:int = 0
        
    def getDataframeFunctionality(self):
        return self.main_dataframe
    
    def addToFilesDict(self, filename:str):
        if filename.endswith('.csv'):
            csv_file_parameter_dict = {"hasHeader":None,
                                        "wantHeader":False,
                                        "Encoding":None,
                                        "Delimiter": None,
                                        "QuoteChar":None,
                                        "skipInitSpace":None,
                                        "lineTerminator":None}
            if filename in self.opened_files_dict:
                self.opened_files_dict[filename+"_"+str(self.multiple_files_counter)] = csv_file_parameter_dict
            else:
                self.opened_files_dict[filename] = csv_file_parameter_dict
        # else:
        #     print("Only CSV Files are allowed!")
        #     raise ValueError
        elif filename.endswith('.xml'):
            if filename in self.opened_files_dict:
                self.opened_files_dict[filename+"_"+str(self.multiple_files_counter)] = {}
            else:
                self.opened_files_dict[filename] = {}
        else:
            print("Only XML or CSV Files are allowed!")
            raise ValueError
        return self.opened_files_dict
    
    # def AddtoXMLList(self, filename:str):
    #     if filename.endswith('.xml'):
    #         if filename in self.opened_xml_files_list:
    #             self.opened_xml_files_list.append(filename+"_"+str(self.multiple_files_counter))
    #             self.multiple_files_counter += 1
    #         else:
    #             self.opened_xml_files_list.append(filename)
    #     else:
    #         print("Only XML Files are allowed!")
    #         raise ValueError
    #     return self.opened_xml_files_list
    
    def csvSniffer(self, filename: str):
        with open(filename, "r") as sniffing_file:
            read_sniffing_file = sniffing_file.read()
            has_header = csv.Sniffer().has_header(read_sniffing_file)
            dialect = csv.Sniffer().sniff(read_sniffing_file)
            return has_header, dialect
    
    def import_with_init_settings(self, filename:str, xsl_file:str=None, notReset:bool=True):    
        if notReset:
            self.addToFilesDict(filename)
        if filename.endswith("_", -2, -1):
            tmp_filename = filename[:-2:]
        else:
            tmp_filename = filename
        if tmp_filename.endswith('.csv'):
            hasSniffHeader, dialect = self.csvSniffer(tmp_filename)
            self.opened_files_dict[tmp_filename]["hasHeader"] = hasSniffHeader
            enc = detect(Path(tmp_filename).read_bytes())
            self.opened_files_dict[tmp_filename]["Encoding"] = enc["encoding"]      
            self.opened_files_dict[tmp_filename]["Delimiter"] = dialect.delimiter
            self.opened_files_dict[tmp_filename]["QuoteChar"] = dialect.quotechar
            self.opened_files_dict[tmp_filename]["skipInitSpace"] = dialect.skipinitialspace
            self.OpenCSVFile(tmp_filename)
            
                
            
        if tmp_filename.endswith('.xml'):
            if xsl_file == None:
                print("Choose XSL File to continue")
            elif xsl_file.endswith(".xsl"): 
                self.getXMLParameters(tmp_filename, xsl_file)             
                self.OpenXMLFile(tmp_filename, True)
            # if notReset:
            #     self.AddtoXMLList(filename)
            
    def update_dataframe(self):
        self.reset()
        self.importer.reset()
        for filename in self.opened_files_dict.keys():
            if filename.endswith("_", -2, -1):
                tmp_filename = filename[:-2:]
            else:
                tmp_filename = filename
            if tmp_filename.endswith(".csv"):
                self.OpenCSVFile(tmp_filename)  
                self.update_header(tmp_filename, self.opened_files_dict[tmp_filename]["wantHeader"])
            if tmp_filename.endswith(".xml"):
                self.OpenXMLFile(tmp_filename, False)
                #self.update_header(tmp_filename, False)
                
    
    def update_csv_with_personal_settings(self, filename:str, wantHeader:bool=None, encoding:str=None, Delimiter:str=None, Quotechar:str=None, skipInitSpace:bool=None,lineTerminator:str=None):
        #self.reset()     
        for other_filenames in self.opened_files_dict.keys():
            if other_filenames == filename:
                if filename.endswith("_", -2, -1):
                    tmp_filename = filename[:-2:]
                else:
                    tmp_filename = filename
                if filename.endswith(".csv"):
                    if wantHeader is not None:
                        self.opened_files_dict[tmp_filename]["wantHeader"] = wantHeader
                    if encoding is not None and encoding in self.importer.encodings_list:
                        self.opened_files_dict[tmp_filename]["Encoding"] = encoding
                    if Delimiter is not None:
                        self.opened_files_dict[tmp_filename]["Delimiter"] = Delimiter
                    if Quotechar is not None:
                        self.opened_files_dict[tmp_filename]["QuoteChar"] = Quotechar
                    if skipInitSpace is not None:
                        self.opened_files_dict[tmp_filename]["skipInitSpace"] = skipInitSpace
                    if lineTerminator is not None:
                        self.opened_files_dict[tmp_filename]["lineTerminator"] = lineTerminator
                    #self.OpenCSVFile(tmp_filename)
                else:
                    print("This method is for updating csv Files with personal Parameters only")
        self.update_dataframe()
            # else:
            #     self.import_with_init_settings(other_filenames, False)
                
            
            
    def update_header(self, filename:str, wantHeader:bool=None):
        if not wantHeader:
            try:
                self.default_header = self.importer.find_header_formats(self.main_dataframe)
            except ImportError as import_error:
                print(import_error)
                return
            main_dataframe_columns = list(self.main_dataframe.columns)
            default_cols = {x: y for x, y in zip(main_dataframe_columns, self.default_header)}
            self.main_dataframe = self.main_dataframe.rename(columns=default_cols)

        else:
            if self.opened_files_dict[filename]["hasHeader"]:
                new_dataframe = pd.read_csv(filename,
                                            header = None,
                                            encoding=self.opened_files_dict[filename]["Encoding"],
                                            sep=self.opened_files_dict[filename]["Delimiter"],
                                            quotechar= self.opened_files_dict[filename]["QuoteChar"],
                                            skipinitialspace=self.opened_files_dict[filename]["skipInitSpace"],
                                            lineterminator=self.opened_files_dict[filename]["lineTerminator"])
                new_header_list = list(new_dataframe.iloc[0])
                main_dataframe_columns = list(self.main_dataframe.columns)
                new_cols = {x: y for x, y in zip(main_dataframe_columns, new_header_list)}
                self.main_dataframe = self.main_dataframe.rename(columns=new_cols)
            else:
                print("File has no header to select")
            # for filename in self.opened_csv_files_list:
            #     if filename.endswith("_", -2, -1):
            #         tmp_filename = filename[:-2:]
            #     else:
            #         tmp_filename = filename
            #     _,dialect = self.csvSniffer(tmp_filename)
            #     new_dataframe = pd.read_csv(tmp_filename, header = None, dialect = dialect)
            #     self.main_dataframe = self.main_dataframe.append(new_dataframe)
            # if wantHeader is not None:
            #     self.settings_csv_dict["wantHeader"] = wantHeader
                
            # if not self.settings_csv_dict["wantHeader"]:
            #     self.default_header = self.importer.find_header_formats(self.main_dataframe)
            #     main_dataframe_columns = list(self.main_dataframe.columns)
            #     default_cols = {x: y for x, y in zip(main_dataframe_columns, self.default_header)}
            #     self.main_dataframe = self.main_dataframe.rename(columns=default_cols)
        
    
    def OpenCSVFile(self, filename:str):    
        if self.opened_files_dict[filename]["hasHeader"]:
            header = "infer"             
        else:
            header = None
        
        try:
            new_dataframe = pd.read_csv(filename,
                                        header = header,
                                        encoding=self.opened_files_dict[filename]["Encoding"],
                                        sep=self.opened_files_dict[filename]["Delimiter"],
                                        quotechar= self.opened_files_dict[filename]["QuoteChar"],
                                        skipinitialspace=self.opened_files_dict[filename]["skipInitSpace"],
                                        lineterminator=self.opened_files_dict[filename]["lineTerminator"])
            column_amount = len(new_dataframe.columns)
        
        
            self.main_dataframe = self.importer.ImportFile(new_dataframe, column_amount, self.opened_files_dict[filename]["hasHeader"])
        
        except OSError as e:
            self.opened_files_dict.pop(filename)
            raise OSError(e)
        
        except ValueError as value_error:
            print(value_error)
            return

        except ImportError as import_error:
            print(import_error)
        print(self.main_dataframe)
        return self.main_dataframe
    
    def getXMLParameters(self, filename:str, xsl_file:str):
        tree = ET.parse(xsl_file)
        root = tree.getroot()
        param_matches = [c.attrib for c in root if 'param' in c.tag]
        #self.parameters_len = len(param_matches)
        for index,_ in enumerate(param_matches):
            self.opened_files_dict[filename][param_matches[index]["name"]] = param_matches[index]["select"]
        self.opened_files_dict[filename]["xsl_file"] = xsl_file
        self.opened_files_dict[filename]["parameters_len"] = len(param_matches)
    
    def addXMLParameter(self, filename:str, param:str, value:str):  
        if filename in self.opened_files_dict.keys():
            if filename.endswith("_", -2, -1):
                tmp_filename = filename[:-2:]
                if not tmp_filename.endswith(".xml"):
                    print("This method is for updating xml Files with personal Parameters only")
                    return
                 
            if param in self.opened_files_dict[filename].keys():
                self.opened_files_dict[filename][param] = "'"+value+"'"
                self.update_dataframe()
                #self.OpenXMLFile(filename, self.settings_xml_dict["xsl_file"], False)
            else:
                print("Parameter could not be found in XSL-Stylesheet")
        else:
            print("XML-File is not in List")
            

             
        
        
    
    def OpenXMLFile(self, filename, init:bool):
        try:
            try:
                xmldoc = etree.parse(filename)
            except lxml.etree.ParseError as parse_error:
                print(parse_error)
                return
            try:
                transformer = etree.XSLT(etree.parse(self.opened_files_dict[filename]["xsl_file"]))
            except lxml.etree.XSLTParseError as xsl_parse_error:
                print(xsl_parse_error)
                return

            if not init:
                parameters = {}
                tmp_settings_list = list(self.opened_files_dict[filename])

                for i in range(self.opened_files_dict[filename]["parameters_len"]):
                    key = tmp_settings_list[i]
                    if len(key) > 0:
                        value = self.opened_files_dict[filename][key]
                        parameters[key] = value


                try:
                    result = str(transformer(xmldoc, **parameters))
                except etree.XSLTApplyError as apply_error:
                    print(apply_error)
                
            
            else: 
                result = str(transformer(xmldoc))
            reader = csv.reader(result.splitlines(), delimiter=',')
            list_reader = list(reader)
            column_amount = len(list_reader[0])
            
            header_regex_list = []
            header_regex_list = self.importer.regex_list_filler(header_regex_list, list_reader[0])
            splice_len = 1
            string_splice_len = splice_len + 1
            for i, header_column_name in enumerate(header_regex_list):
                header_regex_list[i] = header_column_name[string_splice_len:]
                splice_len += 1
                string_splice_len = ceil(log(splice_len, 10)+1)
                
            if any(column != "String" for column in header_regex_list):
                self.opened_files_dict[filename]["hasHeader"] = False
                column_names = None            
            else:
                self.opened_files_dict[filename]["hasHeader"] = True              
                column_names = list_reader.pop(0)
            
            new_dataframe = pd.DataFrame(list_reader, columns=column_names)
        
            
            self.main_dataframe = self.importer.ImportFile(new_dataframe, column_amount,self.opened_files_dict[filename]["hasHeader"])
        
        except OSError as os:
            print(os)
            
        except lxml.etree.XSLTApplyError as transform_error:
            print(transform_error)
            
        except ValueError as value_error:
            print(value_error)
            return

        print(self.main_dataframe)
        return self.main_dataframe
        
                
    def reset(self):
        self.main_dataframe = pd.DataFrame()
        self.__main_dataframe_has_header = False
        self.column_amount = 0
        self.default_header = []            
               
    
    def RemoveFilesFunctionality(self, elem_name:str):
        self.opened_files_dict.pop(elem_name)
        # if elem_name.endswith("_", -2, -1):
        #     elem_name = elem_name[:-2:]
        # if elem_name.endswith('.csv'):
        #     self.opened_csv_files_list.remove(elem_name)
        # if elem_name.endswith('.xml'):
        #     self.opened_xml_files_list.remove(elem_name)
        return self

    def ClearAllFilesFunctionality(self):
        # self.opened_csv_files_list.clear()
        # self.opened_xml_files_list.clear()
        self.opened_files_dict.clear()
        return self

    def ExportFilesFunctionality(self):
        if len(self.opened_files_dict) == 0:
            showwarning("Warning", "No CSV Files to import selected!")
        if len(self.opened_files_dict) == 0:
            showwarning("Warning", "No XML Files to import selected!")

        return self