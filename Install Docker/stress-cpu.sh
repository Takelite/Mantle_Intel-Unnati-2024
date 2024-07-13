#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <target_percentage> <timeout_seconds>"
    exit 1
fi

TARGET_PERCENTAGE=$1
TIMEOUT_SECONDS=$2

if [ "$TARGET_PERCENTAGE" -lt 1 ] || [ "$TARGET_PERCENTAGE" -gt 100 ]; then
    echo "Error: Target percentage must be between 1 and 100."
    exit 1
fi

if [ "$TIMEOUT_SECONDS" -lt 1 ]; then
    echo "Error: Timeout must be a positive integer."
    exit 1
fi

# Number of CPU cores
CPU_CORES=$(nproc)

# Calculate the stress-ng load parameters
LOAD=$(echo "scale=2; $TARGET_PERCENTAGE / 100" | bc)
CPU_LOAD=$(echo "$LOAD * $CPU_CORES" | bc | awk '{print int($1+0.5)}') # Round to nearest integer

# Run stress-ng with calculated load
stress-ng --cpu $CPU_CORES --cpu-load $TARGET_PERCENTAGE --timeout ${TIMEOUT_SECONDS}s

