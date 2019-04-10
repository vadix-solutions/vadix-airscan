import re
import requests

from scanners.base import BaseScanner

class Scanner(BaseScanner):
    mac_vendor_url = "http://app.vadix.io/vendor.csv"
    arp_file = "/proc/net/arp"

    _data = None

    def get_mac_vendor_data(self):
        # ToDo: Read this data like the target and port definitions in screen_scan.py 
        # Do not load it here in this module
        # Also, use JSON in next file def
        mac_table = {}
        if self._data is None:
            self._data = requests.get(self.mac_vendor_url).text
        for t in self._data.splitlines():
            mac, ven = t.split(',')
            mac_table[mac] = ven
        return mac_table

    def get_arp_data(self):
        with open(self.arp_file, "r") as f:
            arp_data = f.read()
            arp_data = re.sub(' +', ' ', arp_data) # Merge spaces

        mac_records = {}
        for r in arp_data.splitlines():
            try:
                ip, hw, flag, mac_address, mask, device = r.split(" ")
                if device.startswith("e") or device.startswith("w"):
                    if mac_address != '00:00:00:00:00:00':
                        mac_records[ip] = mac_address 
            except:
                pass
        return mac_records

    def get_mac_addresses(self, source_data):
        device_arp_table = self.get_arp_data()
        vendor_data = self.get_mac_vendor_data()
        for ip, ip_data in source_data.items():
            ip_mac_addr = device_arp_table.get(ip)
            source_data[ip]['mac'] = ip_mac_addr
            if ip_mac_addr:
                short_mac = "".join(ip_mac_addr.split(":")[:3]).upper()
                source_data[ip]['known_mac_vendor'] = vendor_data.get(short_mac, False)

    def generate_pipeline_steps(self):
        steps = []
        steps.append({
            "func": self.get_mac_addresses,
            "end_text": "Retrieved MAC addresses"
        })
        return steps
