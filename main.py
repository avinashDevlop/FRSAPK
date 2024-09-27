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
from Screens.School.AdminPrincipal.Teacher.TeacherInfoAttendance import AdminTeacherAttendance
from Screens.School.AdminPrincipal.Teacher.TeacherInfoLeaveLetter import TeacherInfoLeaveLetter
from Screens.School.AdminPrincipal.myAttendance.adminMyAttendance import adminAttendanceScreen
from Screens.School.AdminPrincipal.students.studentHome import adminStudentScreen
from Screens.School.AdminPrincipal.staff.staffHome import staffScreen
from Screens.School.AdminPrincipal.schedule.scheduleHome import adminScheduleScreen
#school teacher
from Screens.School.Teacher.SchoolTeacherScreen import SchoolTeacherScreen
from Screens.School.Teacher.myAttendanceTech.myAttendanceTech import myAttendanceTech
from Screens.School.Teacher.myAttendanceTech.FRSregisteration.FRSregister import RegisterWithFace
from Screens.School.Teacher.myAttendanceTech.FacialRecognition import FacialRecognition
from Screens.School.Teacher.myAttendanceTech.aboutAttendance import AttendanceScreen
from Screens.School.Teacher.myAttendanceTech.leaveLetterMain import LeaveLetterMainScreen
from Screens.School.Teacher.myAttendanceTech.leaveLetter import LeaveLetterScreen
from Screens.School.Teacher.aboutSchool.aboutSchoolHome import teacherAboutSchoolScreen
from Screens.School.Teacher.schedule.scheduleHome import teacherScheduleScreen
from Screens.School.Teacher.student.studentHome import teacherStudentScreen
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
        self.screen_manager.add_widget(AdminTeacherAttendance(name='school_admin_teacherInfoAttendence'))
        self.screen_manager.add_widget(TeacherInfoLeaveLetter(name='school_admin_teacherInfoLeaveLetter'))
        self.screen_manager.add_widget(adminAttendanceScreen(name='school_admin_myAttendance'))
        self.screen_manager.add_widget(adminStudentScreen(name='school_admin_studentHome'))
        self.screen_manager.add_widget(staffScreen(name='school_admin_staffHome'))
        self.screen_manager.add_widget(adminScheduleScreen(name='school_admin_scheduleHome'))
        #school teacher
        self.screen_manager.add_widget(SchoolTeacherScreen(name='school_teacher'))
        self.screen_manager.add_widget(myAttendanceTech(name='school_teacher_myAttendance'))
        self.screen_manager.add_widget(RegisterWithFace(name='school_teacher_frsRegister'))
        self.screen_manager.add_widget(FacialRecognition(name='school_teacher_FacialRecognition'))
        self.screen_manager.add_widget(AttendanceScreen(name='school_teacher_aboutAttendance'))
        self.screen_manager.add_widget(LeaveLetterScreen(name='school_teacher_LeaveLetter'))
        self.screen_manager.add_widget(LeaveLetterMainScreen(name='school_teacher_LeaveLetterMain'))
        self.screen_manager.add_widget(teacherAboutSchoolScreen(name='school_teacher_aboutSchool'))
        self.screen_manager.add_widget(teacherStudentScreen(name='school_teacher_student'))
        self.screen_manager.add_widget(teacherScheduleScreen(name='school_teacher_schedule'))
        return self.screen_manager

    def on_start(self):
        # Bind the login button to navigate to the login screen
        home_screen = self.screen_manager.get_screen('home')
        home_screen.login_button.bind(on_release=self.go_to_login)
        home_screen.register_button.bind(on_release=self.go_to_register)  # Bind the register button

    def go_to_login(self):
        self.screen_manager.transition = SlideTransition(direction="left")
        self.screen_manager.current = 'login'

    def go_to_register(self):
        self.screen_manager.transition = SlideTransition(direction="right")
        self.screen_manager.current = 'registration'

    def go_to_home(self):
        self.screen_manager.transition = SlideTransition(direction="left")
        self.screen_manager.current = 'home'


if __name__ == '__main__':
    MainApp().run()