import os
import sys
import json
import socket
import requests
import tempfile
import threading
import ipaddress
from datetime import datetime
from airscan_util import cf_json, banner
from netifaces import interfaces, ifaddresses, AF_INET


class Scanner(object):

    batch_size = 500
    timeout = 0.2   


    def __init__(self, target_ports, *args, **kwargs):
        self.port_scan_data = target_ports
        self.port_list = set([
            port for port_group in self.port_scan_data.values() 
            for port in port_group
        ])
        self._get_target_list()

    def _get_target_list(self):
        targets = []
        device_ip_list = self._get_local_ip4_addresses()
        for device_ip_tuple in device_ip_list:
            ip_range = ipaddress.IPv4Network(device_ip_tuple, strict=False).with_prefixlen
            targets += [str(i) for i in ipaddress.IPv4Network(ip_range)]
        self.targets = list(set(targets))


    def _chunks(self, l, n):
        """Splits 'l' into a set of lists (max size 'n')"""
        chunks = []
        for i in range(0, len(l), n):
            chunks.append(l[i:i + n])
        return chunks
        
        
    def TCP_connect(self, scan_data, target, port):
        """Execute a single TCP port test"""
        # Remove default router IPs
        if target.split(".")[-1] in ['1', '254']:
            return
        
        TCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCPsock.settimeout(self.timeout)
        
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            return

        try:
            TCPsock.connect((ip, port))
            if ip not in scan_data.keys():
                scan_data[ip] = {"open_ports": []}
            scan_data[ip]['open_ports'].append(port)
        except socket.error as e:
            pass
        except Exception as e:
            print("Unexpected error: %s" % e)

        
    def scan_port(self, scan_data, port):
        """Multi-threaded port scan""" 
        # For each address:port combo, execute a batch of threads
        for chunked_targets in self._chunks(self.targets, self.batch_size):
            threads = []
            for target in chunked_targets:
                t = threading.Thread(
                    target=self.TCP_connect, 
                    args=(scan_data, target, port))
                threads.append(t)

            # Starting threads
            for thread in threads:
                thread.start()

            # Locking the script until all threads complete
            for thread in threads:
                thread.join()


    def _get_local_ip4_addresses(self):
        ip_list = []
        for interface in [i for i in interfaces() if i.startswith("e") or i.startswith("w")]:
            for inet_id, link in ifaddresses(interface).items():
                link = link[0]
                if inet_id == AF_INET:
                    print(link)
                    ip_list.append((link['addr'], link['netmask']))
        return ip_list


    def generate_pipeline_steps(self):
        steps = []
        for port in sorted(self.port_list):
            steps.append({
                "func": self.scan_port, "args": [port], 
                "end_text": "Scanning network... (scanned port:%s)" % (port)
            })
        return steps
