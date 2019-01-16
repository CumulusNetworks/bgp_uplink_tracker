# BGP Uplink Tracker
*_This script is community supported._*

Track the status of BGP peers, and bring down dual connected CLAG bonds on a switch when no BGP peers are in the **_ESTABLISHED_** state. This functionality is similar to ifplugd, execpt BGP peer status is tracked, instead of link status.

## Installing
Clone this repo to the switch:
```
git clone https://github.com/CumulusNetworks/bgp_uplink_tracker.git
```

Run the install script:
```
cd bgp_uplink_tracker
sudo ./install.sh
```

## Uninstalling
Run the uninstall script:
```
cd bgp_uplink_tracker
./uninstall.sh
```

## Operation
The script will be controlled by the system service bgp_uplink_tracker:
```
cumulus@leaf01:mgmt-vrf:~$ sudo systemctl status bgp_uplink_tracker.service
● bgp_uplink_tracker.service - BGP Uplink Tracking Script
   Loaded: loaded (/etc/systemd/system/bgp_uplink_tracker.service; enabled)
   Active: active (running) since Mon 2019-01-14 22:51:43 UTC; 1 day 16h ago
 Main PID: 24464 (python)
   CGroup: /system.slice/bgp_uplink_tracker.service
           └─24464 python /etc/bgp_uplink_tracker/bgp_uplink_tracker.py

cumulus@leaf01:mgmt-vrf:~$
```

Events will be logged to syslog:
```
2019-01-14T22:51:44.073484+00:00 leaf01 BGP_Uplink_Tracking: #012##########################################012          BGP Uplink Watcher#012##########################################012  originally written by Eric Pulvino
2019-01-14T22:51:44.187323+00:00 leaf01 BGP_Uplink_Tracking: Detected the following BGP Neighbors:#012{u'peerlink.4094': 'up', u'swp49': 'up', u'swp50': 'up'}
2019-01-14T22:52:44.654885+00:00 leaf01 BGP_Uplink_Tracking: INFO: Neighbor swp49 is down.
2019-01-14T22:53:05.913929+00:00 leaf01 BGP_Uplink_Tracking: INFO: Neighbor swp49 is up.
2019-01-16T15:11:11.668159+00:00 leaf01 BGP_Uplink_Tracking: INFO: Neighbor swp49 is down.
2019-01-16T15:11:17.889926+00:00 leaf01 BGP_Uplink_Tracking: INFO: Neighbor swp49 is up.
2019-01-16T15:12:09.637438+00:00 leaf01 BGP_Uplink_Tracking: INFO: Neighbor peerlink.4094 is down.
2019-01-16T15:12:21.771135+00:00 leaf01 BGP_Uplink_Tracking: INFO: Neighbor swp49 is down.
2019-01-16T15:12:47.145470+00:00 leaf01 BGP_Uplink_Tracking: INFO: Neighbor swp50 is down.
2019-01-16T15:12:47.147236+00:00 leaf01 BGP_Uplink_Tracking: INFO: CLAG Links need to be brought down.
2019-01-16T15:12:47.340292+00:00 leaf01 BGP_Uplink_Tracking:     bringing bond01 interface down...
2019-01-16T15:12:47.349171+00:00 leaf01 BGP_Uplink_Tracking:     bringing bond02 interface down...
2019-01-16T15:13:07.917867+00:00 leaf01 BGP_Uplink_Tracking: INFO: Neighbor swp49 is up.
2019-01-16T15:13:07.918745+00:00 leaf01 BGP_Uplink_Tracking: INFO: CLAG Links need to be brought up.
2019-01-16T15:13:08.040410+00:00 leaf01 BGP_Uplink_Tracking:     bringing bond01 interface up...
2019-01-16T15:13:08.059572+00:00 leaf01 BGP_Uplink_Tracking:     bringing bond02 interface up...
2019-01-16T15:13:18.901910+00:00 leaf01 BGP_Uplink_Tracking: INFO: Neighbor swp50 is up.
```
