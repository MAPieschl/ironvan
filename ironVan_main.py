from kivy.lang import Builder
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import StringProperty
from kivy.config import Config
from kivy.clock import Clock
from functools import partial

from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton, MDRoundFlatButton
from kivymd.uix.dialog import MDDialog

import ironVan_log as ivLog
import ironVan_bus as ivBus
import ironVan_weather as weather

import time

class appElementIDs():
	"""
	appElementIDs groups together all elements from the app into common lists. These lists can then be iterated through to set new colors when changing themes.
	"""
	def __init__(self):
		self.layouts = [
			'nav_bar_layout'
		]
		self.labels = [
			'fresh_water_label',
			'grey_water_label'
		]
		self.buttons = [
			'nav_button_home',
			'nav_button_bemu',
			'nav_button_theme',
			'nav_button_settings',
			'nav_button_power',
			'nav_button_env',
			'nav_button_ws',
			'nav_button_ls'
		]
		self.toggles = [
			'env_fan_quick_switch',
			'env_cool_quick_switch',
			'env_heat_quick_switch',
			'ws_pump_switch',
			'ws_heater_switch',
			'ls_1_quick_switch',
			'ls_2_quick_switch',
			'ls_3_quick_switch',
			'ls_4_quick_switch',
			'ls_1_switch',
			'ls_2_switch',
			'ls_3_switch',
			'ls_4_switch'
		]
		self.cards = [
			'weather_quick_card',
			'time_quick_card',
			'bemu_quick_card',
			'ws_quick_card',
			'ls_quick_card',
			'bemu_home_card',
			'env_home_card',
			'ws_home_card',
			'ls_home_card',
			'settings_home_card'
		]
		self.icons = [
			'nav_button_home',
			'nav_button_bemu',
			'nav_button_theme',
			'nav_button_settings',
			'nav_button_power',
			'nav_button_env',
			'nav_button_ws',
			'nav_button_ls',
			'env_fan_quick_switch',
			'env_cool_quick_switch',
			'env_heat_quick_switch',
			'fresh_water_icon_75',
			'fresh_water_icon_50',
			'fresh_water_icon_25',
			'fresh_water_icon_0',
			'fresh_to_pump_line',
			'ws_pump_switch',
			'ws_heater_switch',
			'pump_to_grey_line',
			'grey_water_icon_75',
			'grey_water_icon_50',
			'grey_water_icon_25',
			'grey_water_icon_0',
			'ls_1_quick_switch',
			'ls_2_quick_switch',
			'ls_3_quick_switch',
			'ls_4_quick_switch',
			'ls_1_switch',
			'ls_2_switch',
			'ls_3_switch',
			'ls_4_switch',
		]

class EnvFanToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'fan_low_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		print(value)
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				print(self.value)
				if self.value == 'fan_low_off':
					print('Turning on...')
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command[self.value]
					)
					print('Command sent...')
					self.value = 'fan_low_auto'
					self.md_bg_color = self.app.toggleOn
					print('Success!')
				else:
					print('Turning off...')
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command[self.value]
					)
					print('Command sent...')
					self.value = 'fan_low_off'
					self.md_bg_color = self.app.toggleOff
					print('Success!')
			except KeyError:
					self.app.noDeviceFound_dialog('Fan')

class EnvCoolToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'ac_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ac_off':
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command[self.value]
					)
					self.value = 'ac_on'
					self.md_bg_color = self.app.toggleOn
				else:
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command[self.value]
					)
					self.value = 'ac_off'
					self.md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Air conditioner')

class EnvHeatToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'heat_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'heat_off':
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command[self.value]
					)
					self.value = 'heat_on'
					self.md_bg_color = self.app.toggleOn
				else:
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command[self.value]
					)
					self.value = 'heat_off'
					self.md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Heat pump')

class WSPumpToggleButton(ToggleButtonBehavior, MDFillRoundFlatButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'water_pump_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'water_pump_off':
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command[self.value]
					)
					self.value = 'water_pump_auto'
					self.md_bg_color = self.app.toggleOn
				else:
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command[self.value]
					)
					self.value = 'water_pump_off'
					self.md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Water pump')

	def set_disabled(self, disabled):
		self.disabled = disabled

class WSHeaterToggleButton(ToggleButtonBehavior, MDFillRoundFlatButton):
	off = StringProperty('water_heater_off')
	auto = StringProperty('water_heater_auto')

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'water_heater_off'
		self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			if self.value == 'water_heater_off':
				self.value = 'water_heater_on'
				self.md_bg_color = self.app.toggleOn
			else:
				self.value = 'water_heater_off'
				self.md_bg_color = self.app.toggleOff

	def set_disabled(self, disabled):
		self.disabled = disabled

class DiningLightToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'ls_1_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ls_1_off':
					command = self.app.bus.activeDevices['lighting'].command['ls_1_toggle'][:]
					command.append(int(self.app.root.ids['ls_1_slider'].value))
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.value = 'ls_1_on'
					self.app.root.ids['ls_1_switch'].md_bg_color = self.app.toggleOn
					self.app.root.ids['ls_1_quick_switch'].md_bg_color = self.app.toggleOn
				else:
					command = self.app.bus.activeDevices['lighting'].command['ls_1_toggle'][:]
					command.append(0)
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.value = 'ls_1_off'
					self.app.root.ids['ls_1_switch'].md_bg_color = self.app.toggleOff
					self.app.root.ids['ls_1_quick_switch'].md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Dining room light')

	def set_disabled(self, disabled):
		self.disabled = disabled

class BedroomLightToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'ls_2_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ls_2_off':
					command = self.app.bus.activeDevices['lighting'].command['ls_2_toggle'][:]
					command.append(int(self.app.root.ids['ls_2_slider'].value))
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.value = 'ls_2_on'
					self.app.root.ids['ls_2_switch'].md_bg_color = self.app.toggleOn
					self.app.root.ids['ls_2_quick_switch'].md_bg_color = self.app.toggleOn
				else:
					command = self.app.bus.activeDevices['lighting'].command['ls_2_toggle'][:]
					command.append(0)
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.value = 'ls_2_off'
					self.app.root.ids['ls_2_switch'].md_bg_color = self.app.toggleOff
					self.app.root.ids['ls_2_quick_switch'].md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Bedroom light')

	def set_disabled(self, disabled):
		self.disabled = disabled

class KitchenLightToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'ls_3_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ls_3_off':
					command = self.app.bus.activeDevices['lighting'].command['ls_3_toggle'][:]
					command.append(int(self.app.root.ids['ls_3_slider'].value))
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.value = 'ls_3_on'
					self.app.root.ids['ls_3_switch'].md_bg_color = self.app.toggleOn
					self.app.root.ids['ls_3_quick_switch'].md_bg_color = self.app.toggleOn
				else:
					command = self.app.bus.activeDevices['lighting'].command['ls_3_toggle'][:]
					command.append(0)
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.value = 'ls_3_off'
					self.app.root.ids['ls_3_switch'].md_bg_color = self.app.toggleOff
					self.app.root.ids['ls_3_quick_switch'].md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Kitchen light')

	def set_disabled(self, disabled):
		self.disabled = disabled

class BathroomLightToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'ls_4_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ls_4_off':
					command = self.app.bus.activeDevices['lighting'].command['ls_4_toggle'][:]
					command.append(int(self.app.root.ids['ls_4_slider'].value))
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.value = 'ls_4_on'
					self.app.root.ids['ls_4_switch'].md_bg_color = self.app.toggleOn
					self.app.root.ids['ls_4_quick_switch'].md_bg_color = self.app.toggleOn
				else:
					command = self.app.bus.activeDevices['lighting'].command['ls_4_toggle'][:]
					command.append(0)
					self.app.bus.send(
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.value = 'ls_4_off'
					self.app.root.ids['ls_4_switch'].md_bg_color = self.app.toggleOff
					self.app.root.ids['ls_4_quick_switch'].md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Bathroom light')

	def set_disabled(self, disabled):
		self.disabled = disabled

class SettingsHomeScreen(Screen):
	pass

class LSHomeScreen(Screen):
	pass

class WSHomeScreen(Screen):
	pass

class EnvHomeScreen(Screen):
	pass

class BEMUHomeScreen(Screen):
	pass

class AppHomeScreen(Screen):
	pass

class PageManager(ScreenManager):
	pass

class ironVanApp(MDApp):

	appIDs = appElementIDs()
	log = ivLog.Log()
	bus = ivBus.Bus(log)

	location = weather.Location()
	weather = weather.Weather()

	def build(self):

		# ---- Build Window ----
		Config.set('graphics', 'resizable', True)
		# Note:  When uncommenting Window.fullscreen, ensure to delete comment out `size: (700, 480)` in the .kv file.
		Window.fullscreen = 'auto'
		
		# ---- Build App Theme ----

		# Custom variables to hold color themes
		self.lightPrimary = 'Teal'
		self.darkPrimary = 'Teal'

		self.lightAccent = 'BlueGray'
		self.darkAccent = 'BlueGray'

		self.theme_cls.theme_style_switch_animation = True
		self.theme_cls.theme_style = 'Light'
		self.theme_cls.primary_palette = self.lightPrimary
		self.theme_cls.accent_palette = self.lightAccent
		self.theme_cls.accent_light_hue = '300'
		self.theme_cls.accent_dark_hue = '800'

		# Master reset for allowing button presses - used globally for debouncing
		# Note:  every button that uses buttonReset MUST reset self.buttonReset after use

		# Button delay is the standard delay used globally for all button debouncing
		self.buttonDelay = 0.25
		self.buttonReset = time.time() + self.buttonDelay

		self.toggleOn = self.theme_cls.primary_light
		self.toggleOff = self.theme_cls.accent_light

		# All pop-up windows must be instantiated under the self.dialogBox object to ensure that dialog boxes do not stack
		self.dialogBox = None

		self.location.getLocation(self)
		Clock.schedule_interval(partial(self.weather.getWeather, self), 10)

		# Initialize bus scan
		# if(len(self.bus.activeDevices) != 0):
		# 	Clock.schedule_interval(self.bus.regularScan, 1)
		# 	Clock.schedule_interval(self.bus.parseResponses, 1)

		return Builder.load_file('ironvan.kv')
	
	def switchTheme(self):
		if time.time() < self.buttonReset: return
		self.buttonReset = time.time() + self.buttonDelay

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

		for id in self.appIDs.labels:
			self.root.ids[id].text_color = (
				self.theme_cls.accent_dark if self.theme_cls.theme_style == 'Light' else self.theme_cls.accent_light
			)

		for id in self.appIDs.buttons:
			self.root.ids[id].md_bg_color = (
				self.theme_cls.primary_light if self.theme_cls.theme_style == 'Light' else self.theme_cls.primary_dark
			)
		
		# Set future changes of toggle state to new theme
		if self.theme_cls.theme_style == 'Light':
			self.toggleOn = self.theme_cls.primary_light
			self.toggleOff = self.theme_cls.accent_light
		else:
			self.toggleOn = self.theme_cls.primary_dark
			self.toggleOff = self.theme_cls.accent_dark

		# Set current state of toggle to new theme
		for id in self.appIDs.toggles:
			if self.theme_cls.theme_style == 'Light':
				if 'off' in self.root.ids[id].value:
					self.root.ids[id].md_bg_color = self.theme_cls.accent_light
				else:
					self.root.ids[id].md_bg_color = self.theme_cls.primary_light
			else:
				if 'off' in self.root.ids[id].value:
					self.root.ids[id].md_bg_color = self.theme_cls.accent_dark
				else:
					self.root.ids[id].md_bg_color = self.theme_cls.primary_dark
				
		for id in self.appIDs.cards:
			self.root.ids[id].md_bg_color = (
				self.theme_cls.bg_darkest if self.theme_cls.theme_style == 'Light' else self.theme_cls.bg_light
			)
			
		for id in self.appIDs.icons:
			if self.theme_cls.theme_style == 'Light':
				if self.root.ids[id].text_color == self.theme_cls.primary_dark:
					self.root.ids[id].text_color = self.theme_cls.primary_light
				else:
					self.root.ids[id].text_color = self.theme_cls.accent_dark
			else:
				if self.root.ids[id].text_color == self.theme_cls.primary_light:
					self.root.ids[id].text_color = self.theme_cls.primary_dark
				else:
					self.root.ids[id].text_color = self.theme_cls.accent_light


	def navButtonRouter(self, id):

		# Copy list of navigation buttons to identify !ids
		otherButtons = self.appIDs.buttons[:]
		otherButtons.remove(id)

		# Create animation for the active button (pop-out)
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

		# Create animation for the retreating button (slide-in)
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
		
		# Call animations to pop-out or slide-in buttons
		animateButtonActive.start(self.root.ids[id])

		lastPage = None
		for otherID in otherButtons:
			if(self.root.ids[otherID].pos_hint['center_x'] != 0.7):
				animateButtonRetreat.start(self.root.ids[otherID])
				lastPage = otherID
				
		match id:
			case 'nav_button_home':
				self.root.ids.page_manager.current = 'app_home_page'
			
			case 'nav_button_bemu':
				self.root.ids.page_manager.current = 'bemu_home_page'
			
			case 'nav_button_env':
				self.root.ids.page_manager.current = 'env_home_page'
			
			case 'nav_button_ws':
				self.root.ids.page_manager.current = 'ws_home_page'
			
			case 'nav_button_ls':
				self.root.ids.page_manager.current = 'ls_home_page'
			
			case 'nav_button_settings':
				self.root.ids.page_manager.current = 'settings_home_page'

	def lightingAdjust(self, *args):
		value = args[1]
		sliderID = args[2]
		
		try:
			match sliderID:
				case 'ls_1_slider':
					command = self.bus.activeDevices['lighting'].command['ls_1_toggle'][:]
				case 'ls_2_slider':
					command = self.bus.activeDevices['lighting'].command['ls_2_toggle'][:]
				case 'ls_3_slider':
					command = self.bus.activeDevices['lighting'].command['ls_3_toggle'][:]
				case 'ls_4_slider':
					command = self.bus.activeDevices['lighting'].command['ls_4_toggle'][:]
				case _:
					print('Error processing lightingAdjust()')
					return
			
			command.append(int(self.root.ids[sliderID].value))
			self.bus.send(
			'command',
			self.bus.activeDevices['lighting'].address,
			command
			)
		except KeyError:
			self.noDeviceFound_dialog('Light')

	
	# ---- Dialob Boxes ----

	def noDeviceFound_dialog(self, deviceName):
		if(self.dialogBox == None):
			self.dialogBox = MDDialog(
				text = f'{deviceName} is not responding.',
				buttons = [
					MDRoundFlatButton(
						text = 'Dismiss',
						on_release = self.closeDialogBox
					),
					MDFillRoundFlatButton(
						text = 'Troubleshoot',
					)],
			)
			self.dialogBox.open()

	def generalError_dialog(self, msg):
		'''
		The 'general error' dialog box does not offer troubleshooting capabilities. Provide a message as the parameter and an 'Ok' button will close the dialog box.
		'''
		if not self.dialogBox:
			self.dialogBox = MDDialog(
				text = f'{msg}',
				buttons = [
					MDFillRoundFlatButton(
						text = 'Ok',
						on_release = self.closeDialogBox
					)
				]
			)
			self.dialogBox.open()

	def closeDialogBox(self, obj):
		self.dialogBox.dismiss()
		self.dialogBox = None

ironVanApp().run()