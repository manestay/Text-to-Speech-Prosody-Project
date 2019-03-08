#!/bin/bash

# this script contains functions for training and running AuToBI

echo_and_run() { echo "\$ $@" ; "$@" ; }

train_autobi() {
    TRAIN_FILES=$1
    MODEL_DIR=$2
    MODEL_NAME=$3
    mkdir -p $MODEL_DIR

    java -cp AuToBI.jar edu.cuny.qc.speech.AuToBI.AuToBITrainer \
    -log4j_config_file=log4j.properties \
    -training_filenames=$TRAIN_FILES \
    -pitch_accent_detector=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_det.model \
    -pitch_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_class.model \
    -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
    -intermediate_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inter_pb_det.model \
    -phrase_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_class.model \
    -phrase_accent_boundary_tone_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_bt_class.model
}

run_common() {
    INPUT_FILES=$1
    MODEL_DIR=$2
    MODEL_NAME=$3
    OUT_DIR=$4
    EXT=$5
    MODE=$6
    mkdir -p $MODEL_DIR
    mkdir -p $OUT_DIR

    if [[ "$(declare -p INPUT_FILES)" =~ "declare -a" ]]; then
        FILES="${INPUT_FILES[@]}"
    elif [ -f "$INPUT_FILES" ]; then
        IFS=''
        FILES="$INPUT_FILES"
    elif [ -d "$INPUT_FILES" ]; then
        FILES="$INPUT_FILES"/*$EXT
    fi
    input_flag="-input_file"
    if [ $MODE = "tongji" ]; then
        input_flag="-tongji_file"
    fi
}

run_autobi() {
    run_common "$@"
    for input_file in $FILES
    do
        WAV="${input_file%.*}".wav
        OUT_FILE=$OUT_DIR/$(basename "$input_file" $EXT)_pred.TextGrid
        OUT_LOG="${OUT_FILE%.*}".log

        # echo_and_run \
        java -jar AuToBI.jar $input_flag="$input_file" \
        -wav_file="$WAV" \
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

run_autobi_limited() {
    run_common "$@"
    for input_file in $FILES
    do
        WAV="${input_file%.*}".wav
        OUT_FILE=$OUT_DIR/$(basename "$input_file" $EXT)_pred.TextGrid
        OUT_LOG="${OUT_FILE%.*}".log

        # echo_and_run \
        java -jar AuToBI.jar $input_flag="$input_file" \
        -wav_file="$WAV" \
        -log4j_config_file=log4j.properties \
        -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
        -intermediate_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inter_pb_det.model \
        -charset=utf16 \
        -out_file=$OUT_FILE | tee $OUT_LOG
    done
}
