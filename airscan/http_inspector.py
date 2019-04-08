import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from airscan_util import cf_json, banner
import pandas as pd


class Scanner(object):
    target_word = 'NVR'

    def get_session(self):
        s = requests.Session()
        retries = Retry(total=1,
                        status_forcelist=[ 500, 502, 503, 504 ])
        s.mount('http://', HTTPAdapter(max_retries=retries))
        return s

    def generate_report(self, ip_port_dataframe):
        sess = self.get_session()
        report_data = {}
        
        for ip_addr, open_ports in ip_port_dataframe.iterrows():
            for port_number, is_port_open in open_ports.to_dict().items():
                report_data[ip_addr] = {}
                url = "http://%s:%s" % (ip_addr, port_number)
                print("Testing HTTP from %s" % (url))
                try:
                    url_res = sess.get(url, timeout=0.1)
                    url_res.raise_for_status()
                except Exception as err:
                    continue
                if url_res.ok:
                    print("Valid Response!")
                    report_data[ip_addr]['HttpResponse'] = True
                    if self.target_word in url_res.text + str(url_res.headers):
                        print("%s in text" % self.target_word)
                        report_data[ip_addr]['FlaggedResponse'] = True

        report_dataframe = pd.DataFrame(report_data).T
        report_dataframe = report_dataframe.fillna(False)
        return report_dataframe