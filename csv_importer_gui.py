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
#TODO: Kommentare und Dokumentation schreiben

class model_interface():
    """This class provides the functionality of the project according to the 
    model-view-separation principle"""

    def __init__(self):
        self.reader = reader.reader()
        self.__index:int = 0
        self.main_dataframe = pd.DataFrame()
        self.selected_listbox_elem:int = -1
        self.wanted_delimiter_all_files:str = None
        
    
    def getDataframe(self):
        self.main_dataframe = self.reader.giveDataframe()

    def ShowFilesInterface(self, listbox:tk.Listbox):
        try:
           
            self.__names = askopenfilenames()
            for filename in self.__names:
                try:
                    if filename.endswith(".csv") or filename.endswith(".xml"):
                        self.reader.read_with_init_settings(filename)
                    else:
                        showwarning("Warning!", "Only CSV or XML Files are allowed!")
                        continue
                except ValueError as value_error:
                    if filename in self.reader.opened_files_dict.keys():
                        self.reader.opened_files_dict.pop(filename)
                    showerror("Error!", value_error)
                    return
            
            listbox.delete(0, tk.END)
            self.__index = 0
            for name in self.reader.opened_files_dict.keys():        
                listbox.insert(self.__index, name)
                self.__index += 1 
            listbox.select_set(self.__index-1)
            self.selected_listbox_elem = self.__index - 1
            listbox.event_generate("<<ListboxSelect>>")  
        except OSError:
            showerror("Error!", "File could not be opened!")


        return self
                       
            

    def RemoveFilesInterface(self, listbox:tk.Listbox):
        selected_elem = listbox.curselection()
        if selected_elem == ():
            return
        elem_name = listbox.get(selected_elem)
        if elem_name in self.reader.opened_files_dict:           
            self.reader.RemoveFilesFunctionality(elem_name)
            listbox.delete(selected_elem)
        else:
            showerror("Error!", "Selected File is not in the List")

        if len(self.reader.opened_files_dict) == 0:
            self.__index = 0
        return self

    def ClearAllFilesInterface(self, listbox:tk.Listbox):
        listbox.delete(0, self.__index)
        self.reader.ClearAllFilesFunctionality()
        self.__index = 0
        return self

    def setUserEncoding(self, listbox:tk.Listbox, encoding_textbox:tk.Entry, wanted_encoding:str):        
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        
        try:
            self.reader.update_csv_with_personal_settings(filename,
                                            None,
                                            wanted_encoding)
            self.updateEncodingTextbox(encoding_textbox, filename) 
            return filename
        except LookupError:
            self.updateEncodingTextbox(encoding_textbox, filename)
            showerror("Error!", "Cannot encode "+filename+" with encoding: "+wanted_encoding)
        except ValueError as value_error:
            showerror("Error!", "For "+filename+" the following encoding error occured: "+value_error)
    
    def updateEncodingTextbox(self, encodings_textbox:tk.Entry, selected_file:str):
        encodings_textbox.delete(0, tk.END)
        if selected_file is not None:
            encodings_textbox.insert(0, self.reader.opened_files_dict[selected_file]["Encoding"])
    
    def setUserDelimiter(self, listbox:tk.Listbox, delimiter_textbox:tk.Entry, wanted_delimiter:str):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        if len(str(wanted_delimiter)) > 1:
            showerror("Error!", "Delimiter has to have a length of 1")
            self.updateDelimiterTextbox(delimiter_textbox, filename)
            return
        try:
            self.reader.update_csv_with_personal_settings(filename,
                                            None,
                                            None,
                                            wanted_delimiter)
            self.updateDelimiterTextbox(delimiter_textbox, filename) 
            return filename
        
        except ValueError:
            if self.wanted_delimiter_all_files == None:
                _,origin_dialect = self.reader.csvSniffer(filename)
                origin_delimiter = origin_dialect.delimiter
            else:
                origin_delimiter = self.wanted_delimiter_all_files
            self.reader.opened_files_dict[filename]["Delimiter"] = origin_delimiter
            self.updateDelimiterTextbox(delimiter_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", "Cannot set Delimiter "+ wanted_delimiter+" for "+filename+", because the number of columns would be different")
            return
            
    def setDelimiterForAllFunctionality(self, listbox:tk.Listbox, delimiter_textbox:tk.Entry, wanted_delimiter:str):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        if len(str(wanted_delimiter)) > 1:
            showerror("Error!", "Delimiter has to have a length of 1")
            self.updateDelimiterTextbox(delimiter_textbox, filename)
            return
        self.wanted_delimiter_all_files = wanted_delimiter
        for filename in self.reader.opened_files_dict:
            self.reader.opened_files_dict[filename]["Delimiter"] = wanted_delimiter
        self.reader.update_dataframe()
        
        
    
    def updateDelimiterTextbox(self, delimiter_textbox:tk.Entry, selected_file:str):
        delimiter_textbox.delete(0, tk.END)
        if selected_file is not None:
            delimiter_textbox.insert(0, self.reader.opened_files_dict[selected_file]["Delimiter"])
    
    
    def setUserQuotechar(self, listbox:tk.Listbox, quotechar_textbox:tk.Entry, wanted_quotechar:str):
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
        
        except ValueError:
            _,origin_dialect = self.reader.csvSniffer(filename)
            self.reader.opened_files_dict[filename]["QuoteChar"] = origin_dialect.quotechar
            self.updateQuotecharTextbox(quotechar_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", wanted_quotechar+" is not a valid Quotechar for"+filename)
            return
        except TypeError as type_error:
            _,origin_dialect = self.reader.csvSniffer(filename)
            self.reader.opened_files_dict[filename]["QuoteChar"] = origin_dialect.quotechar
            self.updateQuotecharTextbox(quotechar_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", type_error)
            return
        
    def updateQuotecharTextbox(self, quotechar_textbox:tk.Entry, selected_file:str):
        quotechar_textbox.delete(0, tk.END)
        if selected_file is not None:
            quotechar_textbox.insert(0, self.reader.opened_files_dict[selected_file]["QuoteChar"])
        
    def setUserHeader(self, listbox:tk.Listbox, header_checkbox_value):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        want_header = bool(header_checkbox_value.get())
        try:
            self.reader.update_csv_with_personal_settings(filename,
                                            want_header,
                                            )
        except ValueError as value_error:
            showerror("Error!", value_error)
            return
        self.updateHeaderCheckbox(header_checkbox_value, filename) 
        return filename
    
        
            
    def updateHeaderCheckbox(self, header_checkbox_value:tk.IntVar, selected_file:str):
        header_checkbox_value.set(0)
        if selected_file is not None:
            selected_file_header = int(self.reader.opened_files_dict[selected_file]["hasHeader"])
            header_checkbox_value.set(selected_file_header)
    
            
    def setUserSkipSpaces(self, listbox:tk.Listbox, skip_spaces_checkbox_value:tk.IntVar):
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
        skip_spaces_checkbox_value.set(0)
        if selected_file is not None:
            selected_file_skip_spaces = int(self.reader.opened_files_dict[selected_file]["skipInitSpace"])
            skip_spaces_checkbox_value.set(selected_file_skip_spaces)
            
    def setUserLineTerminator(self, listbox:tk.Listbox, line_terminator_textbox:tk.Entry, wanted_line_terminator:str):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        if len(str(wanted_line_terminator)) > 1:
            showerror("Error!", "Only length-1 line Terminators are supported")
            self.updateLineTerminatorTextbox(line_terminator_textbox, filename)
            return
        try:
            self.reader.update_csv_with_personal_settings(filename,
                                            None,
                                            None,
                                            None,
                                            None,
                                            None,
                                            wanted_line_terminator)
            self.updateLineTerminatorTextbox(line_terminator_textbox, filename) 
            return filename
        except pd.errors.ParserError as parser_error:
            showerror("Error!", parser_error)
        except ValueError:
            _,origin_dialect = self.reader.csvSniffer(filename)
            self.reader.opened_files_dict[filename]["lineTerminator"] = origin_dialect.lineterminator
            self.updateLineTerminatorTextbox(line_terminator_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", wanted_line_terminator+" is not a valid Line Terminator for"+filename)
            return
        except TypeError as type_error:
            _,origin_dialect = self.reader.csvSniffer(filename)
            self.reader.opened_files_dict[filename]["lineTerminator"] = origin_dialect.lineterminator
            self.updateLineTerminatorTextbox(line_terminator_textbox, filename)
            self.reader.update_dataframe()
            showerror("Error!", type_error)
            return 
        
        

        
    def updateLineTerminatorTextbox(self, line_terminator_textbox:tk.Entry, selected_file:str):
        line_terminator_textbox.delete(0, tk.END)
        if selected_file is not None:
            if self.reader.opened_files_dict[selected_file]["lineTerminator"] == None:
                return
            else:
                line_terminator_textbox.insert(0, ""+self.reader.opened_files_dict[selected_file]["lineTerminator"])
                
    def setUserQuoting(self, listbox:tk.Listbox, quoting_var:tk.IntVar):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
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
        quoting_var.set(0)
        if selected_file is not None:
            selected_file_quoting = self.reader.opened_files_dict[selected_file]["Quoting"]
            quoting_var.set(selected_file_quoting)
            
    def csvReset(self, listbox:tk.Listbox):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        if filename in self.reader.opened_files_dict.keys():
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
            enc = detect(Path(tmp_filename).read_bytes())
            self.reader.opened_files_dict[filename]["lineTerminator"] = None
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
            
        
    def getXSLFile(self, listbox:tk.Listbox, xsl_textbox:tk.Entry, parameter_listbox:tk.Listbox):
        if len(listbox.curselection()) == 0:
            showerror("Error!", "No XML-File selected to set Stylesheet for. Please select XML-File in Listbox")
            return False
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        xsl_file = askopenfile()
        if xsl_file is None:
            return
        if xsl_file.name.endswith(".xsl"):
            try:
                self.reader.getXMLParameters(filename, xsl_file.name)  
            except ValueError as value_error:
                showerror("Error!", value_error)
                return False
            self.reader.opened_files_dict[filename]["xsl_file"] = xsl_file.name
            self.updateXSLFileTextbox(xsl_textbox, filename)
            
            return True

        else:
            showwarning("Warning!", "Only XSL-Files are allowed") 
            return False
    
    def updateXSLFileTextbox(self, xsl_textbox:tk.Entry, selected_file:str):
        xsl_textbox.config(state="normal")
        xsl_textbox.delete(0, tk.END)
        try:
            if self.reader.opened_files_dict[selected_file]["xsl_file"] is not None:
                xsl_textbox.insert(0, self.reader.opened_files_dict[selected_file]["xsl_file"])
                
        except KeyError:
            return
        xsl_textbox.config(state="readonly") 
        
    def showXMLParameterFunctionality(self, listbox:tk.Listbox, parameter_listbox:tk.Listbox, filename:str):      
        index = 0
        tmp_parameters_list = list(self.reader.opened_files_dict[filename])
        try:
            for i in range(self.reader.opened_files_dict[filename]["parameters_len"]):
                parameter_listbox.insert(index, tmp_parameters_list[i])
                index += 1
        except KeyError:
            return
        
    def chooseXMLParameter(self, listbox:tk.Listbox, parameter_listbox:tk.Listbox, xml_parameters_textbox:tk.Entry, filename:str):      
        try:
            selected_elem = parameter_listbox.curselection()
        
            parameter = parameter_listbox.get(selected_elem)
        except tk.TclError:
            return
        
        xml_parameters_textbox.config(state="normal")
        xml_parameters_textbox.delete(0, tk.END)   
        xml_parameters_textbox.insert(0, self.reader.opened_files_dict[filename][parameter][1:-1])
    
    def changeXMLParameter(self, listbox:tk.Listbox, parameter_listbox:tk.Listbox, parameters_textbox:tk.Entry, filename:str):
        try:
            selected_elem = parameter_listbox.curselection()
        
            parameter = parameter_listbox.get(selected_elem)
        except tk.TclError:
            return
        value = parameters_textbox.get()
        if value is not None:
            try:
                self.reader.addXMLParameter(filename, parameter, value)
            except ValueError as value_error:
                self.reader.getXMLParameters(filename, self.reader.opened_files_dict[filename]["xsl_file"]) 
                showerror("Error!", value_error)
    
    def setXMLUserHeader(self, listbox:tk.Listbox, xml_header_var:tk.IntVar):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        want_header = bool(xml_header_var.get())

        self.reader.addXMLParameter(filename, None, None, want_header)
        self.updateXMLUserHeader(xml_header_var, listbox) 
        return filename
    
    def updateXMLUserHeader(self, xml_header_var:tk.IntVar, listbox:tk.Listbox):
        selected_elem = listbox.curselection()
        selected_file = listbox.get(selected_elem)
        xml_header_var.set(0)
        if selected_file is not None:
            selected_file_header = int(self.reader.opened_files_dict[selected_file]["hasHeader"])
            xml_header_var.set(selected_file_header)
    
    def xmlResetFunctionality(self, listbox:tk.Listbox):
        selected_elem = listbox.curselection()
        selected_file = listbox.get(selected_elem)
        self.reader.getXMLParameters(selected_file, self.reader.opened_files_dict[selected_file]["xsl_file"])
        return selected_file
    
    def finalImporterFunctionality(self, import_var_value:tk.IntVar):
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
        if len(str(delimiter)) <= 1 and len(str(quotechar)) <= 1 and len(str(line_terminator)) <= 1:
            if len(str(delimiter)) == 0:
                delimiter = ","
            if len(str(quotechar)) == 0:
                quotechar = "\""
            if len(str(line_terminator)) == 0:
                line_terminator = "\r\n"
            dest_filepath = asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile="export.csv")
            try:
                self.reader.exportAsCSVFile(dest_filepath, encoding, delimiter, quotechar, line_terminator)
            except LookupError as look_up_error:
                raise LookupError(look_up_error)
        else:
            raise ValueError
            
    def finalXMLExportFunctionality(self, encoding:str):
        dest_filepath = asksaveasfilename(defaultextension=".xml",
            filetypes=[("XML file", "*.xml")],
            initialfile="export.xml")
        try:
            self.reader.exportAsXMLFile(dest_filepath, encoding)
        except LookupError as look_up_error:
            raise LookupError(look_up_error)
        except ValueError as value_error:
            raise ValueError(value_error)
    


class view(model_interface):
    """This class is responsible for the GUI"""

    def __init__(self):

        self.root = tk.Tk()
        self.root.minsize(1000, 300)
        super().__init__()
        
        self.Importer_Labelframe = tk.LabelFrame(self.root, text="Importer")
        self.Importer_Labelframe.grid(row=1, column=1, padx=10, pady=10)
        
        self.Konfigurator_Labelframe = tk.LabelFrame(self.root, text="File-Configurator")
        self.Konfigurator_Labelframe.grid(row=3, column=1, padx=10, pady=10)
        
        self.preview_table_Labelframe = tk.LabelFrame(self.root, text="Preview")
        self.preview_table_Labelframe.grid(row=3, column=2, padx=10, pady=10)
       
        self.csv_parameters_list:list = []
        self.csv_parameters_labels:list = []
        self.xml_parameters_list:list = []
        self.xml_parameters_labels:list = []
        self.filename:str = ""
        
        file_buttons_frame = tk.Frame(self.Importer_Labelframe)
        file_buttons_frame.pack(side=tk.LEFT)
        listbox_frame = tk.Frame(self.Importer_Labelframe)
        listbox_frame.pack(side=tk.TOP)
        self.grid_frame = tk.Frame(self.Konfigurator_Labelframe)
        self.grid_frame.pack(side=tk.BOTTOM)
        self.csv_konfigurator_frame = tk.LabelFrame(self.grid_frame, text="CSV-Configurator", fg="gray")
        self.csv_konfigurator_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.csv_parameters_labels.append(self.csv_konfigurator_frame)
        
        self.listbox = tk.Listbox(
            listbox_frame, width=50, selectmode=tk.SINGLE)
        scrollbar_x = tk.Scrollbar(listbox_frame, orient="horizontal")
        scrollbar_y = tk.Scrollbar(listbox_frame)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.BOTH)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.listbox.config(xscrollcommand=scrollbar_x.set)
        self.listbox.config(yscrollcommand=scrollbar_y.set)
        scrollbar_x.config(command=self.listbox.xview)
        scrollbar_y.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.listboxSelectionChanged)  
        
        self.encodings_textbox_label = tk.Label(self.csv_konfigurator_frame, text="Encoding: ", fg="gray")
        self.encodings_textbox_label.grid(row=1, column=1, pady=10)
        self.encoding_textbox = tk.Entry(self.csv_konfigurator_frame, exportselection=0, state="disabled")     
        self.encoding_textbox.grid(row=1,column=2, padx=10, pady=10)
        self.encoding_textbox.bind("<Return>", self.setFileEncoding)
        self.csv_parameters_labels.append(self.encodings_textbox_label)
        self.csv_parameters_list.append(self.encoding_textbox)
        
        self.delimiter_textbox_label = tk.Label(self.csv_konfigurator_frame, text="Delimiter: ", fg="gray")
        self.delimiter_textbox_label.grid(row=3, column=1, pady=10)
        self.delimiter_textbox = tk.Entry(self.csv_konfigurator_frame, exportselection=0, state="disabled", width=2)     
        self.delimiter_textbox.grid(row=3, column=2, padx=10, pady=10)
        self.delimiter_textbox.bind("<Return>", self.setFileDelimiter)   
        self.set_all_delimiter_button = tk.Button(self.csv_konfigurator_frame, text="Set for all Files", state="disabled", command=self.setDelimiterForAll)
        self.set_all_delimiter_button.grid(row=3, column=3, padx=10)
        self.csv_parameters_labels.append(self.delimiter_textbox_label)
        self.csv_parameters_list.append(self.delimiter_textbox) 
        self.csv_parameters_list.append(self.set_all_delimiter_button)   
        
        self.quotechar_textbox_label = tk.Label(self.csv_konfigurator_frame, text="Quotechar: ", fg="gray")
        self.quotechar_textbox_label.grid(row=4, column=1, pady=10)
        self.quotechar_textbox = tk.Entry(self.csv_konfigurator_frame, exportselection=0, state="disabled", width=2)     
        self.quotechar_textbox.grid(row=4, column=2, padx=10, pady=10)
        self.quotechar_textbox.bind("<Return>", self.setFileQuotechar) 
        self.csv_parameters_labels.append(self.quotechar_textbox_label)
        self.csv_parameters_list.append(self.quotechar_textbox) 
        
        self.header_var = tk.IntVar()
        self.header_checkbox_label = tk.Label(self.csv_konfigurator_frame, text="Header: ", fg="gray")
        self.header_checkbox_label.grid(row=5, column=1, pady=10)
        self.header_checkbox = tk.Checkbutton(self.csv_konfigurator_frame, state="disabled", command=self.setFileHeader, variable=self.header_var)
        self.header_checkbox.grid(row=5, column=2, padx=10, pady=10)
        self.csv_parameters_labels.append(self.header_checkbox_label)
        self.csv_parameters_list.append(self.header_checkbox)
        
        self.skip_spaces_var = tk.IntVar()
        self.skip_spaces_checkbox_label = tk.Label(self.csv_konfigurator_frame, text="Skip Initial Spaces: ", fg="gray")
        self.skip_spaces_checkbox_label.grid(row=6, column=1, pady=10)
        self.skip_spaces_checkbox = tk.Checkbutton(self.csv_konfigurator_frame, state="disabled", command=self.setFileSkipSpaces, variable=self.skip_spaces_var)
        self.skip_spaces_checkbox.grid(row=6, column=2, padx=10, pady=10)
        self.csv_parameters_labels.append(self.skip_spaces_checkbox_label)
        self.csv_parameters_list.append(self.skip_spaces_checkbox)
        
        self.line_terminator_textbox_label = tk.Label(self.csv_konfigurator_frame, text="Line Terminator: ", fg="gray")
        self.line_terminator_textbox_label.grid(row=7, column=1, pady=10)
        self.line_terminator_textbox = tk.Entry(self.csv_konfigurator_frame, exportselection=0, state="disabled", width=2)     
        self.line_terminator_textbox.grid(row=7, column=2, padx=10, pady=10)
        self.line_terminator_textbox.bind("<Return>", self.setFileLineTerminator) 
        self.csv_parameters_labels.append(self.line_terminator_textbox_label)
        self.csv_parameters_list.append(self.line_terminator_textbox)
        
        self.quoting_var = tk.IntVar()
        self.quoting_var.set(None)
        self.quoting_radiobuttons_label = tk.Label(self.csv_konfigurator_frame, text="Quoting: ", fg="gray")
        self.quoting_radiobuttons_label.grid(row=8, column=1, pady=10)
        self.quote_minimal_button = tk.Radiobutton(self.csv_konfigurator_frame, text="Minimal", variable=self.quoting_var, value=0, state="disabled", command=self.setFileQuoting)
        self.quote_minimal_button.grid(row=8, column=2, padx=10, pady=10)
        self.quote_all_button = tk.Radiobutton(self.csv_konfigurator_frame, text="All", variable=self.quoting_var, value=1, state="disabled", command=self.setFileQuoting)
        self.quote_all_button.grid(row=8, column=3, padx=10, pady=10)
        self.quote_non_numeric_button = tk.Radiobutton(self.csv_konfigurator_frame, text="Non Numeric", variable=self.quoting_var, value=2, state="disabled", command=self.setFileQuoting)
        self.quote_non_numeric_button.grid(row=9, column=2, padx=10, pady=10)
        self.quote_none_button = tk.Radiobutton(self.csv_konfigurator_frame, text="None", variable=self.quoting_var, value=3, state="disabled", command=self.setFileQuoting)
        self.quote_none_button.grid(row=9, column=3, padx=10, pady=10)
        self.csv_parameters_labels.append(self.quoting_radiobuttons_label)
        self.csv_parameters_list.append(self.quote_minimal_button)
        self.csv_parameters_list.append(self.quote_all_button)
        self.csv_parameters_list.append(self.quote_non_numeric_button)
        self.csv_parameters_list.append(self.quote_none_button)
        
        self.csv_reset_button = tk.Button(self.csv_konfigurator_frame, text="Reset", state="disabled", command=self.csvReset)
        self.csv_reset_button.grid(row=12,column=2, padx=10, pady=10)
        self.csv_parameters_list.append(self.csv_reset_button)
        
        
        
        self.xml_konfigurator_frame = tk.LabelFrame(self.grid_frame, text="XML-Configurator", fg="gray")
        self.xml_konfigurator_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        self.xml_parameters_labels.append(self.xml_konfigurator_frame)
        
        self.xsl_stylesheet_textbox_label = tk.Label(self.xml_konfigurator_frame, text="XSL-Stylesheet:", fg="gray")
        self.xsl_stylesheet_textbox_label.grid(row=1, column=1, padx=10, pady=10)
        xsl_stylesheet_scrollbar_frame = tk.Frame(self.xml_konfigurator_frame)
        xsl_stylesheet_scrollbar_frame.grid(row=1, column=2, padx=10)
        scrollbar_x_stylesheet = tk.Scrollbar(xsl_stylesheet_scrollbar_frame, orient="horizontal")
        self.xsl_stylesheet_textbox = tk.Entry(xsl_stylesheet_scrollbar_frame, state="disabled", width=40, xscrollcommand=scrollbar_x_stylesheet.set)
        scrollbar_x_stylesheet.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.xsl_stylesheet_textbox.pack(side=tk.BOTTOM)
        scrollbar_x_stylesheet.config(command=self.xsl_stylesheet_textbox.xview)
        self.button_add_xsl_File = tk.Button(self.xml_konfigurator_frame, text="Choose XSL File", command=self.OpenXSLFile, state="disabled")
        self.button_add_xsl_File.grid(row=2, column=2)
        self.xml_parameters_labels.append(self.xsl_stylesheet_textbox_label)
        self.xml_parameters_list.append(self.xsl_stylesheet_textbox)
        self.xml_parameters_list.append(self.button_add_xsl_File)
        
        
        self.valid_xsl_file = False
        self.xml_parameters_listbox_label = tk.Label(self.xml_konfigurator_frame, text="XML-Parameters:", fg="gray")
        self.xml_parameters_listbox_label.grid(row=3, column=1, pady=10, padx=10)
        xml_parameter_scrollbar_frame = tk.Frame(self.xml_konfigurator_frame)
        xml_parameter_scrollbar_frame.grid(row=3, column=2, padx=10, pady=10)
        scrollbar_x_parameters = tk.Scrollbar(xml_parameter_scrollbar_frame, orient="horizontal")
        scrollbar_y_parameters = tk.Scrollbar(xml_parameter_scrollbar_frame)
        self.xml_parameter_listbox = tk.Listbox(xml_parameter_scrollbar_frame,
                                                width=20,
                                                height=8,
                                                selectmode=tk.SINGLE,
                                                state="disabled",
                                                xscrollcommand=scrollbar_x_parameters.set,
                                                yscrollcommand=scrollbar_y_parameters.set)
        self.xml_parameter_listbox.bind("<<ListboxSelect>>", self.showXMLParameter) 
        scrollbar_x_parameters.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.xml_parameter_listbox.pack(side=tk.LEFT)
        scrollbar_y_parameters.pack(side=tk.RIGHT, fill=tk.BOTH)
        scrollbar_x_parameters.config(command=self.xml_parameter_listbox.xview)
        scrollbar_y_parameters.config(command=self.xml_parameter_listbox.yview)
        self.xml_parameters_textbox = tk.Entry(self.xml_konfigurator_frame, state="disabled", width=2)
        self.xml_parameters_textbox.bind("<Return>", self.setXMLParameter)
        self.xml_parameters_textbox.grid(row=4, column=2)
        self.xml_parameters_labels.append(self.xml_parameters_listbox_label)
        self.xml_parameters_list.append(self.xml_parameter_listbox)
        self.xml_parameters_list.append(self.xml_parameters_textbox)
        
        self.xml_header_var = tk.IntVar()
        self.xml_header_checkbox_label = tk.Label(self.xml_konfigurator_frame, text="Header: ", fg="gray")
        self.xml_header_checkbox_label.grid(row=5, column=1, pady=10)
        self.xml_header_checkbox = tk.Checkbutton(self.xml_konfigurator_frame, state="disabled", command=self.setXMLHeader, variable=self.xml_header_var)
        self.xml_header_checkbox.grid(row=5, column=2, padx=10, pady=10)
        self.xml_parameters_labels.append(self.xml_header_checkbox_label)
        self.xml_parameters_list.append(self.xml_header_checkbox)
        
        self.xml_reset_button = tk.Button(self.xml_konfigurator_frame, text="Reset", state="disabled", command=self.xmlReset)
        self.xml_reset_button.grid(row=6, column=2, padx=10, pady=10)
        self.xml_parameters_list.append(self.xml_reset_button)
        

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.button_addFile = tk.Button(
            file_buttons_frame, text="Add File/s", command=self.OpenFileGUI)
        self.button_addFile.pack(side=tk.TOP, padx=5, pady=5)
        self.button_removeFile = tk.Button(
            file_buttons_frame, text="Remove selected File", command=self.RemoveFileGUI)
        self.button_removeFile.pack(side=tk.TOP, padx=5, pady=5)
        self.button_removeAllFiles = tk.Button(
            file_buttons_frame, text="Remove all Files", command=self.ClearAllFilesGUI)
        self.button_removeAllFiles.pack(side=tk.TOP, padx=5, pady=5)
        
        self.preview_table = Table(self.preview_table_Labelframe, dataframe=self.main_dataframe)
        self.preview_table.show()

        self.import_export_buttons_frame = tk.Frame(self.root)
        self.import_export_buttons_frame.grid(row=4, column=2)
        
        self.button_importCSV = tk.Button(
            self.import_export_buttons_frame, text="Import as...", command=self.ImportAs)
        self.button_importCSV.pack(side=tk.LEFT, padx=5, pady=10)
        self.button_exportCSV = tk.Button(
            self.import_export_buttons_frame, text="Export as...", command=self.ExportAs)
        self.button_exportCSV.pack(side=tk.LEFT, padx=5, pady=10)
        self.button_exit = tk.Button(
            self.import_export_buttons_frame, text="Cancel", command=self.root.quit)
        self.button_exit.pack(side=tk.LEFT, padx=5, pady=10)

        self.root.mainloop()


    def updatePreview(self):
        self.getDataframe()
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        
        
    def OpenFileGUI(self):
        try:
            super().ShowFilesInterface(self.listbox)
            self.updatePreview()

        except OSError as e:
            showerror("Error!", e)
        

    def RemoveFileGUI(self):
        super().RemoveFilesInterface(self.listbox)
        self.updatePreview()
        
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
        super().ClearAllFilesInterface(self.listbox)
        self.updatePreview()
        
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
        super().setUserEncoding(self.listbox, self.encoding_textbox, self.encoding_textbox.get())  
        self.root.focus_set()    
        self.updatePreview()
        
    def setFileDelimiter(self, return_event):
        super().setUserDelimiter(self.listbox, self.delimiter_textbox, self.delimiter_textbox.get())  
        self.root.focus_set()    
        self.updatePreview()
    
    def setDelimiterForAll(self):
        wanted_delimiter = self.delimiter_textbox.get()
        super().setDelimiterForAllFunctionality(self.listbox, self.delimiter_textbox, wanted_delimiter)
        
        self.root.focus_set()    
        self.updatePreview()
        
    def setFileQuotechar(self, return_event):
        super().setUserQuotechar(self.listbox, self.quotechar_textbox, self.quotechar_textbox.get())  
        self.root.focus_set()    
        self.updatePreview()
        
    def setFileHeader(self):
        super().setUserHeader(self.listbox, self.header_var)  
        self.root.focus_set()    
        self.updatePreview()
    
    def setFileSkipSpaces(self):
        super().setUserSkipSpaces(self.listbox, self.skip_spaces_var)  
        self.root.focus_set()    
        self.updatePreview()
        
    def setFileLineTerminator(self, return_event):
        super().setUserLineTerminator(self.listbox, self.line_terminator_textbox, self.line_terminator_textbox.get()) 
        try: 
            self.root.focus_set()    
            self.updatePreview()
        except IndexError as index_error:
            showerror("Error!", index_error)
            return
        
    def setFileQuoting(self):
        super().setUserQuoting(self.listbox, self.quoting_var)  
        self.root.focus_set()    
        self.updatePreview()
    
    def csvReset(self):
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
        try:
            self.xml_parameter_listbox.config(state="normal")
            self.valid_xsl_file = super().getXSLFile(self.listbox, self.xsl_stylesheet_textbox, self.xml_parameter_listbox)
            if self.valid_xsl_file:
                self.xml_parameters_textbox.config(state="readonly")         
                self.xml_parameters_listbox_label.config(fg="black")
                self.xml_header_checkbox_label.config(fg="black")
                self.xml_header_checkbox.config(state="normal")
                super().showXMLParameterFunctionality(self.listbox, self.xml_parameter_listbox, self.filename)
                super().updateXMLUserHeader(self.xml_header_var, self.listbox)
            self.updatePreview()

        except OSError as e:
            showerror("Error!", e)
    
    def showXMLParameter(self, selection_event):
        super().chooseXMLParameter(self.listbox, self.xml_parameter_listbox, self.xml_parameters_textbox, self.filename)
        self.updatePreview()
    
    def setXMLParameter(self, return_event):
        super().changeXMLParameter(self.listbox, self.xml_parameter_listbox, self.xml_parameters_textbox, self.filename)
        super().chooseXMLParameter(self.listbox, self.xml_parameter_listbox, self.xml_parameters_textbox, self.filename)
        self.root.focus_set()   
        self.updatePreview()
    
    def setXMLHeader(self):
        try:
            super().setXMLUserHeader(self.listbox, self.xml_header_var) 
        except tk.TclError:
            showerror("Error!", "No File to set header for selected. Please select File from listbox")
            return 
        self.root.focus_set()    
        self.updatePreview()
    
    def xmlReset(self):
        try:
            selected_file = super().xmlResetFunctionality(self.listbox)
            if self.valid_xsl_file:
                super().updateXSLFileTextbox(self.xsl_stylesheet_textbox, selected_file)
                self.xml_parameters_listbox_label.config(fg="black")
                self.xml_parameter_listbox.config(state="normal")
                self.xml_parameter_listbox.delete(0, tk.END)
                super().showXMLParameterFunctionality(self.listbox, self.xml_parameter_listbox, self.filename)
                super().updateXMLUserHeader(self.xml_header_var, self.listbox)
        except tk.TclError:
            showerror("Error!", "No File to reset selected. Please select File from listbox")
            return
        self.root.focus_set()   
        self.updatePreview()
        
    
    def listboxSelectionChanged(self, select_event):
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
                
                super().updateEncodingTextbox(self.encoding_textbox, selected_file)
                super().updateDelimiterTextbox(self.delimiter_textbox, selected_file)
                super().updateQuotecharTextbox(self.quotechar_textbox, selected_file)
                super().updateHeaderCheckbox(self.header_var, selected_file)
                super().updateSkipSpacesCheckbox(self.skip_spaces_var, selected_file)
                super().updateLineTerminatorTextbox(self.line_terminator_textbox, selected_file)
                super().updateQuotingRadioButtons(self.quoting_var, selected_file)
                
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
                self.xml_header_checkbox.config(state="normal")
                self.xml_header_checkbox_label.config(fg="black")
                self.xml_reset_button.config(state="normal")
                if self.valid_xsl_file:
                    super().updateXSLFileTextbox(self.xsl_stylesheet_textbox, selected_file)
                    self.xml_parameters_listbox_label.config(fg="black")
                    self.xml_parameter_listbox.config(state="normal")
                    super().showXMLParameterFunctionality(self.listbox, self.xml_parameter_listbox, self.filename)
                    super().updateXMLUserHeader(self.xml_header_var, self.listbox)
                    
    def ImportAs(self):
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
        try:
            super().finalImporterFunctionality(self.import_var.get())
        except ValueError as value_error:
            showerror("Error!", value_error)
            return
        if self.import_var.get() == 1:
            showinfo("Information", "The selected Files were imported as a Dictionary")
        elif self.import_var.get() == 2:
            showinfo("Information", "The selected Files were imported as a List of Lists")
        elif self.import_var.get() == 3:
            showinfo("Information", "The selected Files were imported as a Numpy Array")
        elif self.import_var.get() == 4:
            showinfo("Information", "The selected Files were imported as a Pandas Dataframe")
    
    def ExportAs(self):
        end_index = self.listbox.index("end")
        if end_index == 0:
            showinfo("Information", "No Files to import are available")
        else:
            export_as_window = tk.Toplevel()
            export_as_window.geometry('500x300')
            export_as_window.title("Export as...")
            tab_parent = ttk.Notebook(export_as_window)
            
            csv_tab = tk.Frame(tab_parent)
            xml_tab = tk.Frame(tab_parent)
            
            tab_parent.add(csv_tab, text="CSV Export")
            tab_parent.add(xml_tab, text="XML Export")
            
            tab_parent.pack(expand=1, fill="both")
            
            csv_export_encoding_label = tk.Label(csv_tab, text="Encoding:")
            csv_export_encoding_label.grid(row=1, column=1, padx=10, pady=10)
            self.csv_export_encoding = tk.Entry(csv_tab)
            self.csv_export_encoding.insert(0, "UTF-8")
            self.csv_export_encoding.grid(row=1, column=2, padx=10, pady=10)
            
            csv_export_delimiter_label = tk.Label(csv_tab, text="Delimiter:")
            csv_export_delimiter_label.grid(row=2, column=1, padx=10, pady=10)
            self.csv_export_delimiter = tk.Entry(csv_tab, width=2)
            self.csv_export_delimiter.insert(0, ",")
            self.csv_export_delimiter.grid(row=2, column=2, padx=10, pady=10)
            
            csv_export_quotechar_label = tk.Label(csv_tab, text="Quotechar:")
            csv_export_quotechar_label.grid(row=3, column=1, padx=10, pady=10)
            self.csv_export_quotechar = tk.Entry(csv_tab, width=2)
            self.csv_export_quotechar.insert(0, "\"")
            self.csv_export_quotechar.grid(row=3, column=2, padx=10, pady=10)
            
            csv_export_line_terminator_label = tk.Label(csv_tab, text="Line Terminator:")
            csv_export_line_terminator_label.grid(row=4, column=1, padx=10, pady=10)
            self.csv_export_line_terminator = tk.Entry(csv_tab, width=2)
            self.csv_export_line_terminator.insert(0, "")
            self.csv_export_line_terminator.grid(row=4, column=2, padx=10, pady=10)
            

            xml_export_encoding_label = tk.Label(xml_tab, text="Encoding:")
            xml_export_encoding_label.grid(row=1, column=1, padx=10, pady=10)
            self.xml_export_encoding = tk.Entry(xml_tab)
            self.xml_export_encoding.insert(0, "UTF-8")
            self.xml_export_encoding.grid(row=1, column=2, padx=10, pady=10)
            
            csv_export_button = tk.Button(csv_tab, text="Export", command=self.finalCSVExport)
            csv_export_button.grid(row=5, column=1, padx=10, pady=10)
            
            xml_export_button = tk.Button(xml_tab, text="Export", command=self.finalXMLExport)
            xml_export_button.grid(row=5, column=1, padx=10, pady=10)
            
            cancel_button = tk.Button(export_as_window, text="Cancel", command=export_as_window.destroy)
            cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def finalCSVExport(self):
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
        try:
            super().finalXMLExportFunctionality(self.xml_export_encoding.get())
        except LookupError as look_up_error:
            showerror("Error!", look_up_error)
            return
        except ValueError as value_error:
            showerror("Error!", value_error)
            return
        showinfo("Information", "The selected Files were exported as a XML File")



if __name__ == "__main__":
    app = view()
