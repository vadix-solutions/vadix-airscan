import os
import sys
import json
import socket
import tempfile
import threading
import ipaddress
from datetime import datetime
from airscan_util import cf_json, banner
from netifaces import interfaces, ifaddresses, AF_INET


class Scanner(object):

    port_directory = {
        "webservice": [
            80,81,82,100,888,
            # 8080,8081,8083,
            # 443,3074,8443,
            # 9000,9901,30001,
            # 37777
        ],
        "RTSP": [
            554,
        ]
    }

    known_device_target = {
        "chromecast": [9000, 8443, 8008, 8009]
    }

    batch_size = 500
    timeout = 1     

    def _chunks(self, l, n):
        """Splits 'l' into a set of lists (max size 'n')"""
        chunks = []
        for i in range(0, len(l), n):
            chunks.append(l[i:i + n])
        return chunks
        
        
    def TCP_connect(self, target, port, output, timeout):
        """Execute a single TCP port test"""
        if target.split(".")[-1] in ['1', '254']:
            print("Skipping: %s" % target)
            return
        TCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCPsock.settimeout(timeout)
        try:
            try:
                ip = socket.gethostbyname(target)
            except socket.gaierror:
                print('Hostname could not be resolved: %s' % target)
            TCPsock.connect((ip, port))
            if not output.get(ip):
                output[ip] = {}
            output[ip][port] = True
        except socket.error as e:
            pass
        except Exception as e:
            print("Unexpected error: %s" % e)

        
    def scan_port(self, targets, port, batch_size, timeout):
        """Multi-threaded port scan""" 
        scan_result = {}
        # For each address:port combo, execute a batch of threads
        for chunked_targets in self._chunks(targets, batch_size):
            threads = []
            for target in chunked_targets:
                t = threading.Thread(target=self.TCP_connect, args=(target, port, scan_result, timeout))
                threads.append(t)

            # Starting threads
            for thread in threads:
                thread.start()

            # Locking the script until all threads complete
            for thread in threads:
                thread.join()
        return scan_result

    def run_scan(self, targets, port, batch_size, timeout):
        ###############
        # RUN PORT SCAN
        ###############
        banner("Please wait, scanning %s remote hosts on port %s" % (len(targets), port))
        scanner = Scanner()
        tstart = datetime.now()
        scan_result = scanner.scan_port(targets, port, batch_size, timeout)
        scan_duration = datetime.now() - tstart
        print('Scanning Completed in: %s' % (scan_duration))
        # Printing the information to screen
        print("Scan results: \n%s" % cf_json(scan_result))
        return scan_result

    def ip4_addresses(self):
        ip_list = []
        for interface in [i for i in interfaces() if i.startswith("e") or i.startswith("w")]:
            for inet_id, link in ifaddresses(interface).items():
                link = link[0]
                if inet_id == AF_INET:
                    print(link)
                    ip_list.append((link['addr'], link['netmask']))
        return ip_list

    def generate_report(self):
        report = {}
        ip_list = self.ip4_addresses()
        for ip_tuple in ip_list:
            ip_range = ipaddress.IPv4Network(ip_tuple, strict=False).with_prefixlen
            print("Scanning %s (%s connection batch, timeout=%s)" % (ip_range, self.batch_size, self.timeout))

            targets = []
            targets += [str(i) for i in ipaddress.IPv4Network(ip_range)]
            if len(targets) == 0:
                raise Exception("No targets for scan. Specify file or ip range using -h or -i")
            
            complete_directory = {**self.port_directory, **self.known_device_target}
            port_list = set([item for sublist in complete_directory.values() for item in sublist])
            
            for port in port_list:
                report.update(self.run_scan(targets, port, self.batch_size, self.timeout))

        report = self.prune_known_devices(report)
        return report

    def prune_known_devices(self, report_data):
        detected_devices = {}
        for ip_address, r in report_data.items():
            ports_open = [port for port, port_open in r.items() if port_open]
            print("Testing IP(%s): %s" % (ip_address, ports_open))
            for device_code, port_pattern in self.known_device_target.items():
                if set(ports_open) == set(port_pattern):
                    print("Found device (%s): %s" % (device_code, ip_address))
                    detected_devices[ip_address] = device_code
                    for port in ports_open:
                        report_data[ip_address][port] = False
                    break
        print("Detected devices: %s" % detected_devices)
        return report_data