import re
import pandas as pd

PHONES = "./tri3_cleaned_tongji_all/phones.txt"
SEGMENTS = "./tongji_all/segments"
CTM = "./tri3_cleaned_tongji_all/merged_alignment.txt"
OUT_FILE = "./tri3_cleaned_tongji_all/final_alignment.txt"
FINAL_HEADER = ['file_utt', 'file', 'id', 'utt', 'start', 'dur', 'phone', 'start_utt', 'end_utt',
                'start_real', 'end_real']

def main():
    df_phones = pd.read_csv(PHONES, sep=' ', names=["phone","id"])
    df_segments = pd.read_csv(SEGMENTS, sep=' ', names=["file_utt","file","start_utt","end_utt"])
    df_ctm = pd.read_csv(CTM, sep=' ', names=["file_utt","utt","start","dur","id"])
    df_ctm['file'] = df_ctm['file_utt'].str.replace(re.compile('-[0-9]*$'), '')

    df_ctm2 = df_ctm.merge(df_phones, on='id', how='left')
    df_ctm3 = df_ctm2.merge(df_segments, on=['file_utt', 'file'])
    df_ctm3['start_real'] = df_ctm3['start'] + df_ctm3['start_utt']
    df_ctm3['end_real'] = df_ctm3['start_real'] + df_ctm3['dur']
    df_ctm3 = df_ctm3[FINAL_HEADER]
    df_ctm3.to_csv(OUT_FILE, index=False, sep='\t', float_format='%.5f')
if __name__ == "__main__":
    main()
