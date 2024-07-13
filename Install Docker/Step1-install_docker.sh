#!/bin/bash

# Update the package list and upgrade existing packages
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker’s official GPG key
echo "Adding Docker's GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the Docker repository
echo "Adding Docker repository..."
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update the package list to include the Docker repository
echo "Updating package list..."
sudo apt update

# Install Docker CE
echo "Installing Docker..."
sudo apt install -y docker-ce

# Add the current user to the Docker group
echo "Adding user to Docker group..."
sudo usermod -aG docker $USER

# Notify user to log out and log back in
echo "Installation complete. Please log out and log back in for the changes to take effect."

# Verify the Docker installation
docker --version

# Test Docker installation
echo "Running Docker test container..."
docker run hello-world

echo "Docker installation and test complete."

