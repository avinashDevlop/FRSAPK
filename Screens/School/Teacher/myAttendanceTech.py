from kivy.metrics import dp
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.image import Image
from kivymd.uix.card import MDCard
from kivy.graphics import Color, Rectangle

class myAttendanceTech(MDScreen):
    def update_fields(self, school_name, type_of, role, username):
        self.fields["TypeOf"] = type_of
        self.fields["schoolName"] = school_name
        self.fields["role"] = role
        self.fields["userName"] = username
        self.update_profile_label()  # Update the profile label text
        self.update_title()  # Update the title

    def update_title(self):
        if self.fields["userName"]:
            self.top_bar.title = f"{self.fields['userName']}'s Attendance"
        else:
            self.top_bar.title = "My Attendance"

    def update_profile_label(self):
        if self.fields["userName"]:
            self.profile_label.text = self.fields["userName"]
        else:
            self.profile_label.text = "User"

    def __init__(self, **kwargs):
        super(myAttendanceTech, self).__init__(**kwargs)

        self.fields = {
            "SchoolName": None,
            "TypeOf": None,
            "role": None,
            "userName": None
        }

        # Main layout
        self.layout = MDBoxLayout(orientation='vertical', spacing=dp(10))

        # Top app bar
        self.top_bar = MDTopAppBar(
            title="My Attendance",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            pos_hint={"top": 1},
        )
        self.layout.add_widget(self.top_bar)

        # Top layout for profile card and register button
        self.top_layout = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Profile image and name card
        self.profile_card = MDCard(
            size_hint=(None, None),
            size=(dp(150), dp(200)),
            pos_hint={'center_x': 0.5},
            elevation=0,  # Remove shadow
            orientation='vertical'
        )

        self.profile_image = Image(
            source='./assets/images/ImgSchool/FRSLogo.png',
            size_hint=(None, None),
            size=(dp(150), dp(150)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Remove white background for the logo
        with self.profile_image.canvas.before:
            Color(0, 0, 0, 0)  # Set color to transparent
            self.rect = Rectangle(size=self.profile_image.size, pos=self.profile_image.pos)

        self.profile_card.add_widget(self.profile_image)

        self.profile_label = MDLabel(
            text='User',  # Default text
            halign='center'
        )
        self.profile_card.add_widget(self.profile_label)

        self.top_layout.add_widget(self.profile_card)

        # Register button
        self.register_button = MDRaisedButton(
            text="Register",
            size_hint=(None, None),
            size=(dp(100), dp(40)),
            pos_hint={'center_x': 0.5},
            on_release=self.register
        )
        self.top_layout.add_widget(self.register_button)

        self.layout.add_widget(self.top_layout)

        # Content layout
        self.content_layout = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(20))
        self.layout.add_widget(self.content_layout)

        self.add_widget(self.layout)

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_teacher'

    def register(self, instance):
        screen = self.manager.get_screen('school_teacher_frsRegister')
        screen.update_fields(self.fields["schoolName"], self.fields["TypeOf"], self.fields["role"], self.fields["userName"])
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_teacher_frsRegister'

class AttendanceApp(MDApp):
    def build(self):
        return myAttendanceTech(name='attendance')

if __name__ == '__main__':
    AttendanceApp().run()