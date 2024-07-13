#!/bin/bash
# Download this file and run it in your terminal
# Update package lists
sudo apt-get update

# Install Python
sudo apt-get install -y python3 python3-pip

# Install Tkinter (Linux-specific)
sudo apt-get install -y python3-tk

# Install psutil using apt
sudo apt-get install -y python3-psutil

# Install matplotlib using apt
sudo apt-get install -y python3-matplotlib

# Install Pillow using apt
sudo apt-get install -y python3-pil

# Install turbostat
sudo apt-get install -y linux-tools-$(uname -r)

# Install upower
sudo apt-get install -y upower

# Install lm-sensors
sudo apt-get install -y lm-sensors

# Install power-profiles-daemon
sudo apt-get install -y power-profiles-daemon

# Confirm installation
echo "All dependencies installed successfully!"

