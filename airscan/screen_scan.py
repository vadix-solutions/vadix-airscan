import os
import re
import importlib
from kivy.clock import Clock
from kivy.app import App

from kivy.uix.screenmanager import Screen
from scanners.base import BaseScanner


class ScanScreen(Screen, BaseScanner):
    scan_data = {}
    scanner_pattern = "scn([0-9]+)[A-z_]+"
    scanner_dir = "scanners"


    def on_enter(self, **kwargs):
        self.scan_data = {}
        self.generate_scanner_pipeline()
        self.update_progressbar_trigger = Clock.create_trigger(self.run_pipeline)
        self.update_progressbar_trigger()


    def load_scanners(self, *args, **kwargs):
        all_scndir_files = [
            os.path.splitext(file_name)[0]
            for file_name in os.listdir(self.scanner_dir)
        ]
        available_scanners = [
            file_name
            for file_name in all_scndir_files # for every file in dir
            if re.match(self.scanner_pattern, file_name) # if it looks like a scanner
        ]
        
        scanner_dictionary = {}
        for scn_p in available_scanners:
            module_name = "%s.%s" % (self.scanner_dir, scn_p)
            print("Loading scanner module: %s" % module_name)
            scanner_dictionary[scn_p] = importlib.import_module(module_name).Scanner()
        return scanner_dictionary    


    def generate_scanner_pipeline(self):
        scanner_dictionary = self.load_scanners()
        scanner_list = sorted(list(scanner_dictionary.keys()),
            key=lambda x: re.match(self.scanner_pattern, x).group(1)) # get the number from name
        print("Scanner module order: %s" % scanner_list)
        
        scan_pipeline = []
        for scanner_name in scanner_list:
            scan_pipeline += scanner_dictionary[scanner_name].generate_pipeline_steps()

        # Insert progress percentage into each step object so run_pipeline can use it stateless
        for idx, el in enumerate(scan_pipeline):
            el['progress'] = (idx+1)/len(scan_pipeline) * 100

        self.scan_pipeline = scan_pipeline


    ################################
    # (Re)called by Trigger
    # Required for app functionality
    ################################
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
        else:
            self.parent.current = "result"
