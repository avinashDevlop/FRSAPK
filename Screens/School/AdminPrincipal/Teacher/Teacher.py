from kivy.uix.image import AsyncImage
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse, StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.uix.scrollview import ScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.gridlayout import MDGridLayout
from kivy.metrics import dp
import requests
import time
import logging
from datetime import datetime, timedelta
from firebase_admin import db

class CircularImage(AsyncImage):
    def __init__(self, **kwargs):
        super(CircularImage, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            StencilPush()
            Ellipse(pos=self.pos, size=self.size)
            StencilUse()
            if self.texture:
                Color(1, 1, 1, 1)
                Ellipse(pos=self.pos, size=self.size, texture=self.texture)
            StencilUnUse()
            StencilPop()

    def on_load(self, *args):
        self.update_canvas()

class TeacherScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields = {
            "schoolName": None,
            "typeOf": None,
            "role":None,
            "userName":None
        }

        self.layout = MDBoxLayout(orientation='vertical')

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

        self.scroll_view = ScrollView(do_scroll_x=False)
        self.content_layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        self.scroll_view.add_widget(self.content_layout)
        self.layout.add_widget(self.scroll_view)

        self.add_widget(self.layout)

    def on_pre_enter(self, *args):
        self.check_and_update_layout()

    def update_fields(self, school_name, type_of, role, username):
        self.fields["typeOf"] = type_of
        self.fields["schoolName"] = school_name
        self.fields["role"] = role
        self.fields["userName"] = username
        self.check_and_update_layout()

    def check_and_update_layout(self):
        if self.fields["schoolName"]:
            ref = db.reference(f"{self.fields['typeOf']}/{self.fields['schoolName']}/Teachers")
            teacher_data = ref.get()
            if teacher_data:
                self.display_teachers(teacher_data)
            else:
                self.add_icon()

    def make_request(self, url, retries=3, delay=5):
        for attempt in range(retries):
            try:
                response = requests.get(url)
                return response
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}, retrying in {delay} seconds...")
                time.sleep(delay)
        return None

    def get_attendance_status(self, teacher_name):
        today = datetime.now()
        formatted_month = today.strftime('%m')  # Format the month with leading zeros (e.g., 04, 05)
        
        ref = db.reference(f"{self.fields['typeOf']}/{self.fields['schoolName']}/Teachers/{teacher_name}/attendance/{today.year}/{formatted_month}/{today.day}/status")
        attendance_status = ref.get()

        return attendance_status

    def get_leave_status(self, teacher_name):
        today = datetime.now().date()  # Get current date as a datetime object

        # Firebase reference for leave letters
        ref = db.reference(f"{self.fields['typeOf']}/{self.fields['schoolName']}/Teachers/{teacher_name}/LeaveLetters")
        leave_letters = ref.get()

        if leave_letters:
            for leave_entry in leave_letters.keys():
                leave_data = leave_letters[leave_entry]
                try:
                    # Check if 'From Date' and 'To Date' exist (multi-day leave case) and are not empty
                    from_date = leave_data.get('From Date', '').strip()
                    to_date = leave_data.get('To Date', '').strip()
                    
                    if from_date and to_date:
                        # Parse 'From Date' and 'To Date' in dd-mm-yyyy format
                        start_date = datetime.strptime(from_date, '%d-%m-%Y').date()
                        end_date = datetime.strptime(to_date, '%d-%m-%Y').date()

                        # Check if today's date is within the leave range or the leave starts in the future
                        if today <= end_date:
                            return leave_data  # Return leave data if within range or starting tomorrow
                    elif from_date:  # Handle single-day leave where 'From Date' is the key
                        leave_date = datetime.strptime(from_date, '%d-%m-%Y').date()

                        # Check if today is before or matches the leave date
                        if leave_date >= today:
                            return leave_data  # Return leave data if it's a single-day leave starting today or in the future
                except (ValueError, KeyError) as e:
                    # Log any issues with date parsing or missing fields
                    logging.error(f"[Error processing leave for {teacher_name}] {e}")

        # Debug: Log when no leave data is found
        return None  # Return None if no applicable leave is found

    
    def add_icon(self):
        # Clear the content layout first
        self.content_layout.clear_widgets()

        # Create the icon card
        icon_card = MDCard(
            size_hint=(None, None), 
            size=(150, 150), 
            elevation=1,
            radius=[20],
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Center the card
        )
        
        # Load the icon image
        icon = AsyncImage(source='./assets/images/ImgSchool/AboutSchoolAdd.png')
        icon_card.add_widget(icon)
        
        # Add the icon card directly to the content layout
        self.content_layout.add_widget(icon_card)

    def display_teachers(self, data):
        # Clear the content layout to start fresh
        self.content_layout.clear_widgets()

        # Create the layouts for Leave Letters, Present, and Absent sections
        self.leave_layout = self.create_attendance_layout("Leave Letters")
        self.present_layout = self.create_attendance_layout("Present")
        self.absent_layout = self.create_attendance_layout("Absent")

        # Add the layouts to the main content layout initially
        self.content_layout.add_widget(self.leave_layout)
        self.content_layout.add_widget(self.present_layout)
        self.content_layout.add_widget(self.absent_layout)

        # Loop through the teacher data dictionary
        for teacher_name, teacher_data in data.items():
            # Check attendance status for the teacher
            attendance_status = self.get_attendance_status(teacher_name)

            # If present, add to the present section
            if attendance_status == "present":
                present_teacher_card = self.create_teacher_card(teacher_name, teacher_data, is_leave_card=False)
                self.present_layout.children[0].add_widget(present_teacher_card)
            else:
                # If absent or no attendance, add to the absent section
                absent_teacher_card = self.create_teacher_card(teacher_name, teacher_data, is_leave_card=False)
                self.absent_layout.children[0].add_widget(absent_teacher_card)

            # Check for leave letters for the teacher and add them to the Leave Letters section if found
            leave_letter_data = self.get_leave_status(teacher_name)
            if leave_letter_data:
                leave_teacher_card = self.create_teacher_card(teacher_name, teacher_data, is_leave_card=True)
                self.leave_layout.children[0].add_widget(leave_teacher_card)

        # Check if any layout has no cards, and remove it if it's empty
        if len(self.leave_layout.children[0].children) == 0:
            self.content_layout.remove_widget(self.leave_layout)
        if len(self.present_layout.children[0].children) == 0:
            self.content_layout.remove_widget(self.present_layout)
        if len(self.absent_layout.children[0].children) == 0:
            self.content_layout.remove_widget(self.absent_layout)
        
    def create_attendance_layout(self, title):
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        label = MDLabel(
            text=title,
            halign='left',
            font_style='H6',
            size_hint_y=None,
            height=40,
            padding=(20, 10)
        )
        layout.add_widget(label)

        grid_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        layout.add_widget(grid_layout)

        return layout

    def create_registration_layout(self, title, teachers, registration_status):
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        label = MDLabel(
            text=title,
            halign='left',
            font_style='H6',
            size_hint_y=None,
            height=40,
            padding=(20, 10)
        )
        layout.add_widget(label)

        grid_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        layout.add_widget(grid_layout)

        # Only add unregistered teachers to this layout
        for teacher_name, teacher_data in teachers.items():
            if teacher_data.get('registration_status', True) == registration_status:
                teacher_card = self.create_teacher_card(teacher_name, teacher_data, is_leave_card=False)
                grid_layout.add_widget(teacher_card)

        return layout

    def show_leave_dialog(self, teacher_name, leave_letter_data):
        # Define the correct order for the keys
        ordered_fields = [
            ("Teacher", teacher_name),  # Use teacher_name directly here
            ("Leave Type", leave_letter_data.get("Leave Type", "Unknown")),
            ("Number of Leaves", leave_letter_data.get("Number of Leaves", "Unknown")),
            ("From Date", leave_letter_data.get("From Date", "Unknown")),
            ("Reason for Leave", leave_letter_data.get("Reason for Leave", "Unknown")),
            ("Status", leave_letter_data.get("Status", "Unknown"))
        ]

        # If the number of leaves is greater than 1, add the "To Date" field
        number_of_leaves = leave_letter_data.get("Number of Leaves", 1)
        if int(number_of_leaves) > 1:
            ordered_fields.insert(4, ("To Date", leave_letter_data.get("To Date", "Unknown")))

        # Create a grid layout for the dialog content
        content = MDGridLayout(
            cols=2,  # Two columns: one for keys, one for values
            spacing=10,
            adaptive_height=True  # Let it adjust height based on content
        )

        # Add individual labels for each ordered field
        for key, value in ordered_fields:
            label_key = MDLabel(
                text=f"{key}:",
                theme_text_color="Secondary",  # Key in secondary color
                font_style="Subtitle1",
                size_hint_y=None,
                height=dp(30),
            )
            label_value = MDLabel(
                text=value,
                theme_text_color="Primary",  # Value in primary color
                font_style="Body1",
                size_hint_y=None,
                height=dp(30),
            )

            # Add key-value pair to the grid layout
            content.add_widget(label_key)
            content.add_widget(label_value)

        # Create the dialog
        self.dialog = MDDialog(
            title=f"Leave Letter for {teacher_name}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Approve",
                    on_release=lambda x: self.approve_leave(teacher_name, leave_letter_data)
                ),
                MDRaisedButton(
                    text="Decline",
                    on_release=lambda x: self.decline_leave(teacher_name, leave_letter_data)
                ),
                MDRaisedButton(
                    text="Close",
                    on_release=self.close_dialog
                )
            ]
        )
        self.dialog.open()

    def decline_leave(self, teacher_name, leave_letter_data):
        # Extract relevant data from leave_letter_data
        number_of_leaves = leave_letter_data.get('Number of Leaves')
        from_date = leave_letter_data.get('From Date')
        to_date = leave_letter_data.get('To Date') if leave_letter_data.get('To Date') else ''

        # Construct the Firebase reference
        ref_path = f"{self.fields['typeOf']}/{self.fields['schoolName']}/Teachers/{teacher_name}/LeaveLetters"
        ref = db.reference(ref_path)
        
        print(number_of_leaves,from_date,to_date)
        # Handle single-day or multiple-day leave based on 'Number of Leaves'
        if number_of_leaves == '1':
            leave_ref = ref.child(from_date).child('Status')
        else:
            date_range = f"{from_date}:{to_date}"
            leave_ref = ref.child(date_range).child('Status')
        
        # Update the leave status to 'Declined'
        leave_ref.set('Declined')
        
        # Dismiss the dialog
        self.dialog.dismiss()

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def approve_leave(self, teacher_name, leave_letter_data):
        # Extract relevant data from leave_letter_data
        number_of_leaves = leave_letter_data.get('Number of Leaves')
        from_date = leave_letter_data.get('From Date')
        to_date = leave_letter_data.get('To Date') if leave_letter_data.get('To Date') else ''

        # Construct the Firebase reference path for leave status
        ref_path = f"{self.fields['typeOf']}/{self.fields['schoolName']}/Teachers/{teacher_name}/LeaveLetters"
        ref = db.reference(ref_path)

        print(number_of_leaves, from_date, to_date)

        # Handle single-day or multiple-day leave based on 'Number of Leaves'
        if number_of_leaves == '1':
            # Update leave status to 'Approved'
            leave_ref = ref.child(from_date).child('Status')
            leave_ref.set('Approved')

            # Set attendance for the single day to "absent"
            day, month, year = from_date.split('-')
            attendance_ref = db.reference(f"{self.fields['typeOf']}/{self.fields['schoolName']}/Teachers/{teacher_name}/attendance/{year}/{month}/{day}/status")
            attendance_ref.set("absent")

        else:
            # Multi-day leave handling
            date_range = f"{from_date}:{to_date}"
            leave_ref = ref.child(date_range).child('Status')
            leave_ref.set('Approved')

            # Set attendance for each day in the date range to "absent"
            start_date = datetime.strptime(from_date, '%d-%m-%Y')
            end_date = datetime.strptime(to_date, '%d-%m-%Y')
            current_date = start_date

            while current_date <= end_date:
                day = current_date.strftime('%d')
                month = current_date.strftime('%m')
                year = current_date.strftime('%Y')

                # Update the Firebase attendance status for each day to "absent"
                attendance_ref = db.reference(f"{self.fields['typeOf']}/{self.fields['schoolName']}/Teachers/{teacher_name}/attendance/{year}/{month}/{day}/status")
                attendance_ref.set("absent")

                # Move to the next day
                current_date += timedelta(days=1)

        print(f"Leave for {teacher_name} has been approved.")
        self.dialog.dismiss()


    def create_teacher_card(self, teacher_name, teacher_data, is_leave_card=False):
        # Create the card for each teacher
        card = MDCard(orientation='vertical', size_hint=(None, None), size=(100, 150), padding=5, elevation=2)

        # Check registration status and gender, and set image accordingly
        registration_status = teacher_data.get('registration_status', False)
        gender = teacher_data.get('Gender', '').lower()

        if registration_status and 'image_url' in teacher_data:
            icon_source = teacher_data['image_url']
        else:
            icon_source = 'assets/images/ImgSchool/teacherFemale.png' if gender == 'female' else 'assets/images/ImgSchool/teacherMale.png'

        # Create the CircularImage with the appropriate icon source
        avatar = CircularImage(
            size=(70, 70),
            pos_hint={'center_x': 0.5},
            allow_stretch=True,
            keep_ratio=True,
            source=icon_source
        )
        card.add_widget(avatar)

        name_label = MDLabel(
            text=teacher_data.get('Teacher Name', 'Unknown'),
            halign='center',
            font_style='Caption',
            size_hint_y=None,
            height=30,
            padding=(0, 0)
        )
        card.add_widget(name_label)

        subject_label = MDLabel(
            text=teacher_data.get('Subject', 'Unknown'),
            halign='center',
            font_style='Caption',
            size_hint_y=None,
            height=30,
            padding=(0, 0)
        )
        card.add_widget(subject_label)

        # Bind the card click event to open the leave dialog if leave letter exists
        card.bind(on_release=lambda x: self.open_leave_dialog(teacher_name))

        return card

    def open_leave_dialog(self, teacher_name):
        """Fetch the leave data and open the dialog box for the teacher."""
        # Fetch leave status
        leave_letter_data = self.get_leave_status(teacher_name)

        # Check if leave data is available
        if leave_letter_data:
            self.show_leave_dialog(teacher_name, leave_letter_data)  # Call your dialog function
        else:
            print(f"No leave data available for {teacher_name}.")


    def fetch_live_data(self, teacher_name):
        """Fetch the latest attendance or leave status of the teacher from Firebase and update the UI."""
        # Fetch live attendance status
        attendance_status = self.get_attendance_status(teacher_name)
        
        # Fetch live leave status
        leave_letter_data = self.get_leave_status(teacher_name)

        # Now display the appropriate dialog or update the UI based on the live data
        if leave_letter_data:
            self.show_leave_dialog(teacher_name, leave_letter_data)
        elif attendance_status:
            # Handle attendance status display (e.g., update card or show a message)
            print(f"Attendance status for {teacher_name}: {attendance_status}")
        else:
            print(f"No attendance or leave data available for {teacher_name}.")


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
        role = self.fields["role"]
        userName = self.fields["userName"]
        about_screen = self.manager.get_screen('school_admin_teacherDetails')
        about_screen.update_fields(school_name, type_of, role, userName)
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'school_admin_teacherDetails'