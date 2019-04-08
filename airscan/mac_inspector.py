from getmac import get_mac_address
from airscan_util import cf_json, banner
import pandas as pd


class Scanner(object):
    mac_vendor_url = "http://app.vadix.io/vendor.csv"
    _data = None

    def get_mac_vendor_data(self):
        if self._data is None:
            self._data = pd.read_csv(self.mac_vendor_url)
        return self._data

    def generate_report(self, ip_port_dataframe):
        vendor_data = self.get_mac_vendor_data()
        report_data = {}
        for ip, ip_report_data in ip_port_dataframe.iterrows():
            report_data[ip] = {}
            ip_mac_addr = get_mac_address(ip=ip)
            report_data[ip]['MAC'] = ip_mac_addr

            short_mac = "".join(ip_mac_addr.split(":")[:3]).upper()
            if short_mac in vendor_data.MAC.values:
                match = vendor_data.loc[vendor_data['MAC'] == short_mac]
                report_data[ip]['VendorMatch'] = match['VENDOR_NAME'].values[0]

        report_dataframe = pd.DataFrame(report_data).T
        report_dataframe = report_dataframe.fillna(False)
        return report_dataframe