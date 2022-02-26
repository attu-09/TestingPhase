#!/bin/bash

echo 353 > /sys/class/gpio/export

echo "out" > /sys/class/gpio/gpio353/direction
echo 0 > /sys/class/gpio/gpio353/value

led_state=OFF
while true
do
    network_status=$(nmcli -t -f STATE g)
    internet_status=$(ping -q -c 1 -W 1 8.8.8.8 | awk '/received/ {print $4}')

    if [[ $network_status = connected && $internet_status = 1 ]]
    then
        if [ $led_state = OFF ]
        then
            led_state=ON
            echo 1 > /sys/class/gpio/gpio353/value
            echo "connected"
        fi
    else
        echo 0 > /sys/class/gpio/gpio353/value
        echo "disconnected"
        led_state=OFF
    fi
done

