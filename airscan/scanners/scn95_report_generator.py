import time
from kivy.app import App
from scanners.base import BaseScanner

class Scanner(BaseScanner):

    def prepare_report(self, source_data):
        report = {}
        for ip_addr, ip_data in source_data.items():
            report[ip_addr] = self.prepare_individual_report(ip_data)
        
        print("Report data: %s" % self.cf_json(report))
        App.get_running_app().report = report

    def prepare_individual_report(self, ip_data):
        report = {
            'open_ports': len(ip_data.get('open_ports', [])) > 0,
            'known_mac_vendor': bool(ip_data.get('known_mac_vendor', False)),
            'http_response': len(ip_data.get('http', [])) > 0,
            'http_nvr_response': len(ip_data.get('http_nvr', [])) > 0
        }
        report['risk'] = sum(report.values())
        if report['known_mac_vendor']:
            report['name'] = ip_data.get('known_mac_vendor')
        return report

    def generate_pipeline_steps(self):
        steps = [{
            # HAHAHA this is such a dumb hack but I love how the pipeline works
            "func": lambda x: None,
            "end_text": "Preparing Report.."
            },{
            "func": lambda x, s: time.sleep(s), "args": [0.5],
            "end_text": "Sleeping"
            },{
            "func": self.prepare_report,
            "end_text": "Prepared report"
        }]
        return steps
