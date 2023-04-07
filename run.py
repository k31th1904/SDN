#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import RemoteController
from time import sleep
import json
import os
import time
import requests
import subprocess


class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."
    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        h1 = self.addHost('h1', mac="00:00:00:00:11:11", ip="192.168.1.1/24")
        h2 = self.addHost('h2', mac="00:00:00:00:11:12", ip="192.168.1.2/24")

        self.addLink(h1, s1)
        self.addLink(h2, s2)

        self.addLink(s1, s2)

def collect_mininet_info(net):
    
    #define a dictionary
    info = {
    	"hosts": [],
    	"switches": [],
    	"controllers": [],
    	"links": []
    }
    
    for host in net.hosts:
    	info["hosts"].append({
    	    "name": host.name,
    	    "ip": host.IP(),
    	    "mac": host.MAC()
    	})
    	
    for switch in net.switches:
    	info["switches"].append({
    	    "name": switch.name
    	})
    	
    for controller in net.controllers:
    	info["controllers"].append({
    	    "name": controller.name,
    	    "ip": controller.IP()
    	})
    	
    for link in net.links:
    	info["links"].append({
    	    "src": str(link.intf1),
    	    "dst": str(link.intf2)
    	})
    #return json.dumps(info, indent=2)
    return info
    
    
def save_mininet_info(mininet_info):
    
    with open('mininet_info.json', 'w') as infofile:
    	#infofile.write(mininet_info)
    	json.dump(mininet_info, infofile)
    

def collect_mininet_test_logs():

    #### Get basic info
    
    #Get hosts
    hosts = net.hosts
    
    """ Traffic test and actions should be customized in below section 
    according to topo design"""
    
    # Get host objects (should match your topo design)
    h1 = net.get('h1')
    h2 = net.get('h2')
        
    # Ping from h1 to h2
    ping_output = h1.cmd('ping -c 4', h2.IP())
    
    # Run iperf between h1 and h2
    h1.cmd('iperf -s &')
    iperf_output = h2.cmd('iperf -c',h1.IP(), '-t 10')

    
    # Store results in a dictionary format
    mininet_test_logs = {

	'ping_output': ping_output,
	'iperf_output': iperf_output,
    }

    return mininet_test_logs
    
def save_mininet_test_logs(mininet_test_logs):

    # Write results to a JSON file
    with open('mininet_test_results.json','w') as outfile:
    	json.dump(mininet_test_logs, outfile)



    
def collect_ryu_logs(controller_ip):

    flow_stats_list = []
    port_stats_list = []
    
    switches_url = 'http://{}:8080/stats/switches'.format(controller_ip)
    
    # Get datapath for count
    datapath_ids = requests.get(switches_url).json()
    
    for datapath_id in datapath_ids:
    	
    	flow_stats_url = 'http://{}:8080/stats/flow/{}'.format(controller_ip, datapath_id)
    	port_stats_url = 'http://{}:8080/stats/port/{}'.format(controller_ip, datapath_id)
    
    	# Collect flow statistics
    	flow_stats = requests.get(flow_stats_url).json()
    
    	# Collect port statistics
    	port_stats = requests.get(port_stats_url).json()
    	
    	flow_stats_list.append(flow_stats)
    	port_stats_list.append(port_stats)
    
    return flow_stats_list, port_stats_list
    

def save_ryu_logs(flow_stats_list, port_stats_list):
    
    with open('flow_stats_list.json', 'w') as flow_stats_file:
    	json.dump(flow_stats_list, flow_stats_file)

        
    with open('port_stats_list.json', 'w') as port_stats_file:
        json.dump(port_stats_list, port_stats_file)
        

if __name__ == '__main__':

    #Define Controller IP
    controller_ip = '127.0.0.1'

    #Start Ryu-Manager in the background
    print ("Starting Ryu-Manager...")
    ryu_cmd = "ryu-manager --verbose ryu.app.simple_switch_13 ryu.app.ofctl_rest"
    ryu_process = subprocess.Popen(ryu_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print ("Ryu-Manager Started...")
    sleep(5)
    
    #Start Mininet in parallel
    setLogLevel('info')
    topo = SingleSwitchTopo()
    c1 = RemoteController('c1', ip=controller_ip)
    net = Mininet(topo=topo, controller=c1)
    net.start()
    sleep(5)
    
    """function() can be called here.
    It is possible to add flows to swtiches automatically through additional function 
    with RYU API, before executing test and get logs"""
    
    print ("Collecting mininet info...")
    # Collect mininet basic info
    mininet_info = collect_mininet_info(net)
    
    # Save mininet basic info
    save_mininet_info(mininet_info)
    
    print ("Perform traffic test now...")
    # Traffic test and get mininet log function
    mininet_test_logs = collect_mininet_test_logs()
    
    print ("Collecting mininet logs...")
    # Write mininet log
    save_mininet_test_logs(mininet_test_logs)
    
    print ("Collecting switch logs from RYU API...")
    # Collect logs stats from Ryu
    flow_stats_list, port_stats_list = collect_ryu_logs(controller_ip)
    save_ryu_logs(flow_stats_list, port_stats_list)
    	
    # pause
    #CLI(net)

    # Clean up resources
    net.stop()
    ryu_process.terminate()
    os.system("sudo mn -c")
    
