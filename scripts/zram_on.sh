#!/bin/sh
# Zram activation
modprobe zram

# set the size
echo 512M > /sys/block/zram0/disksize

# format and turn on
mkswap /dev/zram0
swapon /dev/zram0 -p 10