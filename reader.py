# -*- coding: utf-8 -*-#

import pandas as pd
import io
import csv
import re
from pathlib import Path
from chardet import detect
from math import log, ceil, floor 
import csv_xml_importer as cxi
import lxml.etree
from lxml import etree
import xml.etree.ElementTree as ET


class reader():
    """The class reader converts csv and xml Files to Dataframes, lets the user change the parameters of the Files and can export the 
    Files as either a csv or a xml File or import as a Dictionary, a Numpy Array, a List of Lists or a Dataframe"""
    
    def __init__(self):
        """The constructor of the class reader.
        If defines the following attributes for every instance of the class:
            opened_files_dict: This dictionary is keeping track of every File and its Parameters by defining the key as the filename and
                               the value as a dictionary of the parameters
            multiple_files_counter: a counter for every file that has been read multiple times and changes the name of the File to differentiate them in the dictionary
                                    e.g. testFile.csv, testFile.csv_0
            main_dataframe: holds the main dataframe, therefore all the files appended to one dataframe
            column_amount: the amount of columns main_dataframe has
            importer: a instance of the class dataframeAndHeaderHandler to call the methods of this class for every File, which has been converted to a dictionary"""
            
            
        self.opened_files_dict : dict = {}
        self.multiple_files_counter : int = 0
        self.main_dataframe = pd.DataFrame()
        self.column_amount : int = 0
        self.importer = cxi.dataframeAndHeaderHandler()

        
    def giveDataframe(self):
        """A simple Function for giving main_dataframe to another class
        
        Returns:
            main_dataframe: the main dataframe"""
            
        return self.main_dataframe
    
    
    def addToFilesDict(self, filename:str):
        """adds the given filename to opened_files_dict as a key and gives each filename a value of a dictionary for the parameters according to the filetype
        
        Parameters:
            filename: a string, specifying the absolute or relative filepath of the file
        
        Returns:
            opened_files_dict: the updated dictionary with the new entry"""
            
        if filename.endswith('.csv'):
            #if the file is a csv file it gets a value of the following dict for its parameters
            csv_file_parameter_dict = {"hasHeader":None,
                                        "Encoding":None,
                                        "Delimiter": None,
                                        "QuoteChar":None,
                                        "skipInitSpace":None,
                                        "lineTerminator":None,
                                        "Quoting":None}
            #if filename is already in opened_files_dict, it will be added with a counter, because the same key is not allowed in a dictionary
            if filename in self.opened_files_dict:
                self.opened_files_dict[filename+"_"+str(self.multiple_files_counter)] = csv_file_parameter_dict
                self.multiple_files_counter += 1
            else:
                self.opened_files_dict[filename] = csv_file_parameter_dict
        elif filename.endswith('.xml'):
            #the same procedure with xml files
            if filename in self.opened_files_dict:
                self.opened_files_dict[filename+"_"+str(self.multiple_files_counter)] = {}
                self.multiple_files_counter += 1
            else:
                #the parameters of the xml file can only be specified if a xsl Stylesheet is given
                self.opened_files_dict[filename] = {}
        else:
            raise ValueError(filename+" is not a CSV or XML File!")
        return self.opened_files_dict
    
    
    def csvSniffer(self, filename: str):
        """This sniffer is using the sniffer of the csv module to get the most probable parameters of the given file.
        It also sniffs if the file has a header or not.
        
        Parameters:
            filename: a string, specifying the absolute or relative filepath of the file
            
        Returns:
            has_header: a boolean variable, which signals if the file has a header or not
            dialect: the sniffed dialect of the file, e.g. separator, line terminator, quoting,..."""
            
        #slices the end of the filename string, because the file needs to be opened to be read and a file
        #with the counter at the end of each file doesn't exist
        if self.multiple_files_counter <= 1:
            endswith_slice = -2
        else:
            #to ensure that every file is sliced at the right length even if the file counter has multiple digits
            endswith_slice = floor(log(self.multiple_files_counter, 10)+2)
            endswith_slice *= -1
        #defines a tmp_filename string, which is a placeholder for filename to get the dialect
        if filename.endswith("_", endswith_slice, -1):
            tmp_filename = filename[:-2:]
        else:
            tmp_filename = filename
        #opens the file and reads the file to get the header and the parameters
        with open(tmp_filename, "r") as sniffing_file:
            read_sniffing_file = sniffing_file.read()
            has_header = csv.Sniffer().has_header(read_sniffing_file)
            dialect = csv.Sniffer().sniff(read_sniffing_file)
            return has_header, dialect
    
    def read_with_init_settings(self, filename:str): 
        """This function takes a csv File, adds it to opened_files_dict, sniffs its dialect and if it has a header,
        gives the filename in opened_files_dict its corresponding parameter values and calls the method OpenCSVFile
        
        Parameters:
            filename: a string, specifying the absolute or relative filepath of the file
        
        Returns: 
            nothing or void"""
            
        
        self.addToFilesDict(filename)
        #takes the last added element of opened_files_dict, therefore filename
        last_dict_element = list(self.opened_files_dict.keys())[-1]
        #slices the filename for the if condition
        if self.multiple_files_counter <= 1:
            endswith_slice = -6
        else:
            endswith_slice = floor(log(self.multiple_files_counter, 10)+6)
            endswith_slice *= -1
        if last_dict_element.endswith('.csv') or last_dict_element.endswith(".csv_", endswith_slice, -1):
            #sniffs parameters and header
            hasSniffHeader, dialect = self.csvSniffer(last_dict_element)
            self.opened_files_dict[last_dict_element]["hasHeader"] = hasSniffHeader
            #reads bytes of the filename the detect the encoding of the file
            enc = detect(Path(filename).read_bytes())
            self.opened_files_dict[last_dict_element]["Encoding"] = enc["encoding"]    
            #sets the parameters to the sniffed values  
            self.opened_files_dict[last_dict_element]["Delimiter"] = dialect.delimiter
            self.opened_files_dict[last_dict_element]["QuoteChar"] = dialect.quotechar
            self.opened_files_dict[last_dict_element]["skipInitSpace"] = dialect.skipinitialspace
            self.opened_files_dict[last_dict_element]["Quoting"] = dialect.quoting
            self.OpenCSVFile(last_dict_element)          
        
            

            
    def update_dataframe(self):
        """A simple Function which resets the importer and the attributes of the instance of this class to read 
        every file anew if any parameter of any file has changed
        
        Returns:
            nothing or void"""
            
        #resets attributes of this class
        self.reset()
        #resets attributes of dataframeAndHeaderHandler
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
        """This Function updates the parameters of the given csv file with the values the user wants, e.g. encoding, delimiter,... and
        updates main_dataframe
        
        Parameters:
            filename: a string, specifying the absolute or relative filepath of the file
            wantHeader: a boolean value, signaling if the user wants a header or not
            encoding: the encoding given by the user
            delimiter: the delimiter specified by the user
            Quotechar: the character, which will be used for quoting the entries of the csv file
            skipInitSpaces: a boolean variable, signaling if the user wants to delete spaces at the beginning of the entry of the csv File or not
            lineTerminator: the character which will be used to start a new line
            quoting: a integer, which corresponds to a specific quoting style, 0 means minimal quoting, 1 means all entries will be quoted,
                     2 means all non numeric entries will be quoted and 3 means nothing will be quoted

        Returns:
            nothing or void"""
            
        #tests if the given filename is in opened_files_dict
        if filename in self.opened_files_dict.keys():
            if wantHeader is not None:
                #if the user wants no header, every file gets set to header = False to show the default header
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

        #updates main_dataframe  
        self.update_dataframe()
        
    
    def OpenCSVFile(self, filename:str):
        """Opens the given csv file with the specified parameters, converts it to a dataframe and adds this dataframe to main_dataframe
        
        Parameters:
            filename: a string, specifying the absolute or relative filepath of the file
        Returns:
            main_dataframe: the updated main_dataframe with the appended csv File"""
        
        #if the given file is specified to have a header "infer" takes the first row of the dataframe and renames the columns of 
        #the dataframe with the first row else no header will be choosen and the default header from the regular expressions from 
        #dataframeAndHeaderHandler will be shown
        if self.opened_files_dict[filename]["hasHeader"]:
            header = "infer"             
        else:
            header = None
        #slices the string filename to open the file
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
            #converts the csv file with the specified parameters to a dataframe
            new_dataframe = pd.read_csv(tmp_filename,
                                        header = header,
                                        encoding=self.opened_files_dict[filename]["Encoding"],
                                        sep=self.opened_files_dict[filename]["Delimiter"],
                                        quotechar= self.opened_files_dict[filename]["QuoteChar"],
                                        skipinitialspace=self.opened_files_dict[filename]["skipInitSpace"],
                                        lineterminator=self.opened_files_dict[filename]["lineTerminator"],
                                        quoting=self.opened_files_dict[filename]["Quoting"])
            column_amount = len(new_dataframe.columns)
        
            #appends the new dataframe to main_dataframe
            self.main_dataframe = self.importer.ImportFile(new_dataframe, column_amount, self.opened_files_dict[filename]["hasHeader"])
        
        #Error Handling:
        #if the csv File cannot be opened, because it doesn't exist for example
        except OSError as e:
            self.opened_files_dict.pop(filename)
            raise OSError(e)
        #if the encoding is invalid it will be reset to the default value
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
        #if the types of the dataframes don't correspond or the csv file cannot be parsed to a dataframe
        except (ValueError,pd.errors.ParserError) as value_error:
            raise ValueError(value_error)
            
        
        return self.main_dataframe
    
    def getXMLParameters(self, filename:str, xsl_file:str):
        """Searches the given xsl Stylesheet for parameters, gives those parameters to the specified xml File as a dictionary and updates main_dataframe
        
        Parameters:
            filename: a string, specifying the absolute or relative filepath of the file
            xsl_file: a string, specifying the absolute or relative filepath of the xsl Stylesheet
        
        Returns:
            nothing or void"""
        
        
        self.opened_files_dict[filename] = {}
        #parses the xsl Stylesheet for reading using the lxml module
        tree = ET.parse(xsl_file)
        root = tree.getroot()
        #searches every Tag of the Stylesheet for the keyword "param", which specifies parameters
        parameters = [elem.attrib for elem in root if 'param' in elem.tag]
        #adds every parameter to the parameter dictionary, which is the value of the filename in opened_files_dict
        for index,_ in enumerate(parameters):
            self.opened_files_dict[filename][parameters[index]["name"]] = parameters[index]["select"]
        #sets the xsl_file as another key for later use
        self.opened_files_dict[filename]["xsl_file"] = xsl_file
        #gets the amount of parameters the xsl Stylesheet has
        self.opened_files_dict[filename]["parameters_len"] = len(parameters)
        #hasHeader will be used later when opening the file
        self.opened_files_dict[filename]["hasHeader"] = None
        #init will be used when openend the file
        self.opened_files_dict[filename]["init"] = True
        self.update_dataframe()
  
    
    def addXMLParameter(self, filename:str, param:str = None, value:str = None, wantHeader:bool = None):  
        """Changes the values of the Parameters read from the xsl Stylesheet to the ones specified by the user
        
        Parameters:
            filename: a string, specifying the absolute or relative filepath of the file
            param: the parameter of the stylesheet, which will be changed
            value: the new value of param, given by the user
            wantHeader: a boolean variable, which signals if the user wants a header or not
        
        Returns:
            nothing or void"""
        
        if param is not None and value is not None:
            #slices the file to check the filetype
            if self.multiple_files_counter <= 1:
                endswith_slice = -6
            else:
                endswith_slice = floor(log(self.multiple_files_counter, 10)+6)
                endswith_slice *= -1
            if filename.endswith('.xml') or filename.endswith(".xml_", endswith_slice, -1):
                if filename in self.opened_files_dict.keys():                      
                    if param in self.opened_files_dict[filename].keys():
                        #changes the value of the given parameter param to value
                        self.opened_files_dict[filename][param] = "'"+value+"'"

        #changes hasHeader to either True or False
        if wantHeader is not None:
            self.opened_files_dict[filename]["hasHeader"] = wantHeader
        self.update_dataframe()

    
    
    def OpenXMLFile(self, filename:str):
        """Opens the given xml File with the parameters of the xsl Stylesheet and converts it to a dataframe to append it to main_dataframe
        
        Parameters:
            filename: a string, specifying the absolute or relative filepath of the file
        
        Returns:
            main_dataframe: the updated main_dataframe with the appended xml File"""
        
        #slices the string filename to open the file
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
                #parses the xml file using the lxml module
                xmldoc = etree.parse(tmp_filename)
            except lxml.etree.ParseError as parse_error:
                raise lxml.etree.ParseError(parse_error)

            try:
                #parses the xsl Stylesheet using the lxml module
                transformer = etree.XSLT(etree.parse(self.opened_files_dict[filename]["xsl_file"]))
            except lxml.etree.XSLTParseError as xsl_parse_error:
                raise lxml.etree.XSLTParseError(xsl_parse_error)


            parameters = {}
            tmp_settings_list = list(self.opened_files_dict[filename])

            #defines a dictionary parameters and fills it with the parameters read from the xsl Stylesheets and the values of
            #those parameters either from the xsl Stylesheet or given by the user through addXMLParameter
            for i in range(self.opened_files_dict[filename]["parameters_len"]):
                key = tmp_settings_list[i]
                if len(key) > 0:
                    value = self.opened_files_dict[filename][key]
                    parameters[key] = value
            try:
                #converts the xml file with the parameters to a string
                result = str(transformer(xmldoc, **parameters))
            except etree.XSLTApplyError as apply_error:
                raise etree.XSLTApplyError(apply_error)
                
            #converts the string into a reader object from the csv module
            reader = csv.reader(result.splitlines(), delimiter=',')
            #converts the reader object into a list of lists
            list_reader = list(reader)
            column_amount = len(list_reader[0])
            
            #if the xml File is read the first time, the hasHeader key of its parameter dictionary needs to be set
            if self.opened_files_dict[filename]["init"]:             
                header_regex_list = []
                #self built sniffer, which takes the first row of the list of lists from the xml file and uses the regular
                #expressions from dataframeAndHeaderHandles on it
                header_regex_list = self.importer.regex_list_filler(header_regex_list, list_reader[0])
                splice_len = 1
                string_splice_len = (splice_len + 1)*(-1)
                #splices the column numbers from regex_list_filler from the header_regex_list
                for i, header_column_name in enumerate(header_regex_list):
                    header_regex_list[i] = header_column_name[:string_splice_len]
                    splice_len += 1
                    string_splice_len = (ceil(log(splice_len, 10)+1))*(-1)
                
                #if any entry of the list is matched to be anything other than a integer, the first row cannot be a header
                if any(column != "String" for column in header_regex_list):
                    self.opened_files_dict[filename]["hasHeader"] = False
                    column_names = None            
                else:
                    self.opened_files_dict[filename]["hasHeader"] = True              
                    column_names = list_reader.pop(0)
                self.opened_files_dict[filename]["init"] = False
            
            #hasHeader can be chosen from the user
            else:
                if self.opened_files_dict[filename]["hasHeader"]:
                    column_names = list_reader.pop(0)
                elif not self.opened_files_dict[filename]["hasHeader"]:
                    column_names = None
            
            #converts the list of lists to a dataframe with the chosen column_names as a header
            new_dataframe = pd.DataFrame(list_reader, columns=column_names)
        
            #appends new_dataframe to main_dataframe
            self.main_dataframe = self.importer.ImportFile(new_dataframe, column_amount,self.opened_files_dict[filename]["hasHeader"])
        
        #Error Handling
        #if the csv File cannot be opened, because it doesn't exist for example
        except OSError as os:
            raise OSError(os)
         
        #if the xml File can't be transformed into a string using the xsl Stylesheet   
        except lxml.etree.XSLTApplyError as transform_error:
            raise lxml.etree.XSLTApplyError(transform_error)
            
        #if the types of new_dataframe and main_dataframe are different
        except ValueError as value_error:
            raise ValueError(value_error)

        return self.main_dataframe
        
                
    def reset(self):
        """A simple Function which resets main_dataframe to a empty dataframe and the column_amount to 0"""
        
        self.main_dataframe = pd.DataFrame()
        self.column_amount = 0          
               
    
    def RemoveFilesFunctionality(self, elem_name:str):
        """Removes elem_name from openend_files_dict and updates main_dataframe
        
        Parameters: 
            elem_name: a string, specifying the absolute or relative filepath of the file, which must be in opened_files_dict
        
        Returns:
            nothing or void"""
        
        if elem_name in self.opened_files_dict.keys():
            self.opened_files_dict.pop(elem_name)
        self.update_dataframe()


    def ClearAllFilesFunctionality(self):
        """Empties the whole opened_files_dict and updates main_dataframe"""
        
        self.opened_files_dict.clear()
        self.update_dataframe()

    
        
    def importAsDictionary(self):
        """imports main_dataframe as a Dictionary
        
        Returns:
            main_dataframe converted to a Dictionary"""
        
        print(self.main_dataframe.to_dict(orient="list"))
        return self.main_dataframe.to_dict(orient="list")

    def importAsListOfLists(self):
        """imports main_dataframe as a List of Lists
        
        Returns:
            main_dataframe converted to a List of Lists"""
            
        list_of_lists = self.main_dataframe.values.tolist()
        list_of_lists_header = list(self.main_dataframe.columns)
        list_of_lists.insert(0, list_of_lists_header)
        print(list_of_lists)
        return list_of_lists

    def importAsNumPyArray(self):
        """imports main_dataframe as a Numpy Array
        
        Returns:
            main_dataframe converted to a Numpy Array"""
            
        try:
            print(self.main_dataframe.to_numpy())
            return self.main_dataframe.to_numpy()
        except ValueError as value_error:
            raise ValueError(value_error)
    
    def importAsPandasDataframe(self):
        """returns main_dataframe without conversion as its already a dataframe
        
        Returns:
            main_dataframe"""
        print(self.main_dataframe)
        return self.main_dataframe

    def exportAsCSVFile(self, exported_file_path: str, encoding: str = "UTF-8", delimiter: str = ",", quotechar:str ="\"", line_terminator:str = "\r\n"):
        """Converts main_dataframe to a csv File with the given parameters, which can be configured by the user and exports it to the given filepath
        
        Parameters:
            exported_file_path: the absolute or relative filepath, the csv File shall be exported to
            encoding: the encoding the csv File will be encoded in
            delimiter: the delimiter or separator used for the csv file
            quotechar: the character used for quoting
            line_terminator: the character, which will be used for starting a new line in the csv File
        
        Returns:
            nothing or void"""
        
        self.main_dataframe.to_csv(exported_file_path, index=False, sep=delimiter, encoding=encoding, quotechar = quotechar, line_terminator = line_terminator)
        return

    def exportAsXMLFile(self, exported_file_path: str, encoding: str="UTF-8"):
        """Converts main_dataframe to a xml file with the given encoding and exports it to the given filepath
        
        Parameters:
            exported_file_path: the absolute or relative filepath, the csv File shall be exported to
            encoding: the encoding the csv File will be encoded in
        Returns: 
            nothing or void"""
        
        #defines the root element of the xml file the dataframe will be converted to using lxml
        root = etree.Element("root")
        #iterates over every row in the dataframe
        for _, row in self.main_dataframe.iterrows():
            #adds a "row" Tag for every row the dataframe has
            xml_row = etree.SubElement(root, "row")

            #adds a Tag for every element in a row
            for elem in row.index:
                str_elem = str(elem)
                #tests the header elements the tag will be named after, if they conform the xml naming standard
                digit_tester = str_elem[0].isdigit()
                special_char_tester = map(str_elem.startswith, ("\"","xml",".",",",";","<",">"))
                if digit_tester or any(special_char_tester):
                    raise ValueError("Header cannot be converted to XML, because a column starts with a number or a special character")
                try:
                    #adds the entry of the dataframe to the Tag
                    xml_row_elem = etree.SubElement(xml_row, elem)
                except ValueError:
                    raise ValueError(elem+" is no valid Item Tag-name")
                xml_row_elem.text = str(row[elem])

        #converts the root element and every following tag added to root to a xml file using the lxml module
        xml_file_for_export = etree.ElementTree(root)
        #writes the xml file into the file specified by exported_file_path
        xml_file_for_export.write(exported_file_path, pretty_print=True, xml_declaration=True,  encoding=encoding)
