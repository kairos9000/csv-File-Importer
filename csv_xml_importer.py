# -*- coding: utf-8 -*-#

import pandas as pd
import io
import csv
import re
from math import log, ceil


class model():
    """This class is responsible for adding the new Dataframes to the Main Dataframe and 
    finding the corresponding headers of the columns of the Main Dataframe through regular expressions"""

    def __init__(self):
        """The __init__ function is the constructor of the model class. 
        It defines the following attributes for every model object:
        
        types_dict: a dictionary, which contains the regular expression, with whom the Dataframe columns will be tested
        main_dataframe: the Dataframe in which all converted csv and xml Files will be saved
        default_header: a list, containing the column names of the main dataframe the regular expressions found
        column_amoung: an integer, which saves the amount of columns the main dataframe has, to test if the new imported csv or xml File matches the column amount of the main dataframe
        main_dataframe_has_header: a boolean variable, signaling if the main dataframe already has a header of its own
        main_dataframe_has_default_header: a boolean variable, signaling if the main dataframe has a default header from the regular expressions"""
        
        
        self.types_dict : dict = {
                        "Integer": re.compile(r"^\d+$"),
                        "Float": re.compile(r"^\d+(\.|\,)\d+$"),
                        "Coordinate": re.compile(r"^(N|S)?0*\d{1,3}°0*\d{1,3}(′|')0*\d{1,3}\.\d*(″|\")(?(1)|(N|S)) (E|W)?0*\d{1,3}°0*\d{1,3}(′|')0*\d{1,3}\.\d*(″|\")(?(5)|(E|W))$"),
                        "Email": re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"),                       
                        "Time": re.compile(r"^([0-1]\d|2[0-3]):[0-5]\d(:[0-5]\d)*$"),
                        "Date": re.compile(r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$"),
                        "Datetime": re.compile(r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2}).([0-1]\d|2[0-3]):[0-5]\d(:[0-5]\d)*$"),
                        "Web-URL": re.compile(r"^((ftp|http|https):\/\/)?(www\.)?(ftp|http|https|www\.)?([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-]+)+((\/)?([\w].*)+(#|\?)*)*((\/)*\w+\?[a-zA-Z0-9_]+=\w+(&[a-zA-Z0-9_]+=\w+)*)?$"),               
                        "Bool": re.compile(r"^(wahr|falsch|ja|nein|yes|no|true|false|t|f|1|0)$", flags=re.IGNORECASE)      
                    }
        self.main_dataframe = pd.DataFrame()
        self.default_header : list = []
        self.column_amount : int = 0
        self.__main_dataframe_has_header:bool = False
        self.main_dataframe_has_default_header:bool = False

    
    
    def ImportFile(self, new_dataframe:pd.DataFrame, column_amount:int, hasHeader:bool):    
        """ImportFile adds the latest csv or xml File as a Dataframe, adds it to the main dataframe and tests if the header of the main dataframe have to be adjusted
        
        Parameters:
            new_dataframe: the latest csv or xml File converted to a dataframe
            column_amount: the amount of columns new_dataframe has
            hasHeader: a boolean variable, which shows if new_dataframe has a header or not
        
        Returns:
            main_dataframe with the latest csv or xml File appended and the latest header"""
            
        #Tests if the main_dataframe is empty
        #   True: new_dataframe is main_dataframe
        #   False: new_dataframe will be appended to main_dataframe
        if self.main_dataframe.empty:
            self.main_dataframe = new_dataframe
            self.column_amount = column_amount
            self.find_header_formats(self.main_dataframe)

        else:
            #Tests if the column amounts of the two dataframes are the same, if not new_dataframe cannot be appended
            if self.column_amount is not column_amount:
                raise ValueError("The Files have different column amounts")
            
            #Compares the column types of the two dataframes through regular expressions and tests, if the types are compatible,
            #if not a error will be thrown
            #Takes only the first row of the two dataframes and compares the types
            type_list_new_dataframe = list(new_dataframe.iloc[1])
            type_list_main_dataframe = list(self.main_dataframe.iloc[1])
            regex_types_new_dataframe = []
            regex_types_main_dataframe = []
            compare_list_new_dataframe = []
            compare_list_main_dataframe = []
            #fills the two lists with the types, the regular expressions found
            regex_types_new_dataframe = self.regex_list_filler(regex_types_new_dataframe, type_list_new_dataframe)
            regex_types_main_dataframe = self.regex_list_filler(regex_types_main_dataframe, type_list_main_dataframe)
            #splices the entries of the lists, because the function regex_list_filler appends numbers to the types, to differenciate the columns in the dataframe
            splice_len = 1
            string_splice_len = (splice_len + 1)*(-1)
            for item_new, item_main in zip(regex_types_new_dataframe,regex_types_main_dataframe):
                item_new = item_new[:string_splice_len]
                item_main = item_main[:string_splice_len]
                splice_len += 1
                string_splice_len = (ceil(log(splice_len, 10)+1))*(-1)
                compare_list_new_dataframe.append(item_new)
                compare_list_main_dataframe.append(item_main)

            #compares the types of the two dataframes
            if sorted(compare_list_new_dataframe) != sorted(compare_list_main_dataframe):
                raise ValueError("The Types of the Dataframes are not compatible")
                
                
            #tests if new_dataframe has a header
            #   True: the header of new_dataframe is the new header of main_dataframe
            #   False: the header of main_dataframe stays the same
            if hasHeader:
                new_cols = {x: y for x, y in zip(self.main_dataframe, new_dataframe)}
                self.main_dataframe = self.main_dataframe.rename(columns=new_cols)
                

            if not hasHeader:
                new_cols = {x: y for x, y in zip(new_dataframe, self.main_dataframe)}
                new_dataframe = new_dataframe.rename(columns=new_cols)
            
            #appends new_dataframe to main_dataframe
            self.main_dataframe = self.main_dataframe.append(new_dataframe)
        
        #sets the boolean variable, if main_dataframe has a header   
        if hasHeader:
            self.__main_dataframe_has_header = True
            
        #if main_dataframe has no header, a default header will be made with regular expressions and is going to be the header of main_dataframe  
        if not self.__main_dataframe_has_header:
            
            self.default_header = self.find_header_formats(self.main_dataframe)
            main_dataframe_columns = list(self.main_dataframe.columns)
            #creates a dictionary, where the key is the old header value of the columns of the main_dataframe and the value is the default header
            default_cols = {x: y for x, y in zip(main_dataframe_columns, self.default_header)}
            #renames the header
            self.main_dataframe = self.main_dataframe.rename(columns=default_cols)
        
        self.__main_dataframe_has_header = True
                   
        return self.main_dataframe               
            
    def reset(self):
        """A simple function, which resets the main_dataframe, the boolean variable main_dataframe_has_header, the column_amount and the default_header
        and returns nothing or void"""
        
        self.main_dataframe = pd.DataFrame()
        self.__main_dataframe_has_header = False
        self.column_amount = 0
        self.default_header = []
    
    def find_header_formats(self, dataframe):
        """Takes a dataframe and checks the first five rows with regular expressions on their types
        
        Parameter:
            dataframe: the dataframe, of which the types will be evaluated
        
        Returns:
            key_list: a list of the types of the columns from the dataframe"""
            
        row_counter = 0
        first_row = True
        #creates a dictionary, which will contain the types of the first five rows as lists
        type_lists_dict = {"first_row":[],"second_row":[],"third_row":[],"fourth_row":[],"fifth_row":[]}
        #turns the dictionary into and iterable object
        iter_type_lists_dict = iter(type_lists_dict)
        key = next(iter_type_lists_dict)
        #iterates over the rows of the dataframe
        for _, row in dataframe.iterrows():
            #tests if the dataframe has a header, if True the first row will not be analysed, because it contains only strings
            if not self.__main_dataframe_has_header and first_row:
                first_row = False
                continue
            
            row_list = list(row)
            #fills the list with the types of the row
            type_lists_dict[key] = self.regex_list_filler(type_lists_dict[key], row_list)
            if row_counter >= 4:
                break  
            #yields next object from the iterator
            key = next(iter_type_lists_dict) 
                  
            row_counter += 1   
            
        #tests if the lists have the same types
        key_list = type_lists_dict["first_row"]
        for key in type_lists_dict.keys():
            if key_list != type_lists_dict[key] and len(type_lists_dict[key]) != 0:
                key_list_counter = 0
                splice_len = 1
                string_splice_len = (splice_len + 1)*(-1)
                #if the lists have different types, the differentiated types will be replaced with the type String
                for key_list_item, other_list_item in zip(key_list,type_lists_dict[key]):
                    if key_list_item != other_list_item:
                        key_list[key_list_counter] = "String"+key_list_item[string_splice_len:]
                        other_list_item = "String"+other_list_item[string_splice_len:]
                        splice_len += 1
                        string_splice_len = (ceil(log(splice_len, 10)+1))*(-1)
                    key_list_counter += 1     
        return key_list
    
    
    def regex_list_filler(self, regex_list, row):
        """Tests every element of the row on their type
        
        Parameters:
            regex_list: the list, which will contain the types of the rows
            row: the row of the dataframe whose entries will be tested on regular expressions
        
        Returns:
            regex_list: the filled list, with the types of the entries of the row"""
            
        column_counter = 0
        for elem in row:
            #removes spaces from the beginning and the end of the entry
            elem = str(elem).strip()
            #tests the type of the entry
            regex_type = self.regex_tester(elem)
            #appends to the list with a number, to differentiate the columns of the header
            regex_list.append(regex_type+"_"+ str(column_counter))
            column_counter += 1
        
        return regex_list
    
    def regex_tester(self, elem):
        """This Function tests every element on the regular expressions contained in types_dict
        
        Parameters:
            elem: the Element to be tested on every regular expression
        
        Returns:
            key or "String": a string, which indicates the type of elem"""
            
        for key in self.types_dict.keys():
            #returns the key of types_dict the regular expression has matched, e.g. "Bool", "Int",...
            match = self.types_dict[key].fullmatch(elem)
            if match:
                return key
        #If no regular expression fits, "String" will be assumed
        return "String"
    
    
