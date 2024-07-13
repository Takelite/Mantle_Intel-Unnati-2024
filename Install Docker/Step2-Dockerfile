# Use a base image that includes stress-ng
FROM ubuntu:latest

# Install stress-ng and bc
RUN apt-get update && \
    apt-get install -y stress-ng bc && \
    rm -rf /var/lib/apt/lists/*

# Copy the entrypoint script
COPY stress-cpu.sh /usr/local/bin/stress-cpu.sh

# Make the entrypoint script executable
RUN chmod +x /usr/local/bin/stress-cpu.sh

# Set the default command to the entrypoint script
ENTRYPOINT ["/usr/local/bin/stress-cpu.sh"]

