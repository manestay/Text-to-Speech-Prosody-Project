import pandas as pd
import math
import numpy as np
import datetime

TABLE_PREFIX = "games-data-"
DATE_SESSION = "20180217_session"
SUFFIX = "_organized.csv"
TODAY = datetime.date.today().strftime("%Y%m%d")
START_SESSION = 1
END_SESSION = 13

filename = TABLE_PREFIX + DATE_SESSION + "01" + SUFFIX
df = pd.read_csv(filename)

pos_column = pd.Series([None] * len(df))
coref_column = pd.Series([None] * len(df))

for session_number in range(START_SESSION, END_SESSION):
    session_number = str(session_number).zfill(2)

    filename = TABLE_PREFIX + DATE_SESSION + session_number + SUFFIX
    df = pd.read_csv(filename)

    pos_column = df['Stanford_PoS'].combine_first(pos_column)
    coref_column = df['Coreference_IDs'].combine_first(coref_column)

df['Stanford_PoS'] = pos_column
df['Coreference_IDs'] = coref_column

df.to_csv(TABLE_PREFIX + TODAY + ".csv")
