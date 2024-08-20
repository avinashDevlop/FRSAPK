from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from Screens.Home import Home
from Screens.Login import Login
from Screens.Register import Register
# school admin
from Screens.School.AdminPrincipal.SchoolAdminScreen import SchoolAdminScreen
from Screens.School.AdminPrincipal.AboutSchool import AboutSchoolScreen
#school admin teacher
from Screens.School.AdminPrincipal.Teacher.Teacher import TeacherScreen
from Screens.School.AdminPrincipal.Teacher.addTeacher import AddTeacherScreen
from Screens.School.AdminPrincipal.Teacher.TeacherDetails import TeacherDetailsScreen
from Screens.School.AdminPrincipal.Teacher.TeacherInfo import TeacherInfoScreen
#school teacher
from Screens.School.Teacher.SchoolTeacherScreen import SchoolTeacherScreen
from Screens.School.Teacher.myAttendanceTech.myAttendanceTech import myAttendanceTech
from Screens.School.Teacher.myAttendanceTech.FRSregisteration.FRSregister import RegisterWithFace
from Screens.School.Teacher.myAttendanceTech.FacialRecognition import FacialRecognition
from Screens.School.Teacher.myAttendanceTech.aboutAttendance import AttendanceScreen
import os
import firebase_admin
from firebase_admin import credentials, initialize_app


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

        # Determine the path to your service account key JSON file
        service_account_key_path = os.path.join(os.getcwd(), "serviceAccountKey.json")

        # Initialize Firebase only once
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_key_path)
            initialize_app(cred, {
                'databaseURL': 'https://facialrecognitiondb-default-rtdb.firebaseio.com/',
                'storageBucket': 'gs://facialrecognitiondb.appspot.com'
            })

    def build(self):
        self.title = 'Facial Recognition System'
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # Set the window size for all mobiles (this is optional and for demonstration purposes)
        Window.size = (360, 640)  # Example resolution, adjust as needed

        self.screen_manager = ScreenManager(transition=SlideTransition())
        self.screen_manager.add_widget(Home(name='home'))
        self.screen_manager.add_widget(Login(name='login'))
        self.screen_manager.add_widget(Register(name='registration'))
        self.screen_manager.add_widget(SchoolAdminScreen(name='school_admin'))
        self.screen_manager.add_widget(AboutSchoolScreen(name='school_admin_about'))
        #school admin teacher
        self.screen_manager.add_widget(TeacherScreen(name='school_admin_teacher'))
        self.screen_manager.add_widget(AddTeacherScreen(name='school_admin_addTeacher'))
        self.screen_manager.add_widget(TeacherDetailsScreen(name='school_admin_teacherDetails'))
        self.screen_manager.add_widget(TeacherInfoScreen(name='school_admin_teacherInfo'))
        #school teacher
        self.screen_manager.add_widget(SchoolTeacherScreen(name='school_teacher'))
        self.screen_manager.add_widget(myAttendanceTech(name='school_teacher_myAttendance'))
        self.screen_manager.add_widget(RegisterWithFace(name='school_teacher_frsRegister'))
        self.screen_manager.add_widget(FacialRecognition(name='school_teacher_FacialRecognition'))
        self.screen_manager.add_widget(AttendanceScreen(name='school_teacher_aboutAttendance'))
        return self.screen_manager

    def on_start(self):
        # Bind the login button to navigate to the login screen
        home_screen = self.screen_manager.get_screen('home')
        home_screen.login_button.bind(on_release=self.go_to_login)
        home_screen.register_button.bind(on_release=self.go_to_register)  # Bind the register button

    def go_to_login(self, *args):
        self.screen_manager.transition = SlideTransition(direction="left")
        self.screen_manager.current = 'login'

    def go_to_register(self, *args):
        self.screen_manager.transition = SlideTransition(direction="right")
        self.screen_manager.current = 'registration'

    def go_to_home(self, *args):
        self.screen_manager.transition = SlideTransition(direction="left")
        self.screen_manager.current = 'home'


if __name__ == '__main__':
    MainApp().run()