import json
from kivy.app import App
from airscan_util import cf_json, banner
from pygments import lexers
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image

from kivy.animation import Animation

class ResultScreen(Screen):
    headers = ['Device IP', 'Open Ports', 'Vendor', 'Listening', 'Server']
    report_attr = ['open_ports', 'known_mac_vendor', 'http_response', 'http_nvr_response']

    cell_kwargs = {'size_hint_x':.18}

    def on_enter(self, **kwargs):
        # data_report = App.get_running_app().report
        data_report = {
            '192.168.0.200': {
                'open_ports': True, 'known_mac_vendor': False, 
                'http_response': True, 'http_nvr_response': False, 'risk': 2}, 
            '192.168.0.59': {
                'open_ports': True, 'known_mac_vendor': False, 
                'http_response': False, 'http_nvr_response': False, 'risk': 1}
        }
        self.render_summary(data_report)
        self.render_summary_grid(data_report)
        self.fade_in()
        # self.render_advanced_raw(data_report)

    def fade_in(self):
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.ids.summary_main)

    def render_summary(self, data_report):
        highest_risk = max([v['risk'] for v in data_report.values()])
        
        summary_image = 'assets/success.png'
        summary_text = 'You are safe!'
        summary_subtext = 'No suspicious devices were found on network.'
        
        if highest_risk <= 2:
            summary_image = 'assets/warning.png'
            summary_text = 'Some activity found.'
            summary_subtext = 'Some active devices found on your network, but they are not likely to be malicious.'
        else:
            summary_image = 'assets/danger.png'
            summary_text = 'You are at risk.'
            summary_subtext = 'One or more suspicious devices were found on your network.'

        self.ids.summary_image.source = summary_image
        self.ids.summary_string.text = summary_text
        self.ids.summary_substring.text = summary_subtext

    def render_summary_grid(self, data_report):
        layout = self.ids.summary_grid
        layout.clear_widgets()
        
        for header in self.headers:
            layout.add_widget(Button(text=header, disabled=True, **self.cell_kwargs))
        
        for ip, ip_report in sorted(data_report.items(), 
                                         key=lambda kv: kv[1]['risk']):
            layout.add_widget(Label(text=ip, **self.cell_kwargs))
            for key in self.report_attr:
                cond_passed = ip_report[key]
                if cond_passed:
                    image_source = 'assets/success.png' 
                else: 
                    image_source = 'assets/warning.png'
                layout.add_widget(Image(source=image_source, **self.cell_kwargs))

 
    # def render_advanced_raw(self, data_report):
    #     result_text = json.dumps(data_report, 
    #         indent=4, sort_keys=True)
    #     lx = lexers.get_lexer_by_name('json')
    #     self.ids.result_panel.lexer = lx
    #     self.ids.result_panel.text = result_text
