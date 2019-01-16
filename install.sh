#!/bin/bash

PROGRAM="BGP Uplink Tracker"

echo "####################################"
echo "### Installing $PROGRAM... ###"
echo "####################################"

if [ "$(whoami)" != "root" ]; then 
	echo -e "\nERROR: Root is required to run this script! Please re-run with:\n"
	echo "            'sudo -H ./install.sh'"
	exit 1
fi

echo "   -Installing Dependencies (Internet is Required)"
VRF=$(ip vrf identify)
if VRF == "mgmt"; then
    ping -I mgmt 8.8.8.8 -c2 &> /dev/null
else
    ping 8.8.8.8 -c2 &> /dev/null
fi
if [ "$?" == "0" ]; then
    apt-get update -y >/dev/null
    apt-get install python-pip -qy >/dev/null
    pip install pyroute2 >/dev/null
else echo "  ERROR: Cannot reach 8.8.8.8 on the internet. Internet is required to install dependencies."; exit 1
fi

set -e

echo "   -Creating bgp_uplink_tracker Directory @ /etc/bgp_uplink_tracker/ ..."
mkdir -p /etc/bgp_uplink_tracker/

echo "   -Copying bgp_uplink_tracker.py Python Application..."
cp ./bgp_uplink_tracker.py /etc/bgp_uplink_tracker/bgp_uplink_tracker.py

echo "   -Creating Systemd Unit File..."
cat << EOT > /etc/systemd/system/bgp_uplink_tracker.service
[Unit]
Description=BGP Uplink Tracking Script
After=frr.service
 
[Service]
Restart=on-failure
StartLimitInterval=1m
StartLimitBurst=3
TimeoutStartSec=0
#One ExecStart/ExecStop line to prevent hitting bugs in certain systemd versions
ExecStart=/etc/bgp_uplink_tracker/bgp_uplink_tracker.py
 
[Install]
WantedBy=multi-user.target
EOT

echo "   -Enabling $PROGRAM to start automatically at boot..."
systemctl daemon-reload
systemctl enable bgp_uplink_tracker.service
echo "##############################"
echo "### Installation Complete! ###"
echo -e "##############################\n"
echo "        1). Start the service."
echo "               'sudo systemctl restart bgp_uplink_tracker.service'"
echo "        2). Check the health of the running service."
echo "               'sudo systemctl status bgp_uplink_tracker.service'"
echo "        4). Monitor syslog for updates from the service."
echo "               'sudo grep bgp_uplink_tracker /var/log/syslog'"

