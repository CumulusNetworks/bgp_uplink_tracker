#!/bin/bash

echo "##########################################"
echo "### Uninstalling BGP Uplink Tracker... ###"
echo "##########################################"

if [ "$(whoami)" != "root" ]; then 
	echo -e "\nERROR: Root is required to run this script. Please re-run with sudo!"
	exit 1
fi

echo "   -Stopping and Disabling Service..."
systemctl stop bgp_uplink_tracker.service >/dev/null
systemctl disable bgp_uplink_tracker.service >/dev/null
echo "   -Removing bgp_uplink_tracker directory..."
rm -rfv /etc/bgp_uplink_tracker/

echo "   -Removing Systemd Unit File..."
rm -rfv /etc/systemd/system/bgp_uplink_tracker.service
echo "##############################"
echo "### Removal Complete!      ###"
echo "##############################"
