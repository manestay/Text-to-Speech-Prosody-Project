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
import add_supertags
import add_parse_tree_features

CORE_NLP_PATH = config['core_nlp_path']
MEMORY = config['java_memory']

OLD_PREFIX = config['old_table_prefix']
NEW_PREFIX = config['new_table_prefix']
NEW_TABLE_NAME = config['new_table_name']
REMOVE_TEMP = config['remove_temp']
SUPERTAG_DIR = config['supertags']

if __name__ == '__main__':
    with StanfordCoreNLP(CORE_NLP_PATH, memory=MEMORY) as client:
        print('run_stanford.generate_stanford_text()')
        run_stanford.generate_stanford_text()

        print('stanford_pos.parse_pos()')
        stanford_pos.parse_pos(client)

        print('run_stanford.main()')
        run_stanford.main()

        print('add_supertags.main()')
        add_supertags.main(prefix=OLD_PREFIX)

        print('combining...')
        combine(OLD_PREFIX, 'temp_' + NEW_TABLE_NAME)

        print('stanford_parse_columns.main()')
        stanford_parse_columns.main('temp_' + NEW_TABLE_NAME, client)

        print('combining2...')
        combine('temp_' + NEW_PREFIX, 'temp2_' + NEW_TABLE_NAME)

        print('add_parse_tree_features.main()')
        add_parse_tree_features.main('temp2_' + NEW_TABLE_NAME, NEW_TABLE_NAME)

        print('add_new_columns.main()')
        add_new_columns.main(NEW_TABLE_NAME)

        if REMOVE_TEMP:
            for f in glob.glob("temp*.csv"):
                os.remove(f)
            for f in glob.glob("{}_session*.csv".format(OLD_PREFIX)):
                os.remove(f)
            for f in glob.glob("{}_session*.txt".format(OLD_PREFIX)):
                os.remove(f)
