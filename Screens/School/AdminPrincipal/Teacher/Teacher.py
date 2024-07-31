from kivy.uix.image import AsyncImage
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import SlideTransition, ScreenManager
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.gridlayout import GridLayout
import requests
import time
import logging

class TeacherScreen(MDScreen):

    def update_fields(self, school_name, type_of, role, username):
        self.fields["typeOf"] = type_of
        self.fields["schoolName"] = school_name
        self.check_and_update_layout()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields = {
            "schoolName": None,
            "typeOf": None,
        }

        # Main layout
        self.layout = MDBoxLayout(orientation='vertical')

        # Top app bar
        toolbar = MDTopAppBar(
            title="Teacher",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["account-plus", lambda x: self.add_teacher()],
                ["file-document-outline", lambda x: self.teacher_details()]
            ],
            elevation=4,
        )
        self.layout.add_widget(toolbar)

        # We'll add the icon or grid later if needed
        self.content_layout = MDBoxLayout(orientation='vertical')
        self.layout.add_widget(self.content_layout)

        self.add_widget(self.layout)

    def check_and_update_layout(self):
        if self.fields["schoolName"]:
            url = f"https://facialrecognitiondb-default-rtdb.firebaseio.com/School/{self.fields['schoolName']}/Teachers.json"
            response = self.make_request(url)
            if response and response.status_code == 200:
                data = response.json()
                if not data:  # If there's no data, add the icon
                    self.add_icon()
                else:
                    self.display_teachers(data)
            else:
                print("Failed to fetch data from Firebase")

    def make_request(self, url, retries=3, delay=5):
        for attempt in range(retries):
            try:
                response = requests.get(url)
                return response
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}, retrying in {delay} seconds...")
                time.sleep(delay)
        return None

    def add_icon(self):
        self.content_layout.clear_widgets()
        icon_anchor_layout = AnchorLayout()
        icon_card = MDCard(size_hint=(None, None), size=(150, 150), elevation=0)
        icon = AsyncImage(source='./assets/images/ImgSchool/AboutSchoolAdd.png')
        icon_card.add_widget(icon)
        icon_anchor_layout.add_widget(icon_card)
        self.content_layout.add_widget(icon_anchor_layout)

    def display_teachers(self, data):
        self.content_layout.clear_widgets()
        grid = GridLayout(cols=3, spacing=10, padding=5)  # Reduced padding, increased spacing

        for teacher_name, teacher_data in data.items():
            card = MDBoxLayout(orientation='vertical', size_hint=(None, None), size=(110, 140), padding=0)  # Increased size

            # Avatar
            gender = teacher_data.get('Gender', '').lower()
            if gender == 'female':
                icon_source = './assets/images/ImgSchool/teacherFemale.png'
            else:
                icon_source = './assets/images/ImgSchool/teacherMale.png'

            avatar = AsyncImage(
                source=icon_source,
                size_hint=(None, None),
                size=(70, 70),  # Increased image size
                pos_hint={'center_x': 0.5}
            )
            card.add_widget(avatar)

            # Name
            name_label = MDLabel(
                text=teacher_data.get('Teacher Name', 'Unknown'),
                halign='center',
                font_style='Caption',
                size_hint_y=None,
                height=25,  # Increased height
                padding=(0, 0)
            )
            card.add_widget(name_label)

            # Subject
            subject_label = MDLabel(
                text=teacher_data.get('Subject', 'Unknown'),
                halign='center',
                font_style='Caption',
                size_hint_y=None,
                height=25,  # Increased height
                padding=(0, 0)
            )
            card.add_widget(subject_label)

            grid.add_widget(card)

        self.content_layout.add_widget(grid)

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_admin'

    def add_teacher(self):
        school_name = self.fields["schoolName"]
        type_of = self.fields["typeOf"]
        about_screen = self.manager.get_screen('school_admin_addTeacher')
        about_screen.update_fields(school_name, type_of)
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'school_admin_addTeacher'

    def teacher_details(self):
        school_name = self.fields["schoolName"]
        type_of = self.fields["typeOf"]
        about_screen = self.manager.get_screen('school_admin_teacherDetails')
        about_screen.update_fields(school_name, type_of)
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'school_admin_teacherDetails'

class MainApp(MDApp):
    def build(self):
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(TeacherScreen(name='school_admin_teacher'))
        return self.screen_manager

if __name__ == '__main__':
    MainApp().run()