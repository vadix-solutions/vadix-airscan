import re
import csv
import requests
from airscan_util import cf_json, banner


class Scanner(object):
    mac_vendor_url = "http://app.vadix.io/vendor.csv"
    arp_file = "/proc/net/arp"

    _data = None

    def get_mac_vendor_data(self):
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

    def generate_report(self, ip_port_dataframe):
        device_arp_table = self.get_arp_data()
        vendor_data = self.get_mac_vendor_data()
        report_data = {}
        for ip, ip_report_data in ip_port_dataframe.items():
            report_data[ip] = {}
            ip_mac_addr = device_arp_table.get(ip)
            report_data[ip]['MAC'] = ip_mac_addr
            if ip_mac_addr:
                short_mac = "".join(ip_mac_addr.split(":")[:3]).upper()
                report_data[ip]['VendorMatch'] = vendor_data.get(short_mac)
        print(report_data)
        return report_data