# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter.messagebox import showwarning, showinfo
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from PyPDF2 import PdfFileWriter, PdfFileReader

class model():
    def __init__(self):
        self.__opened_files_arr = []
        self.__index = 1
        
    def OpenFiles(self, listbox): 
        self.__names = askopenfilenames()
        for name in self.__names:
            if name.endswith('.pdf'):
                self.__opened_files_arr.append(name)
                listbox.insert(self.__index, name)
                self.__index += 1
            else:
                showwarning("Warning", "Only PDF Files are allowed!")
        return self
                
    def RemoveFiles(self, listbox):
        selected_elem = listbox.curselection()
        if selected_elem == ():
            return
        selected_elem_name = listbox.get(listbox.curselection())
        listbox.delete(selected_elem)
        self.__opened_files_arr.remove(selected_elem_name)
        return self
           
    def ClearAllFiless(self, listbox):
        listbox.delete(0, self.__index)
        self.__opened_files_arr.clear()
        return self
    
    def MergeFiless(self):
        if len(self.__opened_files_arr) == 0:
            showwarning("Warning", "No PDF Files to merge selected!")
            return
        pdfWriter = PdfFileWriter()

        for filename in self.__opened_files_arr:
            pdfFileObj = open(filename, 'rb')
            pdfReader = PdfFileReader(pdfFileObj)

            for pageNum in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(pageNum)
                pdfWriter.addPage(pageObj)


        save_file = asksaveasfilename(defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf")],
            initialfile="merged.pdf")
        pdfOutput = open(save_file, 'wb')
        pdfWriter.write(pdfOutput)
        pdfOutput.close()
        return self
    
class view(model):
    
    def __init__(self):

        self.root = tk.Tk()
        super().__init__()
                
        self.main_labelFrame = tk.LabelFrame(self.root, text="PDF-Merger")
        self.main_labelFrame.pack(padx= 10, pady = 10)
        self.listbox = tk.Listbox(self.main_labelFrame, width = 100)
        scrollbar = tk.Scrollbar(self.main_labelFrame) 
        scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH)
        self.listbox.config(xscrollcommand = scrollbar.set)
        self.listbox.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.listbox.yview) 
        self.listbox.pack(side=tk.RIGHT,padx= 10, pady = 10)

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.helpMenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.helpMenu)
        self.helpMenu.add_command(label="About", command=self.About)
        
        self.button_addPdf = tk.Button(self.main_labelFrame, text="Add PDF", command=self.OpenFile)
        self.button_addPdf.pack(side=tk.LEFT, padx=5, pady=5)
        self.button_removePdf = tk.Button(self.main_labelFrame, text="Remove selected PDF", command=self.RemoveFile)
        self.button_removePdf.pack(side=tk.LEFT, padx=5, pady=5)
        self.button_removeAllPdf = tk.Button(self.main_labelFrame, text="Remove all PDFs", command=self.ClearAllFiles)
        self.button_removeAllPdf.pack(side=tk.LEFT, padx=5, pady=5)
        
        
        self.button_exit = tk.Button(self.root, text="Cancel", command=self.root.quit)
        self.button_exit.pack(side=tk.RIGHT, padx=10, pady=10)
        self.button_mergePdf = tk.Button(self.root, text="Merge PDFs", command=self.MergeFiles)
        self.button_mergePdf.pack(side=tk.RIGHT, padx=10, pady=10)
        

        self.root.mainloop()
        
    def OpenFile(self): 
        super().OpenFiles(self.listbox)

            
    def RemoveFile(self):
        super().RemoveFiles(self.listbox)
    
    
    def ClearAllFiles(self):
        super().ClearAllFiless(self.listbox)    
        
            
    def About(self):
        print("This is a simple example of a menu")
        
               
    def MergeFiles(self):
        super().MergeFiless()

if __name__ == "__main__":
    app = view()       

