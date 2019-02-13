#!/bin/bash

. ./autobi_lib.sh

TRAIN_FILES=/proj/speech/corpora/boston_radio/**/radio/**/*.ala
MODEL_DIR=burnc/
MODEL_NAME=burnc

train_autobi "$TRAIN_FILES" $MODEL_DIR $MODEL_NAME
