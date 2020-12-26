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
#TODO: restliche Parameter von CSV und XML Files in derselben Art änderbar machen wie Encoding-Entry Box

class model_interface():
    """This class provides the functionality of the project according to the 
    model-view-separation principle"""

    def __init__(self):
        self.reader = reader.reader()
        self.__index:int = 0
        self.main_dataframe = pd.DataFrame()
        self.selected_listbox_elem:int = -1
        
    
    def updateDataframe(self):
        self.main_dataframe = self.reader.giveDataframe()

    def ShowFilesInterface(self, listbox):
        try:
           
            self.__names = askopenfilenames()
            for filename in self.__names:
                try:
                    self.reader.read_with_init_settings(filename)
                except ValueError as value_error:
                    showerror("Error!", value_error)
                    return
                    
            self.__filenames_dict = self.reader.opened_files_dict
            listbox.delete(0, self.__index)
            self.__index = 0
            for name in self.__filenames_dict.keys():        
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

        if len(self.__filenames_dict) == 0:
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
            encodings_textbox.insert(0, self.__filenames_dict[selected_file]["Encoding"])
    
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
        except LookupError:
            self.updateEncodingTextbox(delimiter_textbox, filename)
            showerror("Error!", "Cannot set Delimiter "+ wanted_delimiter+" for "+filename)
        except ValueError as value_error:
            showerror("Error!", "For "+filename+" the following encoding error occured: "+value_error)
        
    
    def updateDelimiterTextbox(self, delimiter_textbox, selected_file):
        if selected_file is not None:
            delimiter_textbox.delete(0, tk.END)
            delimiter_textbox.insert(0, self.__filenames_dict[selected_file]["Delimiter"])
        
        
            
        

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
        self.CSV_Importer_Labelframe.pack(side=tk.TOP, padx=10, pady=10)
        
        self.CSV_Konfigurator_Labelframe = tk.LabelFrame(self.root, text="File-Konfigurator")
        self.CSV_Konfigurator_Labelframe.pack(side=tk.TOP, padx=10, pady=10)
        
        self.preview_table_Labelframe = tk.LabelFrame(self.root, text="Preview")
        self.preview_table_Labelframe.pack(padx=10, pady=10, side=tk.TOP)
       
        
        file_buttons_frame = tk.Frame(self.CSV_Importer_Labelframe)
        file_buttons_frame.pack(side=tk.LEFT)
        listbox_frame = tk.Frame(self.CSV_Importer_Labelframe)
        listbox_frame.pack(side=tk.TOP)
        self.grid_frame = tk.Frame(self.CSV_Konfigurator_Labelframe)
        self.grid_frame.pack(side=tk.BOTTOM)
        self.konfigurator_frame = tk.Frame(self.grid_frame)
        self.konfigurator_frame.pack(side=tk.BOTTOM)
        
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
        
        self.encodings_textbox_label = tk.Label(self.konfigurator_frame, text="Encoding: ", fg="gray")
        self.encodings_textbox_label.grid(row=1, column=1, pady=10)
        self.encoding_textbox = tk.Entry(self.konfigurator_frame, exportselection=0, state="disabled")     
        self.encoding_textbox.grid(row=1,column=3, padx=10, pady=10)
        self.encoding_textbox.bind("<Return>", self.setFileEncoding)
        
        self.delimiter_textbox_label = tk.Label(self.konfigurator_frame, text="Delimiter: ", fg="gray")
        self.delimiter_textbox_label.grid(row=3, column=1, pady=10)
        self.delimiter_textbox = tk.Entry(self.konfigurator_frame, exportselection=0, state="disabled")     
        self.delimiter_textbox.grid(row=3, column=3, padx=10, pady=10)
        self.delimiter_textbox.bind("<Return>", self.setFileDelimiter)       
        

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
        self.button_exit.pack(side=tk.RIGHT, padx=10, pady=10)
        self.button_importCSV = tk.Button(
            self.root, text="Import", command=self.MergeFilesGUI)
        self.button_importCSV.pack(side=tk.RIGHT, padx=10, pady=10)
        self.button_exportCSV = tk.Button(
            self.root, text="Export as...", command=self.root.quit)
        self.button_exportCSV.pack(side=tk.RIGHT, padx=10, pady=10)

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
        self.encoding_textbox.delete(0, tk.END)
        self.encodings_textbox_label.config(fg="gray")
        self.encoding_textbox.config(state="disabled")
        
        self.delimiter_textbox.delete(0, tk.END)
        self.delimiter_textbox_label.config(fg="gray")
        self.delimiter_textbox.config(state="disabled")

    def ClearAllFilesGUI(self):
        super().ClearAllFilesInterface(self.listbox)
        self.updateDataframe()
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()
        self.encoding_textbox.delete(0, tk.END)
        self.encodings_textbox_label.config(fg="gray")
        self.encoding_textbox.config(state="disabled")
        
        self.delimiter_textbox.delete(0, tk.END)
        self.delimiter_textbox_label.config(fg="gray")
        self.delimiter_textbox.config(state="disabled")

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
                self.encodings_textbox_label.config(fg="black")
                self.encoding_textbox.config(state="normal")
                
                self.delimiter_textbox_label.config(fg="black")
                self.delimiter_textbox.config(state="normal")
                super().updateEncodingTextbox(self.encoding_textbox, selected_file)
                super().updateDelimiterTextbox(self.delimiter_textbox, selected_file)
            if selected_file.endswith(".xml") or selected_file.endswith(".xml_", endswith_slice, -1):
                showwarning("Warning!", "Hello")
        

    def About(self):
        print("This is a simple example of a menu")


if __name__ == "__main__":
    app = view()
