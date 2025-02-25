import re
import requests
from kivy.core.window import Window
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.toast import toast
from kivy.core.clipboard import Clipboard

class AboutSchoolScreen(MDScreen):
    def update_fields(self, school_name, type_of, role, username):
        self.fields["School Name"].text = school_name
        self.DBLocation["TypeOf"] = type_of
        self.DBLocation["schoolName"] = school_name
        self.populate_fields()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields = {
            "School Name": None,
            "Address": None,
            "City": None,
            "State": None,
            "Zip Code": None,
            "Phone Number": None,
            "Email": None,
            "Website": None,
            "Established Year": None,
            "Coordinates": None,
            # "Latitude": None,
            # "Longitude": None,
            "School Motto": None,
            "Number of Students": None
        }

        self.numeric_fields = [
            "Zip Code",
            "Phone Number",
            "Established Year",
            "Number of Students",
        ]

        self.DBLocation = {
            "TypeOf": "",
            "schoolName": ""
        }

        # Main layout
        layout = MDBoxLayout(orientation='vertical')

        # Top app bar
        toolbar = MDTopAppBar(
            title="About School",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            elevation=4,
        )
        layout.add_widget(toolbar)

        # Scroll view for content
        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', padding=20, spacing=20, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        scroll.add_widget(content)

        # Icon
        icon_card = MDCard(size_hint=(None, None), size=(100, 100), pos_hint={'center_x': 0.5})
        icon = Image(source='./assets/images/ImgSchool/AboutSchoolAdd.png')  # Replace with your icon path
        icon_card.add_widget(icon)
        content.add_widget(icon_card)

        # School information fields
        for field in self.fields:
            text_field = MDTextField(
                hint_text=field,
                mode="rectangle",
                size_hint_y=None,
                height="48dp",
                multiline=False,  # Allows single-line input with clipboard paste functionality
                input_filter='float' if field in self.numeric_fields else None
            )
            text_field.bind(on_text_validate=lambda instance: self.check_paste(instance))  # Check for pasting on validation
            text_field.on_double_tap = self.paste_text  # Enable paste on double-tap
            self.fields[field] = text_field
            content.add_widget(text_field)

        # Submit button
        submit_button = MDRaisedButton(
            text="Submit",
            pos_hint={'center_x': 0.5},
            size_hint=(None, None),
            width="200dp"
        )
        submit_button.bind(on_press=self.submit_form)
        content.add_widget(submit_button)

        # Add scroll view to main layout
        layout.add_widget(scroll)

        self.add_widget(layout)

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_admin'

    def submit_form(self, instance):
        for field_name, text_field in self.fields.items():
            if not text_field.text:
                toast(f"{field_name} is required.")
                return
            if field_name == "Email" and not self.validate_email(text_field.text):
                toast(f"{field_name} is in an invalid format.")
                return
            if field_name == "Phone Number" and not self.validate_phone_number(text_field.text):
                toast(f"{field_name} is in an invalid format.")
                return
            if field_name == "Website" and not self.validate_website(text_field.text):
                toast(f"{field_name} is in an invalid format.")
                return
            if field_name in self.numeric_fields and field_name != "Coordinates" and not text_field.text.replace(".", "").isdigit():
                toast(f"{field_name} should be numeric.")
                return

            # Validate and split "Coordinates" into latitude and longitude
            if field_name == "Coordinates":
                coordinates = text_field.text.split(',')
                if len(coordinates) != 2:
                    toast("Coordinates should be in 'latitude,longitude' format.")
                    return
                try:
                    latitude = float(coordinates[0].strip())
                    longitude = float(coordinates[1].strip())
                except ValueError:
                    toast("Invalid coordinates format.")
                    return

        # Prepare data for Firebase submission
        data = {field_name: text_field.text for field_name, text_field in self.fields.items() if field_name != "Coordinates"}
        data["Latitude"] = latitude
        data["Longitude"] = longitude

        self.send_to_firebase(data)


    def validate_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def validate_phone_number(self, phone_number):
        return re.match(r"^\+?1?\d{9,15}$", phone_number)  # Example regex for international phone numbers

    def validate_website(self, website):
        return re.match(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", website)  # Basic URL validation regex

    def send_to_firebase(self, data):
        school_name = self.DBLocation["schoolName"]
        type_of = self.DBLocation["TypeOf"]
        url = f"https://facialrecognitiondb-default-rtdb.firebaseio.com/{type_of}/{school_name}/schoolDetails.json"

        response = requests.patch(url, json=data)  # Use patch instead of put
        if response.status_code == 200:
            toast("Data submitted successfully!")
        else:
            toast("Failed submission.")

    def populate_fields(self):
        school_name = self.DBLocation["schoolName"]
        type_of = self.DBLocation["TypeOf"]
        url = f"https://facialrecognitiondb-default-rtdb.firebaseio.com/{type_of}/{school_name}/schoolDetails.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                for field_name, value in data.items():
                    if field_name in self.fields and field_name != "Coordinates":
                        self.fields[field_name].text = value
                # Combine latitude and longitude for "Coordinates" field
                if "Latitude" in data and "Longitude" in data:
                    self.fields["Coordinates"].text = f"{data['Latitude']}, {data['Longitude']}"
        else:
            toast("Failed to load data.")


    def paste_text(self, instance):
        instance.text = Clipboard.paste()

    def check_paste(self, instance):
        if instance.focus:
            instance.select_all()


class SchoolApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        return AboutSchoolScreen()


if __name__ == '__main__':
    SchoolApp().run()