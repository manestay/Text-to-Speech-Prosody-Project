import datetime
import os

order_type = 'SPEAKER_ORDER'
core_nlp_path = '/mnt/c/Users/coolw/Dropbox/Programming/corenlp/'
input_table = 'games-data-20180217.csv'
old_date = os.path.splitext(input_table)[0][-8:]
date = datetime.date.today().strftime("%Y%m%d")

config = {
    # files
    'core_nlp_path': core_nlp_path,
    'java_class_path': "{}*:.".format(core_nlp_path),
    'input_table': input_table,
    'old_table_prefix': 'games-data-{}_{}'.format(old_date, order_type),
    'new_table_prefix': 'games-data-{}_{}'.format(date, order_type),
    'new_table_name': 'games-data-{}.csv'.format(date),

    # directories
    'xml_dir': 'xml/',

    # big table info
    'date': date,
    'order_type': order_type,
    'start_session': 1,
    'end_session': 12,

    # options
    'overwrite_xmls': True,
    'remove_temp': True,
    'verbose': True,

    # misc
    'java_memory': '4g',
    'file_suffix': '_{}.txt'.format(order_type),
    'file_xml_ext': '_{}.xml'.format(order_type),
    'combine_suffix': '_organized.csv',

}
