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
#TODO: für Dateien eine dropdownlist anlegen, um jede Datei einzeln zu konfigurieren
    #also über Liste Datei auswählen=> konfigurieren
    #oder einfach in Haupt-Listbox Dateieintrag auswählen


class model_interface():
    """This class provides the functionality of the project according to the 
    model-view-separation principle"""

    def __init__(self):
        self.reader = reader.reader()
        self.__index = 0
        self.main_dataframe = pd.DataFrame()
        
    def getEncodingsList(self):
        return self.reader.giveEncodingsListFurther()
    
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
                    
            self.__filenames_dict = self.reader.opened_files_dict
            listbox.delete(0, self.__index)
            self.__index = 0
            for name in self.__filenames_dict.keys():        
                    listbox.insert(self.__index, name)
                    self.__index += 1 
            listbox.select_set(self.__index-1)
            listbox.event_generate("<<ListboxSelect>>")  
        except OSError:
            showerror("Error!", "File could not be opened!")
        except ValueError:
            showerror("Error!", "Only CSV or XML Files are allowed!")

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

        self.CSV_Importer_Labelframe = tk.LabelFrame(self.root, text="CSV-Importer")
        self.CSV_Importer_Labelframe.pack(side=tk.TOP, padx=10, pady=10)
        
        self.CSV_Konfigurator_Labelframe = tk.LabelFrame(self.root, text="CSV-Konfigurator")
        self.CSV_Konfigurator_Labelframe.pack(side=tk.TOP, padx=10, pady=10)
        
        self.preview_table_Labelframe = tk.LabelFrame(self.root, text="Preview")
        self.preview_table_Labelframe.pack(padx=10, pady=10, side=tk.TOP)
       
        
        file_buttons_frame = tk.Frame(self.CSV_Importer_Labelframe)
        file_buttons_frame.pack(side=tk.LEFT)
        listbox_frame = tk.Frame(self.CSV_Importer_Labelframe)
        listbox_frame.pack(side=tk.TOP)
        encodings_frame = tk.Frame(self.CSV_Konfigurator_Labelframe)
        encodings_frame.pack(side=tk.BOTTOM)
        
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
        encodings_dropdownlist_label = tk.Label(encodings_frame, text="CSV-Encodings: ")
        encodings_dropdownlist_label.pack(side=tk.LEFT)
        self.encoding_value = tk.StringVar()
        self.encoding_dropdownlist = ttk.Combobox(encodings_frame, state="readonly", textvariable=self.encoding_value, values=super().getEncodingsList())     
        self.encoding_dropdownlist.pack(padx=5,pady=5, side=tk.BOTTOM)
        self.encoding_value.set("UTF-8")

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        # self.helpMenu = tk.Menu(self.menu)
        # self.menu.add_cascade(label="Help", menu=self.helpMenu)
        # self.helpMenu.add_command(label="About", command=self.About)

        self.button_addFile = tk.Button(
            file_buttons_frame, text="Add CSV-File", command=self.OpenFileGUI)
        self.button_addFile.pack(side=tk.TOP, padx=5, pady=5)
        self.button_removeFile = tk.Button(
            file_buttons_frame, text="Remove selected File/s", command=self.RemoveFileGUI)
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

    def ClearAllFilesGUI(self):
        super().ClearAllFilesInterface(self.listbox)
        self.updateDataframe()
        self.preview_table.updateModel(TableModel(self.main_dataframe))
        self.preview_table.redraw()

    def MergeFilesGUI(self):
        pass
        #super().MergeFilesInterface()

    def About(self):
        print("This is a simple example of a menu")


if __name__ == "__main__":
    app = view()
