from kivy.lang import Builder
from kivy.core.window import Window
from kivy.animation import Animation

from kivymd.app import MDApp

class appElementIDs():
	"""
	appElementIDs groups together all elements from the app into common lists. These lists can then be iterated through to set new colors when changing themes.
	"""
	def __init__(self):
		self.layouts = [
			'nav_bar_layout'
		]
		self.labels = [
		]
		self.buttons = [
			'nav_button_home',
			'nav_button_electricity',
			'nav_button_theme',
			'nav_button_settings',
			'nav_button_power',
			'nav_button_hvac',
			'nav_button_water',
			'nav_button_lights'
		]
		self.cards = []

class ironVanApp(MDApp):
	appIDs = appElementIDs()
	def build(self):

		# ---- Build Window ----
		Window.size = (700, 480)
		
		# ---- Build App Theme ----

		# Custom variables to hold color themes
		self.lightPrimary = 'Teal'
		self.darkPrimary = 'Teal'

		self.lightAccent = 'Gray'
		self.darkAccent = 'Amber'

		self.theme_cls.theme_style_switch_animation = True
		self.theme_cls.theme_style = 'Light'
		self.theme_cls.primary_palette = self.lightPrimary
		self.theme_cls.accent_palette = self.lightAccent

		return Builder.load_file('ironvan.kv')
	
	def switchTheme(self):

		self.theme_cls.theme_style = (
			'Dark' if self.theme_cls.theme_style == 'Light' else 'Light'
		)
		self.theme_cls.primary_palette = (
			self.darkPrimary if self.theme_cls.primary_palette == self.lightPrimary else self.lightPrimary
		)
		self.theme_cls.accent_palette = (
			self.darkAccent if self.theme_cls.accent_palette == self.lightAccent else self.lightAccent
		)

		for id in self.appIDs.layouts:
			self.root.ids[id].md_bg_color = (
				self.theme_cls.bg_darkest if self.theme_cls.theme_style == 'Light' else self.theme_cls.bg_light
			)
		for id in self.appIDs.buttons:
			print(id)
			self.root.ids[id].md_bg_color = (
				self.theme_cls.primary_light if self.theme_cls.theme_style == 'Light' else self.theme_cls.primary_dark
			)

	def navButtonRouter(self, id):

		otherButtons = self.appIDs.buttons[:]
		print(self.appIDs.buttons)
		otherButtons.remove(id)
		print(self.appIDs.buttons)

		animateButtonActive = Animation(
			pos_hint = {'center_x': 0.8},
			duration = 0.003
		)
		animateButtonActive += Animation(
			pos_hint = {'center_x': 0.87},
			duration = 0.006
		)
		animateButtonActive += Animation(
			pos_hint = {'center_x': 0.95},
			duration = 0.009
		)
		animateButtonActive += Animation(
			pos_hint = {'center_x': 1},
			duration = 0.012
		)

		animateButtonRetreat = Animation(
			pos_hint = {'center_x': 0.95},
			duration = 0.003
		)
		animateButtonRetreat += Animation(
			pos_hint = {'center_x': 0.87},
			duration = 0.006
		)
		animateButtonRetreat += Animation(
			pos_hint = {'center_x': 0.8},
			duration = 0.009
		)
		animateButtonRetreat += Animation(
			pos_hint = {'center_x': 0.7},
			duration = 0.012
		)
		
		animateButtonActive.start(self.root.ids[id])

		for otherID in otherButtons:
			if(self.root.ids[otherID].pos_hint['center_x'] != 0.7):
				animateButtonRetreat.start(self.root.ids[otherID])


ironVanApp().run()