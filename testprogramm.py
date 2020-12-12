# import csv_reader
# import xml_reader

# csv_import = csv_reader.csv_importer()
# xml_import = xml_reader.xml_importer()


# csv_import.import_with_init_settings("C:/Users/Philip/Desktop/regex_test.csv")
# csv_import.import_with_init_settings("C:/Users/Philip/Desktop/regex_test_mitHeader.csv")


# csv_import.update_header(True)


import lxml.etree
from lxml import etree
import xml.etree.ElementTree as ET
import csv
import pandas as pd

# tree = ET.parse('xml2csv.xsl')

# root = tree.getroot()
# match = [c.attrib for c in root if 'param' in c.tag]
# match[0]["select"] = ";"

# print(match)

try:
    try:
        xmldoc = etree.parse("cdcatalog.xml")
    except lxml.etree.ParseError as parse_error:
        print("parse_error")
        exit()
    try:
        transformer = etree.XSLT(etree.parse("xml2csv.xsl"))
        tree = ET.parse('xml2csv.xsl')
    except lxml.etree.XSLTParseError as xsl_parse_error:
        print("xsl_parse_error")
        exit()
    root = tree.getroot()
    match = [c.attrib for c in root if 'param' in c.tag]

    sep_param = ","
    result = str(transformer(xmldoc, **{match[0]["name"]: "\""+sep_param+"\""}, **{match[1]["name"]: "'\"'"}, **{match[2]["name"]: "'\r\n'"}))
    reader = csv.reader(result.splitlines(), delimiter=',')
    list_reader = list(reader)
    print(list_reader)
    column_names = list_reader.pop(0)

    df = pd.DataFrame(list_reader, columns=column_names)
    print(df)
    
except OSError as os:
    print("os")
    
except lxml.etree.XSLTApplyError as transform_error:
    print("transform_error")
    


