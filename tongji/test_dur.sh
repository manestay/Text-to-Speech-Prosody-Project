#!/bin/bash

. ./autobi_lib.sh

INPUT_FILES=/proj/speech/corpora/DUR/test
MODEL_DIR=dur/
MODEL_NAME=dur
OUT_DIR=dur/TextGrids
EXT=.in

MODE=${1:-test} # default mode is test
if [ $MODE = "train" ]
then
    INPUT_FILES=/proj/speech/corpora/DUR/train
    OUT_DIR=dur/TextGrids_train
elif [ $MODE = "tongji" ]
then
    # INPUT_FILES="tongji_files/3-1_无控制_王静_陈姗姗_giver.TextGrid"
    mapfile -t INPUT_FILES < <(find /proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/ -name "*.TextGrid")
    OUT_DIR=$MODEL_NAME/TextGrids_tongji
    EXT=.TextGrid
fi

run_autobi_limited "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
