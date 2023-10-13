#!/bin/sh
# shellcheck disable=SC2116
# shellcheck disable=SC2006
cr=`echo $'\n.'`
cr=${cr%.}

read -n 1 -s -r -p "Press any key to end print test mode $cr"

