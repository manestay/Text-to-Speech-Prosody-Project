#!/bin/bash
mkdir -p tongji_files
find /proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/1picture_ordering_games60groups/1F-F_11X2groups/1-陈姗姗-王静/1语料/ -name "*.TextGrid" -exec cp {} tongji_files/ \;
find /proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/1picture_ordering_games60groups/1F-F_11X2groups/1-陈姗姗-王静/1语料/ -name "*.wav" -exec cp {} tongji_files/ \;
rename "s/\s/_/g" tongji_files/*
dos2unix tongji_files/*.TextGrid
