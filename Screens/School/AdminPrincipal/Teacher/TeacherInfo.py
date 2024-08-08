import re
import requests
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.toast import toast

from firebase_admin import db


class TeacherInfoScreen(MDScreen):
    def update_fields(self, school_name, type_of, teacher_name):
        self.DBLocation["typeOf"] = type_of
        self.DBLocation["schoolName"] = school_name
        self.DBLocation["TeacherName"] = teacher_name
        self.load_teacher_data()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DBLocation = {
            "typeOf": "",
            "schoolName": "",
            "TeacherName": ""
        }
        self.fields = {
            "registration_status": False,
            "Gender": None,
            "Subject": None,
            "Qualification": None,
            "Years of Experience": None,
            "Phone Number": None,
            "Email": None,
            "Address": None,
            "City": None,
            "State": None,
            "Zip Code": None,
        }

        # Main layout
        layout = MDBoxLayout(orientation='vertical')

        # Top app bar
        toolbar = MDTopAppBar(
            title="Teacher Info",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["pencil", lambda x: self.edit_info()]],
            elevation=4,
        )
        layout.add_widget(toolbar)

        # Scroll view for content
        scroll = MDScrollView()
        self.content = MDBoxLayout(orientation='vertical', padding=20, spacing=20, size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)

        # Icon
        icon_card = MDCard(size_hint=(None, None), size=(100, 100), pos_hint={'center_x': 0.5})
        self.icon = Image(source='./assets/images/ImgSchool/teacherMale.png')
        icon_card.add_widget(self.icon)
        self.content.add_widget(icon_card)

        # Teacher name
        self.teacher_name_label = MDLabel(
            text="Teacher Name",
            halign="center",
            theme_text_color="Primary",
            font_style="H6"
        )
        self.content.add_widget(self.teacher_name_label)

        # Teacher information fields
        for field in self.fields:
            field_label = MDLabel(
                text=f"{field} : ",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="48dp"
            )
            self.fields[field] = field_label
            self.content.add_widget(field_label)

        # Add scroll view to main layout
        layout.add_widget(scroll)

        self.add_widget(layout)

    def load_teacher_data(self):
        if all(self.DBLocation.values()):
            ref = db.reference(
                f"{self.DBLocation['typeOf']}/{self.DBLocation['schoolName']}/Teachers/{self.DBLocation['TeacherName']}")
            teacher_data = ref.get()
            # print(teacher_data)
            if teacher_data:
                self.teacher_name_label.text = self.DBLocation['TeacherName']

                for field, label in self.fields.items():
                    value = teacher_data.get(field, "Not provided")
                    label.text = f"{field}: {value}"

                # Update icon based on gender
                gender = teacher_data.get('Gender', '').lower()
                if gender == 'female':
                    self.icon.source = './assets/images/ImgSchool/teacherFemale.png'
                else:
                    self.icon.source = './assets/images/ImgSchool/teacherMale.png'
            else:
                toast("Teacher data not found")
        else:
            toast("Incomplete teacher information")

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_admin_teacherDetails'

    def edit_info(self):
        print('under development')


class TeacherApp(MDApp):
    def build(self):
        return TeacherInfoScreen()


if __name__ == '__main__':
    TeacherApp().run()