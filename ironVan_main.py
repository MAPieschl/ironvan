from kivy.lang import Builder
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import StringProperty, ObjectProperty
from kivy.config import Config
from kivy.clock import Clock
from functools import partial

from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton, MDRoundFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivymd.uix.textfield import MDTextField
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.label import MDLabel

import ironVan_log as ivLog
import ironVan_bus as ivBus
import ironVan_weather as weather
import ironVan_wifi as network
import ironVan_settings as settings

import time
import subprocess
import threading

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
			'grey_water_label',
			'settings_user_settings_title_icon',
			'settings_user_settings_title',
			'settings_user_settings_temp_select_label',
			'settings_user_settings_time_select_label',
			'settings_user_settings_brightness_select_label'
		]
		self.navButtons = [
			'nav_button_home',
			'nav_button_bemu',
			'nav_button_theme',
			'nav_button_settings',
			'nav_button_power',
			'nav_button_env',
			'nav_button_ws',
			'nav_button_ls'
		]
		self.buttons = [
			'settings_user_settings_button_back',
			'user_settings_button'
		]
		self.switches = [
			'env_fan_quick_switch',
			'env_cool_quick_switch',
			'env_heat_quick_switch',
			'wifi_quick_switch',
			'ble_quick_switch',
			'ws_pump_quick_switch',
			'ws_heater_quick_switch',
			'ws_pump_switch',
			'ws_heater_switch',
			'shower_fan_switch',
			'tank_heater_switch',
			'tank_valve_switch',
			'ls_1_quick_switch',
			'ls_2_quick_switch',
			'ls_3_quick_switch',
			'ls_4_quick_switch',
			'ls_1_switch',
			'ls_2_switch',
			'ls_3_switch',
			'ls_4_switch'
		]
		self.toggles = [
			'celsius_toggle',
			'fahrenheit_toggle',
			'hour12_toggle',
			'hour24_toggle'
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
			'settings_home_card',
			'settings_user_settings_card'
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
			'wifi_quick_switch',
			'fresh_water_quick_icon_75',
			'fresh_water_quick_icon_50',
			'fresh_water_quick_icon_25',
			'fresh_water_quick_icon_0',
			'quick_fresh_to_pump_line',
			'ws_pump_quick_switch',
			'ws_heater_quick_switch',
			'quick_pump_to_grey_line',
			'grey_water_quick_icon_75',
			'grey_water_quick_icon_50',
			'grey_water_quick_icon_25',
			'grey_water_quick_icon_0',
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
			'shower_fan_switch',
			'tank_heater_switch',
			'tank_valve_switch',
			'ls_1_quick_switch',
			'ls_2_quick_switch',
			'ls_3_quick_switch',
			'ls_4_quick_switch',
			'ls_1_switch',
			'ls_2_switch',
			'ls_3_switch',
			'ls_4_switch',
		]
		self.keys = [
			'one_key',
			'two_key',
			'three_key',
			'four_key',
			'five_key',
			'six_key',
			'seven_key',
			'eight_key',
			'nine_key',
			'zero_key',
			'q_key',
			'w_key',
			'e_key',
			'r_key',
			't_key',
			'y_key',
			'u_key',
			'i_key',
			'o_key',
			'p_key',
			'a_key',
			's_key',
			'd_key',
			'f_key',
			'g_key',
			'h_key',
			'j_key',
			'k_key',
			'l_key',
			'z_key',
			'x_key',
			'c_key',
			'v_key',
			'b_key',
			'n_key',
			'm_key',
			'shift_key',
			'back_key',
			'symbol_key',
			'space_key',
			'done_key'
		]

class EnvFanToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'fan_high_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'fan_high_off':
					print(f'Turning high fan on')
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command['fan_high_on']
					)
					self.value = 'fan_high_on'
					self.md_bg_color = self.app.toggleOn
				else:
					print('Turning high fan off')
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command['fan_high_off']
					)
					self.value = 'fan_high_off'
					self.md_bg_color = self.app.toggleOff
			except:
					self.app.noDeviceFound_dialog('Fan')

class EnvCoolToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'ac_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ac_off':
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command['ac_on']
					)
					self.value = 'ac_on'
					self.md_bg_color = self.app.toggleOn
				else:
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command['ac_off']
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
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'heat_off':
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command['heat_on']
					)
					self.value = 'heat_on'
					self.md_bg_color = self.app.toggleOn
				else:
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['thermostat'].address,
						self.app.bus.activeDevices['thermostat'].command['heat_off']
					)
					self.value = 'heat_off'
					self.md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Heat pump')

class WifiToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'wifi_off'
		#self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'wifi_off':
					self.value = 'wifi_on'
					self.md_bg_color = self.app.toggleOn
					self.app.wifi.turnWifi('on')
					self.app.wifiConnect_dialog()
				else:
					self.value = 'wifi_off'
					self.md_bg_color = self.app.toggleOff
					self.app.wifi.turnWifi('off')
			except:
					self.app.generalError_dialog('Wifi not available')
   
class BLEToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'ble_off'
		self.set_disabled(True)

	def on_state(self, instance, value):
		if value == 'normal' and time.time() >= self.app.buttonReset:
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ble_off':
					self.value = 'ble_on'
					self.md_bg_color = self.app.toggleOn
				else:
					self.value = 'ble_off'
					self.md_bg_color = self.app.toggleOff
			except:
					self.app.generalError_dialog('Bluetooth not available')

	def set_disabled(self, disabled):
		self.disabled = disabled

class WSPumpToggleButton(ToggleButtonBehavior, MDFillRoundFlatButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'water_pump_off'
		self.set_disabled(False)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			print('Entered water pump on_state()')
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'water_pump_off':
					print('Turning pump on...')
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command['water_pump_auto']
					)
					self.app.root.ids['ws_pump_quick_switch'].value = 'water_pump_auto'
					self.app.root.ids['ws_pump_quick_switch'].md_bg_color = self.app.toggleOn
					
					self.app.root.ids['ws_pump_switch'].value = 'water_pump_auto'
					self.app.root.ids['ws_pump_switch'].md_bg_color = self.app.toggleOn
				else:
					print('Turning pump off...')
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command['water_pump_off']
					)
					self.app.root.ids['ws_pump_quick_switch'].value = 'water_pump_off'
					self.app.root.ids['ws_pump_quick_switch'].md_bg_color = self.app.toggleOff

					self.app.root.ids['ws_pump_switch'].value = 'water_pump_off'
					self.app.root.ids['ws_pump_switch'].md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Water pump')

	def set_disabled(self, disabled):
		self.disabled = disabled

class WSHeaterToggleButton(ToggleButtonBehavior, MDFillRoundFlatButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'water_heater_off'
		self.set_disabled(True)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			if self.value == 'water_heater_off':
					self.app.root.ids['ws_heater_quick_switch'].value = 'water_heater_auto'
					self.app.root.ids['ws_heater_quick_switch'].md_bg_color = self.app.toggleOn
					
					self.app.root.ids['ws_heater_switch'].value = 'water_heater_auto'
					self.app.root.ids['ws_heater_switch'].md_bg_color = self.app.toggleOn
			else:
					self.app.root.ids['ws_heater_quick_switch'].value = 'water_heater_off'
					self.app.root.ids['ws_heater_quick_switch'].md_bg_color = self.app.toggleOff
					
					self.app.root.ids['ws_heater_switch'].value = 'water_heater_off'
					self.app.root.ids['ws_heater_switch'].md_bg_color = self.app.toggleOff

	def set_disabled(self, disabled):
		self.disabled = disabled

class ShowerFanToggleButton(ToggleButtonBehavior, MDFillRoundFlatButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'shower_fan_off'
		self.set_disabled(False)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'shower_fan_off':
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command['shower_fan_auto']
					)
					self.value = 'shower_fan_auto'
					self.md_bg_color = self.app.toggleOn
				else:
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command['shower_fan_off']
					)
					self.value = 'shower_fan_off'
					self.md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Shower fan')

	def set_disabled(self, disabled):
		self.disabled = disabled

class TankHeaterToggleButton(ToggleButtonBehavior, MDFillRoundFlatButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'tank_heater_off'
		self.set_disabled(False)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'tank_heater_off':
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command['tank_heater_auto']
					)
					self.value = 'tank_heater_auto'
					self.md_bg_color = self.app.toggleOn
				else:
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command['tank_heater_off']
					)
					self.value = 'tank_heater_off'
					self.md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Grey tank heater')

class TankValveToggleButton(ToggleButtonBehavior, MDFillRoundFlatButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'tank_valve_close'
		self.set_disabled(False)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'tank_valve_close':
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command['tank_valve_open']
					)
					self.value = 'tank_valve_open'
					self.md_bg_color = self.app.toggleOn
				else:
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['utilities'].address,
						self.app.bus.activeDevices['utilities'].command['tank_valve_close']
					)
					self.value = 'tank_valve_close'
					self.md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Grey tank dump valve')

	def set_disabled(self, disabled):
		self.disabled = disabled

class DiningLightToggleButton(ToggleButtonBehavior, MDIconButton):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
		self.value = 'ls_1_off'
		self.set_disabled(False)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ls_1_off':
					command = self.app.bus.activeDevices['lighting'].command['ls_1_toggle'][:]
					command.append(int(self.app.root.ids['ls_1_slider'].value))
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.app.root.ids['ls_1_switch'].value = 'ls_1_on'
					self.app.root.ids['ls_1_switch'].md_bg_color = self.app.toggleOn

					self.app.root.ids['ls_1_quick_switch'].value = 'ls_1_on'
					self.app.root.ids['ls_1_quick_switch'].md_bg_color = self.app.toggleOn
				else:
					command = self.app.bus.activeDevices['lighting'].command['ls_1_toggle'][:]
					command.append(0)
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.app.root.ids['ls_1_switch'].value = 'ls_1_off'
					self.app.root.ids['ls_1_switch'].md_bg_color = self.app.toggleOff
					self.app.root.ids['ls_1_quick_switch'].value = 'ls_1_off'
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
		self.set_disabled(False)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ls_2_off':
					command = self.app.bus.activeDevices['lighting'].command['ls_2_toggle'][:]
					command.append(int(self.app.root.ids['ls_2_slider'].value))
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.app.root.ids['ls_2_switch'].value = 'ls_2_on'
					self.app.root.ids['ls_2_switch'].md_bg_color = self.app.toggleOn
					self.app.root.ids['ls_2_quick_switch'].value = 'ls_2_on'
					self.app.root.ids['ls_2_quick_switch'].md_bg_color = self.app.toggleOn
				else:
					command = self.app.bus.activeDevices['lighting'].command['ls_2_toggle'][:]
					command.append(0)
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.app.root.ids['ls_2_switch'].value = 'ls_2_off'
					self.app.root.ids['ls_2_switch'].md_bg_color = self.app.toggleOff
					self.app.root.ids['ls_2_quick_switch'].value = 'ls_2_off'
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
		self.set_disabled(False)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ls_3_off':
					command = self.app.bus.activeDevices['lighting'].command['ls_3_toggle'][:]
					command.append(int(self.app.root.ids['ls_3_slider'].value))
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.app.root.ids['ls_3_switch'].value = 'ls_3_on'
					self.app.root.ids['ls_3_switch'].md_bg_color = self.app.toggleOn
					self.app.root.ids['ls_3_quick_switch'].value = 'ls_3_on'
					self.app.root.ids['ls_3_quick_switch'].md_bg_color = self.app.toggleOn
				else:
					command = self.app.bus.activeDevices['lighting'].command['ls_3_toggle'][:]
					command.append(0)
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.app.root.ids['ls_3_switch'].value = 'ls_3_off'
					self.app.root.ids['ls_3_switch'].md_bg_color = self.app.toggleOff
					self.app.root.ids['ls_3_quick_switch'].value = 'ls_3_off'
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
		self.set_disabled(False)

	def on_state(self, instance, value):
		if (value == 'normal' and time.time() >= self.app.buttonReset) or value == 'override':
			self.app.buttonReset = time.time() + self.app.buttonDelay
			try:
				if self.value == 'ls_4_off':
					command = self.app.bus.activeDevices['lighting'].command['ls_4_toggle'][:]
					command.append(int(self.app.root.ids['ls_4_slider'].value))
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.app.root.ids['ls_4_switch'].value = 'ls_4_on'
					self.app.root.ids['ls_4_switch'].md_bg_color = self.app.toggleOn
					self.app.root.ids['ls_4_quick_switch'].value = 'ls_4_on'
					self.app.root.ids['ls_4_quick_switch'].md_bg_color = self.app.toggleOn
				else:
					command = self.app.bus.activeDevices['lighting'].command['ls_4_toggle'][:]
					command.append(0)
					self.app.bus.send(self.app, 
						'command',
						self.app.bus.activeDevices['lighting'].address,
						command
					)
					self.app.root.ids['ls_4_switch'].value = 'ls_4_off'
					self.app.root.ids['ls_4_switch'].md_bg_color = self.app.toggleOff
					self.app.root.ids['ls_4_quick_switch'].value = 'ls_4_off'
					self.app.root.ids['ls_4_quick_switch'].md_bg_color = self.app.toggleOff
			except KeyError:
					self.app.noDeviceFound_dialog('Bathroom light')

	def set_disabled(self, disabled):
		self.disabled = disabled

class SettingsHomeScreen(Screen):
	pass

class UserSettingsScreen(Screen):
	pass

class DeviceScreen(Screen):
	pass

class DebugScreen(Screen):
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

class Keyboard(MDBoxLayout):
	text = StringProperty()
	text_object = ObjectProperty()

class TextEntry(MDRelativeLayout):
	text = StringProperty()
	hint_text = StringProperty()
	entry_type = StringProperty()

class PasswordTextEntry(MDRelativeLayout):
	text = StringProperty()
	hint_text = StringProperty()
	entry_type = StringProperty()

class KeyboardButton(MDFillRoundFlatButton):
	pass

class SettingsToggleButton(ToggleButtonBehavior, MDRoundFlatButton):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = ironVanApp.get_running_app()
	
	def on_state(self, obj, value):
		match obj.text:
			
			# Temperature scale selection
			case 'Fahrenheit':
				if(obj.state == 'down'):
					self.app.userSettings.tempCelsius = False
					self.app.root.ids['celsius_toggle'].md_bg_color = self.app.toggleOff
					self.app.root.ids['fahrenheit_toggle'].md_bg_color = self.app.toggleOn
		
			case 'Celsius':
				if(obj.state == 'down'):
					self.app.userSettings.tempCelsius = True
					self.app.root.ids['fahrenheit_toggle'].md_bg_color = self.app.toggleOff
					self.app.root.ids['celsius_toggle'].md_bg_color = self.app.toggleOn

			# Time format selection
			case '24 hour':
				if(obj.state == 'down'):
					self.app.userSettings.time24hr = True
					self.app.root.ids['hour12_toggle'].md_bg_color = self.app.toggleOff
					self.app.root.ids['hour24_toggle'].md_bg_color = self.app.toggleOn

			case '12 hour':
				if(obj.state == 'down'):
					self.app.userSettings.time24hr = False
					self.app.root.ids['hour24_toggle'].md_bg_color = self.app.toggleOff
					self.app.root.ids['hour12_toggle'].md_bg_color = self.app.toggleOn

class ironVanApp(MDApp):

	appIDs = appElementIDs()
	log = ivLog.Log()
	bus = ivBus.Bus(log)
	location = weather.Location()
	wifi = network.Wifi()
	userSettings = settings.UserSettings()

	def build(self):

		# ---- Build Window ----
		Config.set('graphics', 'resizable', True)
		# Note:  When uncommenting Window.fullscreen, ensure to delete comment out `size: (700, 480)` in the .kv file.
		Window.fullscreen = 'auto'
		

		# ---- Build App Theme ----

		# self.switchThemes() (below) is used to toggle between themes

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

		self.toggleOn = self.theme_cls.primary_light
		self.toggleOff = self.theme_cls.accent_light


		# ---- Initialize Debounce Functionality ----

		# Master reset for allowing button presses - used globally for debouncing
		# Note:  every button that uses buttonReset MUST reset self.buttonReset after use

		# Button delay is the standard delay used globally for all button debouncing
		self.buttonDelay = 0.25
		self.buttonReset = time.time() + self.buttonDelay


		# ---- Build Dialog Boxes ----

		# All pop-up windows must be instantiated under the self.dialogBox object to ensure that dialog boxes do not stack
		self.dialogBox = None

		# The keyboard is a special type of dialog box and will be instantiated under self.keyboard
		self.keyboard = None


		# ---- Initialize User Settings ----

		self.userSettings.initUserSettings(self)

		# ---- Initiate Background Threads ----

		# messageBuffer holds messages to be printed to the debug frame within the main app thread. Messages are added to the message buffer by outside threads, then handled within the main thread using the stateUpdate() method. Format is messageBuffer[device_gmtime] = {[msg, msgType]}, where msgType is 'normal' or 'error' and effects the color of the line printout in the debug frame. When messageBufferLock is set to True in self.stateUpdate(), the message buffer writing function (bus.write2MessageBuffer) will pause processing on the bus thread to ensure the size & contents of the messageBuffer do not change while being read.
		self.messageBuffer = {}
		self.messageBufferLock = False

		bus_thread = threading.Thread(target = self.bus.regularScan, args = (self,), name = 'bus_thread', daemon = True)
		#bus_thread.start()

		wifi_thread = threading.Thread(target = self.wifi.updateWifi, args = (self,), name = 'wifi_thread', daemon = True)
		wifi_thread.start()

		location_thread = threading.Thread(target = self.location.getLocation, args = (self, ), name = 'weather_thread', daemon = True)
		location_thread.start()

		# ---- Initialize GUI State Update ----

		# The stateLoopCounter is used to subdivide updates so that only time-essential updates are made every second. The stateLoopCounter is reset at a value of 600 (~ every 10 minutes), making the minimum update frequency once every 10 minutes
		self.stateLoopCounter = 0
		self.stateLoop = Clock.schedule_interval(self.stateUpdate, 1)

		return

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

		for id in self.appIDs.navButtons:
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
		for id in self.appIDs.switches:
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

		for id in self.appIDs.toggles:
			if self.theme_cls.theme_style == 'Light':
				if 'down' in self.root.ids[id].state:
					self.root.ids[id].md_bg_color = self.theme_cls.primary_light
					self.root.ids[id].text_color = self.theme_cls.accent_light
				else:
					self.root.ids[id].md_bg_color = self.theme_cls.accent_light
					self.root.ids[id].text_color = self.theme_cls.accent_dark
			else:
				if 'down' in self.root.ids[id].state:
					self.root.ids[id].md_bg_color = self.theme_cls.primary_dark
					self.root.ids[id].text_color = self.theme_cls.accent_light
				else:
					self.root.ids[id].md_bg_color = self.theme_cls.accent_dark
					self.root.ids[id].text_color = self.theme_cls.accent_light
					
				
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
		otherButtons = self.appIDs.navButtons[:]
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

	def selectSettingsScreen(self, id):
		match id:
			case 'user_settings_button':
				self.root.ids.page_manager.current = 'settings_user_settings_page'
			case 'device_button':
				self.root.ids.page_manager.current = 'settings_device_page'
			case 'debug_button':
				self.root.ids.page_manager.current = 'settings_debug_page'

	def brightnessAdjust(self, *args):
		level = args[1]
		subprocess.run("sudo sh -c 'echo %i > /sys/class/backlight/10-0045/brightness'" % level, shell = True)

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
			self.bus.send(self, 
			'command',
			self.bus.activeDevices['lighting'].address,
			command
			)
		except KeyError:
			self.noDeviceFound_dialog('Light')

	def stateUpdate(self, *args):

		# -- 1 second loop --
		
		# Lock messageBuffer
		self.messageBufferLock = True

		for key in self.messageBuffer.keys():
			self.log.print2Debug(self, self.messageBuffer[key][0], self.messageBuffer[key][1])

		self.messageBuffer = {}

		# Unlock messageBuffer
		self.messageBufferLock = False


		# -- 10 second loop --

		if(self.stateLoopCounter % 10 == 0):

			# Update device list
			try:
				currentDevices = []
				deviceItem = None

				for child in self.root.ids['settings_device_card_layout'].children:
					if child.text not in self.bus.activeDevices.keys():
						self.root.ids['settings_device_card_layout'].remove_widget(child)
					else:
						currentDevices.append(child.text)

				for device in self.bus.activeDevices.keys():
					if(device not in currentDevices):
						deviceItem = OneLineIconListItem(text = self.bus.activeDevices[device].name)

						deviceItem.add_widget(IconLeftWidget(icon = self.bus.activeDevices[device].icon))

						self.root.ids['settings_device_card_layout'].add_widget(deviceItem)
						
			except ValueError:
				return
			
			# Update time & date
			if(self.userSettings.time24hr == True):
				self.root.ids['home_time_label'].text = time.strftime('%H:%M')
				self.root.ids['home_time_label'].font_style = 'H5'
			else:
				self.root.ids['home_time_label'].text = time.strftime('%I:%M %p')
				self.root.ids['home_time_label'].font_style = 'H6'

				if(self.root.ids['home_time_label'].text[0] == '0'):
					self.root.ids['home_time_label'].text = self.root.ids['home_time_label'].text[1:]

			self.root.ids['home_date_label'].text = time.strftime('%A\n %d %B %y')
				
		# -- 10 minute loop + counter increment --

		if(self.stateLoopCounter % 600 == 0):
			self.stateLoopCounter = 0

		else:
			self.stateLoopCounter += 1

	def write2MessageBuffer(self, key: str, msg: str, msgType: str):
		'''
		Writes msg to the messageBuffer. Use of this function is required to protect the messageBuffer from changing sizes while being parsed.

		Returns True if the message was added successfully and False if a timeout occured
		'''
		timeoutStart = time.time()
		while(self.messageBufferLock == True):
			if(time.time() >= timeoutStart + 10):
				print(f'Timeout occured on messageBuffer - {key}')
				return False
			else:
				continue
			
		self.messageBuffer[key] = [f"{key}: {msg}", msgType]

		return True

	# ---- Dialog Boxes ----

	def noDeviceFound_dialog(self, deviceName):
		if not self.dialogBox:
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

	def checkIfPasswordProtected(self, ssid, passwordAvailable):
		'''
		How to call:

			self.checkIfPasswordProtected(ssid, passwordAvailable)

		A special function used by the wifiConnect_dialog to check if a network requires the user to input a password.
		'''

		if((self.wifi.availableNetworks[ssid][1] == True) and (passwordAvailable == False)):
			self.closeDialogBox('')
			self.password_dialog(ssid)

		elif(self.wifi.availableNetworks[ssid][1] == True and passwordAvailable == True):
			error = self.wifi.connectToNetwork(ssid, self.dialogBox.content_cls.text)

			self.closeDialogBox('')

			if("Error" in error):
				self.generalError_dialog(f'Unable to connect to {ssid}')

		else:
			error = self.wifi.connectToNetwork(ssid)

			self.closeDialogBox('')

			if("Error" in error):
				self.generalError_dialog(f'Unable to connect to {ssid}')

	def updateNetworkList(self, args):
		'''
		How to call:

			self.updateNetworkList('')

		Special function called by the wifiConnect_dialog() to call the wifi.listNetworks function, then convert available wifi networks into a selectable list.
		'''

		# wifi.listNetworks() is an asynchronous function. Becasue of this, the updates here will not apply until a few seconds have passed and the user presses 'Refresh'
		self.wifi.listNetworks()
		
		networkItems = []
		for ssid in self.wifi.availableNetworks.keys():
			networkItems.append(
				OneLineIconListItem(text = ssid,
									on_release=lambda x: self.checkIfPasswordProtected(x.text, False))
			)

			if(self.wifi.availableNetworks[ssid][0] > -50):
				networkItems[len(networkItems) - 1].add_widget(IconLeftWidget(icon = 'wifi-strength-4'))
			elif(self.wifi.availableNetworks[ssid][0] > -70):
				networkItems[len(networkItems) - 1].add_widget(IconLeftWidget(icon = 'wifi-strength-3'))
			elif(self.wifi.availableNetworks[ssid][0] > -90):
				networkItems[len(networkItems) - 1].add_widget(IconLeftWidget(icon = 'wifi-strength-2'))
			else:
				networkItems[len(networkItems) - 1].add_widget(IconLeftWidget(icon = 'wifi-strength-1'))

		return networkItems

	def wifiConnect_dialog(self):
		'''
		Creates a pop-up that lists the available wifi networks, then allows the user to connect to the network.
		'''
		networkItems = self.updateNetworkList('')

		if not self.dialogBox:
			self.dialogBox = MDDialog(
				title = 'Choose Wifi Network',
				type = 'simple',
				items = networkItems,
				buttons = [
					MDRoundFlatButton(
						text = 'Close',
						on_release = self.closeDialogBox
					),
					MDFillRoundFlatButton(
						text = 'Refresh',
						on_release = self.updateNetworkList
					)
				]
			)
		
			self.dialogBox.open()

	def password_dialog(self, ssid):
		'''
		Called by checkIfPasswordProtected function. Creates a pop-up that allows the user to input a password
		'''
		if not self.dialogBox:
			self.dialogBox = MDDialog(
				title = 'Input Password',
				type = 'custom',
				content_cls = PasswordTextEntry(
					entry_type = 'password'
				),
				buttons = [
					MDRoundFlatButton(
						text = 'Cancel',
						on_release = self.closeDialogBox
					),
					MDFillRoundFlatButton(
						text = 'Submit',
						on_release=lambda x: self.checkIfPasswordProtected(ssid, True)
					)
				]
			)

			self.dialogBox.open()

	def closeApp(tag: str):
		subprocess.run(["sudo", "shutdown", tag, "now"])
	
	def power_dialog(self, obj):
		if not self.dialogBox:
			self.dialogBox = MDDialog(
				title = 'How would you like to power down?',
				type = 'simple',
				buttons = [
					MDRoundFlatButton(
						text = 'Cancel',
						on_release = self.closeDialogBox
					),
					MDFillRoundFlatButton(
						text = 'Restart',
						on_release = lambda x: self.closeApp('-r')
					),
					MDFillRoundFlatButton(
						text = 'Shutdown',
						on_release = lambda x: self.closeApp('')
					)
				]
			)

			self.dialogBox.open()

	def closeDialogBox(self, obj):
		self.dialogBox.dismiss()
		self.dialogBox = None

	# ---- Keyboard ----
 
	def shiftCase(self, obj):
		for id in self.appIDs.keys:
			if(id[1] == '_'):
				if(obj.ids[id].text.islower()):
					obj.ids[id].text = obj.ids[id].text.upper()
				else:
					obj.ids[id].text = obj.ids[id].text.lower()

	def symbolKeys(self, obj):
		for id in self.appIDs.keys:
			match id:
				case 'one_key':
					if (obj.ids[id].text != ' [ '):
						obj.ids[id].text = ' [ '
					else:
						obj.ids[id].text = '1'

				case 'two_key':
					if (obj.ids[id].text != ']'):
						obj.ids[id].text = ']'
					else:
						obj.ids[id].text = '2'

				case 'three_key':
					if (obj.ids[id].text != '{'):
						obj.ids[id].text = '{'
					else:
						obj.ids[id].text = '3'

				case 'four_key':
					if (obj.ids[id].text != '}'):
						obj.ids[id].text = '}'
					else:
						obj.ids[id].text = '4'

				case 'five_key':
					if (obj.ids[id].text != '#'):
						obj.ids[id].text = '#'
					else:
						obj.ids[id].text = '5'

				case 'six_key':
					if (obj.ids[id].text != '%'):
						obj.ids[id].text = '%'
					else:
						obj.ids[id].text = '6'

				case 'seven_key':
					if (obj.ids[id].text != '^'):
						obj.ids[id].text = '^'
					else:
						obj.ids[id].text = '7'

				case 'eight_key':
					if (obj.ids[id].text != '*'):
						obj.ids[id].text = '*'
					else:
						obj.ids[id].text = '8'

				case 'nine_key':
					if (obj.ids[id].text != '+'):
						obj.ids[id].text = '+'
					else:
						obj.ids[id].text = '9'

				case 'zero_key':
					if (obj.ids[id].text != '='):
						obj.ids[id].text = '='
					else:
						obj.ids[id].text = '0'

				case 'q_key':
					if (obj.ids[id].text != '-'):
						obj.ids[id].text = '-'
					else:
						obj.ids[id].text = 'q'

				case 'w_key':
					if (obj.ids[id].text != '/'):
						obj.ids[id].text = '/'
					else:
						obj.ids[id].text = 'w'

				case 'e_key':
					if (obj.ids[id].text != ':'):
						obj.ids[id].text = ':'
					else:
						obj.ids[id].text = 'e'

				case 'r_key':
					if (obj.ids[id].text != ';'):
						obj.ids[id].text = ';'
					else:
						obj.ids[id].text = 'r'

				case 't_key':
					if (obj.ids[id].text != '('):
						obj.ids[id].text = '('
					else:
						obj.ids[id].text = 't'

				case 'y_key':
					if (obj.ids[id].text != ')'):
						obj.ids[id].text = ')'
					else:
						obj.ids[id].text = 'y'

				case 'u_key':
					if (obj.ids[id].text != '$'):
						obj.ids[id].text = '$'
					else:
						obj.ids[id].text = 'u'

				case 'i_key':
					if (obj.ids[id].text != '&'):
						obj.ids[id].text = '&'
					else:
						obj.ids[id].text = 'i'

				case 'o_key':
					if (obj.ids[id].text != '@'):
						obj.ids[id].text = '@'
					else:
						obj.ids[id].text = 'o'

				case 'p_key':
					if (obj.ids[id].text != '"'):
						obj.ids[id].text = '"'
					else:
						obj.ids[id].text = 'p'

				case 'a_key':
					if (obj.ids[id].text != '_'):
						obj.ids[id].text = '_'
					else:
						obj.ids[id].text = 'a'

				case 's_key':
					if (obj.ids[id].text != '\\'):
						obj.ids[id].text = '\\'
					else:
						obj.ids[id].text = 's'

				case 'd_key':
					if (obj.ids[id].text != '|'):
						obj.ids[id].text = '|'
					else:
						obj.ids[id].text = 'd'

				case 'f_key':
					if (obj.ids[id].text != '~'):
						obj.ids[id].text = '~'
					else:
						obj.ids[id].text = 'f'

				case 'g_key':
					if (obj.ids[id].text != '<'):
						obj.ids[id].text = '<'
					else:
						obj.ids[id].text = 'g'

				case 'h_key':
					if (obj.ids[id].text != '>'):
						obj.ids[id].text = '>'
					else:
						obj.ids[id].text = 'h'

				case 'j_key':
					if (obj.ids[id].text != '.'):
						obj.ids[id].text = '.'
					else:
						obj.ids[id].text = 'j'

				case 'k_key':
					if (obj.ids[id].text != ','):
						obj.ids[id].text = ','
					else:
						obj.ids[id].text = 'k'

				case 'l_key':
					if (obj.ids[id].text != '?'):
						obj.ids[id].text = '?'
					else:
						obj.ids[id].text = 'l'

				case 'z_key':
					if (obj.ids[id].text != ''):
						obj.ids[id].text = ''
					else:
						obj.ids[id].text = 'z'

				case 'x_key':
					if (obj.ids[id].text != ''):
						obj.ids[id].text = ''
					else:
						obj.ids[id].text = 'x'

				case 'c_key':
					if (obj.ids[id].text != '!'):
						obj.ids[id].text = '!'
					else:
						obj.ids[id].text = 'c'

				case 'v_key':
					if (obj.ids[id].text != "'"):
						obj.ids[id].text = "'"
					else:
						obj.ids[id].text = 'v'

				case 'b_key':
					if (obj.ids[id].text != ''):
						obj.ids[id].text = ''
					else:
						obj.ids[id].text = 'b'

				case 'n_key':
					if (obj.ids[id].text != ''):
						obj.ids[id].text = ''
					else:
						obj.ids[id].text = 'n'

				case 'm_key':
					if (obj.ids[id].text != ''):
						obj.ids[id].text = ''
					else:
						obj.ids[id].text = 'm'

 
	def keyboard_dialog(self, obj):
		
		if not self.keyboard:
			self.keyboard = MDDialog(
				title = '',
				type = 'custom',
				content_cls = Keyboard(
					text = obj.text,
					text_object = obj,
				),
				size_hint = (None, None),
				size = (Window.width, Window.width)
			)
			
			self.keyboard.open()
		
		else:
			self.keyboard.dismiss()
			self.keyboard = None

if __name__ == '__main__':
	ironVanApp().run()