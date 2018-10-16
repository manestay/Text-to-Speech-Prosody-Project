'''
This script runs all the scripts to generate a big table with all of the new columns.

'''

from example_config import config
import glob
import os
from stanfordcorenlp import StanfordCoreNLP
import sys

# scripts
import stanford_pos
import run_stanford
from combine_session_tables import combine
import CleanCorefs
import stanford_parse_columns
import add_new_columns

CORE_NLP_PATH = config['core_nlp_path']
MEMORY = config['java_memory']

OLD_PREFIX = config['old_table_prefix']
NEW_PREFIX = config['new_table_prefix']
NEW_TABLE_NAME = config['new_table_name']
REMOVE_TEMP = config['remove_temp']

if __name__ == '__main__':
    with StanfordCoreNLP(CORE_NLP_PATH, memory=MEMORY) as client:
        print('run_stanford.generate_stanford_text()')
        run_stanford.generate_stanford_text()
        print('stanford_pos.parse_pos()')
        stanford_pos.parse_pos(client)
        print('run_stanford.main()')
        run_stanford.main()

        print('combine...')
        combine(OLD_PREFIX, 'temp_' + NEW_TABLE_NAME)

        print('stanford_parse_columns.main()')
        stanford_parse_columns.main('temp_' + NEW_TABLE_NAME, client)
        print('combining2...')
        combine('temp_' + NEW_PREFIX, 'temp2_' + NEW_TABLE_NAME)
        print('add_new_columns.main()')
        add_new_columns.main('temp2_' + NEW_TABLE_NAME)

        if os.path.isfile(NEW_TABLE_NAME):
            print('{} already exists, not renaming {}'.format(NEW_TABLE_NAME, NEW_PREFIX + '.csv'))
        else:
            os.rename(NEW_PREFIX + '.csv', NEW_TABLE_NAME)

        # if REMOVE_TEMP:
        #     for f in glob.glob("temp*.csv"):
        #         os.remove(f)
        #     for f in glob.glob("*session*x  .csv"):
        #         os.remove(f)
