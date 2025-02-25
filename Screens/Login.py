import os
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import SlideTransition
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivy.properties import StringProperty
from kivy.graphics import Color, Line
from firebase_admin import db
from kivymd.toast import toast
import string
import random
from kivy.core.text import LabelBase

# Construct the path to the font file
font_path = os.path.join(os.path.dirname(__file__), 'fonts/FontBundles-Olivia-Script', 'Olivia-Regular.ttf')

# Register the custom font
LabelBase.register(name='Olivia-Regular', fn_regular=font_path)


class CustomOneLineIconListItem(OneLineIconListItem):
    icon = StringProperty()


class CustomButton(MDRaisedButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgb=get_color_from_hex('#bdbdbd'))
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)), width=1.2)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))


class Login(MDScreen):
    def __init__(self, **kwargs):
        super(Login, self).__init__(**kwargs)

        # Main layout
        self.layout = MDBoxLayout(orientation='vertical', spacing=dp(25))

        # Top app bar
        self.top_bar = MDTopAppBar(
            title="Login",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            size_hint_y=None,
            height=dp(50)
        )
        self.layout.add_widget(self.top_bar)

        # Scrollable content
        self.scroll_view = ScrollView()
        self.scroll_layout = MDBoxLayout(orientation='vertical', padding=[dp(20), dp(15), dp(20), dp(20)],
                                         spacing=dp(20), size_hint_y=None)
        self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))

        # Type of dropdown
        self.type_of_button = CustomButton(
            text="Type of",
            size_hint=(1, None),
            height=dp(40),
            halign="left",
            padding=(dp(10), 0),
            md_bg_color=get_color_from_hex("#FAFAFA"),
            text_color=get_color_from_hex("#a4a4a4")
        )
        self.type_of_menu = MDDropdownMenu(
            caller=self.type_of_button,
            items=[],
            width_mult=4,
            position="center"
        )
        self.type_of_button.bind(on_release=self.open_type_of_menu)
        self.scroll_layout.add_widget(self.type_of_button)

        # Company dropdown
        self.company_button = CustomButton(
            text="Select Your Company",
            size_hint=(1, None),
            height=dp(40),
            halign="left",
            padding=(dp(10), 0),
            md_bg_color=get_color_from_hex("#FAFAFA"),
            text_color=get_color_from_hex("#a4a4a4")
        )
        self.company_menu = MDDropdownMenu(
            caller=self.company_button,
            items=[],
            width_mult=4,
            position="center",
        )
        self.company_button.bind(on_release=self.open_company_menu)
        self.scroll_layout.add_widget(self.company_button)

        # Role dropdown
        self.role_button = CustomButton(
            text="Select Role",
            size_hint=(1, None),
            height=dp(40),
            halign="left",
            padding=(dp(10), 0),
            md_bg_color=get_color_from_hex("#FAFAFA"),
            text_color=get_color_from_hex("#a4a4a4")
        )
        self.role_menu = MDDropdownMenu(
            caller=self.role_button,
            items=[],
            width_mult=4,
            position="center",
        )
        self.role_button.bind(on_release=self.update_role_menu)
        self.scroll_layout.add_widget(self.role_button)

        # Username dropdown
        self.username_button = CustomButton(
            text="Select Your Username",
            size_hint=(1, None),
            height=dp(40),
            halign="left",
            padding=(dp(10), 0),
            md_bg_color=get_color_from_hex("#FAFAFA"),
            text_color=get_color_from_hex("#a4a4a4")
        )
        self.username_menu = MDDropdownMenu(
            caller=self.username_button,
            items=[],
            width_mult=4,
            position="center",
        )
        self.username_button.bind(on_release=self.open_username_menu)
        self.scroll_layout.add_widget(self.username_button)

        # Password field
        self.password_field = MDTextField(
            hint_text="Password",
            password=True,
            size_hint=(1, None),
            height=dp(40),
            mode="rectangle"
        )
        self.scroll_layout.add_widget(self.password_field)

        # CAPTCHA
        self.captcha_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40), spacing=dp(10),
                                          pos_hint={'center_x': 0.5})

        self.captcha_input = MDTextField(
            hint_text="Enter CAPTCHA",
            size_hint=(0.5, None),
            height=dp(40),
            mode="rectangle"
        )
        self.captcha_layout.add_widget(self.captcha_input)

        self.captcha_text = self.generate_captcha()
        self.captcha_label = MDLabel(
            text=self.captcha_text,
            halign='center',
            size_hint=(0.4, None),
            height=dp(40),
            theme_text_color="Secondary",
            font_name='Olivia-Regular'
        )
        self.captcha_layout.add_widget(self.captcha_label)

        self.refresh_captcha_button = MDIconButton(
            icon="refresh",
            size_hint=(0.1, None),
            height=dp(40),
            width=dp(40),
            pos_hint={'center_y': 0.5},
            on_release=self.refresh_captcha
        )
        self.captcha_layout.add_widget(self.refresh_captcha_button)

        self.scroll_layout.add_widget(self.captcha_layout)

        # Phone number field
        self.phone_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            spacing=dp(10),
            padding=(dp(0), dp(10),dp(0),dp(10))
        )

        self.country_button = CustomButton(
            text="+91",
            size_hint=(None, None),
            width=dp(80),
            height=dp(40),
            halign="center",
            padding=(dp(5), 0),
            md_bg_color=get_color_from_hex("#FAFAFA"),
            text_color=get_color_from_hex("#2196f3")
        )
        self.country_menu_items = [
            {"text": "+91 (IN)", "viewclass": "OneLineListItem",
             "on_release": lambda x="+91": self.set_country_code(x)},
            {"text": "+1 (US)", "viewclass": "OneLineListItem",
             "on_release": lambda x="+1": self.set_country_code(x)},
            {"text": "+44 (UK)", "viewclass": "OneLineListItem",
             "on_release": lambda x="+44": self.set_country_code(x)},
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
            padding=(dp(70), dp(0)),
            input_filter='int',
            max_text_length=10
        )

        self.phone_layout.add_widget(self.country_button)
        self.phone_layout.add_widget(self.phone_field)

        # Inside the __init__ method, after creating the fields
        self.password_field.bind(text=self.validate_form)
        self.captcha_input.bind(text=self.validate_form)
        self.phone_field.bind(text=self.validate_form)

        # Login button
        self.login_button = CustomButton(
            text="LOGIN",
            size_hint=(1, None),
            height=dp(40),
            halign="center",
            padding=(dp(10), 0)
        )
        self.scroll_layout.add_widget(self.login_button)

        # Bind the login button to the validate_login method
        self.login_button.bind(on_release=self.validate_login)

        # Add Forgot Details and WhatsApp icon
        self.forgot_details_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            height=dp(40),
            spacing=dp(10),
            pos_hint={'center_x': 0.5}
        )
        self.forgot_details_label = MDLabel(
            text='Forgot Details',
            halign='center',
            size_hint=(None, None),
            width=dp(120),
            height=dp(40),
            pos_hint={'center_y': 0.5},
            valign='middle'
        )
        self.whatsapp_button = MDIconButton(
            icon="whatsapp",
            size_hint=(None, None),
            height=dp(40),
            width=dp(40),
            pos_hint={'center_y': 0.5},
            icon_size=dp(24)
        )
        self.forgot_details_layout.add_widget(self.forgot_details_label)
        self.forgot_details_layout.add_widget(self.whatsapp_button)
        self.scroll_layout.add_widget(self.forgot_details_layout)

        self.scroll_view.add_widget(self.scroll_layout)
        self.layout.add_widget(self.scroll_view)
        self.add_widget(self.layout)

        # Initialize selected values
        self.selected_type_of = None
        self.selected_company = None
        self.selected_role = None
        self.selected_username = None

        # Fetch and populate the "Type of" dropdown
        self.populate_type_of_dropdown()

        # Bind text input fields to the validation method
        self.password_field.bind(text=self.validate_form)
        self.captcha_input.bind(text=self.validate_form)

    def set_country_code(self, code):
        self.country_button.text = code
        self.country_menu.dismiss()

    def update_role_menu(self, instance):
        role_menu_items = []
        if self.selected_type_of == "Company":
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
        elif self.selected_type_of in ["Institute", "School"]:
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
        elif self.selected_type_of == "Organization":
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
        elif self.selected_type_of == "Business":
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

        self.role_menu.items = role_menu_items
        self.role_menu.open()

    def generate_captcha(self, length=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def refresh_captcha(self, *args):
        self.captcha_text = self.generate_captcha()
        self.captcha_label.text = self.captcha_text

    def set_item(self, button, text):
        button.text = text
        button.text_color = get_color_from_hex("#2196f3")
        if button == self.type_of_button:
            self.type_of_menu.dismiss()
            self.update_company_button_title(text)
            self.selected_type_of = text
        elif button == self.company_button:
            self.company_menu.dismiss()
            self.selected_company = text
        elif button == self.role_button:
            self.role_menu.dismiss()
            self.selected_role = text
            self.update_login_fields()
            if self.selected_role == "Teacher":
                self.populate_teacher_dropdown()
            else:
                self.populate_username_dropdown()
        elif button == self.username_button:
            self.username_menu.dismiss()
            self.selected_username = text
        self.validate_form()

    def populate_teacher_dropdown(self):
        if self.selected_type_of and self.selected_company:
            ref = db.reference(f'{self.selected_type_of}/{self.selected_company}/Teachers')
            data = ref.get()
            if data:
                menu_items = [
                    {"text": username, "viewclass": "OneLineListItem",
                     "on_release": lambda x=username: self.set_item(self.username_button, x)}
                    for username in data
                ]
                self.username_menu.items = menu_items
    def update_company_button_title(self, type_of):
        titles = {
            "Company": "Select Your Company",
            "Institute": "Select Your Institute",
            "School": "Select Your School",
            "Organization": "Select Your Organization",
            "Business": "Select Your Business",
        }
        self.company_button.text = titles.get(type_of, "Select Your Company")

    def open_type_of_menu(self, instance):
        self.populate_type_of_dropdown()
        self.type_of_menu.open()

    def open_company_menu(self, instance):
        if self.selected_type_of:
            self.update_company_menu_items(self.selected_type_of)
            self.company_menu.open()

    def open_username_menu(self, instance):
        if self.selected_type_of and self.selected_company and self.selected_role:
            self.populate_username_dropdown()
            self.username_menu.open()

    def update_company_menu_items(self, type_of):
        ref = db.reference(f'/{type_of}')
        data = ref.get()
        if data:
            menu_items = [
                {"text": company, "viewclass": "OneLineListItem",
                 "on_release": lambda x=company: self.set_item(self.company_button, x)}
                for company in data
            ]
            self.company_menu.items = menu_items

    def populate_username_dropdown(self):
        if self.selected_type_of and self.selected_company and self.selected_role:
            ref = db.reference(f'/{self.selected_type_of}/{self.selected_company}/{self.selected_role}')
            data = ref.get()
            if data:
                menu_items = [
                    {"text": username, "viewclass": "OneLineListItem",
                     "on_release": lambda x=username: self.set_item(self.username_button, x)}
                    for username in data
                ]
                self.username_menu.items = menu_items

    def populate_type_of_dropdown(self):
        ref = db.reference('/')
        data = ref.get()
        if data:
            menu_items = [
                {"text": item, "viewclass": "OneLineListItem",
                 "on_release": lambda x=item: self.set_item(self.type_of_button, x)}
                for item in data
            ]
            self.type_of_menu.items = menu_items

    def go_back(self):
        self.clear_fields()
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'home'

    def fetch_phone_number_and_country_code(self):
        if self.selected_type_of and self.selected_company and self.selected_role and self.selected_username:
            ref = db.reference(f'{self.selected_type_of}/{self.selected_company}/Teachers/{self.selected_username}')
            data = ref.get()
            if data:
                return data.get('Country Code'), data.get('Phone Number')
        return None, None

    def fetch_password(self):
        if self.selected_type_of and self.selected_company and self.selected_role and self.selected_username:
            ref = db.reference(
                f'/{self.selected_type_of}/{self.selected_company}/{self.selected_role}/{self.selected_username}')
            data = ref.get()
            if data:
                return data.get('password')  # Assuming the password is stored under the key 'password'
        return None

    def validate_captcha(self):
        return self.captcha_input.text == self.captcha_text

    def update_login_fields(self):
        # Remove all optional fields first
        if self.password_field in self.scroll_layout.children:
            self.scroll_layout.remove_widget(self.password_field)
        if self.captcha_layout in self.scroll_layout.children:
            self.scroll_layout.remove_widget(self.captcha_layout)
        if self.phone_layout in self.scroll_layout.children:
            self.scroll_layout.remove_widget(self.phone_layout)

        # Find the index of the username button
        username_index = self.scroll_layout.children.index(self.username_button)

        if self.selected_role in ["Staff", "Teacher"]:
            # Add phone layout just below the username button
            self.scroll_layout.add_widget(self.phone_layout, index=username_index)
        else:
            # Add password field and then captcha layout just below the username button
            self.scroll_layout.add_widget(self.password_field, index=username_index)
            self.scroll_layout.add_widget(self.captcha_layout, index=username_index)

        self.validate_form()

    def validate_form(self, *args):
        if self.selected_role in ["Staff", "Teacher"]:
            if self.selected_username and self.phone_field.text:
                self.login_button.disabled = False
            else:
                self.login_button.disabled = True
        else:
            if self.selected_username and self.password_field.text:
                self.login_button.disabled = False
            else:
                self.login_button.disabled = True

    def validate_login(self, instance):
        if self.selected_role in ["Staff", "Teacher"]:
            # Fetch the phone number and country code from the database
            ref = db.reference(f'{self.selected_type_of}/{self.selected_company}/Teachers/{self.selected_username}')
            data = ref.get()
            if data:
                db_country_code = data.get("Country Code")
                db_phone_number = data.get("Phone Number")

                # Verify the phone number and country code
                if db_country_code == self.country_button.text.strip() and db_phone_number == self.phone_field.text.strip():
                    # Send login data to the SchoolAdmin screen
                    school_admin_screen = self.manager.get_screen('school_teacher')
                    school_admin_screen.update_content(
                        type_of=self.selected_type_of,
                        company=self.selected_company,
                        role=self.selected_role,
                        username=self.selected_username
                    )
                    self.clear_fields()
                    self.manager.transition = SlideTransition(direction="down")
                    self.manager.current = "school_teacher"
                else:
                    toast("Invalid phone number.")
            else:
                toast("User data not found.")
        else:
            if not self.validate_captcha():
                toast("Invalid CAPTCHA, please try again.")
                self.refresh_captcha()
                return

            stored_password = self.fetch_password()
            if stored_password and stored_password == self.password_field.text:
                toast("Login successful!")
                # Proceed to the next screen or functionality
                if self.selected_type_of == "School":
                    if self.selected_role == "Principal" or self.selected_role == "Admin":
                        # Send login data to the SchoolAdmin screen
                        school_admin_screen = self.manager.get_screen('school_admin')
                        school_admin_screen.update_content(
                            type_of=self.selected_type_of,
                            company=self.selected_company,
                            role=self.selected_role,
                            username=self.selected_username
                        )
                        self.clear_fields()
                        self.manager.transition = SlideTransition(direction="down")
                        self.manager.current = "school_admin"
                    elif self.selected_role == "Staff" or self.selected_role == "Teacher":
                        # Send login data to the SchoolAdmin screen
                        school_admin_screen = self.manager.get_screen('school_teacher')
                        school_admin_screen.update_content(
                            type_of=self.selected_type_of,
                            company=self.selected_company,
                            role=self.selected_role,
                            username=self.selected_username
                        )
                        self.clear_fields()
                        self.manager.transition = SlideTransition(direction="down")
                        self.manager.current = "school_teacher"
            else:
                toast("Invalid password")
                # Show an error message or take appropriate action

    def clear_fields(self):
        self.type_of_button.text = "Type of"
        self.type_of_button.text_color = get_color_from_hex("#a4a4a4")
        self.company_button.text = "Select Your Company"
        self.company_button.text_color = get_color_from_hex("#a4a4a4")
        self.role_button.text = "Select Your Role"
        self.role_button.text_color = get_color_from_hex("#a4a4a4")
        self.username_button.text = "Select Your Username"
        self.username_button.text_color = get_color_from_hex("#a4a4a4")
        self.password_field.text = ""
        self.captcha_input.text = ""
        self.refresh_captcha()

        self.selected_type_of = None
        self.selected_company = None
        self.selected_role = None
        self.selected_username = None

        self.phone_field.text = ""
        self.update_login_fields()