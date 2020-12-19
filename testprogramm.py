import reader

importer = reader.reader()


<<<<<<< HEAD
importer.import_with_init_settings("regex_test.csv")
importer.import_with_init_settings("regex_test.csv")
importer.update_csv_with_personal_settings("regex_test.csv_0", False)
#importer.update_csv_with_personal_settings("regex_test.csv_0", True)
#importer.update_csv_with_personal_settings("regex_test.csv", True)
=======
importer.read_with_init_settings("regex_test_mitHeader.csv")
importer.read_with_init_settings("regex_test_mitHeader.csv")
importer.update_csv_with_personal_settings("regex_test_mitHeader.csv_0", False)
importer.update_csv_with_personal_settings("regex_test_mitHeader.csv_0", True)
importer.update_csv_with_personal_settings("regex_test_mitHeader.csv", True)
>>>>>>> 3376c76f308e2ff647183f1ad243d4ffd8ad2493

importer.importAsDictionary()
importer.importAsListOfLists()
importer.importAsNumPyArray()
importer.exportAsCSVFile("C:/Users/Nutzer/Desktop/regex_test.csv")
importer.exportAsXMLFile("C:/Users/Nutzer/Desktop/regex_test.xml")

# importer.import_with_init_settings("cdcatalog.xml","xml2csv.xsl")
# importer.addXMLParameter("cdcatalog.xml", "sep",",")
# importer.addXMLParameter("cdcatalog.xml",None,None,False)
    


