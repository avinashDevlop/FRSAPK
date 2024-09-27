from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from firebase_admin import db

class TeacherDetailsScreen(MDScreen):
    def update_fields(self, school_name, type_of ,role , userName):
        self.DBLocation["typeOf"] = type_of
        self.DBLocation["schoolName"] = school_name
        self.DBLocation["role"]  = role
        self.DBLocation["userName"] = userName

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DBLocation = {
            "typeOf": "",
            "schoolName": "",
            "role": "",
            "userName": ""
        }
        # Set up the layout
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)

        # Top app bar
        self.toolbar = MDTopAppBar(
            title="Teacher Details",
            elevation=4,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["account-plus", lambda x: self.account_action()]]
        )
        self.layout.add_widget(self.toolbar)

        # Scrollable list for teacher items
        self.scroll = ScrollView()
        self.list = MDList()
        self.scroll.add_widget(self.list)
        self.layout.add_widget(self.scroll)

        # Fetch teacher data when screen is shown
        self.on_enter = self.fetch_teacher_data

    def fetch_teacher_data(self):
        type_of = self.DBLocation["typeOf"]
        school_name = self.DBLocation["schoolName"]
        ref = db.reference(f'{type_of}/{school_name}/Teachers')
        teachers = ref.get()
        self.list.clear_widgets()
        if teachers is None:
            self.list.add_widget(TwoLineAvatarIconListItem(
                text="No teachers found",
                secondary_text="",
            ))
            return
        for teacher_id, teacher_info in teachers.items():
            gender_icon = "account-circle"
            if 'Gender' in teacher_info:
                gender_icon = "face-man" if teacher_info['Gender'].lower() == "male" else "face-woman"
            self.add_teacher_item(teacher_id, teacher_info['Teacher Name'], teacher_info['Subject'], gender_icon)

    def add_teacher_item(self, teacher_id, name, subject, icon):
        item = TwoLineAvatarIconListItem(
            text=name,
            secondary_text=subject,
            on_release=lambda x: self.navigate_to_teacher_info(teacher_id)
        )
        left_icon = IconLeftWidget(icon=icon)
        item.add_widget(left_icon)
        right_icon = IconRightWidget(icon="chevron-right")
        right_icon.bind(on_release=lambda x: self.navigate_to_teacher_info(name))
        item.add_widget(right_icon)
        self.list.add_widget(item)

    def navigate_to_teacher_info(self, name):
        teacher_info_screen = self.manager.get_screen('school_admin_teacherInfo')
        teacher_info_screen.update_fields(self.DBLocation["schoolName"], self.DBLocation["typeOf"],self.DBLocation["role"], name)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'school_admin_teacherInfo'

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_admin_teacher'

    def account_action(self):
        type_of = self.DBLocation["typeOf"]
        school_name = self.DBLocation["schoolName"]
        about_screen = self.manager.get_screen('school_admin_addTeacher')
        about_screen.update_fields(school_name, type_of)
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'school_admin_addTeacher'

class TeacherDetailsApp(MDApp):
    def build(self):
        return TeacherDetailsScreen()

if __name__ == '__main__':
    TeacherDetailsApp().run()