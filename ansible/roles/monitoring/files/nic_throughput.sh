#!/bin/bash

HOSTNAME="${COLLECTD_HOSTNAME:-`hostname -f`}"
INTERVAL="${COLLECTD_INTERVAL:-10}"

declare -A rx_measurements
declare -A tx_measurements

nics=$(find /sys/class/net/ -type l -exec basename {} \;)

for nic in $nics
do
  rx_measurements[$nic]=$(cat /sys/class/net/$nic/statistics/rx_bytes)
  tx_measurements[$nic]=$(cat /sys/class/net/$nic/statistics/tx_bytes)
done

while sleep "$INTERVAL"
do

  for nic in $nics
  do
    let current_rx_bytes=$(cat /sys/class/net/$nic/statistics/rx_bytes)
    let current_tx_bytes=$(cat /sys/class/net/$nic/statistics/tx_bytes)

    let rx_throughput=current_rx_bytes-rx_measurements[$nic]
    let tx_throughput=current_tx_bytes-tx_measurements[$nic]

    echo PUTVAL \"$HOSTNAME/network-bandwidth-usage/if_octets-$nic\" interval=$INTERVAL N:${rx_throughput}:${tx_throughput}

    rx_measurements[$nic]=$current_rx_bytes
    tx_measurements[$nic]=$current_tx_bytes

  done

done
