#!/bin/bash

watch " ls *.log | xargs -n1 -I{} sh -c 'echo {}; cat {} | grep SAVE_ALERT | sort | uniq -c'"

