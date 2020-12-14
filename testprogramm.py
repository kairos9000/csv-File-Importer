import reader

importer = reader.reader()


importer.import_with_init_settings("regex_test_mitHeader - Copy.csv")

importer.import_with_init_settings("cdcatalog.xml","cdcatalog2csv.xsl")
importer.addXMLParameter("cdcatalog.xml", "sep",",")

    


