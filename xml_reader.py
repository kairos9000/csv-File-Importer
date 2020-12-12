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

#TODO: Funktion, die xml-Files in Dataframes überführt, mit Parameter Anpassung

class xml_importer():
    def __init__(self):
        self.opened_xml_files_list : list =  []
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
    
    def OpenXMLFiles(self):
        try:
            try:
                xmldoc = etree.parse("cdcatalog.xml")
            except lxml.etree.ParseError as parse_error:
                print("parse_error")
                exit()
            try:
                transformer = etree.XSLT(etree.parse("xml2csv.xsl"))
                tree = ET.parse('xml2csv.xsl')
            except lxml.etree.XSLTParseError as xsl_parse_error:
                print("xsl_parse_error")
                exit()
            root = tree.getroot()
            match = [c.attrib for c in root if 'param' in c.tag]

            sep_param = ","
            result = str(transformer(xmldoc, **{match[0]["name"]: "\""+sep_param+"\""}, **{match[1]["name"]: "'\"'"}, **{match[2]["name"]: "'\r\n'"}))
            reader = csv.reader(result.splitlines(), delimiter=',')
            list_reader = list(reader)
            print(list_reader)
            column_names = list_reader.pop(0)

            df = pd.DataFrame(list_reader, columns=column_names)
            print(df)
    
        except OSError as os:
            print("os")
            
        except lxml.etree.XSLTApplyError as transform_error:
            print("transform_error")
    
    def reset(self):
        self.main_dataframe = pd.DataFrame()
        self.__main_dataframe_has_header = False
        self.column_amount = 0
        self.default_header = []            
               
    
    def RemoveFilesFunctionality(self, elem_name:str):
        self.opened_xml_files_list.remove(elem_name)
        return self

    def ClearAllFilesFunctionality(self):
        self.opened_xml_files_list.clear()
        return self
        
        