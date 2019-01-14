#!/usr/bin/env python

""" BGP Uplink Watcher
This script monitors the state of BGP neighbors.
If all BGP neighbors are down, it is assumed all
Uplinks have been lost and the script will bring
down any links which are participating in CLAG so
as to influence hosts to not send data to this
switch.
"""

print("""
#########################################
          BGP Uplink Watcher
#########################################
  originally written by Eric Pulvino
""")

import os
import json
import time
import pprint
import subprocess
from pyroute2 import IPRoute

### Hardcoded Items
frr_logfile='/var/log/frr/frr.log'
clag_link_state = None

bgp_uplinks = {} 

def detect_bgp_neighbors():
    """ Detect BGP Neighbor Function
    This function pulls JSON information from a running FRR instance to
    determine the configured BGP neighbors and their state.
    """
    global bgp_uplinks
    try:
        bgp_neighbors_json = subprocess.check_output(['/usr/bin/vtysh -c "show ip bgp sum json"'], shell=True)
        #bgp_neighbors_json = subprocess.check_output(['net','show','bgp','sum','json'])
    except:
        raise SystemExit("ERROR: Could not fetch BGP Neighbor information from FRR.")
    bgp_neighbors = json.loads(bgp_neighbors_json)

    bgp_uplinks = {}
    for peer in bgp_neighbors['ipv4Unicast']['peers']:
        if bgp_neighbors['ipv4Unicast']['peers'][peer]['state'] == 'Established':
            bgp_uplinks[peer] = 'up'
        else: 
            bgp_uplinks[peer] = 'down'
    print("Detected the following BGP Neighbors:\n%s"%bgp_uplinks)    

def follow_file(thefile):
    """ Follow Function
    Calling this function on a file descriptor returns a generator object
    which can be iterated over to retrieve new lines in the file as they 
    are written.
    """
    thefile.seek(0, os.SEEK_END) # End-of-file
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1) # Sleep briefly
            continue
        yield line

def change_link_state(link_list,linkstate):
    """ Link State Change Function
    Calling this function with a list of interface names and a desired
    state will have the netlink library attempt to enforce the desired
    state on the specified links in the list
    """
    # Initialize the pyroute2 library
    ip = IPRoute()

    ifindex_dict={}
    # key is interface name, value is the interface index number

    # Create the ifindex_dict
    for interface in ip.get_links():
        ifindex_dict[interface['attrs'][0][1]]=interface['index']

    # Down the clag links individually by ifindex
    for interface in link_list:
        print("    bringing %s interface %s..."%(interface,linkstate))
        ip.link('set', index=ifindex_dict[interface], state=linkstate)

def handle_clag_links(linkstate):
    """ CLAG Handler
    This function identifies which links are participating in CLAG.
    The function only detects when links have a valid CLAG id which
    is not 0, meaning that VNIs and other automatically detected
    interfaces will be ignored from a control perspective.
    """
    if linkstate != "up" and linkstate != "down": 
        raise SystemExit("ERROR: Valid states are 'up' or 'down'.")
    print("INFO: CLAG Links need to be brought %s."%linkstate)
    try:
        clag_info_json = subprocess.check_output(['/usr/bin/clagctl','-j'])
    except:
        raise SystemExit("ERROR: Could not fetch CLAG information.")
    clag_info = json.loads(clag_info_json)
    clag_links = []
    for interface in clag_info['clagIntfs']:
        if clag_info['clagIntfs'][interface]['clagId'] != 0 and clag_info['clagIntfs'][interface]['operstate'] != linkstate: 
            clag_links.append(interface)
    if len(clag_links) > 0: change_link_state(clag_links,linkstate)
    else: print("INFO: There are no CLAG links which need adjustment.")

def track_neighbors(neighbor,state):
    """ Track Neighbors Function
    This function takes the neighbor and state information received and
    updates the global neighbor state datastructure. It also parses that
    datastructure afterwards and takes the action to handle any required
    state changes to links participating in CLAG.
    """
    global clag_link_state
    global bgp_uplinks
    # Update the neighbor state
    if state == 'down' or state == 'up' and neighbor in bgp_uplinks:
        bgp_uplinks[neighbor] = state
    #pprint.pprint(bgp_uplinks)

    down_set = []
    up_set = []
    for neighbor in bgp_uplinks:
        if bgp_uplinks[neighbor] == 'down': down_set.append(neighbor)
        elif bgp_uplinks[neighbor] == 'up': up_set.append(neighbor)
        else: up_set.append(neighbor)
    #print("down_set is %s"%down_set)
    #print("up_set is %s"%up_set)
    if len(up_set) == 0:
        # All BGP Uplinks are down -- kill the clag links
        handle_clag_links('down')
        clag_link_state = 'down'
    else:
        # At least one BGP Uplink is present
        # If previously holding clag links down, bring them up
        if clag_link_state == 'down':
            handle_clag_links('up')
            clag_link_state = 'up'

def parse_line(line):
    """ Parse Line Function
    This function parses the lines of the FRR log file one by one
    """
    # Parse the line and identify neighbor and state
    searchterm_position=line.find('neighbor')
    if searchterm_position == -1: return
    substring=line[searchterm_position:]
    words=substring.split()
    neighbor = words[1].split('(')[0]
    state = words[5].lower()
    print('INFO: Neighbor %s is %s.'%(neighbor,state))

    # Handle the neighbor state update
    track_neighbors(neighbor,state)


def main():

    detect_bgp_neighbors()

    # Starting the TAIL of the file
    file = open(frr_logfile)
    lines = follow_file(file)

    # Parse the lines as they arrive
    for line in lines:
        if "bgpd" in line and "ADJCHANGE" in line:
            #print(line)
            parse_line(line)


if __name__ == '__main__':
    main()



