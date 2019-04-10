#!/bin/bash

. ./autobi_lib.sh

readarray -t INPUT_FILES < tongji/test.txt
# INPUT_FILES=/proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/1picture_ordering_games60groups/1F-F_11X2groups/7-董研-姚玲丽/1语料/3-2_姚玲丽_董研_follower.TextGrid
MODEL_DIR=tongji_test/
MODEL_NAME=tongji_test

train_autobi_limited "$INPUT_FILES" $MODEL_DIR $MODEL_NAME tongji
