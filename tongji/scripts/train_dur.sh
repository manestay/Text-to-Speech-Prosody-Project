#!/bin/bash

. scripts/autobi_lib.sh

TRAIN_FILES=/proj/speech/corpora/DUR/train/*.in
MODEL_DIR=dur/
MODEL_NAME=dur
EXT=.in

train_autobi "$TRAIN_FILES" $MODEL_DIR $MODEL_NAME $EXT
