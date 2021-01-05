# -*- coding: utf-8 -*-

import tkinter as tk
import pandas as pd
import io
from tkinter import ttk 
from pandastable import Table, TableModel
import reader
from tkinter.messagebox import showwarning, showinfo, showerror
from tkinter.filedialog import askopenfilenames, asksaveasfilename, askopenfile
from pathlib import Path
from chardet import detect
from math import log, ceil, floor 

class reader_and_gui_interface():
    """This class acts as an interface between instances of the class reader
    and instances of the class gui, to separate these two classes, so that 
    reader can be operated as an API and the class gui just takes the methods of reader
    and realises them in a gui"""

    def __init__(self):
        """The constructor of the class reader_and_gui_interface.
        If defines the following attributes for every instance of the class:
        
            reader: a instance of the class reader, to have the methods and attributes of reader available for the gui
            index: an integer, which counts the Elements of the main Listbox in the gui, where the filenames are stored
            main_dataframe: the main dataframe, to which all opened files are appended to, if they are compatible"""
            
        self.reader = reader.reader()
        self.__index:int = 0
        self.main_dataframe = pd.DataFrame()

        
    
    def getDataframe(self):
        """A simple function, which gets main_dataframe from the reader object and puts it in main_dataframe 
        of this object, to update pandastable
        
        Returns:
            nothing or void"""
        
        self.main_dataframe = self.reader.giveDataframe()

    def ShowFilesInterface(self, listbox:tk.Listbox):
        """ShowFilesInterface asks the user to select the file or files he wants to see,
        opens them with the method read_with_init_settings of the reader object, but only if they are
        csv or xml files, and inserts them in the listbox for files in the gui
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected

        Returns:
            nothing or void"""
        
        try:  
            self.__names = askopenfilenames()
            for filename in self.__names:
                try:
                    #tests if the file is a csv or xml file
                    if filename.endswith(".csv") or filename.endswith(".xml"):
                        #opens each file with its sniffed parameters
                        #for xml files a additional xsl Stylesheet has to be chosen later
                        self.reader.read_with_init_settings(filename)
                    else:
                        showwarning("Warning!", "Only CSV or XML Files are allowed!")
                        continue
                except ValueError as value_error:
                    #deletes files which cannot be opened and read from opened_files_dict
                    if filename in self.reader.opened_files_dict.keys():
                        self.reader.opened_files_dict.pop(filename)
                    showerror("Error!", value_error)
                    
            
            listbox.delete(0, tk.END)
            self.__index = 0
            #inserts each filename in the listbox with its corresponding index
            for name in self.reader.opened_files_dict.keys():        
                listbox.insert(self.__index, name)
                self.__index += 1 
            #gives each entry of the listbox a selection event, to select the file and change its parameters later
            listbox.select_set(self.__index-1)
            listbox.event_generate("<<ListboxSelect>>")  
        except OSError:
            showerror("Error!", "File could not be opened!")
                       
            

    def RemoveFilesInterface(self, listbox:tk.Listbox):
        """Removes Files from the main listbox and from the opened_files_dict dictionary
        
        Parameters: 
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
        
        Returns:
            nothing or void"""
        
        #gets the index of the selected element of the listbox
        selected_elem = listbox.curselection()
        if selected_elem == ():
            return
        #gets the name of the selected element
        elem_name = listbox.get(selected_elem)
        if elem_name in self.reader.opened_files_dict:   
            #removes file from listbox and dictionary        
            self.reader.RemoveFilesFunctionality(elem_name)
            listbox.delete(selected_elem)
        else:
            showerror("Error!", "Selected File is not in the List")

        #if the dictionary gets empty while removing files the listbox index will be reset
        if len(self.reader.opened_files_dict) == 0:
            self.__index = 0

    def ClearAllFilesInterface(self, listbox:tk.Listbox):
        """Clears the whole listbox and opened_files_dict of entries
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
        
        Returns:
            nothing or void"""
            
        listbox.delete(0, self.__index)
        self.reader.ClearAllFilesFunctionality()
        self.__index = 0

    def setUserEncoding(self, listbox:tk.Listbox, encoding_textbox:tk.Entry, wanted_encoding:str):       
        """This Function takes the string, the user typed in the textbox for encoding for this file and 
        tries to set the encoding of the file to this string.
        If its not a valid encoding, the default sniffed encoding of the file will be used
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            encoding_textbox: a Entry widget from tkinter, in which the user can type in the wanted encoding
            wanted_encoding: the string the user typed into encoding_textbox
        
        Returns:
            filename: the selected filename from the listbox"""
            
        #gets selected element of the listbox 
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        
        try:
            #updates the csv file with the wanted encoding
            self.reader.update_csv_with_personal_settings(filename,
                                            None,
                                            wanted_encoding)
            return filename
        #if the encoding is not valid for this file
        except LookupError:
            #updates the encoding textbox, to show the default encoding sniffed from the file
            self.updateEncodingTextbox(encoding_textbox, filename)
            showerror("Error!", "Cannot encode "+filename+" with encoding: "+wanted_encoding)
        #if the file cannot be parsed or another error occurs
        except ValueError as value_error:
            showerror("Error!", "For "+filename+" the following encoding error occured: "+value_error)
    
    def updateEncodingTextbox(self, encodings_textbox:tk.Entry, selected_file:str):
        """updates the textbox for encoding, so that it shows the encoding used to decode the file
        
        Parameters:
            encodings_textbox: a Entry widget from tkinter, in which the user can type in the wanted encoding
            selected_file: the file, which has been selected in the main listbox
        
        Returns:
            nothing or void"""
            
        #empties textbox
        encodings_textbox.delete(0, tk.END)
        if selected_file is not None:
            #overwrites contents of the textbox with the encoding used for selected_file
            encodings_textbox.insert(0, self.reader.opened_files_dict[selected_file]["Encoding"])
    
    def setUserDelimiter(self, listbox:tk.Listbox, delimiter_textbox:tk.Entry, wanted_delimiter:str):
        """Sets the delimiter or separator of the file selected in the listbox to the string the user typed into the textbox for
        the delimiter
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            delimiter_textbox: a Entry widget for the user to type in the wanted delimiter
            wanted_delimiter: the string the user typed into delimiter_textbox, which will be used as a delimiter
        
        Returns:
            filename: the selected file from the main listbox"""
            
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        #length-2-Delimiters are invalid
        if len(str(wanted_delimiter)) > 1:
            showerror("Error!", "Delimiter has to have a length of 1")
            self.updateDelimiterTextbox(delimiter_textbox, filename)
            return
        try:
            #updates the dataframe with the new delimiter
            self.reader.update_csv_with_personal_settings(filename,
                                            None,
                                            None,
                                            wanted_delimiter)
            self.updateDelimiterTextbox(delimiter_textbox, filename) 
            return filename
        
        #if a ValueError occurs the default Delimiter, which has been sniffed from the file will be set again and a Error Message pops up
        except ValueError:
            _,origin_dialect = self.reader.csvSniffer(filename)
            origin_delimiter = origin_dialect.delimiter
            self.reader.opened_files_dict[filename]["Delimiter"] = origin_delimiter
            self.updateDelimiterTextbox(delimiter_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", wanted_delimiter+" is a invalid Delimiter for "+filename)
            return      
        
    
    def updateDelimiterTextbox(self, delimiter_textbox:tk.Entry, selected_file:str):
        """Updates the Textbox the Delimiter is placed in, to show the user which Delimiter is currently used
        
        Parameters:
            delimiter_textbox: a Entry widget for the user to type in the wanted delimiter
            selected_file: the file, which has been selected in the main listbox
        
        Returns:
            nothing or void"""
        
        delimiter_textbox.delete(0, tk.END)
        if selected_file is not None:
            delimiter_textbox.insert(0, self.reader.opened_files_dict[selected_file]["Delimiter"])
    
    
    def setUserQuotechar(self, listbox:tk.Listbox, quotechar_textbox:tk.Entry, wanted_quotechar:str):
        """Sets the character, which will be used for the quoting of the file selected in the listbox
        to the string the user typed into the textbox for the quotchar
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            quotechar_textbox: a Entry widget for the user to type in the wanted quotechar
            wanted_quotechar: the character the user typed into quotechar_textbox, which will be used as the quotechar
        
        Returns:
            filename: the selected file from the main listbox"""
            
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        
        try:
            self.reader.update_csv_with_personal_settings(filename,
                                            None,
                                            None,
                                            None,
                                            wanted_quotechar)
            self.updateQuotecharTextbox(quotechar_textbox, filename) 
            return filename
        
        #Error Handling
        #sets the quotechar back to the default sniffed value if the quotechar is invalid
        except ValueError:
            _,origin_dialect = self.reader.csvSniffer(filename)
            self.reader.opened_files_dict[filename]["QuoteChar"] = origin_dialect.quotechar
            self.updateQuotecharTextbox(quotechar_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", wanted_quotechar+" is not a valid Quotechar for"+filename)
            return
        #sets the quotechar back to the default sniffed value if another error occurs
        except TypeError as type_error:
            _,origin_dialect = self.reader.csvSniffer(filename)
            self.reader.opened_files_dict[filename]["QuoteChar"] = origin_dialect.quotechar
            self.updateQuotecharTextbox(quotechar_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", type_error)
            return
        
    def updateQuotecharTextbox(self, quotechar_textbox:tk.Entry, selected_file:str):
        """Updates the Textbox the character for the quoting of the file is placed in,
        to show the user which character is currently used
        
        Parameters:
            quotechar_textbox: a Entry widget for the user to type in the wanted quotechar
            selected_file: the file, which has been selected in the main listbox
        
        Returns:
            nothing or void"""
            
        quotechar_textbox.delete(0, tk.END)
        if selected_file is not None:
            quotechar_textbox.insert(0, self.reader.opened_files_dict[selected_file]["QuoteChar"])
        
    def setUserHeader(self, listbox:tk.Listbox, header_checkbox_value):
        """Takes the boolean value of the checkbox for the header and sets the Header of the file accordingly
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            header_checkbox_value: the boolean value of the header checkbox
            
        Returns:
            filename: the selected file from the main listbox"""
         
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        #the value has to be converted to bool, because the variable, which tracks the status of the checkbox can only
        #be set to 0 or 1
        want_header = bool(header_checkbox_value.get())
        try:
            self.reader.update_csv_with_personal_settings(filename,
                                                        want_header)
        #if a header cannot be set
        except ValueError as value_error:
            showerror("Error!", value_error)
            return
        
        self.updateHeaderCheckbox(header_checkbox_value, filename) 
        return filename
    
        
            
    def updateHeaderCheckbox(self, header_checkbox_value:tk.IntVar, selected_file:str):
        """updates the checkbox in the gui to show if the header is set or not
        
        Parameters:
            header_checkbox_value: the value of the checkbox for the header
            selected_file: the file, which has been selected in the main listbox
        
        Returns:
            nothing or void"""
            
        header_checkbox_value.set(0)
        if selected_file is not None:
            #needs to be converted to int, because the checkbox only takes 0 or 1
            selected_file_header = int(self.reader.opened_files_dict[selected_file]["hasHeader"])
            header_checkbox_value.set(selected_file_header)
    
            
    def setUserSkipSpaces(self, listbox:tk.Listbox, skip_spaces_checkbox_value:tk.IntVar):
        """Takes the boolean value of the skip_spaces_checkbox and skips the spaces at the beginning of a entry of the dataframe
        if there are any
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            skip_spaces_checkbox_value: the boolean value of the skip_spaces_checkbox
            
        Returns:
            filename: the selected file from the main listbox"""
            
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        want_skip_spaces = bool(skip_spaces_checkbox_value.get())

        self.reader.update_csv_with_personal_settings(filename,
                                            None,
                                            None,
                                            None,
                                            None,
                                            want_skip_spaces)
        self.updateSkipSpacesCheckbox(skip_spaces_checkbox_value, filename) 
        return filename
    
        
            
    def updateSkipSpacesCheckbox(self, skip_spaces_checkbox_value:tk.IntVar, selected_file:str):
        """updates the checkbox in the gui to show if skip_spaces is set or not
        
        Parameters:
            skip_spaces_checkbox_value: the boolean value of the skip_spaces_checkbox
            selected_file: the file, which has been selected in the main listbox
        
        Returns:
            nothing or void"""
            
        skip_spaces_checkbox_value.set(0)
        if selected_file is not None:
            selected_file_skip_spaces = int(self.reader.opened_files_dict[selected_file]["skipInitSpace"])
            skip_spaces_checkbox_value.set(selected_file_skip_spaces)
            
    def setUserLineTerminator(self, listbox:tk.Listbox, line_terminator_textbox:tk.Entry, wanted_line_terminator:str):
        """Sets the character, which will be used for the end of a line of the file selected in the listbox
        to the string the user typed into the textbox for the Line Terminator
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            line_terminator_textbox: a Entry widget for the user to type in the wanted Line Terminator
            wanted_line_terminator: the character the user typed into line_terminator_textbox, which will be used as the Line Terminator
        
        Returns:
            filename: the selected file from the main listbox"""
            
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        #only length-1-line terminators are valid
        if len(str(wanted_line_terminator)) > 1:
            showerror("Error!", "Only length-1 line Terminators are supported")
            self.updateLineTerminatorTextbox(line_terminator_textbox, filename)
            return
        try:
            #updates the dataframe with the wanted Line Terminator
            self.reader.update_csv_with_personal_settings(filename,
                                            None,
                                            None,
                                            None,
                                            None,
                                            None,
                                            wanted_line_terminator)
            self.updateLineTerminatorTextbox(line_terminator_textbox, filename) 
            return filename
        
        #Error Handling
        #Parse Error: if the Line Terminator character can't be parsed
        except pd.errors.ParserError as parser_error:
            showerror("Error!", parser_error)
        #if a ValueError occurs, the default sniffed Line Terminator from the file will be used again
        except ValueError:
            _,origin_dialect = self.reader.csvSniffer(filename)
            self.reader.opened_files_dict[filename]["lineTerminator"] = origin_dialect.lineterminator
            self.updateLineTerminatorTextbox(line_terminator_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", wanted_line_terminator+" is not a valid Line Terminator for"+filename)
            return
        #the same as with a ValueError
        except TypeError as type_error:
            _,origin_dialect = self.reader.csvSniffer(filename)
            self.reader.opened_files_dict[filename]["lineTerminator"] = origin_dialect.lineterminator
            self.updateLineTerminatorTextbox(line_terminator_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", type_error)
            return 
        
        
    def updateLineTerminatorTextbox(self, line_terminator_textbox:tk.Entry, selected_file:str):
        """Updates the Textbox the character for the Line Terminator of the file is placed in,
        to show the user which character is currently used
        
        Parameters:
            line_terminator_textbox: a Entry widget for the user to type in the wanted Line Terminator
            selected_file: the file, which has been selected in the main listbox
        
        Returns:
            nothing or void"""
            
        line_terminator_textbox.delete(0, tk.END)
        if selected_file is not None:
            #if no Line Terminator is given, nothing will be written into the textbox
            if self.reader.opened_files_dict[selected_file]["lineTerminator"] == None:
                return
            else:
                line_terminator_textbox.insert(0, ""+self.reader.opened_files_dict[selected_file]["lineTerminator"])
                
                
    def setUserQuoting(self, listbox:tk.Listbox, quoting_var:tk.IntVar):
        """Sets the quoting style of the File according to the selected radio Button in the gui.
        There are four different quoting styles to choose:
        0: Minimal quoting
        1: Everything will be quoted
        2: All non numeric fields of the dataframe will be quoted
        3: nothing will be quoted
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            quoting_var: the integer variable, which has one of the four above mentioned values to set the quoting style
        
        Returns:
            filename: the selected file from the main listbox"""
            
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        #gets the integer value to set the quoting
        quoting = quoting_var.get()
        self.reader.update_csv_with_personal_settings(filename,
                                                    None,
                                                    None,
                                                    None,
                                                    None,
                                                    None,
                                                    None,
                                                    quoting,
                                                    )
        self.updateQuotingRadioButtons(quoting_var, filename) 
        
        return filename
    
    def updateQuotingRadioButtons(self, quoting_var:tk.IntVar, selected_file:str):
        """updates the variable for the quoting style, so the right radio button is selected in the gui
        
        Parameters:
            quoting_var: the integer variable, which has one of the four above mentioned values to set the quoting style
            selected_file: the file, which has been selected in the main listbox
        
        Returns:
            nothing or void"""
        
        quoting_var.set(0)
        if selected_file is not None:
            selected_file_quoting = self.reader.opened_files_dict[selected_file]["Quoting"]
            #sets the variable to the value of the quoting, to select the according radio button
            quoting_var.set(selected_file_quoting)
            
            
    def csvReset(self, listbox:tk.Listbox):
        """Resets the selected csv File to have its default values for its Parameters again through sniffing from the file
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
        
        Returns:
            filename: the selected file from the main listbox"""
            
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        if filename in self.reader.opened_files_dict.keys():
            #sniffs dialect and header from file again
            sniffHeader, dialect = self.reader.csvSniffer(filename)
            if self.reader.multiple_files_counter <= 1:
                endswith_slice = -2
            else:
                endswith_slice = floor(log(self.reader.multiple_files_counter, 10)+2)
                endswith_slice *= -1
            if filename.endswith("_", endswith_slice, -1):
                tmp_filename = filename[:endswith_slice:]
            else:
                tmp_filename = filename
            #sniffs encoding
            enc = detect(Path(tmp_filename).read_bytes())
            self.reader.opened_files_dict[filename]["lineTerminator"] = None
            #updates file with default parameters
            self.reader.update_csv_with_personal_settings(filename,
                                                          sniffHeader,
                                                          enc["encoding"],
                                                          dialect.delimiter,
                                                          dialect.quotechar,
                                                          dialect.skipinitialspace,
                                                          self.reader.opened_files_dict[filename]["lineTerminator"],
                                                          dialect.quoting)
            return filename
        else:
            showerror("Error!", "File cannot be found in Listbox")
            return
            
        
    def getXSLFile(self, listbox:tk.Listbox, xsl_textbox:tk.Entry):
        """reads xsl Stylesheer from file dialog
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            xsl_textbox: The textbox the relative or absolute filpath of the xsl Stylesheet will be written in
        
        Returns:
            True of False to check if the xsl Stylesheet can be used for the xml or not"""
         
        if len(listbox.curselection()) == 0:
            showerror("Error!", "No XML-File selected to set Stylesheet for. Please select XML-File in Listbox")
            return False
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        #file dialog to select xsl File
        xsl_file = askopenfile()
        if xsl_file is None:
            return
        if xsl_file.name.endswith(".xsl"):
            try:
                #reads Parameters from xsl Stylesheet
                self.reader.getXMLParameters(filename, xsl_file.name)  
            except ValueError as value_error:
                showerror("Error!", value_error)
                return False
            self.reader.opened_files_dict[filename]["xsl_file"] = xsl_file.name
            #writes the relative or absolute filepath in the textbox
            self.updateXSLFileTextbox(xsl_textbox, filename)
            
            return True

        else:
            showwarning("Warning!", "Only XSL-Files are allowed") 
            return False
    
    def updateXSLFileTextbox(self, xsl_textbox:tk.Entry, selected_file:str):
        """updates the xsl textbox to write the absolute or relative filepath of the
        xsl Stylesheet in it
        
        Parameters:
            xsl_textbox: the textbox for the filepath
            selected_file: the file, which has been selected in the main listbox
        
        Returns:
            nothing or void"""
        
        #sets state of the textbox to normal
        xsl_textbox.config(state="normal")
        xsl_textbox.delete(0, tk.END)
        try:
            if self.reader.opened_files_dict[selected_file]["xsl_file"] is not None:
                xsl_textbox.insert(0, self.reader.opened_files_dict[selected_file]["xsl_file"])
                
        except KeyError:
            return
        #sets state of the textbox back to readonly, so the user cannot change the filepath of the xsl Stylesheet in the gui
        xsl_textbox.config(state="readonly") 
        
    def showXMLParameterFunctionality(self, listbox:tk.Listbox, parameter_listbox:tk.Listbox, filename:str):  
        """writes the found xsl Parameters in the listbox in the xml configurator labelframe
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            parameter_listbox: the listbox for the xsl Parameters found in the xsl Stylesheet
            filename: the selected file, whose parameters shall be written in parameter_listbox
            
        Returns:
            nothing or void"""
            
        index = 0
        #gets list of parameters from the xml file, which have been read beforehand
        tmp_parameters_list = list(self.reader.opened_files_dict[filename])
        try:
            #inserts the parameters in the listbox
            for i in range(self.reader.opened_files_dict[filename]["parameters_len"]):
                parameter_listbox.insert(index, tmp_parameters_list[i])
                index += 1
        except KeyError:
            return
        
    def chooseXMLParameter(self, listbox:tk.Listbox, parameter_listbox:tk.Listbox, xml_parameters_textbox:tk.Entry, filename:str):
        """This function lets the user choose a parameter from parameter_listbox, and the corresponding value of the parameter
        will be written in xml_parameters_textbox
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            parameter_listbox: the listbox for the xsl Parameters found in the xsl Stylesheet
            xml_parameters_textbox: a textbox below parameter_listbox in the gui, to write an change the parameter value
            filename: the selected file, whose parameters shall be written in parameter_listbox
        Returns:
            nothing or void"""
            
        try:
            selected_elem = parameter_listbox.curselection()
        
            parameter = parameter_listbox.get(selected_elem)
        except tk.TclError:
            return
        
        #writes the default value of the parameter in xml_parameters_textbox
        xml_parameters_textbox.config(state="normal")
        xml_parameters_textbox.delete(0, tk.END)   
        xml_parameters_textbox.insert(0, self.reader.opened_files_dict[filename][parameter][1:-1])
    
    def changeXMLParameter(self, listbox:tk.Listbox, parameter_listbox:tk.Listbox, parameters_textbox:tk.Entry, filename:str):
        """lets the user change the content of the Parameters textbox to set a personal value for the parameter
        
        Parameters: 
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            parameter_listbox: the listbox for the xsl Parameters found in the xsl Stylesheet
            parameters_textbox: a textbox below parameter_listbox in the gui, to write an change the parameter value
            filename: the selected file, whose parameters shall be written in parameter_listbox
        
        Returns:
            nothing or void"""
            
        try:
            selected_elem = parameter_listbox.curselection()        
            parameter = parameter_listbox.get(selected_elem)
        except tk.TclError:
            return
        #gets the value the user has typed into the textbox
        value = parameters_textbox.get()
        if value is not None:
            try:
                #updates the dataframe with the changed parameter
                self.reader.addXMLParameter(filename, parameter, value)
            #if a error occurs all parameters will be set back to their default values
            except ValueError as value_error:
                self.reader.getXMLParameters(filename, self.reader.opened_files_dict[filename]["xsl_file"]) 
                showerror("Error!", value_error)
    
    def setXMLUserHeader(self, listbox:tk.Listbox, xml_header_var:tk.IntVar):
        """gets the value of the checkbox for the xml header of the selected file and sets the header accordingly
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
            xml_header_var: the variable, which holds the selected value of the checkbox for the header
        
        Returns:
            filename: the selected file from the main listbox"""
            
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        #the variable for the checkbox can only have the values 0 or 1, so it has to be converted to a bool
        want_header = bool(xml_header_var.get())

        self.reader.addXMLParameter(filename, None, None, want_header)
        self.updateXMLUserHeader(xml_header_var, listbox) 
        return filename
    
    def updateXMLUserHeader(self, xml_header_var:tk.IntVar, listbox:tk.Listbox):
        """updates the checkbox to show, if the xml file has a header or not
        
        Parameters:
            xml_header_var: the variable, which holds the selected value of the checkbox for the header
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
        
        Returns:
            nothing or void"""
            
        selected_elem = listbox.curselection()
        selected_file = listbox.get(selected_elem)
        xml_header_var.set(0)
        if selected_file is not None:
            #value of the checkbox can only be 0 or 1, so boolean values have to be converted to int
            selected_file_header = int(self.reader.opened_files_dict[selected_file]["hasHeader"])
            xml_header_var.set(selected_file_header)
    
    def xmlResetFunctionality(self, listbox:tk.Listbox):
        """resets the selected xml file to its default values from the xsl Stylesheet
        
        Parameters:
            listbox: the main listbox at the top of the gui window, to show which files have been selected and in which order
                    they have been selected
        Returns:
            selected_file: the selected file from the main listbox"""
            
        selected_elem = listbox.curselection()
        selected_file = listbox.get(selected_elem)
        #resets Parameters with the given xsl Stylesheet
        self.reader.getXMLParameters(selected_file, self.reader.opened_files_dict[selected_file]["xsl_file"])
        return selected_file
    
    def finalImporterFunctionality(self, import_var_value:tk.IntVar):
        """imports the chosen files according to a value from the radiobuttons
        
        Parameters:
            import_var_value: the value, which decides what data type the dataframe will be converted to
                            1: import as a dictionary
                            2: import as a List of Lists
                            3: import as a Numpy Array
                            4: import as a Dataframe
        
        Returns:
            nothing or void"""
            
        if import_var_value == 1:
            self.reader.importAsDictionary()
        elif import_var_value ==2:
            self.reader.importAsListOfLists()
        elif import_var_value == 3:
            try:
                self.reader.importAsNumPyArray()
            except ValueError as value_error:
                raise ValueError(value_error)
        elif import_var_value == 4:
            self.reader.importAsPandasDataframe()
            
    def finalCSVExportFunctionality(self, encoding:str, delimiter:str, quotechar:str, line_terminator:str):
        """exports the chosen files as a csv file
        
        Parameters:
            encoding: the encoding of the csv file
            delimiter: the delimiter of the csv file
            quotechar: the character, which shall be used for quoting
            line_terminator: the character, which shall be used for ending lines
        
        Returns:
            nothing or void"""
            
        #delimiter, quotechar and line_terminator can only be length-1-characters
        if len(str(delimiter)) <= 1 and len(str(quotechar)) <= 1 and len(str(line_terminator)) <= 1:
            #default values if nothing is chosen
            if len(str(delimiter)) == 0:
                delimiter = ","
            if len(str(quotechar)) == 0:
                quotechar = "\""
            if len(str(line_terminator)) == 0:
                line_terminator = "\r\n"
            #the realtive or absolute filepath, the csv file will be saved at
            dest_filepath = asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile="export.csv")
            try:
                #converts main_dataframe to a csv file
                self.reader.exportAsCSVFile(dest_filepath, encoding, delimiter, quotechar, line_terminator)
            except LookupError as look_up_error:
                raise LookupError(look_up_error)
        else:
            raise ValueError
            
    def finalXMLExportFunctionality(self, encoding:str):
        """exports the chosen files as a xml file
        
        Parameters:
            encoding: the encoding of the xml file
        
        Returns:
            nothing or void"""
            
        #the realtive or absolute filepath, the csv file will be saved at
        dest_filepath = asksaveasfilename(defaultextension=".xml",
            filetypes=[("XML file", "*.xml")],
            initialfile="export.xml")
        try:
            #converts main_dataframe to a xml file
            self.reader.exportAsXMLFile(dest_filepath, encoding)
        except LookupError as look_up_error:
            raise LookupError(look_up_error)
        except ValueError as value_error:
            raise ValueError(value_error)
    


class gui(reader_and_gui_interface):
    """This class is responsible for the GUI and to call the methods from the interface class"""

    def __init__(self):
        """The constructor of the class gui. 
        It defines the Elements of the gui and a reader_and_gui_interface"""
        
        #main window of the gui, where all elements are placed in
        self.root = tk.Tk()
        self.root.minsize(1200, 630)
        self.root.title("CSV_XML_Importer")
        self.root.config(bg="gray16")
        #defines a reader_and_gui_interface object, to get access to its methods
        super().__init__()
        
        #Labelframe of the importer window, for the file listbox and the import buttons
        self.Importer_Labelframe = tk.LabelFrame(self.root, text="Importer", bg="gray24", fg="white")
        self.Importer_Labelframe.grid(row=1, column=1, padx=10, pady=10, sticky='NSEW')
        
        #labelframe for the csv and xml configurator
        self.Configurator_Labelframe = tk.LabelFrame(self.root, text="File-Configurator", bg="gray24", fg="white")
        self.Configurator_Labelframe.grid(row=1, column=2, padx=10, pady=10)
        
        #labelframe for the pandastable preview of the file
        self.preview_table_Labelframe = tk.LabelFrame(self.root, text="Preview", bg="gray24", fg="white")
        self.preview_table_Labelframe.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="NSEW")
       
        #lists for the csv and xml parameters, to shorten the coloring of all the elements
        self.csv_parameters_list:list = []
        self.csv_parameters_labels:list = []
        self.xml_parameters_list:list = []
        self.xml_parameters_labels:list = []
        #saves last selected filename, if the listbox loses focus
        self.filename:str = ""
        
        #defines the frames for the file buttons and the listbox to place them in the labelframe
        file_buttons_frame = tk.Frame(self.Importer_Labelframe, bg="gray24")
        file_buttons_frame.pack(side=tk.LEFT)
        listbox_frame = tk.Frame(self.Importer_Labelframe, bg="gray24")
        listbox_frame.pack(side=tk.TOP)
        
        #labelframe for the csv file configurator
        self.csv_configurator_frame = tk.LabelFrame(self.Configurator_Labelframe, text="CSV-Configurator", fg="gray")
        self.csv_configurator_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.csv_parameters_labels.append(self.csv_configurator_frame)
        
        #listbox for the filenames
        self.listbox = tk.Listbox(listbox_frame, width=50, selectmode=tk.SINGLE, height=17)
        scrollbar_x_listbox = tk.Scrollbar(listbox_frame, orient="horizontal")
        scrollbar_y_listbox = tk.Scrollbar(listbox_frame)
        scrollbar_x_listbox.pack(side=tk.BOTTOM, fill=tk.BOTH)
        scrollbar_y_listbox.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.listbox.config(xscrollcommand=scrollbar_x_listbox.set)
        self.listbox.config(yscrollcommand=scrollbar_y_listbox.set)
        scrollbar_x_listbox.config(command=self.listbox.xview)
        scrollbar_y_listbox.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.BOTTOM, padx=10, pady=10)
        #executes listboxSelectionChanged if a item from the listbox is selected
        self.listbox.bind("<<ListboxSelect>>", self.listboxSelectionChanged)  
        
        #textbox to show the encoding and to let the user change the encoding of the csv files
        self.encodings_textbox_label = tk.Label(self.csv_configurator_frame, text="Encoding: ", fg="gray")
        self.encodings_textbox_label.grid(row=1, column=1, pady=2)
        self.encoding_textbox = tk.Entry(self.csv_configurator_frame, exportselection=0, state="disabled")     
        self.encoding_textbox.grid(row=1,column=2, padx=2, pady=2)
        self.encoding_textbox.bind("<Return>", self.setFileEncoding)
        #saves the textbox and its label in the lists, for coloring
        self.csv_parameters_labels.append(self.encodings_textbox_label)
        self.csv_parameters_list.append(self.encoding_textbox)
        
        #textbox for the delimiter of the csv files
        self.delimiter_textbox_label = tk.Label(self.csv_configurator_frame, text="Delimiter: ", fg="gray")
        self.delimiter_textbox_label.grid(row=3, column=1, pady=5)
        self.delimiter_textbox = tk.Entry(self.csv_configurator_frame, exportselection=0, state="disabled", width=2)     
        self.delimiter_textbox.grid(row=3, column=2, padx=5, pady=5)
        #sets the new delimiter to the content of the textbox if Enter is pressed
        self.delimiter_textbox.bind("<Return>", self.setFileDelimiter)   
        self.csv_parameters_labels.append(self.delimiter_textbox_label)
        self.csv_parameters_list.append(self.delimiter_textbox) 
        
        #textbox for the character, which will be used for quoting in the csv files
        self.quotechar_textbox_label = tk.Label(self.csv_configurator_frame, text="Quotechar: ", fg="gray")
        self.quotechar_textbox_label.grid(row=4, column=1, pady=4)
        self.quotechar_textbox = tk.Entry(self.csv_configurator_frame, exportselection=0, state="disabled", width=2)     
        self.quotechar_textbox.grid(row=4, column=2, padx=4, pady=4)
        self.quotechar_textbox.bind("<Return>", self.setFileQuotechar) 
        self.csv_parameters_labels.append(self.quotechar_textbox_label)
        self.csv_parameters_list.append(self.quotechar_textbox) 
        
        #checkbox to activate or deactivate the header for the selected csv file
        self.header_var = tk.IntVar()
        self.header_checkbox_label = tk.Label(self.csv_configurator_frame, text="Header: ", fg="gray")
        self.header_checkbox_label.grid(row=5, column=1, pady=4)
        self.header_checkbox = tk.Checkbutton(self.csv_configurator_frame, state="disabled", command=self.setFileHeader, variable=self.header_var)
        self.header_checkbox.grid(row=5, column=2, padx=4, pady=4)
        self.csv_parameters_labels.append(self.header_checkbox_label)
        self.csv_parameters_list.append(self.header_checkbox)
        
        #checkbox to set if initial spaces of a field should be skipped or not in csv files
        self.skip_spaces_var = tk.IntVar()
        self.skip_spaces_checkbox_label = tk.Label(self.csv_configurator_frame, text="Skip Initial Spaces: ", fg="gray")
        self.skip_spaces_checkbox_label.grid(row=6, column=1, pady=4)
        self.skip_spaces_checkbox = tk.Checkbutton(self.csv_configurator_frame, state="disabled", command=self.setFileSkipSpaces, variable=self.skip_spaces_var)
        self.skip_spaces_checkbox.grid(row=6, column=2, padx=4, pady=4)
        self.csv_parameters_labels.append(self.skip_spaces_checkbox_label)
        self.csv_parameters_list.append(self.skip_spaces_checkbox)
        
        #textbox for the character, which is used for the line Terminator and to change the line terminator
        self.line_terminator_textbox_label = tk.Label(self.csv_configurator_frame, text="Line Terminator: ", fg="gray")
        self.line_terminator_textbox_label.grid(row=7, column=1, pady=4)
        self.line_terminator_textbox = tk.Entry(self.csv_configurator_frame, exportselection=0, state="disabled", width=2)     
        self.line_terminator_textbox.grid(row=7, column=2, padx=4, pady=4)
        self.line_terminator_textbox.bind("<Return>", self.setFileLineTerminator) 
        self.csv_parameters_labels.append(self.line_terminator_textbox_label)
        self.csv_parameters_list.append(self.line_terminator_textbox)
        
        #radiobuttons to select the 4 different styles of quoting, minimal, all, non numeric and none
        self.quoting_var = tk.IntVar()
        self.quoting_var.set(None)
        self.quoting_radiobuttons_label = tk.Label(self.csv_configurator_frame, text="Quoting: ", fg="gray")
        self.quoting_radiobuttons_label.grid(row=8, column=1, pady=4)
        self.quote_minimal_button = tk.Radiobutton(self.csv_configurator_frame, text="Minimal", variable=self.quoting_var, value=0, state="disabled", command=self.setFileQuoting)
        self.quote_minimal_button.grid(row=8, column=2, padx=4, pady=4)
        self.quote_all_button = tk.Radiobutton(self.csv_configurator_frame, text="All", variable=self.quoting_var, value=1, state="disabled", command=self.setFileQuoting)
        self.quote_all_button.grid(row=8, column=3, padx=4, pady=4)
        self.quote_non_numeric_button = tk.Radiobutton(self.csv_configurator_frame, text="Non Numeric", variable=self.quoting_var, value=2, state="disabled", command=self.setFileQuoting)
        self.quote_non_numeric_button.grid(row=9, column=2, padx=4, pady=4)
        self.quote_none_button = tk.Radiobutton(self.csv_configurator_frame, text="None", variable=self.quoting_var, value=3, state="disabled", command=self.setFileQuoting)
        self.quote_none_button.grid(row=9, column=3, padx=4, pady=4)
        self.csv_parameters_labels.append(self.quoting_radiobuttons_label)
        self.csv_parameters_list.append(self.quote_minimal_button)
        self.csv_parameters_list.append(self.quote_all_button)
        self.csv_parameters_list.append(self.quote_non_numeric_button)
        self.csv_parameters_list.append(self.quote_none_button)
        
        #reset button the reset all parameters of the selected csv file to its defaults
        self.csv_reset_button = tk.Button(self.csv_configurator_frame, text="Reset", state="disabled", command=self.csvReset)
        self.csv_reset_button.grid(row=12,column=2, padx=10, pady=10)
        self.csv_parameters_list.append(self.csv_reset_button)
        
        
        #frame for the xml parameters
        self.xml_konfigurator_frame = tk.LabelFrame(self.Configurator_Labelframe, text="XML-Configurator", fg="gray")
        self.xml_konfigurator_frame.pack(side=tk.RIGHT, padx=2, pady=2)
        self.xml_parameters_labels.append(self.xml_konfigurator_frame)
        
        #textbox to show the relative or absolute filepath of the xsl Stylesheet for the selected xml file
        self.xsl_stylesheet_textbox_label = tk.Label(self.xml_konfigurator_frame, text="XSL-Stylesheet:", fg="gray")
        self.xsl_stylesheet_textbox_label.grid(row=1, column=1, padx=2, pady=2)
        xsl_stylesheet_scrollbar_frame = tk.Frame(self.xml_konfigurator_frame)
        xsl_stylesheet_scrollbar_frame.grid(row=1, column=2, padx=2)
        scrollbar_x_stylesheet = tk.Scrollbar(xsl_stylesheet_scrollbar_frame, orient="horizontal")
        self.xsl_stylesheet_textbox = tk.Entry(xsl_stylesheet_scrollbar_frame, state="disabled", width=40, xscrollcommand=scrollbar_x_stylesheet.set)
        scrollbar_x_stylesheet.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.xsl_stylesheet_textbox.pack(side=tk.BOTTOM)
        scrollbar_x_stylesheet.config(command=self.xsl_stylesheet_textbox.xview)
        #button, which opens a file dialog to choose a xsl Stylesheet
        self.button_add_xsl_File = tk.Button(self.xml_konfigurator_frame, text="Choose XSL File", command=self.OpenXSLFile, state="disabled")
        self.button_add_xsl_File.grid(row=2, column=2)
        self.xml_parameters_labels.append(self.xsl_stylesheet_textbox_label)
        self.xml_parameters_list.append(self.xsl_stylesheet_textbox)
        self.xml_parameters_list.append(self.button_add_xsl_File)
        
        #used for validation later on, if a valid xsl file is chosen
        self.valid_xsl_file = False
        
        self.xml_parameters_listbox_label = tk.Label(self.xml_konfigurator_frame, text="XML-Parameters:", fg="gray")
        self.xml_parameters_listbox_label.grid(row=3, column=1, pady=2, padx=2)
        xml_parameter_scrollbar_frame = tk.Frame(self.xml_konfigurator_frame)
        xml_parameter_scrollbar_frame.grid(row=3, column=2, padx=2, pady=2)
        scrollbar_x_parameters = tk.Scrollbar(xml_parameter_scrollbar_frame, orient="horizontal")
        scrollbar_y_parameters = tk.Scrollbar(xml_parameter_scrollbar_frame)
        #listbox, which shows the parameters, which have been found in the xsl Stylesheet
        self.xml_parameter_listbox = tk.Listbox(xml_parameter_scrollbar_frame,
                                                width=20,
                                                height=8,
                                                selectmode=tk.SINGLE,
                                                state="disabled",
                                                xscrollcommand=scrollbar_x_parameters.set,
                                                yscrollcommand=scrollbar_y_parameters.set)
        #executes showXMLParameter everytime a item from the listbox is selected
        self.xml_parameter_listbox.bind("<<ListboxSelect>>", self.showXMLParameter) 
        scrollbar_x_parameters.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.xml_parameter_listbox.pack(side=tk.LEFT)
        scrollbar_y_parameters.pack(side=tk.RIGHT, fill=tk.BOTH)
        scrollbar_x_parameters.config(command=self.xml_parameter_listbox.xview)
        scrollbar_y_parameters.config(command=self.xml_parameter_listbox.yview)
        #shows the value of the xml parameter, which has been selected in the parameter listbox
        self.xml_parameters_textbox = tk.Entry(self.xml_konfigurator_frame, state="disabled", width=2)
        self.xml_parameters_textbox.bind("<Return>", self.setXMLParameter)
        self.xml_parameters_textbox.grid(row=4, column=2)
        self.xml_parameters_labels.append(self.xml_parameters_listbox_label)
        self.xml_parameters_list.append(self.xml_parameter_listbox)
        self.xml_parameters_list.append(self.xml_parameters_textbox)
        
        #checkbox to activate or deactivate the header of the xml selected xml file
        self.xml_header_var = tk.IntVar()
        self.xml_header_checkbox_label = tk.Label(self.xml_konfigurator_frame, text="Header: ", fg="gray")
        self.xml_header_checkbox_label.grid(row=5, column=1, pady=2)
        self.xml_header_checkbox = tk.Checkbutton(self.xml_konfigurator_frame, state="disabled", command=self.setXMLHeader, variable=self.xml_header_var)
        self.xml_header_checkbox.grid(row=5, column=2, padx=2, pady=2)
        self.xml_parameters_labels.append(self.xml_header_checkbox_label)
        self.xml_parameters_list.append(self.xml_header_checkbox)
        
        #resets the parameters of the selected xml file to its defaults
        self.xml_reset_button = tk.Button(self.xml_konfigurator_frame, text="Reset", state="disabled", command=self.xmlReset)
        self.xml_reset_button.grid(row=6, column=2, padx=2, pady=2)
        self.xml_parameters_list.append(self.xml_reset_button)

        #opens a file dialog to let the user chose a csv or xml file
        self.button_addFile = tk.Button(
            file_buttons_frame, text="Add File/s", command=self.OpenFileGUI)
        self.button_addFile.pack(side=tk.TOP, padx=5, pady=5)
        #removes the selected csv or xml file
        self.button_removeFile = tk.Button(
            file_buttons_frame, text="Remove selected File", command=self.RemoveFileGUI)
        self.button_removeFile.pack(side=tk.TOP, padx=5, pady=5)
        #removes all files
        self.button_removeAllFiles = tk.Button(
            file_buttons_frame, text="Remove all Files", command=self.ClearAllFilesGUI)
        self.button_removeAllFiles.pack(side=tk.TOP, padx=5, pady=5)
        
        #pandastable preview of the chosen files
        self.preview_table = Table(self.preview_table_Labelframe, dataframe=self.main_dataframe, height=150)
        self.preview_table.show()

        #frame for the import, export and cancel buttons
        self.import_export_buttons_frame = tk.Frame(self.root, bg="gray16")
        self.import_export_buttons_frame.grid(row=4, column=2, sticky="E")
        
        #opens a toplevel window to let the user decide to which data type the dataframe should be imported
        self.button_import_as = tk.Button(
            self.import_export_buttons_frame, text="Import as...", command=self.ImportAs)
        self.button_import_as.pack(side=tk.LEFT, padx=5, pady=10)
        #opens a toplevel window to let the user export the dataframe as a csv or xml file
        self.button_export_as = tk.Button(
            self.import_export_buttons_frame, text="Export as...", command=self.ExportAs)
        self.button_export_as.pack(side=tk.LEFT, padx=5, pady=10)
        #closes the gui
        self.button_exit = tk.Button(
            self.import_export_buttons_frame, text="Cancel", command=self.root.quit)
        self.button_exit.pack(side=tk.LEFT, padx=5, pady=10)

        self.root.mainloop()


    def updatePreview(self):
        """A simple Function to update the pandastable preview table
        
        Returns:
            nothing or void"""
            
        self.getDataframe()
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        
        
    def OpenFileGUI(self):
        """Opens and shows csv and xml files in the gui
        
        Returns:
            nothing or void"""
        try:
            super().ShowFilesInterface(self.listbox)
            self.updatePreview()

        except OSError as e:
            showerror("Error!", e)
        

    def RemoveFileGUI(self):
        """Removes csv and xml files from the gui and opened_files_dict
        
        Returns:
            nothing or void"""
        super().RemoveFilesInterface(self.listbox)
        self.updatePreview()
        
        #sets every configurator element to unresponsive, because no file is selected
        self.encoding_textbox.delete(0, tk.END)
        self.delimiter_textbox.delete(0, tk.END)
        self.quotechar_textbox.delete(0, tk.END)
        self.header_var.set(0)
        self.skip_spaces_var.set(0)
        self.line_terminator_textbox.delete(0, tk.END)
        self.quoting_var.set(None)
        
        for elem in self.csv_parameters_labels:
            elem.config(fg="gray")
        for elem in self.csv_parameters_list:
            elem.config(state="disabled")
            
        self.xsl_stylesheet_textbox.config(state="normal")
        self.xsl_stylesheet_textbox.delete(0, tk.END)
        self.xsl_stylesheet_textbox.config(state="readonly")
        self.xml_parameters_textbox.delete(0, tk.END)
        self.xml_parameter_listbox.delete(0, tk.END)
        self.xml_header_var.set(0)
        self.valid_xsl_file = False
        
        for elem in self.xml_parameters_labels:
            elem.config(fg="gray")
        for elem in self.xml_parameters_list:
            elem.config(state="disabled")


    def ClearAllFilesGUI(self):
        """Removes all csv and xml files from the gui and opened_files_dict
        
        Returns:
            nothing or void"""
        super().ClearAllFilesInterface(self.listbox)
        self.updatePreview()
        
        #sets every configurator element to unresponsive, because no file is selected
        self.encoding_textbox.delete(0, tk.END)
        self.delimiter_textbox.delete(0, tk.END)
        self.quotechar_textbox.delete(0, tk.END)
        self.header_var.set(0)
        self.skip_spaces_var.set(0)
        self.line_terminator_textbox.delete(0, tk.END)
        self.quoting_var.set(None)
        
        for elem in self.csv_parameters_labels:
            elem.config(fg="gray")
        for elem in self.csv_parameters_list:
            elem.config(state="disabled")
        
        self.xsl_stylesheet_textbox.config(state="normal")
        self.xsl_stylesheet_textbox.delete(0, tk.END)
        self.xsl_stylesheet_textbox.config(state="readonly")
        self.xml_parameters_textbox.delete(0, tk.END)
        self.xml_parameter_listbox.delete(0, tk.END)
        self.xml_header_var.set(0)
        self.valid_xsl_file = False
        
        for elem in self.xml_parameters_labels:
            elem.config(fg="gray")
        for elem in self.xml_parameters_list:
            elem.config(state="disabled")


        
    def setFileEncoding(self, return_event):
        """sets the encoding of the selected csv file in the listbox to the encoding, which is given in the
        encoding textbox. If its not possible to set the encoding the default encoding from the file will be taken.
        The Textbox is confirmed by pressing enter
        
        Returns:
            nothing or void"""
        super().setUserEncoding(self.listbox, self.encoding_textbox, self.encoding_textbox.get())
        #sets the focus to the root element after pressing enter, to let the user know that the input has been processed  
        self.root.focus_set()    
        self.updatePreview()
        
    def setFileDelimiter(self, return_event):
        """sets the delimiter of the selected csv file in the listbox to the delimiter, which is given in the
        delimiter textbox. If its not possible to set the delimiter the default delimiter from the file will be taken.
        The Textbox is confirmed by pressing enter
        
        Returns:
            nothing or void"""
        super().setUserDelimiter(self.listbox, self.delimiter_textbox, self.delimiter_textbox.get())  
        self.root.focus_set()    
        self.updatePreview()
        
    def setFileQuotechar(self, return_event):
        """sets the character used for quoting of the selected csv file in the listbox to the character, which is given in the
        quotechar textbox. If its not possible to set the character the default quoting character from the file will be taken.
        The Textbox is confirmed by pressing enter
        
        Returns:
            nothing or void"""
        super().setUserQuotechar(self.listbox, self.quotechar_textbox, self.quotechar_textbox.get())  
        self.root.focus_set()    
        self.updatePreview()
        
    def setFileHeader(self):
        """gets the value of the checkbox responsible for the csv header and activates or deactivates the header
        
        Returns:
            nothing or void"""
        super().setUserHeader(self.listbox, self.header_var)  
        self.root.focus_set()    
        self.updatePreview()
    
    def setFileSkipSpaces(self):
        """gets the value of the checkbox responsible for skipping initial spaces for csv files and 
        skips or doesn't skip initial spaces
        
        Returns:
            nothing or void"""
        super().setUserSkipSpaces(self.listbox, self.skip_spaces_var)  
        self.root.focus_set()    
        self.updatePreview()
        
    def setFileLineTerminator(self, return_event):
        """sets the character used for line termination of the selected csv file in the listbox to the character, which is given in the
        lineTerminator textbox. If its not possible to set the character the default line terminator character from the file will be taken.
        The Textbox is confirmed by pressing enter
        
        Returns:
            nothing or void"""
        super().setUserLineTerminator(self.listbox, self.line_terminator_textbox, self.line_terminator_textbox.get()) 
        try: 
            self.root.focus_set()    
            self.updatePreview()
        except IndexError as index_error:
            showerror("Error!", index_error)
            return
        
    def setFileQuoting(self):
        """gets the value of the selected radio button and sets the quoting of the csv files to one of the four possible styles,
        minimal, all, non numeric and none
        
        Returns:
            nothing or void"""
        super().setUserQuoting(self.listbox, self.quoting_var)  
        self.root.focus_set()    
        self.updatePreview()
    
    def csvReset(self):
        """Resets every csv parameter of the selected file to its default sniffed value
        
        Returns:
            nothing or void"""
        selected_file = super().csvReset(self.listbox)
        super().updateEncodingTextbox(self.encoding_textbox, selected_file)
        super().updateDelimiterTextbox(self.delimiter_textbox, selected_file)
        super().updateQuotecharTextbox(self.quotechar_textbox, selected_file)
        super().updateHeaderCheckbox(self.header_var, selected_file)
        super().updateSkipSpacesCheckbox(self.skip_spaces_var, selected_file)
        super().updateLineTerminatorTextbox(self.line_terminator_textbox, selected_file)
        super().updateQuotingRadioButtons(self.quoting_var, selected_file)
        self.root.focus_set()    
        self.updatePreview()
        
    def OpenXSLFile(self):
        """asks the user to choose a xsl Stylesheet. If a valid Stylesheet is chosen, all other elements of the xml
        Configurator will be made responsive, except for the textbox, where the filepath of the xsl file is stored in,
        to prevent the user from changing the filepath without the file dialog
        
        Returns:
            nothing or void"""
        try:
            self.xml_parameter_listbox.config(state="normal")
            self.valid_xsl_file = super().getXSLFile(self.listbox, self.xsl_stylesheet_textbox)
            if self.valid_xsl_file:
                self.xml_parameters_textbox.config(state="readonly")         
                self.xml_parameters_listbox_label.config(fg="black")
                self.xml_header_checkbox_label.config(fg="black")
                self.xml_header_checkbox.config(state="normal")
                self.xml_reset_button.config(state="normal")
                super().showXMLParameterFunctionality(self.listbox, self.xml_parameter_listbox, self.filename)
                super().updateXMLUserHeader(self.xml_header_var, self.listbox)
            self.updatePreview()

        except OSError as e:
            showerror("Error!", e)
    
    def showXMLParameter(self, selection_event):
        """shows the found xml Parameters from the stylesheet in the listbox for the xml Parameters
        
        Returns:
            nothing or void"""
        super().chooseXMLParameter(self.listbox, self.xml_parameter_listbox, self.xml_parameters_textbox, self.filename)
        self.updatePreview()
    
    def setXMLParameter(self, return_event):
        """lets the user choose a xml parameter from the listbox. The value of the parameter will be shown in the textbox
        below in the gui to let the user change it
        
        Returns:
            nothing or void"""
        super().changeXMLParameter(self.listbox, self.xml_parameter_listbox, self.xml_parameters_textbox, self.filename)
        super().chooseXMLParameter(self.listbox, self.xml_parameter_listbox, self.xml_parameters_textbox, self.filename)
        self.root.focus_set()   
        self.updatePreview()
    
    def setXMLHeader(self):
        """gets the value of the xml header checkbox and activates or deactivates the header accordingly
        
        Returns:
            nothing or void"""
        try:
            super().setXMLUserHeader(self.listbox, self.xml_header_var) 
        except tk.TclError:
            showerror("Error!", "No File to set header for selected. Please select File from listbox")
            return 
        self.root.focus_set()    
        self.updatePreview()
    
    def xmlReset(self):
        """resets every parameter from the chosen xml file and resets the header
        
        Returns:
            nothing or void"""
        try:
            selected_file = super().xmlResetFunctionality(self.listbox)
            if self.valid_xsl_file:
                super().updateXSLFileTextbox(self.xsl_stylesheet_textbox, selected_file)
                self.xml_parameters_listbox_label.config(fg="black")
                self.xml_parameter_listbox.config(state="normal")
                self.xml_reset_button.config(state="normal")
                self.xml_parameter_listbox.delete(0, tk.END)
                super().showXMLParameterFunctionality(self.listbox, self.xml_parameter_listbox, self.filename)
                super().updateXMLUserHeader(self.xml_header_var, self.listbox)
        except tk.TclError:
            showerror("Error!", "No File to reset selected. Please select File from listbox")
            return
        self.root.focus_set()   
        self.updatePreview()
        
    
    def listboxSelectionChanged(self, select_event):
        """This method will be called everytime the user selects a entry in the main listbox for the files.
        It sets the according configurator to the values of its parameters
        
        Returns:
            nothing or void"""
        try:
            listbox_selection_index = self.listbox.curselection()
            self.filename = self.listbox.get(listbox_selection_index)
        except tk.TclError:
            return
        
        if len(listbox_selection_index) == 0:
            return
        else:
            if self.reader.multiple_files_counter <= 1:
                endswith_slice = -6
            else:
                endswith_slice = floor(log(self.reader.multiple_files_counter, 10)+6)
                endswith_slice *= -1
                
            selected_file = self.listbox.get(listbox_selection_index)
            #makes the csv configurator responsive and the xml configurator unresponsive, if a csv file is selected
            if selected_file.endswith(".csv") or selected_file.endswith(".csv_", endswith_slice, -1):
                self.xsl_stylesheet_textbox.config(state="normal")
                self.xsl_stylesheet_textbox.delete(0, tk.END)
                self.xsl_stylesheet_textbox.config(state="readonly")
                self.xml_parameters_textbox.delete(0, tk.END)
                self.xml_parameter_listbox.delete(0, tk.END)
                self.xml_header_var.set(0)
                for elem in self.xml_parameters_labels:
                    elem.config(fg="gray")
                for elem in self.xml_parameters_list:
                    elem.config(state="disabled")
                    
                for elem in self.csv_parameters_labels:
                    elem.config(fg="black")
                for elem in self.csv_parameters_list:
                    elem.config(state="normal")
                
                #updates every parameter box with the values of the file
                super().updateEncodingTextbox(self.encoding_textbox, selected_file)
                super().updateDelimiterTextbox(self.delimiter_textbox, selected_file)
                super().updateQuotecharTextbox(self.quotechar_textbox, selected_file)
                super().updateHeaderCheckbox(self.header_var, selected_file)
                super().updateSkipSpacesCheckbox(self.skip_spaces_var, selected_file)
                super().updateLineTerminatorTextbox(self.line_terminator_textbox, selected_file)
                super().updateQuotingRadioButtons(self.quoting_var, selected_file)
            
            #makes the xml configurator responsive and the csv configurator unresponsive, if a xml file is selected 
            if selected_file.endswith(".xml") or selected_file.endswith(".xml_", endswith_slice, -1):
                self.encoding_textbox.delete(0, tk.END)
                self.delimiter_textbox.delete(0, tk.END)
                self.quotechar_textbox.delete(0, tk.END)
                self.header_var.set(0)
                self.skip_spaces_var.set(0)
                self.line_terminator_textbox.delete(0, tk.END)
                self.quoting_var.set(None)
                
                for elem in self.csv_parameters_labels:
                    elem.config(fg="gray")
                for elem in self.csv_parameters_list:
                    elem.config(state="disabled")
                self.xml_parameters_textbox.config(state="normal")  
                self.xml_parameters_textbox.delete(0, tk.END)
                self.xml_parameters_textbox.config(state="readonly")
                self.xml_parameter_listbox.delete(0, tk.END)
                    
                self.xml_konfigurator_frame.config(fg="black")
                self.xsl_stylesheet_textbox_label.config(fg="black")
                self.xsl_stylesheet_textbox.config(state="readonly")
                self.button_add_xsl_File.config(state="normal")

                #only updates the boxes for the parameters of the xml file if a valid xsl Stylesheet is selected
                if self.valid_xsl_file:
                    super().updateXSLFileTextbox(self.xsl_stylesheet_textbox, selected_file)
                    self.xml_parameters_listbox_label.config(fg="black")
                    self.xml_parameter_listbox.config(state="normal")
                    self.xml_reset_button.config(state="normal")
                    super().showXMLParameterFunctionality(self.listbox, self.xml_parameter_listbox, self.filename)
                    super().updateXMLUserHeader(self.xml_header_var, self.listbox)
                    
    def ImportAs(self):
        """This function will be called if the "Import As..." Button is clicked.
        if defines a toplevel window to let the user decide into what data type the dataframe should be converted to.
        The available data types are: dictionary, list of lists, numpy array and dataframe
        
        Returns:
            nothing or void"""
        #checks if the listbox is empty
        end_index = self.listbox.index("end")
        if end_index == 0:
            showinfo("Information", "No Files to import are available")
        else:
            import_as_window = tk.Toplevel()
            import_as_window.geometry('300x300')
            import_as_window.title("Import as...")
            self.import_var = tk.IntVar()
            self.import_var.set(1)
            dictionary_import_button = tk.Radiobutton(import_as_window, text="Dictionary", variable=self.import_var, value=1)
            dictionary_import_button.grid(row=1, column=1, padx=10, pady=10)
            list_of_lists_import_button = tk.Radiobutton(import_as_window, text="List of Lists", variable=self.import_var, value=2)
            list_of_lists_import_button.grid(row=2, column=1, padx=10, pady=10)
            numpy_array_import_button = tk.Radiobutton(import_as_window, text="Numpy Array", variable=self.import_var, value=3)
            numpy_array_import_button.grid(row=3, column=1, padx=10, pady=10)
            pandas_dataframe_import_button = tk.Radiobutton(import_as_window, text="Pandas Dataframe", variable=self.import_var, value=4)
            pandas_dataframe_import_button.grid(row=4, column=1, padx=10, pady=10)
            
            import_button = tk.Button(import_as_window, text="Import", command=self.finalImporter)
            import_button.grid(row=5, column=3, padx=10, pady=10)
            
            cancel_button = tk.Button(import_as_window, text="Cancel", command=import_as_window.destroy)
            cancel_button.grid(row=5, column=4, padx=10, pady=10)
    
    def finalImporter(self):
        """gets the radiobutton value of the "Import As..." Toplevel window and converts the dataframe to the selected data type
        
        Returns:
            nothing or void"""
        try:
            super().finalImporterFunctionality(self.import_var.get())
        except ValueError as value_error:
            showerror("Error!", value_error)
            return
        #shows information into which data type the dataframe has been converted to
        if self.import_var.get() == 1:
            showinfo("Information", "The selected Files were imported as a Dictionary")
        elif self.import_var.get() == 2:
            showinfo("Information", "The selected Files were imported as a List of Lists")
        elif self.import_var.get() == 3:
            showinfo("Information", "The selected Files were imported as a Numpy Array")
        elif self.import_var.get() == 4:
            showinfo("Information", "The selected Files were imported as a Pandas Dataframe")
    
    def ExportAs(self):
        """This method is called, if the "Export As..." button is clicked and defines a toplevel window, to let
        the user decide if he wants to export the dataframe as a csv or xml file and with what parameters
        
        Returns:
            nothing or void"""
        end_index = self.listbox.index("end")
        if end_index == 0:
            showinfo("Information", "No Files to import are available")
        else:
            export_as_window = tk.Toplevel()
            export_as_window.geometry('500x300')
            export_as_window.title("Export as...")
            tab_parent = ttk.Notebook(export_as_window)
            
            #parts the toplevel into tabs to let the user switch between csv or xml file
            csv_tab = tk.Frame(tab_parent)
            xml_tab = tk.Frame(tab_parent)
            
            tab_parent.add(csv_tab, text="CSV Export")
            tab_parent.add(xml_tab, text="XML Export")
            
            tab_parent.pack(expand=1, fill="both")
            
            #lets the user decide the encoding of the csv file, default is UTF-8
            csv_export_encoding_label = tk.Label(csv_tab, text="Encoding:")
            csv_export_encoding_label.grid(row=1, column=1, padx=10, pady=10)
            self.csv_export_encoding = tk.Entry(csv_tab)
            self.csv_export_encoding.insert(0, "UTF-8")
            self.csv_export_encoding.grid(row=1, column=2, padx=10, pady=10)
            
            #lets the user decide the delimiter of the csv file, default is ","
            csv_export_delimiter_label = tk.Label(csv_tab, text="Delimiter:")
            csv_export_delimiter_label.grid(row=2, column=1, padx=10, pady=10)
            self.csv_export_delimiter = tk.Entry(csv_tab, width=2)
            self.csv_export_delimiter.insert(0, ",")
            self.csv_export_delimiter.grid(row=2, column=2, padx=10, pady=10)
            
            #lets the user decide the character, which will be used for quoting of the csv file, default is "
            csv_export_quotechar_label = tk.Label(csv_tab, text="Quotechar:")
            csv_export_quotechar_label.grid(row=3, column=1, padx=10, pady=10)
            self.csv_export_quotechar = tk.Entry(csv_tab, width=2)
            self.csv_export_quotechar.insert(0, "\"")
            self.csv_export_quotechar.grid(row=3, column=2, padx=10, pady=10)
            
            #lets the user decide the character, which will be used for line termination of the csv file, default is "\r\n"
            csv_export_line_terminator_label = tk.Label(csv_tab, text="Line Terminator:")
            csv_export_line_terminator_label.grid(row=4, column=1, padx=10, pady=10)
            self.csv_export_line_terminator = tk.Entry(csv_tab, width=2)
            self.csv_export_line_terminator.insert(0, "")
            self.csv_export_line_terminator.grid(row=4, column=2, padx=10, pady=10)
            
            #lets the user decide the encoding of the xml file, default is UTF-8
            xml_export_encoding_label = tk.Label(xml_tab, text="Encoding:")
            xml_export_encoding_label.grid(row=1, column=1, padx=10, pady=10)
            self.xml_export_encoding = tk.Entry(xml_tab)
            self.xml_export_encoding.insert(0, "UTF-8")
            self.xml_export_encoding.grid(row=1, column=2, padx=10, pady=10)
            
            #calls finalCSVExport
            csv_export_button = tk.Button(csv_tab, text="Export", command=self.finalCSVExport)
            csv_export_button.grid(row=5, column=1, padx=10, pady=10)
            
            #calls finalXMLExport
            xml_export_button = tk.Button(xml_tab, text="Export", command=self.finalXMLExport)
            xml_export_button.grid(row=5, column=1, padx=10, pady=10)
            
            cancel_button = tk.Button(export_as_window, text="Cancel", command=export_as_window.destroy)
            cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def finalCSVExport(self):
        """exports the selected files as a csv file to the filepath the user gives, with the given parameters of the toplevel window
        
        Returns:
            nothing or void"""
        try:
            super().finalCSVExportFunctionality(self.csv_export_encoding.get(), 
                                                self.csv_export_delimiter.get(),
                                                self.csv_export_quotechar.get(),
                                                self.csv_export_line_terminator.get())
        except LookupError as look_up_error:
            showerror("Error!", look_up_error)
            return
        except ValueError:
            showerror("Error!", "Delimiter, Quotechar and Line Terminator can only have 1-length chars each")
            return
        showinfo("Information", "The selected Files were exported as a CSV File")
    
    def finalXMLExport(self):
        """exports the selected files as a xml file to the filepath the user gives, with the given parameters of the toplevel window
        
        Returns:
            nothing or void"""
        try:
            super().finalXMLExportFunctionality(self.xml_export_encoding.get())
        except LookupError as look_up_error:
            showerror("Error!", look_up_error)
            return
        except ValueError as value_error:
            showerror("Error!", value_error)
            return
        showinfo("Information", "The selected Files were exported as a XML File")


#executes the program, if it is not imported as a module, and shows the gui window
if __name__ == "__main__":
    GUI = gui()
