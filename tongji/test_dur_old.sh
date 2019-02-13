#!/bin/bash

# runs old AuToBI models on DUR test files
# separate script because only 2 models, instead of 6

INPUT_FILES=/proj/speech/corpora/DUR/test/*.in
MODEL_DIR=/proj/speech/corpora/DUR/models
MODEL_NAME=DUR
OUT_DIR=dur_old/TextGrids

MODE=${1:-test}
if [ $MODE = "train" ]
then
    INPUT_FILES=/proj/speech/corpora/DUR/train/*.in
    OUT_DIR=dur_old/TextGrids_train
fi

mkdir -p $MODEL_DIR
mkdir -p $OUT_DIR

for input_file in $INPUT_FILES
do
    WAV="${input_file%.*}".wav
    OUT_FILE=$OUT_DIR/$(basename $input_file .in)_pred.TextGrid
    OUT_LOG="${OUT_FILE%.*}".log
    java -jar AuToBI.jar -input_file=$input_file \
    -wav_file=$WAV \
    -log4j_config_file=log4j.properties \
    -pitch_accent_detector=${MODEL_DIR}/${MODEL_NAME}.pad.model \
    -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.ipd.model \
    -out_file=$OUT_FILE | tee $OUT_LOG
done
