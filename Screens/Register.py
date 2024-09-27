from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import SlideTransition
from kivy.utils import get_color_from_hex
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
import re
from twilio.rest import Client
import os
from firebase_admin import db
import random
from kivy.properties import ObjectProperty

# Ensure the environment variables are set
os.environ['TWILIO_ACCOUNT_SID'] = 'ACb3fafc23ffc094440f19e652ba91a1e2'
os.environ['TWILIO_AUTH_TOKEN'] = 'eb0a2728c740add095ef982fb3933658'
os.environ['TWILIO_SERVICE_SID'] = 'VAe814c9ac1f8924d7058398b0f23b29e2'

class CustomButton(MDRaisedButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = get_color_from_hex("#f1f1f1")  # Set button color to #FAFAFA
        self.text_color = get_color_from_hex("#a4a4a4")

class Register(MDScreen):
    otp_input = ObjectProperty(None)
    country_button = ObjectProperty(None)
    phone_field = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Register, self).__init__(**kwargs)

        # Main layout
        self.layout = MDBoxLayout(orientation='vertical', spacing=dp(30))

        # Top app bar
        self.top_bar = MDTopAppBar(
            title="Register",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            size_hint_y=None,
            height=dp(56),
            anchor_title='center'
        )
        self.layout.add_widget(self.top_bar)

        # Scrollable content
        self.scroll_view = ScrollView()
        self.scroll_layout = MDBoxLayout(orientation='vertical', padding=[dp(20), dp(20), dp(20), dp(20)],
                                         spacing=dp(20), size_hint_y=None)
        self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))

        # Institution/Company Type dropdown
        self.type_button = CustomButton(
            text="Select Type",
            size_hint=(1, None),
            height=dp(40),
            halign="left",
            padding=(dp(10), dp(15)),
        )
        self.type_menu_items = [
            {"text": "Company", "viewclass": "OneLineListItem",
             "on_release": lambda x="Company": self.set_item(self.type_button, x)},
            {"text": "Institute", "viewclass": "OneLineListItem",
             "on_release": lambda x="Institute": self.set_item(self.type_button, x)},
            {"text": "Organization", "viewclass": "OneLineListItem",
             "on_release": lambda x="Organization": self.set_item(self.type_button, x)},
            {"text": "Business", "viewclass": "OneLineListItem",
             "on_release": lambda x="Business": self.set_item(self.type_button, x)},
            {"text": "School", "viewclass": "OneLineListItem",
             "on_release": lambda x="School": self.set_item(self.type_button, x)},
        ]
        self.type_menu = MDDropdownMenu(
            caller=self.type_button,
            items=self.type_menu_items,
            width_mult=4,
            position="center",
        )
        self.type_button.bind(on_release=lambda x: self.type_menu.open())
        self.scroll_layout.add_widget(self.type_button)

        # Institute/Company Name field
        self.name_field = MDTextField(
            hint_text="Institute/Company Name",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(40),
        )
        self.scroll_layout.add_widget(self.name_field)

        # Role dropdown
        self.role_button = CustomButton(
            text="Select Role",
            size_hint=(1, None),
            height=dp(40),
            halign="left",
            padding=(dp(10), dp(15)),
        )
        self.role_menu = MDDropdownMenu(
            caller=self.role_button,
            items=[],
            width_mult=4,
            position="center",
        )
        self.role_button.bind(on_release=lambda x: self.role_menu.open())
        self.scroll_layout.add_widget(self.role_button)

        # Email field
        self.email_field = MDTextField(
            hint_text="Email",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(40),
        )
        self.scroll_layout.add_widget(self.email_field)

        # Country Code dropdown and Phone field in a horizontal layout
        self.phone_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40), spacing=dp(20),padding=(dp(10),dp(10),dp(0),dp(-10)))

        self.country_button = CustomButton(
            text="+91",
            size_hint=(None, None),
            width=dp(100),
            height=dp(200),
            halign="center",
            padding=(dp(10),dp(15)),
        )
        self.country_menu_items = [
            {"text": "+91 (IN)", "viewclass": "OneLineListItem",
             "on_release": lambda x="+91": self.set_item(self.country_button, x)},
            {"text": "+1 (US)", "viewclass": "OneLineListItem",
             "on_release": lambda x="+1": self.set_item(self.country_button, x)},
            {"text": "+44 (UK)", "viewclass": "OneLineListItem",
             "on_release": lambda x="+44": self.set_item(self.country_button, x)},
            # Add more country codes as needed
        ]
        self.country_menu = MDDropdownMenu(
            caller=self.country_button,
            items=self.country_menu_items,
            width_mult=4,
            position="center",
            max_height=dp(200),
        )
        self.country_button.bind(on_release=lambda x: self.country_menu.open())

        self.phone_field = MDTextField(
            hint_text="Phone Number",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(40),
            padding=(dp(40),0),
            input_filter='int',
            max_text_length=10
        )

        self.phone_layout.add_widget(self.country_button)
        self.phone_layout.add_widget(self.phone_field)
        self.scroll_layout.add_widget(self.phone_layout)

        # Username field
        self.username_field = MDTextField(
            hint_text="Username",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(40),
        )
        self.scroll_layout.add_widget(self.username_field)

        # Password field
        self.password_field = MDTextField(
            hint_text="Password",
            mode="rectangle",
            password=True,
            size_hint=(1, None),
            height=dp(40),
        )
        self.scroll_layout.add_widget(self.password_field)

        # Confirm Password field
        self.confirm_password_field = MDTextField(
            hint_text="Confirm Password",
            mode="rectangle",
            password=True,
            size_hint=(1, None),
            height=dp(40),
        )
        self.scroll_layout.add_widget(self.confirm_password_field)

        # Register button
        self.register_button = MDRaisedButton(
            text="REGISTER",
            size_hint=(1, None),
            height=dp(40),
            md_bg_color=(0.39, 0.58, 0.93, 1)
        )
        self.register_button.bind(on_release=self.validate_form)
        self.scroll_layout.add_widget(self.register_button)

        # Customer Care label and email icon
        self.customer_care_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            width=dp(200),  # Adjust width to center the layout
            height=dp(40),
            spacing=dp(10),
            pos_hint={'center_x': 0.5}
        )
        self.customer_care_label = MDLabel(
            text="Customer Care",
            halign='center',
            size_hint=(None, None),
            width=dp(120),
            height=dp(40),
            pos_hint={'center_y': 0.5}
        )
        self.email_icon = MDIconButton(
            icon='email',
            size_hint=(None, None),
            height=dp(40),
            width=dp(40),
            pos_hint={'center_y': 0.5}
        )

        self.customer_care_layout.add_widget(self.customer_care_label)
        self.customer_care_layout.add_widget(self.email_icon)
        self.scroll_layout.add_widget(self.customer_care_layout)

        self.scroll_view.add_widget(self.scroll_layout)
        self.layout.add_widget(self.scroll_view)
        self.add_widget(self.layout)

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "home"  # Change this if you have a different screen to go back to

    def set_item(self, button, text):
        button.text = text
        button.text_color = get_color_from_hex("#2196f3")
        if button == self.type_button:
            self.type_menu.dismiss()
            if text in ["Company"]:
                self.name_field.hint_text = "Company Name"
            elif text == "Institute":
                self.name_field.hint_text = "Institute Name"
            elif text == "School":
                self.name_field.hint_text = "School Name"
            elif text == "Organization":
                self.name_field.hint_text = "Organization Name"
            elif text == "Business":
                self.name_field.hint_text = "Business Name"
            self.name_field.text = ""  # Clear any previous text
            self.update_role_menu(text)
        elif button == self.role_button:
            self.role_menu.dismiss()
        elif button == self.country_button:
            self.country_menu.dismiss()

    def update_role_menu(self, selected_type):
        role_menu_items = []
        if selected_type == "Company":
            role_menu_items = [
                {"text": "HR", "viewclass": "OneLineListItem",
                 "on_release": lambda x="HR": self.set_item(self.role_button, x)},
                {"text": "Manager", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Manager": self.set_item(self.role_button, x)},
                {"text": "Admin", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Admin": self.set_item(self.role_button, x)},
                {"text": "CEO", "viewclass": "OneLineListItem",
                 "on_release": lambda x="CEO": self.set_item(self.role_button, x)},
            ]
        elif selected_type == "Institute":
            role_menu_items = [
                {"text": "Principal", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Principal": self.set_item(self.role_button, x)},
                {"text": "Teacher", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Teacher": self.set_item(self.role_button, x)},
                {"text": "Staff", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Staff": self.set_item(self.role_button, x)},
                {"text": "Admin", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Admin": self.set_item(self.role_button, x)},
            ]
        elif selected_type == "Organization":
            role_menu_items = [
                {"text": "Leader", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Leader": self.set_item(self.role_button, x)},
                {"text": "Member", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Member": self.set_item(self.role_button, x)},
                {"text": "Volunteer", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Volunteer": self.set_item(self.role_button, x)},
                {"text": "Coordinator", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Coordinator": self.set_item(self.role_button, x)},
            ]
        elif selected_type == "Business":
            role_menu_items = [
                {"text": "Owner", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Owner": self.set_item(self.role_button, x)},
                {"text": "Partner", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Partner": self.set_item(self.role_button, x)},
                {"text": "Employee", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Employee": self.set_item(self.role_button, x)},
                {"text": "Admin", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Admin": self.set_item(self.role_button, x)},
            ]
        elif selected_type == "School":
            role_menu_items = [
                {"text": "Principal", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Principal": self.set_item(self.role_button, x)},
                {"text": "Teacher", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Teacher": self.set_item(self.role_button, x)},
                {"text": "Staff", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Staff": self.set_item(self.role_button, x)},
                {"text": "Admin", "viewclass": "OneLineListItem",
                 "on_release": lambda x="Admin": self.set_item(self.role_button, x)},
            ]

        self.role_menu.items = role_menu_items

    def validate_form(self, instance):
        if self.validate_inputs():
            self.generate_and_send_otp()

    def validate_inputs(self):
        if self.type_button.text == "Select Type":
            toast("Please select a type.")
            return False
        if not self.name_field.text:
            toast("Please enter the name of your Institute/Company.")
            return False
        if self.role_button.text == "Select Role":
            toast("Please select your role.")
            return False
        if not self.email_field.text or not re.match(r"[^@]+@[^@]+\.[^@]+", self.email_field.text):
            toast("Please enter a valid email address.")
            return False
        if not self.phone_field.text or len(self.phone_field.text) != 10:
            toast("Please enter a valid 10-digit phone number.")
            return False
        if not self.username_field.text:
            toast("Please enter a username.")
            return False
        if not self.password_field.text:
            toast("Please enter a password.")
            return False
        if self.password_field.text != self.confirm_password_field.text:
            toast("Passwords do not match.")
            return False
        return True

    def generate_and_send_otp(self):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        service_sid = os.getenv('TWILIO_SERVICE_SID')

        if not account_sid or not auth_token or not service_sid:
            toast("Twilio credentials are not set.")
            return

        client = Client(account_sid, auth_token)
        phone_number = f"{self.country_button.text.strip()}{self.phone_field.text.strip()}"

        try:
            verification = client.verify \
                .v2 \
                .services(service_sid) \
                .verifications \
                .create(to=phone_number, channel='sms')

            self.otp_sid = verification.sid  # Store the OTP verification SID
            toast("OTP sent to your mobile number.")
            self.show_otp_dialog()
        except Exception as e:
            toast(f"Failed to send OTP: {str(e)}")
            print(f"Error details: {str(e)}")  # Log error details

    def show_otp_dialog(self):
        self.otp_input = MDTextField(
            hint_text="Enter OTP",
            size_hint=(1, None),
            height=dp(48),
        )
        self.otp_dialog = MDDialog(
            title="Enter OTP",
            type="custom",
            content_cls=self.otp_input,
            buttons=[
                MDRaisedButton(
                    text="VERIFY",
                    on_release=self.verify_otp
                ),
                MDRaisedButton(
                    text="CANCEL",
                    on_release=lambda x: self.otp_dialog.dismiss()
                ),
            ],
        )
        self.otp_dialog.open()
    def verify_otp(self, instance):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        service_sid = os.getenv('TWILIO_SERVICE_SID')

        if not account_sid or not auth_token or not service_sid:
            toast("Twilio credentials are not set.")
            return

        entered_otp = self.otp_input.text.strip()  # Ensure it's a string and remove any leading/trailing whitespace
        phone_number = f"{self.country_button.text.strip()}{self.phone_field.text.strip()}"

        client = Client(account_sid, auth_token)

        try:
            verification_check = client.verify \
                .v2 \
                .services(service_sid) \
                .verification_checks \
                .create(to=phone_number, code=entered_otp)

            if verification_check.status == "approved":
                toast("OTP verified successfully!")
                self.otp_dialog.dismiss()
                self.register_user()
            else:
                toast("Failed to verify OTP.")
                print(f"Verification status: {verification_check.status}")  # Log status for debugging
        except Exception as e:
            toast(f"Failed to verify OTP: {e}")
            print(f"Error details: {str(e)}")  # Log error details

    def register_user(self):
        type_ = self.type_button.text
        name = self.name_field.text
        role = self.role_button.text
        email = self.email_field.text
        phone = self.phone_field.text
        username = self.username_field.text
        password = self.password_field.text
        country_code = self.country_button.text

        # Prepare user data for Firebase
        user_data = {
            f"{type_}Name": name,
            "email": email,
            "phone": f"{country_code} {phone}",
            "username": username,
            "password": password  # Note: In a real-world app, never store plaintext passwords. Use hashing.
        }

        try:
            # Write user data to Firebase Realtime Database
            ref = db.reference(f'{type_}/{name}/{role}/{username}')
            ref.set(user_data)

            # Show a success message and clear the form
            toast("Registration successful!")
            self.clear_form()

            self.manager.transition = SlideTransition(direction="up")
            self.manager.current = "login"
        except Exception as e:
            toast(f"Registration failed: {str(e)}")
    def clear_form(self):
        self.type_button.text = "Select Type"
        self.name_field.text = ""
        self.role_button.text = "Select Role"
        self.email_field.text = ""
        self.phone_field.text = ""
        self.username_field.text = ""
        self.password_field.text = ""
        self.confirm_password_field.text = ""