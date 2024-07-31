from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.metrics import dp


class Home(MDScreen):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)

        self.layout = MDBoxLayout(orientation='vertical', padding=[dp(20), dp(20), dp(20), dp(20)], spacing=dp(20))

        # Add settings icon in a FloatLayout to position it at the top right
        self.float_layout = MDFloatLayout(size_hint=(1, None), height=dp(40))
        self.settings_button = MDIconButton(icon="cog", pos_hint={'right': 1, 'top': 1})
        self.float_layout.add_widget(self.settings_button)
        self.layout.add_widget(self.float_layout)

        # Add logo
        self.logo = Image(source='assets/images/frslogoimg.jpg', size_hint=(1, 0.4), allow_stretch=True)
        self.layout.add_widget(self.logo)

        # Add title
        self.title = MDLabel(text='Facial Recognition System', font_style="H6", halign="center", size_hint=(1, None),
                             height=dp(40))
        self.layout.add_widget(self.title)

        # Add login button
        self.login_button = MDRaisedButton(text='LOGIN', size_hint=(1, None), height=dp(50))
        self.layout.add_widget(self.login_button)

        # Add register button
        self.register_button = MDRaisedButton(text='REGISTER', size_hint=(1, None), height=dp(50))
        self.layout.add_widget(self.register_button)

        # Add customer care label and icon in a BoxLayout to position them on one line at the bottom
        self.customer_care_layout = MDBoxLayout(orientation='horizontal', size_hint=(None, None), height=dp(60),
                                                spacing=dp(10), pos_hint={'center_x': 0.5})
        self.customer_care_label = MDLabel(text='Customer Care', halign='center', size_hint=(None, None), width=dp(120),
                                           height=dp(40), pos_hint={'center_y': 0.5})
        self.customer_care_button = MDIconButton(icon="email", size_hint=(None, None), height=dp(40), width=dp(40),
                                                 pos_hint={'center_y': 0.5})
        self.customer_care_layout.add_widget(self.customer_care_label)
        self.customer_care_layout.add_widget(self.customer_care_button)
        self.layout.add_widget(self.customer_care_layout)

        self.add_widget(self.layout)