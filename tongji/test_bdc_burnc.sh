#!/bin/bash

# test the previously trained bdc_burnc models

. ./autobi_lib.sh

INPUT_FILES=/proj/speech/corpora/boston_radio/**/labnews/**/** # files not used for training
MODEL_DIR=bdc_burnc/
MODEL_NAME=bdc_burnc
OUT_DIR=bdc_burnc/TextGrids
EXT=.ala

MODE=${1:-test}
if [ $MODE = "train" ]
then
    INPUT_FILES=/proj/speech/corpora/boston_radio/**/radio/**
    OUT_DIR=burnc/TextGrids_train
elif [ $MODE = "tongji" ]
then
    # INPUT_FILES="tongji_files/3-1_无控制_王静_陈姗姗_giver.TextGrid"
    mapfile -t INPUT_FILES < <(find /proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/ -name "*.TextGrid")
    OUT_DIR=$MODEL_NAME/TextGrids_tongji
    EXT=.TextGrid
fi

run_autobi "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
