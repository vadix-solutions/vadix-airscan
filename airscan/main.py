import kivy.app
import kivy.uix.boxlayout
import kivy.uix.textinput
import kivy.uix.label
import kivy.uix.button

from device_scanner import Scanner as VdxDevScanner
from mac_inspector import Scanner as VdxMacScanner
from http_inspector import Scanner as VdxHttpScanner
from airscan_util import cf_json, banner

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from screen_scan import ScanScreen
from screen_result import ResultScreen


class MainScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass


class Airscan(kivy.app.App):
    report = {}
    
    def build(self):
        pass
    
    def generate_report_real(self, progress_bar):
        
        progress_bar.value = 10

        df_lisening_ips = vdx_dev_scanner.generate_report()
        
        progress_bar.value = 50

        df_flagged_macs = vdx_mac_scanner.generate_report(df_lisening_ips)
        
        progress_bar.value = 70
        df_flagged_http = vdx_http_scanner.generate_report(df_lisening_ips)

        progress_bar.value = 90
        source_data_df = {}
        for ip, port_scan in df_lisening_ips.items():
            source_data_df[ip] = {
                'open_ports': port_scan
            }
            source_data_df[ip].update(df_flagged_macs.get(ip, {}))
            source_data_df[ip].update(df_flagged_http.get(ip, {}))

        print(cf_json(source_data_df))
        progress_bar.value = 100
        self.label.text = self.get_summary(source_data_df)
    
    def get_summary(self, source_data_df):
        ip_threats = {}
        for ip, results in source_data_df.items():
            threatlevel = 0
            if results.get('VendorMatch'):
                threatlevel += 1
            if max(results.get('open_ports', {}).values()):
                threatlevel += 1
            if results.get('HttpResponse'):
                threatlevel += 1
            if results.get('FlaggedResponse'):
                threatlevel += 1
            ip_threats[ip] = "(%s/%s) threats detected" % (threatlevel, 4)
        summary_text = "\n".join(["IP (%s): %s" % (ip, threattext) for ip, threattext in ip_threats.items()])
        return summary_text
            
if __name__ == "__main__":
    airscan = Airscan()
    airscan.run()
