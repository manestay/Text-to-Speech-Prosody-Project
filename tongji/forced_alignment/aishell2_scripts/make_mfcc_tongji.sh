#!/bin/bash

for i in  exp/tri3_cleaned_tongji_all/ali.*.gz;
  do ../../../src/bin/ali-to-phones --ctm-output exp/tri3_cleaned/final.mdl \
  ark:"gunzip -c $i|" -> ${i%.gz}.ctm;
done;
