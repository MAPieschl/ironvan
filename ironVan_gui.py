import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

import ironVan_log as log
import ironVan_bus as bus

class MainScreenManager(ScreenManager):
    def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.mainApp = App.get_running_app()

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
          
        self.mainApp = App.get_running_app()

class ironVanApp(App):

    screenManager = MainScreenManager()
    log = log.Log(screenManager)
    bus = bus.Bus(screenManager, log)

    def build(self):
            self.screenManager.add_widget(HomeScreen(name = 'home_screen'))
            self.screenManager.current = 'home_screen'

            return self.screenManager