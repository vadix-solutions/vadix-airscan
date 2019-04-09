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
        print("Filtering devices found")
        print(source_data)
        return source_data


    def prepare_report(self, source_data):
        report = {}
        print("Changing to result page")
        App.get_running_app().report = report
        print(source_data)
        self.parent.current = "result"


    def generate_scan_pipeline(self):
        scan_pipeline = []
        scan_pipeline += self.vdx_dev_scanner.generate_pipeline_steps()
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

    # scan_pipeline = [
    #     {
    #         'func': None, 
    #         'progress': 0,
    #         'text': 'Scanning network devices.. (this will take a minute)'
    #     },{
    #         'name': 'ip_scan',
    #         'func': vdx_dev_scanner.generate_report, 
    #         'progress': 15,
    #         'text': 'Inspecting network device hardware ID..'
    #     },{
    #         'name': 'mac_scan',
    #         'func': vdx_mac_scanner.generate_report, 
    #         'progress': 75,
    #         'arg_result': 'ip_scan',
    #         'text': 'Inspecting network device HTTP behavior..'
    #     },{
    #         'name': 'http_scan',
    #         'func': vdx_http_scanner.generate_report, 
    #         'arg_result': 'ip_scan',
    #         'progress': 90,
    #         'text': 'Reviewing results..'
    #     }
    # ]