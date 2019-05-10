#!/bin/bash

# test the previously trained bdc_burnc models

. scripts/autobi_lib.sh

INPUT_FILES=/proj/speech/corpora/boston_radio/**/labnews/**/** # files not used for training
MODEL_DIR=bdc_burnc/
MODEL_NAME=bdc_burnc
OUT_DIR=bdc_burnc/TextGrids
EXT=.ala

MODE=${1:-test}
if [ $MODE = "train" ]; then
    MODE=input
    INPUT_FILES=/proj/speech/corpora/boston_radio/**/radio/**
    OUT_DIR=bdc_burnc/TextGrids_train
elif [ $MODE = "tongji" ]; then
    readarray -t INPUT_FILES < tongji/test.txt
    OUT_DIR=$MODEL_NAME/TextGrids_tongji
    EXT=.TextGrid
    run_autobi_limited "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
    exit 1
elif [ $MODE = "dur" ]
then
    MODE=input
    INPUT_FILES=/proj/speech/corpora/DUR/test
    OUT_DIR=bdc_burnc/TextGrids_dur
    EXT=.in
elif [ $MODE = "cospro" ]
then
    readarray -t INPUT_FILES < /proj/tts/data/COSPRO/test.txt
    INPUT_FILES=( "${INPUT_FILES[@]/%/\/TextGrids\/*.TextGrid}" ) # append *.TextGrid to array
    INPUT_FILES=$(join_by , "${INPUT_FILES[@]}")
    OUT_DIR=bdc_burnc/TextGrids_cospro
    EXT=.TextGrid
fi

run_autobi "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
