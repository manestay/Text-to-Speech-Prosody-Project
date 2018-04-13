'''
This script runs all the scripts to generate a big table with all of the new columns.

'''

import os, sys
from example_config import config
import glob

# scripts
import StanfordPoS
import Run_Stanford
from CombineSessionTables import combine
import StanfordParseColumns
import AddNewColumns

OLD_PREFIX = config['old_table_prefix']
NEW_PREFIX = config['new_table_prefix']
NEW_TABLE_NAME = config['new_table_name']
REMOVE_TEMP = config['remove_temp']

if __name__ == '__main__':
    # print('Run_Stanford.generateStanfordText()')
    # Run_Stanford.generateStanfordText()
    # print('StanfordPoS')
    # StanfordPoS.parse_pos()
    # print('Run_Stanford.main()')
    # Run_Stanford.main()
    # print('combining1...')
    # combine(OLD_PREFIX, 'temp_' + NEW_TABLE_NAME)

    print('StanfordParseColumns.main()')
    StanfordParseColumns.main('temp_' + NEW_TABLE_NAME)
    print('combining2...')
    combine('temp_' + NEW_PREFIX, 'temp2_' + NEW_TABLE_NAME)
    print('AddNewColumns')
    AddNewColumns.main('temp2_' + NEW_TABLE_NAME)

    if os.path.isfile(NEW_TABLE_NAME):
        print('{} already exists, not renaming {}'.format(NEW_TABLE_NAME, NEW_PREFIX + '.csv'))
    else:
        os.rename(NEW_PREFIX + '.csv', NEW_TABLE_NAME)

    if REMOVE_TEMP:
        for f in glob.glob("temp*.csv"):
            os.remove(f)
        for f in glob.glob("*session*_organized.csv"):
            os.remove(f)
