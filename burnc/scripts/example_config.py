import datetime
import os

core_nlp_path = 'INSERT PATH HERE'
input_table = 'burnc-20181102.csv'
old_date = os.path.splitext(input_table)[0][-8:]
date = datetime.date.today().strftime("%Y%m%d")

config = {
  # files
  'core_nlp_path': core_nlp_path,
  'java_class_path': "{}*:.".format(core_nlp_path),
  'input_table': input_table,
  'old_table_prefix': 'burnc-{}'.format(old_date),
  'new_table_prefix': 'burnc-{}'.format(date),
  'new_table_name': 'burnc-{}.csv'.format(date),

  # directories
  'xml_dir': 'xml/',
  'txt_dir': 'txt/',
  'csv_dir': 'csv/',
  'csv_mention_dir': 'csv_mentions/',

  # big table info
  'date': date,
  'start_session': 1,
  'num_sessions': [10,34,10],
  'first_speaker': 1,
  'last_speaker': 3,
  'speaker_gender': 'f',

  # options
  'clean_xmls': True,
  'remove_temp': True,
  'verbose': True,

  # misc
  'java_memory': '4g',
  'file_suffix': '.txt',
  'file_xml_ext': '.xml',
  'combine_suffix': '_organized.csv',

}
