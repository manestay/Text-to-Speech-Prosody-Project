#! /bin/bash

DIR=dur/
TRAIN_FILES=/proj/speech/corpora/DUR/train/dur*.in

java -cp AuToBI.jar edu.cuny.qc.speech.AuToBI.AuToBITrainer \
-training_filenames=$TRAIN_FILES \
-pitch_accent_detector=${DIR}dur.pitch_acc_det.model \
-pitch_accent_classifier=${DIR}dur.pitch_acc_class.model \
-intonational_phrase_boundary_detector=${DIR}dur.inton_pb_det.model \
-intermediate_phrase_boundary_detector=${DIR}dur.inter_pb_det.model \
-phrase_accent_classifier=${DIR}phrase_acc_class.model \
-phrase_accent_boundary_tone_classifier=${DIR}phrase_acc_bt_class.model
