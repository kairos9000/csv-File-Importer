import reader

importer = reader.reader()


importer.import_with_init_settings("regex_test_mitHeader.csv")
importer.import_with_init_settings("regex_test_mitHeader.csv")
importer.update_csv_with_personal_settings("regex_test_mitHeader.csv_0", False)
importer.update_csv_with_personal_settings("regex_test_mitHeader.csv_0", True)
importer.update_csv_with_personal_settings("regex_test_mitHeader.csv", True)

importer.importAsDictionary()
importer.importAsListOfLists()
importer.importAsNumPyArray()
importer.exportAsCSVFile("C:/Users/Philip/Desktop/regex_test.csv")
importer.exportAsXMLFile("C:/Users/Philip/Desktop/regex_test.xml")

# importer.import_with_init_settings("cdcatalog.xml","xml2csv.xsl")
# importer.addXMLParameter("cdcatalog.xml", "sep",",")
# importer.addXMLParameter("cdcatalog.xml",None,None,False)
    


