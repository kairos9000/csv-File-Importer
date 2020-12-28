# -*- coding: utf-8 -*-

import tkinter as tk
import pandas as pd
import io
from tkinter import ttk 
from pandastable import Table, TableModel
import reader
import csv_xml_importer as cxi
from tkinter.messagebox import showwarning, showinfo, showerror
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from PyPDF2 import PdfFileWriter, PdfFileReader
from pathlib import Path
from chardet import detect
from math import log, ceil, floor 
#TODO: restliche Parameter von CSV realisieren(lineTerminator und quoting(mit integers)) und XML parameter als Listbox mit Entry daneben

class model_interface():
    """This class provides the functionality of the project according to the 
    model-view-separation principle"""

    def __init__(self):
        self.reader = reader.reader()
        self.__index:int = 0
        self.main_dataframe = pd.DataFrame()
        self.selected_listbox_elem:int = -1
        self.wanted_delimiter_all_files:str = None
        
    
    def updateDataframe(self):
        self.main_dataframe = self.reader.giveDataframe()

    def ShowFilesInterface(self, listbox):
        try:
           
            self.__names = askopenfilenames()
            for filename in self.__names:
                try:
                    self.reader.read_with_init_settings(filename)
                except ValueError as value_error:
                    if filename in self.reader.opened_files_dict.keys():
                        self.reader.opened_files_dict.pop(filename)
                    showerror("Error!", value_error)
                    return
            
            listbox.delete(0, self.__index)
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
    
    # def OpenFilesInterface(self, encoding, table, listbox):
    #     try:
    #         self.__csv_file = self.reader.OpenCSVFile(encoding)
    #     #         table.redraw()
                
            
    #     except OSError as e:
    #         listbox.delete(self.__index-1)
    #         showerror("Error!", e)
                
            
            

    def RemoveFilesInterface(self, listbox):
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

    def ClearAllFilesInterface(self, listbox):
        listbox.delete(0, self.__index)
        self.reader.ClearAllFilesFunctionality()
        self.__index = 0
        return self

    def setUserEncoding(self, listbox, encoding_textbox, wanted_encoding):        
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
    
    def updateEncodingTextbox(self, encodings_textbox, selected_file):
        if selected_file is not None:
            encodings_textbox.delete(0, tk.END)
            encodings_textbox.insert(0, self.reader.opened_files_dict[selected_file]["Encoding"])
    
    def setUserDelimiter(self, listbox, delimiter_textbox, wanted_delimiter):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        
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
            
    def setDelimiterForAllFunctionality(self, wanted_delimiter):
        self.wanted_delimiter_all_files = wanted_delimiter
        for filename in self.reader.opened_files_dict:
            self.reader.opened_files_dict[filename]["Delimiter"] = wanted_delimiter
        self.reader.update_dataframe()
        
        
    
    def updateDelimiterTextbox(self, delimiter_textbox, selected_file):
        if selected_file is not None:
            delimiter_textbox.delete(0, tk.END)
            delimiter_textbox.insert(0, self.reader.opened_files_dict[selected_file]["Delimiter"])
    
    
    def setUserQuotechar(self, listbox, quotechar_textbox, wanted_quotechar):
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
        
    def updateQuotecharTextbox(self, quotechar_textbox, selected_file):
        if selected_file is not None:
            quotechar_textbox.delete(0, tk.END)
            quotechar_textbox.insert(0, self.reader.opened_files_dict[selected_file]["QuoteChar"])
        
    def setUserHeader(self, listbox, header_checkbox_value):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        want_header = bool(header_checkbox_value.get())

        self.reader.update_csv_with_personal_settings(filename,
                                        want_header,
                                        )
        self.updateHeaderCheckbox(header_checkbox_value, filename) 
        return filename
    
        
            
    def updateHeaderCheckbox(self, header_checkbox_value, selected_file):
        if selected_file is not None:
            selected_file_header = int(self.reader.opened_files_dict[selected_file]["hasHeader"])
            header_checkbox_value.set(selected_file_header)
    
            
    def setUserSkipSpaces(self, listbox, skip_spaces_checkbox_value):
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
    
        
            
    def updateSkipSpacesCheckbox(self, skip_spaces_checkbox_value, selected_file):
        if selected_file is not None:
            selected_file_skip_spaces = int(self.reader.opened_files_dict[selected_file]["skipInitSpace"])
            skip_spaces_checkbox_value.set(selected_file_skip_spaces)
            
    def setUserLineTerminator(self, listbox, line_terminator_textbox, wanted_line_terminator):
        selected_elem = listbox.curselection()
        filename = listbox.get(selected_elem)
        if len(wanted_line_terminator) > 1:
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
        
    def updateLineTerminatorTextbox(self, line_terminator_textbox, selected_file):
        if selected_file is not None:
            if self.reader.opened_files_dict[selected_file]["lineTerminator"] == None:
                line_terminator_textbox.delete(0, tk.END)
                line_terminator_textbox.insert(0, "")
            else:
                line_terminator_textbox.delete(0, tk.END)
                line_terminator_textbox.insert(0, ""+self.reader.opened_files_dict[selected_file]["lineTerminator"])
                
    def setUserQuoting(self, listbox, quoting_var):
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
    
    def updateQuotingRadioButtons(self, quoting_var, selected_file):
        if selected_file is not None:
            selected_file_quoting = self.reader.opened_files_dict[selected_file]["Quoting"]
            quoting_var.set(selected_file_quoting)
            
    def csvReset(self, listbox):
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
                                                          dialect.quoting
                                                          )
            return filename
        else:
            showerror("Error!", "File cannot be found in Listbox")
            return
            
        
            
        

    # def MergeFilesInterface(self):
    #     if len(self.reader.opened_csv_files_list) == 0:
    #         showwarning("Warning", "No CSV Files to import selected!")
    #         return
        # save_file = asksaveasfilename(defaultextension=".csv",
        #                               filetypes=[("CSV file", "*.csv")],
        #                               initialfile="import.csv")
        # pdfWriter = PdfFileWriter()

        # for filename in self.__opened_files_arr:
        #     if filename.endswith("_", -2, -1):
        #         filename = filename[:-2:]

        #     pdfFileObj = open(filename, 'rb')
        #     pdfReader = PdfFileReader(pdfFileObj)

        #     for pageNum in range(pdfReader.numPages):
        #         pageObj = pdfReader.getPage(pageNum)
        #         pdfWriter.addPage(pageObj)

        # if save_file == "":
        #     return
        # pdfOutput = open(save_file, 'wb')
        # pdfWriter.write(pdfOutput)
        # pdfOutput.close()
        #return self


class view(model_interface):
    """This class is responsible for the GUI"""

    def __init__(self):

        self.root = tk.Tk()
        self.root.minsize(1000, 300)
        super().__init__()
        
        self.CSV_Importer_Labelframe = tk.LabelFrame(self.root, text="Importer")
        self.CSV_Importer_Labelframe.grid(row=1, column=3, padx=10, pady=10)
        
        self.CSV_Konfigurator_Labelframe = tk.LabelFrame(self.root, text="File-Konfigurator")
        self.CSV_Konfigurator_Labelframe.grid(row=3, column=1, padx=10, pady=10)
        
        self.preview_table_Labelframe = tk.LabelFrame(self.root, text="Preview")
        self.preview_table_Labelframe.grid(row=3, column=3, padx=10, pady=10)
       
        
        file_buttons_frame = tk.Frame(self.CSV_Importer_Labelframe)
        file_buttons_frame.pack(side=tk.LEFT)
        listbox_frame = tk.Frame(self.CSV_Importer_Labelframe)
        listbox_frame.pack(side=tk.TOP)
        self.grid_frame = tk.Frame(self.CSV_Konfigurator_Labelframe)
        self.grid_frame.pack(side=tk.BOTTOM)
        self.csv_konfigurator_frame = tk.LabelFrame(self.grid_frame, text="CSV-Konfigurator", fg="gray")
        self.csv_konfigurator_frame.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        self.listbox = tk.Listbox(
            listbox_frame, width=100, selectmode=tk.SINGLE)
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
        
        self.delimiter_textbox_label = tk.Label(self.csv_konfigurator_frame, text="Delimiter: ", fg="gray")
        self.delimiter_textbox_label.grid(row=3, column=1, pady=10)
        self.delimiter_textbox = tk.Entry(self.csv_konfigurator_frame, exportselection=0, state="disabled")     
        self.delimiter_textbox.grid(row=3, column=2, padx=10, pady=10)
        self.delimiter_textbox.bind("<Return>", self.setFileDelimiter)   
        self.set_all_delimiter_button = tk.Button(self.csv_konfigurator_frame, text="Set for all Files", state="disabled", command=self.setDelimiterForAll)
        self.set_all_delimiter_button.grid(row=3, column=3, padx=10)    
        
        self.quotechar_textbox_label = tk.Label(self.csv_konfigurator_frame, text="Quotechar: ", fg="gray")
        self.quotechar_textbox_label.grid(row=4, column=1, pady=10)
        self.quotechar_textbox = tk.Entry(self.csv_konfigurator_frame, exportselection=0, state="disabled")     
        self.quotechar_textbox.grid(row=4, column=2, padx=10, pady=10)
        self.quotechar_textbox.bind("<Return>", self.setFileQuotechar) 
        
        self.header_var = tk.IntVar()
        self.header_checkbox_label = tk.Label(self.csv_konfigurator_frame, text="Header: ", fg="gray")
        self.header_checkbox_label.grid(row=5, column=1, pady=10)
        self.header_checkbox = tk.Checkbutton(self.csv_konfigurator_frame, state="disabled", command=self.setFileHeader, variable=self.header_var)
        self.header_checkbox.grid(row=5, column=2, padx=10, pady=10)
        
        self.skip_spaces_var = tk.IntVar()
        self.skip_spaces_checkbox_label = tk.Label(self.csv_konfigurator_frame, text="Skip Initial Spaces: ", fg="gray")
        self.skip_spaces_checkbox_label.grid(row=6, column=1, pady=10)
        self.skip_spaces_checkbox = tk.Checkbutton(self.csv_konfigurator_frame, state="disabled", command=self.setFileSkipSpaces, variable=self.skip_spaces_var)
        self.skip_spaces_checkbox.grid(row=6, column=2, padx=10, pady=10)
        
        self.line_terminator_textbox_label = tk.Label(self.csv_konfigurator_frame, text="Line Terminator: ", fg="gray")
        self.line_terminator_textbox_label.grid(row=7, column=1, pady=10)
        self.line_terminator_textbox = tk.Entry(self.csv_konfigurator_frame, exportselection=0, state="disabled")     
        self.line_terminator_textbox.grid(row=7, column=2, padx=10, pady=10)
        self.line_terminator_textbox.bind("<Return>", self.setFileLineTerminator) 
        
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
        
        self.csv_reset_button = tk.Button(self.csv_konfigurator_frame, text="Reset", state="disabled", command=self.csvReset)
        self.csv_reset_button.grid(row=12,column=2, padx=10, pady=10)
        

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        # self.helpMenu = tk.Menu(self.menu)
        # self.menu.add_cascade(label="Help", menu=self.helpMenu)
        # self.helpMenu.add_command(label="About", command=self.About)

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

        self.button_exit = tk.Button(
            self.root, text="Cancel", command=self.root.quit)
        self.button_exit.grid(row=4, column=8, padx=10, pady=10)
        self.button_importCSV = tk.Button(
            self.root, text="Import", command=self.MergeFilesGUI)
        self.button_importCSV.grid(row=4, column=6, padx=10, pady=10)
        self.button_exportCSV = tk.Button(
            self.root, text="Export as...", command=self.root.quit)
        self.button_exportCSV.grid(row=4, column=7, padx=10, pady=10)

        self.root.mainloop()

    def OpenFileGUI(self):
        try:
            super().ShowFilesInterface(self.listbox)
            self.updateDataframe()
            self.preview_table.updateModel(TableModel(self.main_dataframe))
            self.preview_table.redraw()

        except OSError as e:
            showerror("Error!", e)
        

    def RemoveFileGUI(self):
        super().RemoveFilesInterface(self.listbox)
        self.updateDataframe()
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        self.csv_konfigurator_frame.config(fg="gray")
        self.encoding_textbox.delete(0, tk.END)
        self.encodings_textbox_label.config(fg="gray")
        self.encoding_textbox.config(state="disabled")
        
        self.delimiter_textbox.delete(0, tk.END)
        self.delimiter_textbox_label.config(fg="gray")
        self.delimiter_textbox.config(state="disabled")
        self.set_all_delimiter_button.config(state="disabled")
        
        self.quotechar_textbox.delete(0, tk.END)
        self.quotechar_textbox_label.config(fg="gray")
        self.quotechar_textbox.config(state="disabled")
        
        self.header_var.set(0)
        self.header_checkbox_label.config(fg="gray")
        self.header_checkbox.config(state="disabled")
        
        self.skip_spaces_var.set(0)
        self.skip_spaces_checkbox_label.config(fg="gray")
        self.skip_spaces_checkbox.config(state="disabled")
        
        self.line_terminator_textbox.delete(0, tk.END)
        self.line_terminator_textbox_label.config(fg="gray")
        self.line_terminator_textbox.config(state="disabled")
        
        self.quoting_var.set(None)
        self.quoting_radiobuttons_label.config(fg="gray")
        self.quote_minimal_button.config(state="disabled")
        self.quote_all_button.config(state="disabled")
        self.quote_non_numeric_button.config(state="disabled")
        self.quote_none_button.config(state="disabled")
        
        self.csv_reset_button.config(state="disabled")


    def ClearAllFilesGUI(self):
        super().ClearAllFilesInterface(self.listbox)
        self.updateDataframe()
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        self.encoding_textbox.delete(0, tk.END)
        self.csv_konfigurator_frame.config(fg="gray")
        self.encodings_textbox_label.config(fg="gray")
        self.encoding_textbox.config(state="disabled")
        
        self.delimiter_textbox.delete(0, tk.END)
        self.delimiter_textbox_label.config(fg="gray")
        self.delimiter_textbox.config(state="disabled")
        self.set_all_delimiter_button.config(state="disabled")
        
        self.quotechar_textbox.delete(0, tk.END)
        self.quotechar_textbox_label.config(fg="gray")
        self.quotechar_textbox.config(state="disabled")
        
        self.header_var.set(0)
        self.header_checkbox_label.config(fg="gray")
        self.header_checkbox.config(state="disabled")
        
        self.skip_spaces_var.set(0)
        self.skip_spaces_checkbox_label.config(fg="gray")
        self.skip_spaces_checkbox.config(state="disabled")
        
        self.line_terminator_textbox.delete(0, tk.END)
        self.line_terminator_textbox_label.config(fg="gray")
        self.line_terminator_textbox.config(state="disabled")
        
        self.quoting_var.set(None)
        self.quoting_radiobuttons_label.config(fg="gray")
        self.quote_minimal_button.config(state="disabled")
        self.quote_all_button.config(state="disabled")
        self.quote_non_numeric_button.config(state="disabled")
        self.quote_none_button.config(state="disabled")
        
        self.csv_reset_button.config(state="disabled")

    def MergeFilesGUI(self):
        pass
        #super().MergeFilesInterface()
        
    def setFileEncoding(self, return_event):
        super().setUserEncoding(self.listbox, self.encoding_textbox, self.encoding_textbox.get())  
        self.root.focus_set()    
        self.updateDataframe()            
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        
    def setFileDelimiter(self, return_event):
        super().setUserDelimiter(self.listbox, self.delimiter_textbox, self.delimiter_textbox.get())  
        self.root.focus_set()    
        self.updateDataframe()            
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
    
    def setDelimiterForAll(self):
        wanted_delimiter = self.delimiter_textbox.get()
        super().setDelimiterForAllFunctionality(wanted_delimiter)
        
        self.root.focus_set()    
        self.updateDataframe()            
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        
    def setFileQuotechar(self, return_event):
        super().setUserQuotechar(self.listbox, self.quotechar_textbox, self.quotechar_textbox.get())  
        self.root.focus_set()    
        self.updateDataframe()            
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        
    def setFileHeader(self):
        super().setUserHeader(self.listbox, self.header_var)  
        self.root.focus_set()    
        self.updateDataframe()            
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
    
    def setFileSkipSpaces(self):
        super().setUserSkipSpaces(self.listbox, self.skip_spaces_var)  
        self.root.focus_set()    
        self.updateDataframe()            
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        
    def setFileLineTerminator(self, return_event):
        super().setUserLineTerminator(self.listbox, self.line_terminator_textbox, self.line_terminator_textbox.get())  
        self.root.focus_set()    
        self.updateDataframe()            
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        
    def setFileQuoting(self):
        super().setUserQuoting(self.listbox, self.quoting_var)  
        self.root.focus_set()    
        self.updateDataframe()            
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
    
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
        self.updateDataframe()            
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        
        
        
        
    
    def listboxSelectionChanged(self, select_event):
        listbox_selection_index = self.listbox.curselection()
        
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
                self.csv_konfigurator_frame.config(fg="black")
                self.encodings_textbox_label.config(fg="black")
                self.encoding_textbox.config(state="normal")
                
                self.delimiter_textbox_label.config(fg="black")
                self.delimiter_textbox.config(state="normal")
                self.set_all_delimiter_button.config(state="normal")
                
                self.quotechar_textbox_label.config(fg="black")
                self.quotechar_textbox.config(state="normal")
                
                self.header_checkbox_label.config(fg="black")
                self.header_checkbox.config(state="normal")
                
                self.skip_spaces_checkbox_label.config(fg="black")
                self.skip_spaces_checkbox.config(state="normal")
                
                self.line_terminator_textbox_label.config(fg="black")
                self.line_terminator_textbox.config(state="normal")
                
                self.quoting_radiobuttons_label.config(fg="black")
                self.quote_minimal_button.config(state="normal")
                self.quote_all_button.config(state="normal")
                self.quote_non_numeric_button.config(state="normal")
                self.quote_none_button.config(state="normal")
                
                self.csv_reset_button.config(state="normal")
                super().updateEncodingTextbox(self.encoding_textbox, selected_file)
                super().updateDelimiterTextbox(self.delimiter_textbox, selected_file)
                super().updateQuotecharTextbox(self.quotechar_textbox, selected_file)
                super().updateHeaderCheckbox(self.header_var, selected_file)
                super().updateSkipSpacesCheckbox(self.skip_spaces_var, selected_file)
                super().updateLineTerminatorTextbox(self.line_terminator_textbox, selected_file)
                super().updateQuotingRadioButtons(self.quoting_var, selected_file)
            if selected_file.endswith(".xml") or selected_file.endswith(".xml_", endswith_slice, -1):
                showwarning("Warning!", "Hello")
        

    def About(self):
        print("This is a simple example of a menu")


if __name__ == "__main__":
    app = view()
