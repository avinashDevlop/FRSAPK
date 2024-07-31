import re
import requests
from kivy.uix.screenmanager import SlideTransition
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.graphics import Color, Line
from kivymd.uix.label import MDLabel


class BorderedButton(MDFlatButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(150 / 255, 150 / 255, 150 / 255, 1)
            self.border = Line(width=1, rectangle=(self.x, self.y, self.width, self.height))
        self.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, *args):
        self.border.rectangle = (self.x, self.y, self.width, self.height)


class AddTeacherScreen(MDScreen):
    def update_fields(self, school_name, type_of):
        self.DBLocation["typeOf"] = type_of
        self.DBLocation["schoolName"] = school_name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.DBLocation = {
            "typeOf": "",
            "schoolName": ""
        }

        self.fields = {
            "Teacher Name": None,
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

        self.numeric_fields = [
            "Zip Code",
            "Years of Experience"
        ]

        # Main layout
        layout = MDBoxLayout(orientation='vertical', spacing=dp(10))

        # Top app bar
        toolbar = MDTopAppBar(
            title="Add Teacher",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            elevation=4,
        )
        layout.add_widget(toolbar)

        # Scroll view for content
        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), size_hint_y=None,
                              adaptive_height=True)
        scroll.add_widget(content)

        # Icon
        icon_card = MDCard(size_hint=(None, None), size=(dp(100), dp(100)), pos_hint={'center_x': 0.5})
        icon = Image(source='./assets/images/ImgSchool/AboutSchoolAdd.png')
        icon_card.add_widget(icon)
        content.add_widget(icon_card)

        # Iterate over a copy of the dictionary keys
        for field in list(self.fields.keys()):
            if field == "Gender":
                # Add gender selection here
                gender_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
                gender_label = MDLabel(text="Gender", size_hint=(None, None), size=(dp(80), dp(40)))
                self.gender_male = MDCheckbox(group='gender', size_hint=(None, None), size=(dp(40), dp(40)))
                self.gender_female = MDCheckbox(group='gender', size_hint=(None, None), size=(dp(40), dp(40)))

                male_label = MDFlatButton(text="Male", size_hint=(None, None), size=(dp(50), dp(40)))
                female_label = MDFlatButton(text="Female", size_hint=(None, None), size=(dp(60), dp(40)))

                male_label.bind(on_release=lambda x: self.select_gender(self.gender_male))
                female_label.bind(on_release=lambda x: self.select_gender(self.gender_female))

                gender_layout.add_widget(gender_label)
                gender_layout.add_widget(self.gender_male)
                gender_layout.add_widget(male_label)
                gender_layout.add_widget(self.gender_female)
                gender_layout.add_widget(female_label)

                self.fields["Gender"] = (self.gender_male, self.gender_female)
                content.add_widget(gender_layout)
            elif field == "Phone Number":
                # Add phone number layout
                self.phone_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60),
                                                spacing=dp(10))

                self.country_button = BorderedButton(
                    text="+91",
                    size_hint=(None, None),
                    width=dp(80),
                    height=dp(48),
                    halign="center",
                )
                self.country_menu_items = [
                    {"text": "+91 (IN)", "viewclass": "OneLineListItem",
                     "on_release": lambda x="+91": self.set_item(self.country_button, x)},
                    {"text": "+1 (US)", "viewclass": "OneLineListItem",
                     "on_release": lambda x="+1": self.set_item(self.country_button, x)},
                    {"text": "+44 (UK)", "viewclass": "OneLineListItem",
                     "on_release": lambda x="+44": self.set_item(self.country_button, x)},
                ]
                self.country_menu = MDDropdownMenu(
                    caller=self.country_button,
                    items=self.country_menu_items,
                    width_mult=4,
                    max_height=dp(200),
                )
                self.country_button.bind(on_release=lambda x: self.country_menu.open())

                self.phone_field = MDTextField(
                    hint_text="Phone Number",
                    mode="rectangle",
                    size_hint_x=1,
                    height=dp(48),
                    input_filter='int',
                    max_text_length=10
                )

                self.phone_layout.add_widget(self.country_button)
                self.phone_layout.add_widget(self.phone_field)

                content.add_widget(self.phone_layout)
                self.fields["Phone Number"] = (self.country_button, self.phone_field)
            else:
                text_field = MDTextField(
                    hint_text=field,
                    mode="rectangle",
                    size_hint_y=None,
                    height=dp(48),
                    input_filter='int' if field in self.numeric_fields else None
                )
                self.fields[field] = text_field
                content.add_widget(text_field)

        # Submit button
        submit_button = MDRaisedButton(
            text="Submit",
            pos_hint={'center_x': 0.5},
            size_hint=(None, None),
            width=dp(200)
        )
        submit_button.bind(on_press=self.submit_form)
        content.add_widget(submit_button)

        # Add scroll view to main layout
        layout.add_widget(scroll)

        self.add_widget(layout)

    def select_gender(self, checkbox):
        checkbox.active = True

    def go_back(self):
        school_name = self.DBLocation["schoolName"]
        type_of = self.DBLocation["typeOf"]
        about_screen = self.manager.get_screen('school_admin_teacher')
        about_screen.update_fields(school_name, type_of,'none','none')
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_admin_teacher'

    def submit_form(self, instance):
        data = {}
        for field_name, field in self.fields.items():
            if field_name == "Phone Number":
                country_button, phone_field = field
                if not phone_field.text:
                    toast(f"{field_name} is required.")
                    return
                if not self.validate_phone_number(phone_field.text):
                    toast(f"{field_name} is in an invalid format.")
                    return
                data["Country Code"] = country_button.text
                data[field_name] = phone_field.text
            elif field_name == "Gender":
                male, female = field
                if male.active:
                    data[field_name] = "Male"
                elif female.active:
                    data[field_name] = "Female"
                else:
                    toast(f"{field_name} is required.")
                    return
            else:
                if not field.text:
                    toast(f"{field_name} is required.")
                    return
                if field_name == "Email" and not self.validate_email(field.text):
                    toast(f"{field_name} is in an invalid format.")
                    return
                if field_name in self.numeric_fields and not field.text.isdigit():
                    toast(f"{field_name} should be numeric.")
                    return
                data[field_name] = field.text

        self.send_to_firebase(data)

    def validate_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def validate_phone_number(self, phone_number):
        return re.match(r"^\d{10}$", phone_number)

    def send_to_firebase(self, data):
        school_name = self.DBLocation["schoolName"]
        type_of = self.DBLocation["typeOf"]
        teacherName = self.fields["Teacher Name"].text
        url = f"https://facialrecognitiondb-default-rtdb.firebaseio.com/{type_of}/{school_name}/Teachers/{teacherName}.json"  # Replace with your Firebase URL

        response = requests.patch(url, json=data)  # Use patch instead of put
        if response.status_code == 200:
            toast("Data submitted successfully!")
            self.clear_fields()  # Clear fields after successful submission
        else:
            toast("Failed submission.")

    def set_item(self, instance, text_item):
        instance.text = text_item
        self.country_menu.dismiss()

    def clear_fields(self):
        for field_name, field in self.fields.items():
            if field_name == "Phone Number":
                country_button, phone_field = field
                country_button.text = "+91"  # Reset to default country code
                phone_field.text = ""
            elif field_name == "Gender":
                male, female = field
                male.active = False
                female.active = False
            else:
                field.text = ""


class SchoolApp(MDApp):
    def build(self):
        return AddTeacherScreen()


if __name__ == '__main__':
    SchoolApp().run()