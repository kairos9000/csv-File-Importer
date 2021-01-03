import reader

importer = reader.reader()


importer.read_with_init_settings("C:/Users/Philip/Desktop/testfiles_20201221/ttt.csv")
#importer.read_with_init_settings("regex_test.csv")
importer.update_csv_with_personal_settings("C:/Users/Philip/Desktop/testfiles_20201221/ttt.csv", False)
importer.update_csv_with_personal_settings("C:/Users/Philip/Desktop/testfiles_20201221/ttt.csv", True)
importer.read_with_init_settings("C:/Users/Philip/Desktop/testfiles_20201221/regexWithHeader.csv")
#importer.update_csv_with_personal_settings("regex_test.csv_0", True)
#importer.update_csv_with_personal_settings("regex_test.csv", True)
# importer.update_csv_with_personal_settings("regex_test.csv", None, None, ";")
# importer.importAsDictionary()
# importer.importAsListOfLists()
# importer.importAsNumPyArray()
# importer.exportAsCSVFile("C:/Users/Philip/Desktop/regex_test.csv")
# importer.exportAsXMLFile("C:/Users/Philip/Desktop/regex_test.xml")

# importer.import_with_init_settings("cdcatalog.xml","xml2csv.xsl")
# importer.addXMLParameter("cdcatalog.xml", "sep",",")
# importer.addXMLParameter("cdcatalog.xml",None,None,False)
    


