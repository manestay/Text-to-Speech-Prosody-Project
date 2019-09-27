#!/bin/sh

#  splitAlignments.py
#
#
#  Created by Eleanor Chodroff on 3/25/15.
#
#
#
import csv
import os
import sys
results=[]
BASE_DIR = './split_alignments/'
os.makedirs(BASE_DIR, exist_ok=True)
#name = name of first text file in final_ali.txt
#name_fin = name of final text file in final_ali.txt

name = "俞赛男_张宜成_follower_有控制--28-2--4-俞赛男-张宜成"
name_fin = "黄竞男_陈晓云_排序规则--25-2--11-黄竞男-陈晓云"
try:
    with open("tri3_cleaned_tongji_all/final_alignment.txt") as f:
        next(f) #skip header
        for line in f:
            columns=line.split("\t")
            name_prev = name
            name = columns[1]
            if (name_prev != name):
                try:
                    with open(os.path.join(BASE_DIR, name_prev + ".txt"),'w') as fwrite:
                        writer = csv.writer(fwrite)
                        fwrite.write("\n".join(results))
                        fwrite.close()
                #print name
                except Exception as e:
                    print("Failed to write file",e)
                    sys.exit(2)
                del results[:]
                results.append(line[0:-1])
            else:
                results.append(line[0:-1])
except Exception as e:
    print("Failed to read file",e)
    sys.exit(1)
# this prints out the last textfile (nothing following it to compare with)
try:
    with open(os.path.join(BASE_DIR, name_prev + ".txt"),'w') as fwrite:
        writer = csv.writer(fwrite)
        fwrite.write("\n".join(results))
        fwrite.close()
                #print name
except Exception as e:
    print("Failed to write file",e)
    sys.exit(2)
