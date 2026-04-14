#!/bin/bash
# METATRON Ubuntu Server Setup Script
# Run: bash start.sh

set -e

echo "=== METATRON Server Setup ==="

# Update system
apt update && apt upgrade -y

# Install security tools
apt install -y nmap masscan nikto whatweb gobuster curl dnsutils whois sslscan

# Python and pip
apt install -y python3 python3-pip python3-venv

# Install RustScan (requires Rust)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
cargo install rustscan

# Install sublist3r
apt install -y git
git clone https://github.com/aboul3la/Sublist3r.git /opt/sublist3r
cd /opt/sublist3r
pip install -r requirements.txt
ln -s /opt/sublist3r/sublist3r.py /usr/local/bin/sublist3r
chmod +x /usr/local/bin/sublist3r

# Install testssl
git clone --depth 1 https://github.com/drwetter/testssl.sh.git /opt/testssl
ln -s /opt/testssl/testssl.sh /usr/local/bin/testssl
chmod +x /usr/local/bin/testssl

# Install theHarvester
git clone https://github.com/laramies/theHarvester.git /opt/theHarvester
cd /opt/theHarvester
pip install -r requirements.txt
ln -s /opt/theHarvester/theHarvester.py /usr/local/bin/theHarvester
chmod +x /usr/local/bin/theHarvester

# Install wfuzz
pip install wfuzz

# Python dependencies
cd /opt/metatron
pip install -r requirements.txt

echo "=== Setup Complete ==="