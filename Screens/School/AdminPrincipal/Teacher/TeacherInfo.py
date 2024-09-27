from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivy.uix.image import AsyncImage
from kivymd.uix.scrollview import MDScrollView
from kivymd.toast import toast
from kivy.graphics import Ellipse, StencilPush, StencilUse, StencilUnUse, StencilPop
from firebase_admin import db
class TeacherInfoScreen(MDScreen):
    def update_fields(self, school_name, type_of, role, teacher_name):
        self.DBLocation["typeOf"] = type_of
        self.DBLocation["schoolName"] = school_name
        self.DBLocation["TeacherName"] = teacher_name
        self.DBLocation["role"] = 'Teacher'
        self.load_teacher_data()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DBLocation = {
            "typeOf": "",
            "schoolName": "",
            "TeacherName": "",
            "role":"",
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

        # Icon (Circular Image)
        icon_card = MDCard(size_hint=(None, None), size=(100, 100), pos_hint={'center_x': 0.5}, md_bg_color=[0, 0, 0, 0], elevation=0)
        icon_box = MDBoxLayout(size_hint=(None, None), size=(100, 100))

        # Create a circular image
        self.icon = AsyncImage(
            source='assets/images/ImgSchool/teacherMale.png',  # Default image
            allow_stretch=True,
            keep_ratio=True,
        )
        
        # Add stencil and ellipse to make the image circular
        with icon_box.canvas.before:
            StencilPush()
            Ellipse(pos=icon_box.pos, size=icon_box.size)
            StencilUse()

        icon_box.add_widget(self.icon)

        with icon_box.canvas.after:
            StencilUnUse()
            StencilPop()

        # Bind the update of the ellipse to the icon_box's size and pos
        icon_box.bind(pos=self.update_ellipse, size=self.update_ellipse)

        icon_card.add_widget(icon_box)
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

        # Add Attendance and Leave Letter Cards
        self.add_attendance_and_leave_options()

        # Add scroll view to main layout
        layout.add_widget(scroll)

        self.add_widget(layout)

    def add_attendance_and_leave_options(self):
        # Attendance Card
        attendance_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height="80dp",
            padding=20,
            md_bg_color=[0.7, 0.5, 1, 1],  # Background color (purple)
            ripple_behavior=True,
            on_release=lambda x: self.show_attendance(),
        )
        attendance_label = MDLabel(
            text="Attendance",
            halign="center",
            theme_text_color="Primary",
            font_style="H6",
        )
        attendance_card.add_widget(attendance_label)
        self.content.add_widget(attendance_card)

        # Leave Letter Card
        leave_letter_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height="80dp",
            padding=20,
            md_bg_color=[0.7, 0.5, 1, 1],  # Background color (purple)
            ripple_behavior=True,
            on_release=lambda x: self.show_leave_letter(),
        )
        leave_letter_label = MDLabel(
            text="Leave Letter",
            halign="center",
            theme_text_color="Primary",
            font_style="H6",
        )
        leave_letter_card.add_widget(leave_letter_label)
        self.content.add_widget(leave_letter_card)

    def show_attendance(self):
        screen = self.manager.get_screen('school_admin_teacherInfoAttendence')
        screen.update_fields(self.DBLocation["schoolName"], self.DBLocation["typeOf"], self.DBLocation["role"], self.DBLocation["TeacherName"])
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_admin_teacherInfoAttendence'

    def show_leave_letter(self):
        screen = self.manager.get_screen('school_admin_teacherInfoLeaveLetter')
        screen.update_fields(self.DBLocation["schoolName"], self.DBLocation["typeOf"], self.DBLocation["role"], self.DBLocation["TeacherName"])
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_admin_teacherInfoLeaveLetter'

    def update_ellipse(self, instance, value):
        """ Updates the Ellipse based on the icon_box's size and position """
        for instr in instance.canvas.before.children:
            if isinstance(instr, Ellipse):
                instr.pos = instance.pos
                instr.size = instance.size

    def load_teacher_data(self):
        if all(self.DBLocation.values()):
            ref = db.reference(
                f"{self.DBLocation['typeOf']}/{self.DBLocation['schoolName']}/Teachers/{self.DBLocation['TeacherName']}")
            teacher_data = ref.get()
            
            if teacher_data:
                self.teacher_name_label.text = self.DBLocation['TeacherName']

                # Update all fields
                for field, label in self.fields.items():
                    value = teacher_data.get(field, "Not provided")
                    label.text = f"{field}: {value}"

                # Check registration status and set image
                registration_status = teacher_data.get('registration_status', False)
                gender = teacher_data.get('Gender', '').lower()

                if registration_status and 'image_url' in teacher_data:
                    self.icon.source = teacher_data['image_url']
                else:
                    self.icon.source = 'assets/images/ImgSchool/teacherFemale.png' if gender == 'female' else 'assets/images/ImgSchool/teacherMale.png'

            else:
                toast("Teacher data not found")
        else:
            toast("Incomplete teacher information")

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_admin_teacherDetails'

    def edit_info(self):
        print('under development')