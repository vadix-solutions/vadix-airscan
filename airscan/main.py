import kivy.app
import kivy.uix.boxlayout
import kivy.uix.textinput
import kivy.uix.label
import kivy.uix.button


class SimpleApp(kivy.app.App):
	def build(self):
		self.textInput = kivy.uix.textinput.TextInput()
		
		self.label = kivy.uix.label.Label(text="Your Message.")
		self.button = kivy.uix.button.Button(text="Click Me.")
		self.button.bind(on_press=self.displayMessage)
		
		self.boxLayout = kivy.uix.boxlayout.BoxLayout(orientation="vertical")
		self.boxLayout.add_widget(self.textInput)
		self.boxLayout.add_widget(self.label)
		self.boxLayout.add_widget(self.button)
		
		return self.boxLayout
		
	def displayMessage(self, btn):
		self.label.text = self.textInput.text

if __name__ == "__main__":
	simpleApp = SimpleApp()
	simpleApp.run()