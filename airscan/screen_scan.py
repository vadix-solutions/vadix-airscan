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

import time

class ScanScreen(Screen):
    vdx_dev_scanner = VdxDevScanner()
    vdx_mac_scanner = VdxMacScanner()
    vdx_http_scanner = VdxHttpScanner()

    pipeline_index = 0
    scan_data = {}
    report = {}

    def generate_report(self, _):
        try:
            current_step = self.scan_pipeline[self.pipeline_index]
        except IndexError:
            print("We're done")
            self.summarise_report()
            return 

        if self.progress_value >= current_step['progress']:
            required_func = current_step['func']
            print("Next percentage (%s), requires running: %s" % (current_step['progress'], required_func))
            if required_func:
                if current_step.get('arg_result'):
                    data = required_func(self.scan_data[current_step['arg_result']])
                else:
                    data = required_func()
                self.scan_data[current_step.get('name', current_step['progress'])] = data  
            self.pipeline_index += 1
            self.ids.status_label.text = current_step['text']
        
        self.progress_value += 1
        self.ids.progress_bar.value = self.progress_value
        self.update_progressbar_trigger()

    def summarise_report(self):
        source_data_df = {}
        for ip, port_scan in self.scan_data['ip_scan'].items():
            source_data_df[ip] = {
                'open_ports': port_scan
            }
            source_data_df[ip].update(self.scan_data['mac_scan'].get(ip, {}))
            source_data_df[ip].update(self.scan_data['http_scan'].get(ip, {}))
        App.get_running_app().report = source_data_df
        self.ids.progress_bar.value = 100
        self.parent.current = "result"
        print(cf_json(App.get_running_app().report))

    def on_enter(self, **kwargs):
        App.get_running_app().report = {}
        self.progress_value = 0
        self.pipeline_index = 0
        self.scan_data = {}
        
        print("I am in the scanning part on start")
        self.update_progressbar_trigger = Clock.create_trigger(self.generate_report)
        self.update_progressbar_trigger()

    scan_pipeline = [
        {
            'func': None, 
            'progress': 0,
            'text': 'Scanning network devices.. (this will take a minute)'
        },{
            'name': 'ip_scan',
            'func': vdx_dev_scanner.generate_report, 
            'progress': 15,
            'text': 'Inspecting network device hardware ID..'
        },{
            'name': 'mac_scan',
            'func': vdx_mac_scanner.generate_report, 
            'progress': 75,
            'arg_result': 'ip_scan',
            'text': 'Inspecting network device HTTP behavior..'
        },{
            'name': 'http_scan',
            'func': vdx_http_scanner.generate_report, 
            'arg_result': 'ip_scan',
            'progress': 90,
            'text': 'Reviewing results..'
        }
    ]