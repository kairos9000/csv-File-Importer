#import csv_xml_importer as cxi 

# model = cxi.model()

# model.import_with_init_settings("C:/Users/Philip/Desktop/regex_test.csv")
# model.import_with_init_settings("C:/Users/Philip/Desktop/regex_test_mitHeader.csv")


# model.update_header(False)

from lxml import etree
import pandas as pd
import csv
xmldoc = etree.parse("cdcatalog.xml")
transformer = etree.XSLT(etree.parse("xml2csv.xsl"))
# + Fehlerbehandlung: Datei-, Parsing-, Transformationsfehler
result = str(transformer(xmldoc, param1="value"))
#print(result.splitlines())
reader = csv.reader(result.splitlines(), delimiter=',')
list_reader = list(reader)
print(list_reader)
column_names = list_reader[0]

df = pd.DataFrame(list_reader, columns=column_names)
print(df)
