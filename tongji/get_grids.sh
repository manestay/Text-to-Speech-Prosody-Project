#!/bin/bash
mkdir -p tongji_files
find /proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/1picture_orderding\ _games60groups/1F-F_11X2groups/11黄竞男-陈晓云 -name "*.TextGrid" -exec cp {} tongji_files/ \;
find /proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/1picture_orderding\ _games60groups/1F-F_11X2groups/11黄竞男-陈晓云 -name "*.wav" -exec cp {} tongji_files/ \;
rename "s/\s/_/g" tongji_files/*
