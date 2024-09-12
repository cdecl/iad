#!/bin/bash

BASEDIR=$(cd $(dirname "$0") && pwd)
source $BASEDIR/venv/bin/activate

# 스크립트 실행 경로 설정 (예: bot.py가 있는 경로)
SCRIPT_PATH="$BASEDIR/bot.py"
LOG_FILE="$BASEDIR/bot.log"
PID_FILE="$BASEDIR/bot.pid"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2> /dev/null; then
        echo "Bot is already running (PID: $(cat $PID_FILE))"
    else
        echo "Starting bot..."
        nohup python -u $SCRIPT_PATH 2> /dev/null 1> $LOG_FILE & echo $! > $PID_FILE
        echo "Bot started (PID: $(cat $PID_FILE))"
    fi
}

stop() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2> /dev/null; then
        echo "Stopping bot (PID: $(cat $PID_FILE))..."
        kill $(cat $PID_FILE)
        rm -f $PID_FILE
        echo "Bot stopped."
    else
        echo "Bot is not running."
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2> /dev/null; then
        echo "Bot is running (PID: $(cat $PID_FILE))"
    else
        echo "Bot is not running."
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac