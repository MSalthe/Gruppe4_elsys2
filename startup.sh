#!/bin/sh
echo "Setting up hotspot..."
sudo nmcli device wifi hotspot ssid Dexteritas password 12345678

echo "Starting main..."
x-terminal-emulator -e "sudo python3 main.py"  

echo "Starting backend..."
python3 backend.py  