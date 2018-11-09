import os
from example_config import config
import xml.etree.ElementTree as ET

XML_DIR = config['xml_dir']

def clean_corefs(speaker_id,session_number):
  '''
  :param speaker_id: speaker for which to clean the xml file
  :param session_number: session number for which to clean the xml file 
  '''
  for file in os.listdir(XML_DIR):
    if file == "{}_{}.xml".format(speaker_id,session_number):
      print("Cleaning " + file)
      tree = ET.parse(XML_DIR + file)
      root = tree.getroot()

      corefs = root[0][2]

      for coref in corefs:
        for mention in coref:
          start = int(mention.find('start').text)
          head = int(mention.find('head').text)
          text = mention.find('text').text

          if len(text.split()) > 1:
            token = text.split()[head - start]
            mention.find('start').text = str(head)
            mention.find('end').text = str(head + 1)
            mention.find('text').text = token

        tree.write(XML_DIR + file)
