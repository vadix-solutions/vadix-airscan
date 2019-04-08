import kivy.app
import kivy.uix.boxlayout
import kivy.uix.textinput
import kivy.uix.label
import kivy.uix.button
import dfgui
import pandas as pd

from device_scanner import Scanner as VdxDevScanner
from mac_inspector import Scanner as VdxMacScanner
from http_inspector import Scanner as VdxHttpScanner


class SimpleApp(kivy.app.App):
	def build(self):
		self.textInput = kivy.uix.textinput.TextInput()
		
		self.label = kivy.uix.label.Label(text="Your Message.")
		self.button = kivy.uix.button.Button(text="Click Me.")
		self.button.bind(on_press=self.generate_report)
		
		self.boxLayout = kivy.uix.boxlayout.BoxLayout(orientation="vertical")
		self.boxLayout.add_widget(self.textInput)
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
		source_data_df = pd.concat([
			df_lisening_ips,
			df_flagged_macs,
			df_flagged_http,
		], axis=1)
		print(source_data_df)
		self.label.text = str(source_data_df)
		# report_dataframe = self.summarise_data(source_data_df)

		# dfgui.show(source_data_df)
		
	def displayMessage(self, btn):
		self.label.text = self.textInput.text

if __name__ == "__main__":
	simpleApp = SimpleApp()
	simpleApp.run()
