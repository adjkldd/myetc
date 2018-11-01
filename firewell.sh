#!/bin/sh

# ./firewell.sh 23.105.206.228 16001 hipassword

addr="23.105.206.228"
port="16001"
passwd="hipassword"

if [ $# -eq 3 ]; then
  addr="$1"
  port="$2"
  passwd="$3"
fi

sslocal -qq -s $addr -p $port -k $passwd -m aes-256-cfb
