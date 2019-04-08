import kivy.app
import kivy.uix.boxlayout
import kivy.uix.textinput
import kivy.uix.label
import kivy.uix.button

from device_scanner import Scanner as VdxDevScanner
from mac_inspector import Scanner as VdxMacScanner
from http_inspector import Scanner as VdxHttpScanner
from airscan_util import cf_json, banner


class SimpleApp(kivy.app.App):
	def build(self):
		self.label = kivy.uix.label.Label(text="Your Message.")
		self.button = kivy.uix.button.Button(text="Click Me.")
		self.button.bind(on_press=self.generate_report)
		
		self.boxLayout = kivy.uix.boxlayout.BoxLayout(orientation="vertical")
		self.boxLayout.add_widget(self.label)
		self.boxLayout.add_widget(self.button)
		
		return self.boxLayout
	
	def generate_report(self,btn):
		vdx_dev_scanner = VdxDevScanner()
		vdx_mac_scanner = VdxMacScanner()
		vdx_http_scanner = VdxHttpScanner()

		df_lisening_ips = vdx_dev_scanner.generate_report()
		df_flagged_macs = vdx_mac_scanner.generate_report(df_lisening_ips)
		df_flagged_http = vdx_http_scanner.generate_report(df_lisening_ips)

		source_data_df = {}
		for ip, port_scan in df_lisening_ips.items():
			source_data_df[ip] = {
				'open_ports': port_scan
			}
			source_data_df[ip].update(df_flagged_macs.get(ip, {}))
			source_data_df[ip].update(df_flagged_http.get(ip, {}))

		print(cf_json(source_data_df))
		self.label.text = str(source_data_df)
		
if __name__ == "__main__":
	simpleApp = SimpleApp()
	simpleApp.run()
