import csv_xml_importer as cxi 

model = cxi.model()

model.import_with_init_settings("C:/Users/Philip/Desktop/regex_test_mitHeader.csv")
model.import_with_init_settings("C:/Users/Philip/Desktop/regex_test.csv")

model.update_with_personal_settings(False,"UTF-8",";","\"",True,"\n")
