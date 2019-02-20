#!/bin/bash

# test the previously trained bdc_burnc models

. ./autobi_lib.sh

INPUT_FILES=/proj/speech/corpora/boston_radio/**/labnews/**/** # files not used for training
MODEL_DIR=bdc_burnc/
MODEL_NAME=bdc_burnc
OUT_DIR=bdc_burnc1/TextGrids
EXT=.ala

MODE=${1:-test}
if [ $MODE = "train" ]
then
    INPUT_FILES=/proj/speech/corpora/boston_radio/**/radio/**
    OUT_DIR=burnc/TextGrids_train
fi

run_autobi "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT
