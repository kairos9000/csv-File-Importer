# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter.messagebox import showwarning, showinfo
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from PyPDF2 import PdfFileWriter, PdfFileReader


class model():
    """This class provides the functionality of the project according to the 
    model-view-separation principle"""

    def __init__(self):
        self.__opened_files_arr = []
        self.__index = 0
        self.__multiple_files_counter = 0
        #  TODO: try:
               
        #        except Datei kann nicht codiert werden error:
                
        #        except Datei kann nicht geöffnet werden error:

    def OpenFilesFunctionality(self, listbox):
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
        save_file = asksaveasfilename(defaultextension=".csv",
                                      filetypes=[("CSV file", "*.csv")],
                                      initialfile="import.csv")
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
        self.listbox = tk.Listbox(
            self.CSV_Importer_Labelframe, width=100, selectmode=tk.MULTIPLE)
        scrollbar_x = tk.Scrollbar(self.CSV_Importer_Labelframe, orient="horizontal")
        scrollbar_y = tk.Scrollbar(self.CSV_Importer_Labelframe)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.BOTH)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.listbox.config(xscrollcommand=scrollbar_x.set)
        self.listbox.config(yscrollcommand=scrollbar_y.set)
        scrollbar_x.config(command=self.listbox.xview)
        scrollbar_y.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.RIGHT, padx=10, pady=10)
        #TODO: listbox und entry mit einzelnen labelframes trennen und encoding angeben ermöglichen
        self.encoding_textbox = tk.Entry(self.CSV_Importer_Labelframe, width=100)
        self.encoding_textbox.pack(padx=5,pady=5, side=tk.BOTTOM)

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.helpMenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.helpMenu)
        self.helpMenu.add_command(label="About", command=self.About)

        self.button_addFile = tk.Button(
            self.CSV_Importer_Labelframe, text="Add CSV-File", command=self.OpenFileGUI)
        self.button_addFile.pack(side=tk.TOP, padx=5, pady=(25, 5))
        self.button_removeFile = tk.Button(
            self.CSV_Importer_Labelframe, text="Remove selected File/s", command=self.RemoveFileGUI)
        self.button_removeFile.pack(side=tk.TOP, padx=5, pady=5)
        self.button_removeAllFiles = tk.Button(
            self.CSV_Importer_Labelframe, text="Remove all Files", command=self.ClearAllFilesGUI)
        self.button_removeAllFiles.pack(side=tk.TOP, padx=5, pady=5)

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
        super().OpenFilesFunctionality(self.listbox)

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
