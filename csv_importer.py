# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter.messagebox import showwarning, showinfo
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from PyPDF2 import PdfFileWriter, PdfFileReader


class App():
    def __init__(self):
        self.root = tk.Tk()
        
        self.__opened_files_arr = []
        
        self.__v = tk.StringVar()
        self.__v.set(1)

        self.w = tk.LabelFrame(self.root)
        self.w.pack(padx= 10, pady = 10)
        self.text_label_frame = tk.Listbox(self.w, width = 100)
        scrollbar = tk.Scrollbar(self.w) 
        scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH)
        self.text_label_frame.config(xscrollcommand = scrollbar.set)
        self.text_label_frame.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.text_label_frame.yview) 
        self.text_label_frame.pack(side=tk.RIGHT,padx= 10, pady = 10)

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.fileMenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="Add PDF", command=self.OpenFile)
        self.fileMenu.add_command(label="Remove file", command=self.RemoveFile)
        self.fileMenu.add_command(label="Clear all files", command=self.ClearAllFiles)
        self.fileMenu.add_command(label="Merge PDFs", command=self.MergeFiles)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.root.quit)

        self.helpMenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.helpMenu)
        self.helpMenu.add_command(label="About", command=self.About)
        
        self.button_addPdf = tk.Button(self.w, text="Add PDF", command=self.OpenFile)
        self.button_addPdf.pack(side=tk.LEFT, padx=5, pady=5)
        self.button_mergePdf = tk.Button(self.w, text="Merge PDFs", command=self.MergeFiles)
        self.button_mergePdf.pack(side=tk.LEFT, padx=5, pady=5)

        self.root.mainloop()
        
    def OpenFile(self): 
        self.__names = askopenfilenames()
        for name in self.__names:
            if name.endswith('.pdf'):
                self.__opened_files_arr.append(name)
            else:
                showwarning("Warning", "Only PDF Files are allowed!")
        self.clear()
        self.print_file_names(self.__opened_files_arr)
        
    def clear(self):
        for label in self.text_label_frame.winfo_children():
            label.destroy()
    
    def print_file_names(self, file_arr):
        for file_name in file_arr:
            self.text_label_frame.insert(1, file_name)
            
    def RemoveFile(self):
        self.menu_window = tk.Toplevel()
        self.radio_button_frame = tk.LabelFrame(self.menu_window, relief = tk.FLAT, labelanchor = "nw", padx = 10, pady = 10)
        self.radio_button_frame.pack()
        self.ok_button = tk.Button(self.menu_window, 
                    text="OK", fg="green",
                    command=self.menu_window.destroy)
        
        self.remove_button = tk.Button(self.menu_window, 
                    text="Remove", fg="red",
                    command= lambda: self.remove_func(self.menu_window, self.radio_button_frame))
        self.ok_button.pack(side = tk.BOTTOM)
        self.remove_button.pack(side = tk.BOTTOM)
        self.radio_buttons_func(self.radio_button_frame)
        
    def radio_buttons_func(self, radio_button_frame):  
        if len(self.__opened_files_arr) == 0:
            self.warning_label = tk.Label(radio_button_frame, text = "No File to remove!")
            self.warning_label.pack()        
        for label in self.__opened_files_arr:
            radio_buttons = tk.Radiobutton(radio_button_frame, 
                    text=label,
                    padx = 20, 
                    variable=self.__v,
                    value=label)
            radio_buttons.pack()
            
    def remove_func(self, menu_window, radio_button_frame):
        remove_label = self.__v.get()
        if remove_label in self.__opened_files_arr:
            self.__opened_files_arr.remove(remove_label)
            self.clear_radio_buttons(radio_button_frame)
            self.radio_buttons_func(radio_button_frame)
        self.clear()
        self.print_file_names(self.__opened_files_arr)
        
    def clear_radio_buttons(self, radio_button_frame):
        for self.button in radio_button_frame.winfo_children():
            self.button.destroy()
            
    def About(self):
        print("This is a simple example of a menu")
        
    def ClearAllFiles(self):
        self.__opened_files_arr.clear()
        self.clear()
        
    def MergeFiles(self):
        if len(self.__opened_files_arr) == 0:
            showwarning("Warning", "No PDF Files to merge selected!")
            return
        self.pdfWriter = PdfFileWriter()

        for filename in self.__opened_files_arr:
            self.pdfFileObj = open(filename, 'rb')
            self.pdfReader = PdfFileReader(self.pdfFileObj)

            for self.pageNum in range(self.pdfReader.numPages):
                self.pageObj = self.pdfReader.getPage(self.pageNum)
                self.pdfWriter.addPage(self.pageObj)


        self.save_file = asksaveasfilename(defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf")],
            initialfile="merged.pdf")
        self.pdfOutput = open(self.save_file, 'wb')
        self.pdfWriter.write(self.pdfOutput)
        self.pdfOutput.close()

app = App()       

