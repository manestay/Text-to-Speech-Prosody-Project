import pandas as pd
import math
import numpy as np
import datetime
import glob

TABLE_PREFIX = "big-table-PoS_20180401_GIVEN_"
DATE_SESSION = "session"
SUFFIX = "_organized.csv"
TODAY = datetime.date.today().strftime("%Y%m%d")
START_SESSION = 1
END_SESSION = 13

def combine1():
    filename = TABLE_PREFIX + DATE_SESSION + "01" + SUFFIX
    df = pd.read_csv(filename)

    pos_column = pd.Series([None] * len(df))
    coref_column = pd.Series([None] * len(df))

    for session_number in range(START_SESSION, END_SESSION):
        session_number = str(session_number).zfill(2)

        filename = TABLE_PREFIX + DATE_SESSION + str(session_number) + SUFFIX
        print(filename)
        df = pd.read_csv(filename)

        pos_column = df['Stanford_PoS'].combine_first(pos_column)
        coref_column = df['Coreference_IDs'].combine_first(coref_column)

    df['Stanford_PoS'] = pos_column
    df['Coreference_IDs'] = coref_column

    df.to_csv(TABLE_PREFIX + TODAY + ".csv")

def combine2(prefix=TABLE_PREFIX, date_session=DATE_SESSION, suffix=SUFFIX, date=TODAY):
    csvs = glob.glob(prefix + date_session + "*" + suffix)

    df_list = []
    for filename in sorted(csvs):
        df_list.append(pd.read_csv(filename))
    full_df = pd.concat(df_list)

    full_df.to_csv(prefix + date_session + "_merged.csv")

if __name__ == '__main__':
    # combine1()
    combine2()
