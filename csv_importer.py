# -*- coding: utf-8 -*-


import tkinter as tk
import pandas as pd
import io
from tkinter import ttk 
from pandastable import Table
from tkinter.messagebox import showwarning, showinfo, showerror
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from PyPDF2 import PdfFileWriter, PdfFileReader


class model():
    """This class provides the functionality of the project according to the 
    model-view-separation principle"""

    def __init__(self):
        self.__opened_files_arr = []
        self.__index = 0
        self.__multiple_files_counter = 0
        self.encodings_list = ["UTF-8", "UTF-16", "UTF-32", "ASCII",
                               "ISO-8859-1", "ISO-8859-2", "ISO-8859-5", "ISO-8859-7", "ISO-8859-8", "ISO-2022-CN", "ISO-2022-KR", "ISO-2022-JP",
                               "windows-1251",  "windows-1250", "windows-1251",  "windows-1252", "windows-1253",  "windows-1255", 
                               "GB2312", "GB18030", 
                               "Big5",
                               "EUC-KR", "EUC-TW", "EUC-JP",
                               "HZ-GB-2312",
                               "SHIFT_JIS",  
                               "KOI8-R",
                               "MacCyrillic",
                               "IBM855", "IBM866",
                               "TIS-620"
                                ]
        #  TODO: try:
               
        #        except Datei kann nicht codiert werden error:
                
        #        except Datei kann nicht geöffnet werden error:
    def getEncodingsList(self):
        return self.encodings_list

    def ShowFilesFunctionality(self, listbox):
        self.__names = askopenfilenames()
        for name in self.__names:
            if name.endswith('.csv'):
                if name in self.__opened_files_arr:
                    self.__opened_files_arr.append(
                        name+"_"+str(self.__multiple_files_counter))
                    listbox.insert(self.__index, name+"_" +
                                   str(self.__multiple_files_counter))
                    self.__multiple_files_counter += 1
                else:
                    self.__opened_files_arr.append(name)
                    listbox.insert(self.__index, name)
                self.__index += 1
            else:
                showwarning("Warning", "Only CSV Files are allowed!")
        return self
    
    def OpenFilesFunctionality(self, encoding, table):
        for filename in self.__opened_files_arr:
            # if filename.endswith("_", -2, -1):
            #     filename = filename[:-2:]
            try:
                self.__csv_file = pd.read_csv(filename, encoding=encoding)
                table.importCSV(filename)
            
            except OSError as e:
                showerror("Error!", e)
                
            
            

    def RemoveFilesFunctionality(self, listbox):
        selected_elems = listbox.curselection()
        if selected_elems == ():
            return
        for elem in selected_elems[::-1]:
            elem_name = listbox.get(elem)
            self.__opened_files_arr.remove(elem_name)
            listbox.delete(elem)

        if len(self.__opened_files_arr) == 0:
            self.__index = 0
        return self

    def ClearAllFilesFunctionality(self, listbox):
        listbox.delete(0, self.__index)
        self.__opened_files_arr.clear()
        self.__index = 0
        return self

    def MergeFilesFunctionality(self):
        if len(self.__opened_files_arr) == 0:
            showwarning("Warning", "No CSV Files to import selected!")
            return
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
        return self


class view(model):
    """This class is responsible for the GUI"""

    def __init__(self):

        self.root = tk.Tk()
        self.root.minsize(1000, 300)
        super().__init__()

        self.CSV_Importer_Labelframe = tk.LabelFrame(self.root, text="CSV-Importer")
        self.CSV_Importer_Labelframe.pack(padx=10, pady=10)
        
        self.preview_table_Labelframe = tk.LabelFrame(self.root, text="Preview")
        self.preview_table_Labelframe.pack(padx=10, pady=10, side=tk.BOTTOM)
       
        
        file_buttons_frame = tk.Frame(self.CSV_Importer_Labelframe)
        file_buttons_frame.pack(side=tk.LEFT)
        listbox_frame = tk.Frame(self.CSV_Importer_Labelframe)
        listbox_frame.pack(side=tk.TOP)
        encodings_frame = tk.Frame(self.CSV_Importer_Labelframe)
        encodings_frame.pack(side=tk.BOTTOM)
        
        self.listbox = tk.Listbox(
            listbox_frame, width=100, selectmode=tk.MULTIPLE)
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

        self.helpMenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.helpMenu)
        self.helpMenu.add_command(label="About", command=self.About)

        self.button_addFile = tk.Button(
            file_buttons_frame, text="Add CSV-File", command=self.OpenFileGUI)
        self.button_addFile.pack(side=tk.TOP, padx=5, pady=5)
        self.button_removeFile = tk.Button(
            file_buttons_frame, text="Remove selected File/s", command=self.RemoveFileGUI)
        self.button_removeFile.pack(side=tk.TOP, padx=5, pady=5)
        self.button_removeAllFiles = tk.Button(
            file_buttons_frame, text="Remove all Files", command=self.ClearAllFilesGUI)
        self.button_removeAllFiles.pack(side=tk.TOP, padx=5, pady=5)
        
        self.preview_table = Table(self.preview_table_Labelframe)
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
        super().ShowFilesFunctionality(self.listbox)
        super().OpenFilesFunctionality(self.encoding_value.get(), self.preview_table)

    def RemoveFileGUI(self):
        super().RemoveFilesFunctionality(self.listbox)

    def ClearAllFilesGUI(self):
        super().ClearAllFilesFunctionality(self.listbox)

    def MergeFilesGUI(self):
        super().MergeFilesFunctionality()

    def About(self):
        print("This is a simple example of a menu")


if __name__ == "__main__":
    app = view()
