#!/bin/bash

# ls *.log | xargs -n1 -I{} sh -c 'echo {}; cat {} | grep SAVE_ALERT | sort | uniq -c'

BASEDIR=$(cd $(dirname "$0") && pwd)
source $BASEDIR/venv/bin/activate

LOGFILE="$BASEDIR/$1.log"
echo $(date) > $LOGFILE


if [ "$1" == "1" ]; then 
	## 8원
	python -u $BASEDIR/goods.py list https://t-s1.srk.co.kr/RewardMission/quizMission/CpOzxn5C5Uhu7JA/N24031720015159734326?inapp= >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	## 10
	python -u $BASEDIR/run.py list https://t-s1.srk.co.kr//RewardMission/searchMission/CpOzxn5C5Uhu7JA/N24031720015159734326?inapp=N >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	python bot.py send "$(ls "$1".log | xargs -n1 -I{} sh -c 'echo {}; cat {} | grep SAVE_ALERT | sort | uniq -c')"

elif [ "$1" == "11" ]; then 
	## 티머니GO 
	python -u $BASEDIR/goods.py list https://t-s2.srk.co.kr/RewardMission/quizMission/AhkU8gVNJlcYl2s/A5EB88B7-7D22-497B-B9EE-FCBDD4A65A9D/7e0390f33d01ae1eff7ad89bbbc4ef62 >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	# 야핏 
	python -u $BASEDIR/run.py list https://t-s2.srk.co.kr/RewardMission/searchMission/AhkU8gVNJlcYl2s/IFVBFBBF456-DEEB-4C5E-BB43-EC1D652BA00B/7c7f8e8edc90a2cb34d45631941e04fd >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	python bot.py send "$(ls "$1".log | xargs -n1 -I{} sh -c 'echo {}; cat {} | grep SAVE_ALERT | sort | uniq -c')"

elif [[ "$1" == "2" ]]; then 
	## 8
	python -u $BASEDIR/goods.py list https://t-s1.srk.co.kr/RewardMission/quizMission/CpOzxn5C5Uhu7JA/N24031720152998346787/ >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	## 10
	python -u $BASEDIR/run.py list https://t-s1.srk.co.kr/RewardMission/searchMission/CpOzxn5C5Uhu7JA/N24031720152998346787/ >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	python bot.py send "$(ls "$1".log | xargs -n1 -I{} sh -c 'echo {}; cat {} | grep SAVE_ALERT | sort | uniq -c')"

elif [[ "$1" == "22" ]]; then 
	## 티머니GO 
	python -u $BASEDIR/goods.py list https://t-s2.srk.co.kr/RewardMission/quizMission/AhkU8gVNJlcYl2s/CD246185-67D8-4828-9839-AA31FAB06C1E/523eed55e3adf229365188959c6ec992  >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	## 야핏 
	python -u $BASEDIR/run.py list https://t-s2.srk.co.kr/RewardMission/searchMission/AhkU8gVNJlcYl2s/IFV3700889A-D2DF-4079-BC31-12966894E89E/134427131d5992b8ecde9a8adcac4b6b >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	python bot.py send "$(ls "$1".log | xargs -n1 -I{} sh -c 'echo {}; cat {} | grep SAVE_ALERT | sort | uniq -c')"

elif [ "$1" == "3" ]; then 
	## 하나
	python -u $BASEDIR/run.py list https://t-s2.srk.co.kr/RewardMission/searchMission/AhkU8gVNJlcYl2s/IFVA5D0D8A9-0DEF-4587-AC50-6FAE9387582E/54546bd02d8162fe19bb84e493d04e3b >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	## L포인트
	python -u $BASEDIR/run.py list https://t-s2.srk.co.kr/RewardMission/searchMission/AhkU8gVNJlcYl2s/IFV79C19318-A12E-4D84-A0B7-912200108DFF/1a47a7ceebc459f3c519346bca131f55 >> $LOGFILE
	echo "SAVE_ALERT END" >> $LOGFILE

	python bot.py send "$(ls "$1".log | xargs -n1 -I{} sh -c 'echo {}; cat {} | grep SAVE_ALERT | sort | uniq -c')"
fi

