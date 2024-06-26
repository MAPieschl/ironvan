from kivymd.uix.label import MDLabel

class Log():
    def __init__(self):
        self.label = []
    
    def print2Debug(self, app, msg: str, mType: str):
        '''
        Prints message to the settings debug view.

        Arguments:
         - app - main app instance
         - msg - unformatted message -> message will be emboldend and line management is handled by the function
         - type - 'normal' (will be printed in green) // 'error' (will be printed in red)
        '''
        match mType:
            case 'error':
                color = (252/255, 3/255, 3/255, 1)
            case _:
                color = (44/255, 252/255, 3/255, 1)

        app.root.ids['debug_layout'].add_widget(MDLabel(text = '[b]{}[/b]'.format(msg),
                                                        markup = True,
                                                        theme_text_color = 'Custom',
                                                        text_color = color,
                                                        size_hint_y = None,
                                                        height = 50))

        if(len(app.root.ids['debug_layout'].children) > 20):
            app.root.ids['debug_layout'].remove_widget(app.root.ids['debug_layout'].children[len(app.root.ids['debug_layout'].children) - 1])