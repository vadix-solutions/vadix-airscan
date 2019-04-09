import json
from kivy.app import App
from airscan_util import cf_json, banner
from pygments import lexers
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import BooleanProperty

class ResultScreen(Screen):
    isShownMenu = BooleanProperty(True)
    atRisk = BooleanProperty(False)

    headers = ['Device IP', 'Open Ports', 'Vendor', 'Listening', 'Server']
    cell_kwargs = {'size_hint_x':.18}

    def on_enter(self, **kwargs):
        data_report = App.get_running_app().report
        self.render_summary_grid(data_report)
        self.render_advanced_raw(data_report)

    def render_summary_grid(self, data_report):
        self.atRisk = False
        layout = self.ids.summary_grid
        layout.clear_widgets()
        
        summary_report = {}
        for ip, result_data in data_report.items():
            summary_report[ip] = [
                max(list(result_data['open_ports'].values())),
                int(result_data.get('VendorMatch') is not None),
                int(result_data.get('HttpResponse', False)),
                int(result_data.get('FlaggedResponse', False)),
            ]
            if max(summary_report[ip]):
                self.atRisk = True
        
        for header in self.headers:
            layout.add_widget(Button(text=header, disabled=True, **self.cell_kwargs))
        
        for ip, summary_report in sorted(summary_report.items(), 
            key=lambda kv: sum(kv[1])):
            layout.add_widget(Label(text=ip, **self.cell_kwargs))

            for cond_passed in summary_report:
                image_source = 'assets/warning.png' if cond_passed else 'assets/success.png'
                layout.add_widget(Image(source=image_source, **self.cell_kwargs))


 
    def render_advanced_raw(self, data_report):
        result_text = json.dumps(data_report, 
            indent=4, sort_keys=True)
        lx = lexers.get_lexer_by_name('json')
        self.ids.result_panel.lexer = lx
        self.ids.result_panel.text = result_text
