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
#TODO: Header von XML Dateien erkennen können
#TODO: dict für die Dateien anlegen, da jede Datei ihre eigenen Parameter braucht
#TODO: Parameter von XSL Stylesheet durch GUI änderbar machen durch Parameter Werte Paar => Listbox mit Parametern, einlesen durch Klasse und ausgeben in Listbox und dann Parameter durch Entry änderbar machen

class reader():
    def __init__(self):
        self.opened_csv_files_list : list =  []
        self.settings_csv_dict : dict = {"hasHeader":None,"wantHeader":False,"Encoding":None,"Delimiter": None, "QuoteChar":None,"skipInitSpace":None,"lineTerminator":None}        
        self.opened_xml_files_list : list =  []
        self.settings_xml_dict : dict = {}
        self.multiple_files_counter : int = 0
        self.main_dataframe = pd.DataFrame()
        self.default_header : list = []
        self.column_amount : int = 0
        self.__main_dataframe_has_header:bool = False
        self.main_dataframe_has_default_header:bool = False
        self.importer = cxi.model()
        self.parameters_len:int = 0
        
    def getDataframeFunctionality(self):
        return self.main_dataframe
    
    def AddtoCSVList(self, filename:str):
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
    
    def AddtoXMLList(self, filename:str):
        if filename.endswith('.xml'):
            if filename in self.opened_xml_files_list:
                self.opened_xml_files_list.append(filename+"_"+str(self.multiple_files_counter))
                self.multiple_files_counter += 1
            else:
                self.opened_xml_files_list.append(filename)
        else:
            print("Only XML Files are allowed!")
            raise ValueError
        return self.opened_xml_files_list
    
    def csvSniffer(self, filename: str):
        with open(filename, "r") as sniffing_file:
            read_sniffing_file = sniffing_file.read()
            has_header = csv.Sniffer().has_header(read_sniffing_file)
            dialect = csv.Sniffer().sniff(read_sniffing_file)
            return has_header, dialect
    
    def import_with_init_settings(self, filename:str, xsl_file:str=None, notReset:bool=True):
        if filename.endswith("_", -2, -1):
            filename = filename[:-2:]
        
        if filename.endswith('.csv'):
            hasSniffHeader, dialect = self.csvSniffer(filename)
            self.settings_csv_dict["hasHeader"] = hasSniffHeader
            enc = detect(Path(filename).read_bytes())
            self.settings_csv_dict["Encoding"] = enc["encoding"]      
            self.settings_csv_dict["Delimiter"] = dialect.delimiter
            self.settings_csv_dict["QuoteChar"] = dialect.quotechar
            self.settings_csv_dict["skipInitSpace"] = dialect.skipinitialspace
            self.OpenCSVFile(filename)
            if notReset:
                self.AddtoCSVList(filename)
                
            
        if filename.endswith('.xml'):
            if xsl_file == None:
                print("Choose XSL File to continue")
            elif xsl_file.endswith(".xsl"): 
                self.getXMLParameters(xsl_file)             
                self.OpenXMLFile(filename, xsl_file, True)
            if notReset:
                self.AddtoXMLList(filename)
            
        
    
    def update_csv_with_personal_settings(self, filename:str, wantHeader:bool=None, encoding:str=None, Delimiter:str=None, Quotechar:str=None, skipInitSpace:bool=None,lineTerminator:str=None):
        self.reset()
        
        for other_filenames in self.opened_csv_files_list:
            if other_filenames == filename:
                if filename.endswith("_", -2, -1):
                    tmp_filename = filename[:-2:]
                else:
                    tmp_filename = filename
                if wantHeader is not None:
                    self.settings_csv_dict["wantHeader"] = wantHeader
                if encoding is not None and encoding in self.importer.encodings_list:
                    self.settings_csv_dict["Encoding"] = encoding
                if Delimiter is not None:
                    self.settings_csv_dict["Delimiter"] = Delimiter
                if Quotechar is not None:
                    self.settings_csv_dict["QuoteChar"] = Quotechar
                if skipInitSpace is not None:
                    self.settings_csv_dict["skipInitSpace"] = skipInitSpace
                if lineTerminator is not None:
                    self.settings_csv_dict["lineTerminator"] = lineTerminator
                self.OpenCSVFile(tmp_filename)
            else:
                self.import_with_init_settings(other_filenames, False)
                
            
            
    def update_header(self, wantHeader:bool=None):
        if wantHeader:
            print(self.main_dataframe)
            return self.main_dataframe
        self.reset()
        for filename in self.opened_csv_files_list:
            if filename.endswith("_", -2, -1):
                tmp_filename = filename[:-2:]
            else:
                tmp_filename = filename
            _,dialect = self.csvSniffer(tmp_filename)
            new_dataframe = pd.read_csv(tmp_filename, header = None, dialect = dialect)
            self.main_dataframe = self.main_dataframe.append(new_dataframe)
        if wantHeader is not None:
            self.settings_csv_dict["wantHeader"] = wantHeader
            
        if not self.settings_csv_dict["wantHeader"]:
            self.default_header = self.importer.find_header_formats(self.main_dataframe)
            main_dataframe_columns = list(self.main_dataframe.columns)
            default_cols = {x: y for x, y in zip(main_dataframe_columns, self.default_header)}
            self.main_dataframe = self.main_dataframe.rename(columns=default_cols)
            
        print(self.main_dataframe)
        return self.main_dataframe
    
    def OpenCSVFile(self, filename:str):    
        if self.settings_csv_dict["hasHeader"]:
            header = "infer"             
        else:
            header = None
        
        try:
            new_dataframe = pd.read_csv(filename, encoding=self.settings_csv_dict["Encoding"], header=header, sep=self.settings_csv_dict["Delimiter"], quotechar= self.settings_csv_dict["QuoteChar"],
                                        skipinitialspace=self.settings_csv_dict["skipInitSpace"], lineterminator=self.settings_csv_dict["lineTerminator"])
            column_amount = len(new_dataframe.columns)
        
        
            self.main_dataframe = self.importer.ImportFile(new_dataframe, column_amount,self.settings_csv_dict["hasHeader"])
        
        except OSError as e:
            self.opened_csv_files_list.pop(filename)
            raise OSError(e)
        
        except ValueError as value_error:
            print(value_error)
            return

        except ImportError as import_error:
            print(import_error)
        print(self.main_dataframe)
        return self.main_dataframe
    
    def getXMLParameters(self, xsl_file):
        tree = ET.parse(xsl_file)
        root = tree.getroot()
        param_matches = [c.attrib for c in root if 'param' in c.tag]
        self.parameters_len = len(param_matches)
        for index,_ in enumerate(param_matches):
            self.settings_xml_dict[param_matches[index]["name"]] = param_matches[index]["select"]
        self.settings_xml_dict["xsl_file"] = xsl_file
        return self.settings_xml_dict
    
    def addXMLParameter(self, filename:str, param:str, value:str):       
        if self.settings_xml_dict:
            if param in self.settings_xml_dict.keys():
                self.settings_xml_dict[param] = "'"+value+"'"
                self.OpenXMLFile(filename, self.settings_xml_dict["xsl_file"], False)
            else:
                print("Parameter could not be found in XSL-Stylesheet")
            

             
        
        
    
    def OpenXMLFile(self, filename, xsl_file:str, init:bool):
        try:
            try:
                xmldoc = etree.parse(filename)
            except lxml.etree.ParseError as parse_error:
                print(parse_error)
                return
            try:
                transformer = etree.XSLT(etree.parse(xsl_file))
            except lxml.etree.XSLTParseError as xsl_parse_error:
                print(xsl_parse_error)
                return

            if not init:
                tmp_parameters_list = ["","","",""]
                tmp_values_list = ["","","",""]
                tmp_settings_list = list(self.settings_xml_dict)
                for i in range(self.parameters_len):
                    tmp_parameters_list[i] = tmp_settings_list[i]
                    tmp_values_list[i] = self.settings_xml_dict[tmp_settings_list[i]]
                print(tmp_values_list, tmp_parameters_list)
                try:
                    result = str(transformer(xmldoc, **{tmp_parameters_list[0]: tmp_values_list[0]}, **{tmp_parameters_list[1]: tmp_values_list[1]},
                                        **{tmp_parameters_list[2]: tmp_values_list[2]}))
                except etree.XSLTApplyError as apply_error:
                    print(apply_error)
                
            
            else: 
                result = str(transformer(xmldoc))
            reader = csv.reader(result.splitlines(), delimiter=',')
            list_reader = list(reader)
            
            column_amount = len(list_reader[0])
            column_names = list_reader.pop(0)#None
            self.settings_xml_dict["hasHeader"] = True
            new_dataframe = pd.DataFrame(list_reader, columns=column_names)
        
            
            self.main_dataframe = self.importer.ImportFile(new_dataframe, column_amount,self.settings_xml_dict["hasHeader"])
        
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
        if elem_name.endswith("_", -2, -1):
            elem_name = elem_name[:-2:]
        if elem_name.endswith('.csv'):
            self.opened_csv_files_list.remove(elem_name)
        if elem_name.endswith('.xml'):
            self.opened_xml_files_list.remove(elem_name)
        return self

    def ClearAllFilesFunctionality(self):
        self.opened_csv_files_list.clear()
        self.opened_xml_files_list.clear()
        return self

    def ExportFilesFunctionality(self):
        if len(self.opened_csv_files_list) == 0:
            showwarning("Warning", "No CSV Files to import selected!")
        if len(self.opened_xml_files_list) == 0:
            showwarning("Warning", "No XML Files to import selected!")

        return self