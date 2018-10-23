import pandas as pd
import math
import numpy as np
import datetime
import glob
from example_config import config

TODAY = config['date']
START_SESSION = config['start_session']
END_SESSION = config['end_session']

SESSION = 'session'

def combine(prefix, new_table_name='', date=TODAY):
    if not new_table_name:
        new_table_name = 'merged_{}.csv'.format(prefix.split('_')[0])
        print(new_table_name)
    print('{}_session*.csv'.format(prefix))
    csvs = glob.glob('{}_session*.csv'.format(prefix))

    df_list = []
    for filename in sorted(csvs):
        df_list.append(pd.read_csv(filename))
    full_df = pd.concat(df_list)

    full_df.to_csv(new_table_name, index=False)
    return new_table_name

if __name__ == '__main__':
    combine('')
