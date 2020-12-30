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


class reader():
    def __init__(self):
        self.opened_files_dict : dict = {}
        self.multiple_files_counter : int = 0
        self.main_dataframe = pd.DataFrame()
        self.default_header : list = []
        self.column_amount : int = 0
        self.__main_dataframe_has_header:bool = False
        self.main_dataframe_has_default_header:bool = False
        self.importer = cxi.model()

        
    def giveDataframe(self):
        return self.main_dataframe
    
    
    def addToFilesDict(self, filename:str):
        if filename.endswith('.csv'):
            csv_file_parameter_dict = {"hasHeader":None,
                                        "Encoding":None,
                                        "Delimiter": None,
                                        "QuoteChar":None,
                                        "skipInitSpace":None,
                                        "lineTerminator":None,
                                        "Quoting":None}
            if filename in self.opened_files_dict:
                self.opened_files_dict[filename+"_"+str(self.multiple_files_counter)] = csv_file_parameter_dict
                self.multiple_files_counter += 1
            else:
                self.opened_files_dict[filename] = csv_file_parameter_dict
        elif filename.endswith('.xml'):
            if filename in self.opened_files_dict:
                self.opened_files_dict[filename+"_"+str(self.multiple_files_counter)] = {}
                self.multiple_files_counter += 1
            else:
                self.opened_files_dict[filename] = {}
        else:
            raise ValueError(filename+" is not a CSV or XML File!")
        return self.opened_files_dict
    
    
    def csvSniffer(self, filename: str):
        if self.multiple_files_counter <= 1:
            endswith_slice = -2
        else:
            endswith_slice = floor(log(self.multiple_files_counter, 10)+2)
            endswith_slice *= -1
        if filename.endswith("_", endswith_slice, -1):
            tmp_filename = filename[:-2:]
        else:
            tmp_filename = filename
        with open(tmp_filename, "r") as sniffing_file:
            read_sniffing_file = sniffing_file.read()
            has_header = csv.Sniffer().has_header(read_sniffing_file)
            dialect = csv.Sniffer().sniff(read_sniffing_file)
            return has_header, dialect
    
    def read_with_init_settings(self, filename:str, xsl_file:str=None):    
        self.addToFilesDict(filename)
        last_dict_element = list(self.opened_files_dict.keys())[-1]
        if self.multiple_files_counter <= 1:
            endswith_slice = -6
        else:
            endswith_slice = floor(log(self.multiple_files_counter, 10)+6)
            endswith_slice *= -1
        if last_dict_element.endswith('.csv') or last_dict_element.endswith(".csv_", endswith_slice, -1):
            hasSniffHeader, dialect = self.csvSniffer(last_dict_element)
            self.opened_files_dict[last_dict_element]["hasHeader"] = hasSniffHeader
            enc = detect(Path(filename).read_bytes())
            self.opened_files_dict[last_dict_element]["Encoding"] = enc["encoding"]      
            self.opened_files_dict[last_dict_element]["Delimiter"] = dialect.delimiter
            self.opened_files_dict[last_dict_element]["QuoteChar"] = dialect.quotechar
            self.opened_files_dict[last_dict_element]["skipInitSpace"] = dialect.skipinitialspace
            self.opened_files_dict[last_dict_element]["Quoting"] = dialect.quoting
            self.OpenCSVFile(last_dict_element)          
        
            

            
    def update_dataframe(self):
        self.reset()
        self.importer.reset()
        for filename in self.opened_files_dict.keys():
            if self.multiple_files_counter <= 1:
                endswith_slice = -6
            else:
                endswith_slice = floor(log(self.multiple_files_counter, 10)+6)
                endswith_slice *= -1
            if filename.endswith(".csv") or filename.endswith(".csv_", endswith_slice, -1):
                self.OpenCSVFile(filename)  
                
            elif filename.endswith(".xml") or filename.endswith(".xml_", endswith_slice, -1):
                self.OpenXMLFile(filename)
                
    
    def update_csv_with_personal_settings(self, filename:str, wantHeader:bool=None, encoding:str=None, Delimiter:str=None, Quotechar:str=None, skipInitSpace:bool=None,lineTerminator:str=None, quoting:int=None):   
        for other_filenames in self.opened_files_dict.keys():
            if other_filenames == filename:
                if wantHeader is not None:
                    if wantHeader == False:
                        for key in self.opened_files_dict.keys():
                            self.opened_files_dict[key]["hasHeader"] = wantHeader
                    self.opened_files_dict[filename]["hasHeader"] = wantHeader
                if encoding is not None:
                    self.opened_files_dict[filename]["Encoding"] = encoding
                if Delimiter is not None:
                    self.opened_files_dict[filename]["Delimiter"] = Delimiter
                if Quotechar is not None:
                    self.opened_files_dict[filename]["QuoteChar"] = Quotechar
                if skipInitSpace is not None:
                    self.opened_files_dict[filename]["skipInitSpace"] = skipInitSpace
                if lineTerminator is not None:
                    self.opened_files_dict[filename]["lineTerminator"] = lineTerminator
                if quoting is not None:
                    self.opened_files_dict[filename]["Quoting"] = quoting

            
        self.update_dataframe()
        
    
    def OpenCSVFile(self, filename:str):
        if self.opened_files_dict[filename]["hasHeader"]:
            header = "infer"             
        else:
            header = None
        if self.multiple_files_counter <= 1:
            endswith_slice = -2
        else:
            endswith_slice = floor(log(self.multiple_files_counter, 10)+2)
            endswith_slice *= -1
        if filename.endswith("_", endswith_slice, -1):
            tmp_filename = filename[:endswith_slice:]
        else:
            tmp_filename = filename
        try:
            new_dataframe = pd.read_csv(tmp_filename,
                                        header = header,
                                        encoding=self.opened_files_dict[filename]["Encoding"],
                                        sep=self.opened_files_dict[filename]["Delimiter"],
                                        quotechar= self.opened_files_dict[filename]["QuoteChar"],
                                        skipinitialspace=self.opened_files_dict[filename]["skipInitSpace"],
                                        lineterminator=self.opened_files_dict[filename]["lineTerminator"],
                                        quoting=self.opened_files_dict[filename]["Quoting"])
            column_amount = len(new_dataframe.columns)
        
        
            self.main_dataframe = self.importer.ImportFile(new_dataframe, column_amount, self.opened_files_dict[filename]["hasHeader"])
            
        except OSError as e:
            self.opened_files_dict.pop(filename)
            raise OSError(e)
        except (UnicodeDecodeError,LookupError):
            if self.multiple_files_counter <= 1:
                endswith_slice = -2
            else:
                endswith_slice = floor(log(self.multiple_files_counter, 10)+2)
                endswith_slice *= -1
            if filename.endswith("_", endswith_slice, -1):
                tmp_filename = filename[:endswith_slice:]
            else:
                tmp_filename = filename
            enc = detect(Path(tmp_filename).read_bytes())
            self.opened_files_dict[filename]["Encoding"] = enc["encoding"] 
            self.update_dataframe()
            raise LookupError
        except (ValueError,pd.errors.ParserError) as value_error:
            raise ValueError(value_error)
            
        
        return self.main_dataframe
    
    def getXMLParameters(self, filename:str, xsl_file:str):
        self.opened_files_dict[filename] = {}
        tree = ET.parse(xsl_file)
        root = tree.getroot()
        param_matches = [c.attrib for c in root if 'param' in c.tag]
        for index,_ in enumerate(param_matches):
            self.opened_files_dict[filename][param_matches[index]["name"]] = param_matches[index]["select"]
        self.opened_files_dict[filename]["xsl_file"] = xsl_file
        self.opened_files_dict[filename]["parameters_len"] = len(param_matches)
        self.opened_files_dict[filename]["hasHeader"] = None
        self.opened_files_dict[filename]["init"] = True
        self.update_dataframe()
    
    def addXMLParameter(self, filename:str, param:str = None, value:str = None, wantHeader:bool = None):  
        if param is not None and value is not None:
            if self.multiple_files_counter <= 1:
                endswith_slice = -6
            else:
                endswith_slice = floor(log(self.multiple_files_counter, 10)+6)
                endswith_slice *= -1
            if filename.endswith('.xml') or filename.endswith(".xml_", endswith_slice, -1):
                if filename in self.opened_files_dict.keys():                      
                    if param in self.opened_files_dict[filename].keys():
                        self.opened_files_dict[filename][param] = "'"+value+"'"

        if wantHeader is not None:
            self.opened_files_dict[filename]["hasHeader"] = wantHeader
        self.update_dataframe()
            

             
        
        
    
    def OpenXMLFile(self, filename:str):
        if self.multiple_files_counter <= 1:
            endswith_slice = -2
        else:
            endswith_slice = floor(log(self.multiple_files_counter, 10)+2)
            endswith_slice *= -1
        if filename.endswith("_", endswith_slice, -1):
            tmp_filename = filename[:endswith_slice:]
        else:
            tmp_filename = filename
        try:
            try:
                xmldoc = etree.parse(tmp_filename)
            except lxml.etree.ParseError as parse_error:
                raise lxml.etree.ParseError(parse_error)

            try:
                transformer = etree.XSLT(etree.parse(self.opened_files_dict[filename]["xsl_file"]))
            except lxml.etree.XSLTParseError as xsl_parse_error:
                raise lxml.etree.XSLTParseError(xsl_parse_error)


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
                raise etree.XSLTApplyError(apply_error)
                

            reader = csv.reader(result.splitlines(), delimiter=',')
            list_reader = list(reader)
            column_amount = len(list_reader[0])
            
            if self.opened_files_dict[filename]["init"]:             
                header_regex_list = []
                header_regex_list = self.importer.regex_list_filler(header_regex_list, list_reader[0])
                splice_len = 1
                string_splice_len = (splice_len + 1)*(-1)
                for i, header_column_name in enumerate(header_regex_list):
                    header_regex_list[i] = header_column_name[:string_splice_len]
                    splice_len += 1
                    string_splice_len = (ceil(log(splice_len, 10)+1))*(-1)
  
                if any(column != "String" for column in header_regex_list):
                    self.opened_files_dict[filename]["hasHeader"] = False
                    column_names = None            
                else:
                    self.opened_files_dict[filename]["hasHeader"] = True              
                    column_names = list_reader.pop(0)
                self.opened_files_dict[filename]["init"] = False
            
            else:
                if self.opened_files_dict[filename]["hasHeader"]:
                    column_names = list_reader.pop(0)
                elif not self.opened_files_dict[filename]["hasHeader"]:
                    column_names = None
            
            new_dataframe = pd.DataFrame(list_reader, columns=column_names)
        
            
            self.main_dataframe = self.importer.ImportFile(new_dataframe, column_amount,self.opened_files_dict[filename]["hasHeader"])
        
        except OSError as os:
            raise OSError(os)
            
        except lxml.etree.XSLTApplyError as transform_error:
            raise lxml.etree.XSLTApplyError(transform_error)
            
        except ValueError as value_error:
            raise ValueError(value_error)

        return self.main_dataframe
        
                
    def reset(self):
        self.main_dataframe = pd.DataFrame()
        self.__main_dataframe_has_header = False
        self.column_amount = 0
        self.default_header = []            
               
    
    def RemoveFilesFunctionality(self, elem_name:str):
        self.opened_files_dict.pop(elem_name)
        self.update_dataframe()
        return self

    def ClearAllFilesFunctionality(self):
        self.opened_files_dict.clear()
        self.update_dataframe()
        return self

    
        
    def importAsDictionary(self):
        print(self.main_dataframe.to_dict(orient="list"))
        return self.main_dataframe.to_dict(orient="list")

    def importAsListOfLists(self):
        list_of_lists = self.main_dataframe.values.tolist()
        list_of_lists_header = list(self.main_dataframe.columns)
        list_of_lists.insert(0, list_of_lists_header)
        print(list_of_lists)
        return list_of_lists

    def importAsNumPyArray(self):
        try:
            print(self.main_dataframe.to_numpy())
            return self.main_dataframe.to_numpy()
        except ValueError as value_error:
            raise ValueError(value_error)

    def exportAsCSVFile(self, exported_file_path: str, encoding: str = "UTF-8", delimiter: str = ",", quotechar:str ="\"", line_terminator:str = "\r\n"):
        self.main_dataframe.to_csv(exported_file_path, index=False, sep=delimiter, encoding=encoding, quotechar = quotechar, line_terminator = line_terminator)
        return

    def exportAsXMLFile(self, exported_file_path: str, encoding: str="UTF-8"):
        root = etree.Element("root")
        for _, row in self.main_dataframe.iterrows():
            try:
                xml_row = etree.SubElement(root, "row")
            except ValueError:
                raise ValueError(root+" is no valid Root Tag-name")
            for elem in row.index:
                str_elem = str(elem)
                digit_tester = str_elem[0].isdigit()
                special_char_tester = map(str_elem.startswith, ("\"","xml",".",",",";","<",">"))
                if digit_tester or any(special_char_tester):
                    raise ValueError("Header cannot be converted to XML, because a column starts with a number or a special character")
                try:
                    xml_row_elem = etree.SubElement(xml_row, elem)
                except ValueError:
                    raise ValueError(elem+" is no valid Item Tag-name")
                xml_row_elem.text = str(row[elem])

        document = etree.ElementTree(root)
        document.write(exported_file_path, pretty_print=True, xml_declaration=True,  encoding=encoding)
