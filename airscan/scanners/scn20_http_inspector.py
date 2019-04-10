import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from scanners.base import BaseScanner


class Scanner(BaseScanner):
    target_word = 'NVR'

    def get_session(self):
        s = requests.Session()
        retries = Retry(total=1,
                        status_forcelist=[ 500, 502, 503, 504 ])
        s.mount('http://', HTTPAdapter(max_retries=retries))
        return s

    def inspect_http(self, source_data):
        # ToDo: Make this threaded like the port_scanner
        sess = self.get_session()
        
        for ip_addr, ip_data in source_data.items():
            for port_number in ip_data['open_ports']:
                url = "http://%s:%s" % (ip_addr, port_number)
                try:
                    url_res = sess.get(url, timeout=0.1)
                    url_res.raise_for_status()
                except Exception as err:
                    continue
                if url_res.ok:
                    if 'http' not in source_data[ip_addr].keys():
                        source_data[ip_addr]['http'] = []
                    source_data[ip_addr]['http'].append(url)

                    if 'http_nvr' not in source_data[ip_addr].keys():
                        source_data[ip_addr]['http_nvr'] = []
                    if self.target_word in url_res.text + str(url_res.headers):
                        source_data[ip_addr]['http_nvr'].append(url)


    def generate_pipeline_steps(self):
        steps = []
        steps.append({
            "func": self.inspect_http,
            "end_text": "Inspected HTTP responses"
        })
        return steps
