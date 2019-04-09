import json
import time

import kivy.app
import kivy.uix.boxlayout
import kivy.uix.textinput
import kivy.uix.label
import kivy.uix.button

from kivy.clock import Clock
from kivy.app import App

from device_scanner import Scanner as VdxDevScanner
from mac_inspector import Scanner as VdxMacScanner
from http_inspector import Scanner as VdxHttpScanner
from airscan_util import cf_json, banner

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition


class ScanScreen(Screen):
    scan_data = {}

    port_scan_url_file = ("http://app.vadix.io/ports.json", "assets/ports.json")
    devices_url_file = ("http://app.vadix.io/devices.json", "assets/devices.json")
    

    def load_scanner(self, *args, **kwargs):
        self.known_devices = self._get_json_url_or_file(self.devices_url_file)
        self.target_ports = self._get_json_url_or_file(self.port_scan_url_file)

        self.vdx_dev_scanner = VdxDevScanner(self.target_ports)
        self.vdx_mac_scanner = VdxMacScanner()
        self.vdx_http_scanner = VdxHttpScanner()

    
    def _get_json_url_or_file(self, url_file):
        url, file_path = url_file
        try:
            print("Loading Json from URL: %s" % url)
            json_def = requests.get(url).json()
        except:
            print("Request failed, loading default file: %s" % file_path)
            with open(file_path, "r") as jf:
                json_def = json.load(jf)
        print("Returning: %s" % json_def)
        return json_def


    def on_enter(self, **kwargs):
        self.scan_data = {}
        self.load_scanner()
        self.generate_scan_pipeline()
        self.update_progressbar_trigger = Clock.create_trigger(self.run_pipeline)
        self.update_progressbar_trigger()


    def run_pipeline(self, _):
        current_step = self.scan_pipeline.pop(0) # get first element
        print("Running step: %s" % current_step)
        
        # Form the function call from pipeline data
        required_func = current_step['func']
        required_func(self.scan_data, 
            *current_step.get('args', []), **current_step.get('kwargs', {}))

        # Update the progress bar and status text
        self.ids.status_label.text = current_step['end_text']
        self.ids.progress_bar.value = current_step['progress']
        
        # Check if there are more tasks to run
        if len(self.scan_pipeline) > 0:
            self.update_progressbar_trigger()


    def filter_known_devices(self, source_data):
        print("Source data: %s" % source_data)
        detected_known_devices = {}
        for ip, ip_data in source_data.items():
            known_device = self.is_device_known(ip_data)
            if known_device:
                detected_known_devices[ip] = known_device

        print("Matched known devices: %s" % detected_known_devices)
        for ip, known_device in detected_known_devices.items():
            del(source_data[ip])
            source_data[known_device] = {}


    def is_device_known(self, ip_data):
        mac = ip_data.get('mac')
        open_ports = ip_data.get('open_ports', [])

        for device, device_heuristic in self.known_devices.items():
            heuristic_keys = device_heuristic.keys()
            # Test if a mac Address matches
            if mac and 'mac' in heuristic_keys:
                if not max([mac.startswith(vmac) for vmac in device_heuristic.get("mac")]):
                    continue
            # Test a port groups match
            if open_ports and 'open_ports' in heuristic_keys:
                if not max([sorted(open_ports) == sorted(dev_op) for dev_op in device_heuristic.get("open_ports")]):
                    continue
            # Must be known
            return device


    def prepare_report(self, source_data):
        report = {}
        for ip_addr, ip_data in source_data.items():
            report[ip_addr] = self.prepare_individual_report(ip_data)

        App.get_running_app().report = report
        # Bring us to the result screen
        self.parent.current = "result"


    def prepare_individual_report(self, ip_data):
        report = {
            'open_ports': len(ip_data.get('open_ports', [])) > 0,
            'known_mac_vendor': ip_data.get('known_mac_vendor', False),
            'http_response': len(ip_data.get('http', [])) > 0,
            'http_nvr_response': len(ip_data.get('http_nvr', [])) > 0
        }
        report['risk'] = sum(report.values())
        return report


    def generate_scan_pipeline(self):
        scan_pipeline = []
        scan_pipeline += self.vdx_dev_scanner.generate_pipeline_steps()
        scan_pipeline += self.vdx_mac_scanner.generate_pipeline_steps()
        scan_pipeline += self.vdx_http_scanner.generate_pipeline_steps()
        scan_pipeline += self.end_pipeline_steps

        # Insert progress percentage into each step object so run_pipeline can use it stateless
        for idx, el in enumerate(scan_pipeline):
            el['progress'] = (idx+1)/len(scan_pipeline) * 100

        self.scan_pipeline = scan_pipeline


    @property
    def end_pipeline_steps(self):
        return [
            {
                "func": self.filter_known_devices, 
                "end_text": "Filtered known devices"
            },{
                "func": self.prepare_report, 
                "end_text": "Prepared report"
            },
        ]
