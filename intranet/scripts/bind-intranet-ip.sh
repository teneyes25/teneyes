#!/usr/bin/env sh
set -eu

INTRANET_IP="${INTRANET_IP:-192.168.0.6}"

if ip addr show | grep -q "${INTRANET_IP}/32"; then
  echo "${INTRANET_IP} is already bound."
  exit 0
fi

sudo ip addr add "${INTRANET_IP}/32" dev lo
echo "Bound ${INTRANET_IP} to loopback for local intranet testing."
