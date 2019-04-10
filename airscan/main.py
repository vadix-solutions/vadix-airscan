import kivy.app
import kivy.uix.boxlayout
import kivy.uix.textinput
import kivy.uix.label
import kivy.uix.button

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from screen_scan import ScanScreen
from screen_result import ResultScreen

class MainScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

class Airscan(kivy.app.App):
    report = {}
    scan_data = {}

    def build(self):
        pass
            
if __name__ == "__main__":
    airscan = Airscan()
    airscan.run()
