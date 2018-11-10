#!/bin/bash

echo_and_run() { echo "\$ $@" ; "$@" ; }

audix=audix-data-2018-11-09.csv
burnc=burnc-20181106.csv
games=games-data-20181029.csv

echo_and_run python3 configurable_classifier.py break  --no-rank --train $audix > runs/break_audix_audix.txt & \
echo_and_run python3 configurable_classifier.py break  --no-rank --train $burnc > runs/break_burnc_burnc.txt &  wait
echo_and_run python3 configurable_classifier.py break  --no-rank --train $audix --test $burnc > runs/break_audix_burnc.txt & \
echo_and_run python3 configurable_classifier.py break  --no-rank --train $burnc --test $audix > runs/break_burnc_audix.txt & wait
echo_and_run python3 configurable_classifier.py break  --no-rank --train $games > runs/break_games_games.txt & \
echo_and_run python3 configurable_classifier.py break  --no-rank --train $games --test $burnc > runs/break_games_burnc.txt & wait
echo_and_run python3 configurable_classifier.py break  --no-rank --train $games --test $audix > runs/break_games_audix.txt & \
\
echo_and_run python3 configurable_classifier.py accent --no-rank --train $audix > runs/accent_audix_audix.txt & wait
echo_and_run python3 configurable_classifier.py accent --no-rank --train $burnc > runs/accent_burnc_burnc.txt & \
echo_and_run python3 configurable_classifier.py accent --no-rank --train $audix --test $burnc > runs/accent_audix_burnc.txt & wait
echo_and_run python3 configurable_classifier.py accent --no-rank --train $burnc --test $audix > runs/accent_burnc_audix.txt & \
echo_and_run python3 configurable_classifier.py accent --no-rank --train $games > runs/accent_games_games.txt & wait
echo_and_run python3 configurable_classifier.py accent --no-rank --train $games --test $burnc > runs/accent_games_burnc.txt & \
echo_and_run python3 configurable_classifier.py accent --no-rank --train $games --test $audix > runs/accent_games_audix.txt & wait
