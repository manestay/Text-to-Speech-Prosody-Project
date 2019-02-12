#!/bin/bash

# this script contains functions for running AuToBI

echo_and_run() { echo "\$ $@" ; "$@" ; }

train_autobi() {
    TRAIN_FILES=$1
    MODEL_DIR=$2
    MODEL_NAME=$3
    mkdir -p $MODEL_DIR

    java -cp AuToBI.jar edu.cuny.qc.speech.AuToBI.AuToBITrainer \
    -training_filenames=$TRAIN_FILES \
    -pitch_accent_detector=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_det.model \
    -pitch_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_class.model \
    -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
    -intermediate_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inter_pb_det.model \
    -phrase_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_class.model \
    -phrase_accent_boundary_tone_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_bt_class.model
}

run_autobi() {
    INPUT_FILES=$1
    MODEL_DIR=$2
    MODEL_NAME=$3
    OUT_DIR=$4
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
        -pitch_accent_detector=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_det.model \
        -pitch_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_class.model \
        -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
        -intermediate_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inter_pb_det.model \
        -phrase_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_class.model \
        -phrase_accent_boundary_tone_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_bt_class.model \
        -out_file=$OUT_FILE | tee $OUT_LOG
    done
}
