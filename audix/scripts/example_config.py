import datetime
import os

core_nlp_path = '/home/bl2557/corenlp/'
input_table = 'archived_tables/audix-data-2018-10-05.csv'
old_date = os.path.splitext(input_table)[0][-8:]
date = datetime.date.today().strftime("%Y-%m-%d")

config = {
    # files
    'core_nlp_path': core_nlp_path,
    'java_class_path': "{}*:.".format(core_nlp_path),
    'input_table': input_table,
    'old_table_prefix': os.path.splitext(os.path.basename(input_table))[0],
    'new_table_prefix': 'audix-data-{}'.format(date),
    'new_table_name': 'audix-data-{}.csv'.format(date),

    # directories
    'xml_dir': 'xml/',
    'xml_dir_cleaned': 'xml_cleaned/',
    'clean_xmls': True,
    'supertags': 'pretrained_stag',

    # big table info
    'date': date,
    'start_session': 1,
    'end_session': 6,

    # options
    'overwrite_xmls': False,
    'remove_temp': True,
    'verbose': True,

    # misc
    'java_memory': '8g',
    'file_suffix': '.txt',
    'file_xml_ext': '.xml',
}
