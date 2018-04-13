import xml.etree.ElementTree as ET
import os
from example_config import config

XML_DIR = config['xml_dir']

for file in os.listdir(XML_DIR):
    if file.endswith(".xml"):
        print("Cleaning " + file)
        tree = ET.parse(XML_DIR + file)
        root = tree.getroot()

        corefs = root[0][2]

        for coref in corefs:
            for mention in coref:
                start = int(mention.find('start').text)
                end = int(mention.find('end').text)
                head = int(mention.find('head').text)
                text = mention.find('text').text

                if len(text.split()) > 1:
                    token = text.split()[head - start]
                    mention.find('start').text = str(head)
                    mention.find('end').text = str(head + 1)
                    mention.find('text').text = token

        tree.write(XML_DIR + file)
