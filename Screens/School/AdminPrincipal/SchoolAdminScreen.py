from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.logger import Logger
from kivy.core.window import Window
from Screens.School.AdminPrincipal.AboutSchool import AboutSchoolScreen

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = get_color_from_hex('#3498db')
        self.border = (1, 1, 1, 1)

class ProfileLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "L"
        self.font_size = '20sp'
        self.color = get_color_from_hex('#34495e')
        self.size_hint = (None, None)
        self.size = (40, 40)
        with self.canvas.before:
            Color(*get_color_from_hex('#ffffff'))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            Logger.info("Profile label clicked!")
            App.get_running_app().root.current = 'home'
            return True
        return super().on_touch_down(touch)

class SchoolAdminScreen(Screen):
    def update_content(self, type_of, company, role, username):
        global type_of_global, schoolName, role_global, username_global

        type_of_global = type_of
        schoolName = company
        role_global = role
        username_global = username

        # print(f"Type of: {type_of_global}")
        # print(f"schoolName: {schoolName}")
        # print(f"Role: {role_global}")
        # print(f"Username: {username_global}")

        self.school_name_label.text = f"{schoolName} {type_of_global}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*get_color_from_hex('#ecf0f1'))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        top_bar = BoxLayout(size_hint=(1, 0.1), pos_hint={'top': 1}, padding=[20, 10])
        with top_bar.canvas.before:
            Color(*get_color_from_hex('#34495e'))
            self.top_bar_rect = Rectangle(size=top_bar.size, pos=top_bar.pos)
        top_bar.bind(size=self._update_top_bar_rect, pos=self._update_top_bar_rect)

        self.school_name_label = Label(text="", size_hint=(0.9, 1), color=get_color_from_hex('#ffffff'))

        profile_label = ProfileLabel(pos_hint={'center_y': 0.5, 'right': 0.98})
        profile_label.bind(on_touch_down=self.go_home)

        top_bar.add_widget(self.school_name_label)
        top_bar.add_widget(profile_label)

        scroll_view = ScrollView(size_hint=(1, 0.9), pos_hint={'x': 0, 'y': 0})
        options_layout = BoxLayout(orientation='vertical', spacing=20, padding=[20, 20, 20, 20], size_hint_y=None)
        options_layout.bind(minimum_height=options_layout.setter('height'))

        options = [
            ("About School", './assets/images/ImgSchool/AboutSchool.png', 'school_admin_about'),
            ("My Attendance", './assets/images/ImgSchool/myAttendance.png', 'school_admin_myAttendance'),
            ("Teachers", './assets/images/ImgSchool/Teacher.png', 'school_admin_teacher'),
            ("Students", './assets/images/ImgSchool/Student.png', 'school_admin_studentHome'),
            ("Staff", './assets/images/ImgSchool/Staff.png', 'school_admin_staffHome'),
            ("Schedule", './assets/images/ImgSchool/Schedule.png', 'school_admin_scheduleHome'),
        ]

        for i in range(0, len(options), 2):
            row = BoxLayout(spacing=20, size_hint_y=None, height=150)
            for j in range(2):
                if i + j < len(options):
                    option_layout = BoxLayout(orientation='vertical', padding=[0, 0], size_hint=(0.5, None))
                    img = AsyncImage(source=options[i + j][1], size_hint=(1, None), height=80)
                    img.bind(on_error=self.image_load_error)
                    img.bind(on_touch_down=self.go_to_screen(options[i + j][2]))
                    btn = RoundedButton(text=options[i + j][0], size_hint=(1, None), height=60)
                    btn.cursor = "hand"
                    btn.bind(on_touch_down=self.go_to_screen(options[i + j][2]))
                    option_layout.add_widget(img)
                    option_layout.add_widget(btn)
                    row.add_widget(option_layout)
            options_layout.add_widget(row)

        scroll_view.add_widget(options_layout)

        self.add_widget(top_bar)
        self.add_widget(scroll_view)

        Window.bind(mouse_pos=self.on_mouse_move)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_top_bar_rect(self, instance, value):
        self.top_bar_rect.pos = instance.pos
        self.top_bar_rect.size = instance.size

    def image_load_error(self, instance, value):
        Logger.error(f"Failed to load image: {instance.source}")

    def go_home(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.manager.current = 'home'
            return True
        return False

    def go_to_screen(self, screen_name):
        def on_touch_down(instance, touch):
            if instance.collide_point(*touch.pos):
                if screen_name == 'school_admin_about':
                    about_screen = self.manager.get_screen('school_admin_about')
                    about_screen.update_fields(schoolName, type_of_global, role_global, username_global)
                elif screen_name == 'school_admin_teacher':
                    about_screen = self.manager.get_screen('school_admin_teacher')
                    about_screen.update_fields(schoolName, type_of_global, role_global, username_global)
                self.manager.current = screen_name
                return True
            return False
        return on_touch_down

    def on_mouse_move(self, window, pos):
        hover_widgets = [w for w in self.walk() if isinstance(w, (Button, Label, AsyncImage))]
        for widget in hover_widgets:
            if widget.collide_point(*pos):
                Window.set_system_cursor("hand")
                break
        else:
            Window.set_system_cursor("arrow")

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.login_button = Button(text="Login", size_hint=(1, 0.1))
        self.register_button = Button(text="Register", size_hint=(1, 0.1))
        layout.add_widget(self.login_button)
        layout.add_widget(self.register_button)
        self.add_widget(layout)

class MyAttendanceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="My Attendance"))
        back_button = Button(text="Back to Home", size_hint=(1, 0.1))
        back_button.bind(on_press=self.go_home)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def go_home(self, instance):
        self.manager.current = 'home'

class TeachersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Teachers"))
        back_button = Button(text="Back to Home", size_hint=(1, 0.1))
        back_button.bind(on_press=self.go_home)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def go_home(self, instance):
        self.manager.current = 'home'

class StudentsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Students"))
        back_button = Button(text="Back to Home", size_hint=(1, 0.1))
        back_button.bind(on_press=self.go_home)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def go_home(self, instance):
        self.manager.current = 'home'

class StaffScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Staff"))
        back_button = Button(text="Back to Home", size_hint=(1, 0.1))
        back_button.bind(on_press=self.go_home)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def go_home(self, instance):
        self.manager.current = 'home'

class ScheduleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Schedule"))
        back_button = Button(text="Back to Home", size_hint=(1, 0.1))
        back_button.bind(on_press=self.go_home)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def go_home(self, instance):
        self.manager.current = 'home'

class MyApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition(direction="up"))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SchoolAdminScreen(name='school_admin'))
        sm.add_widget(MyAttendanceScreen(name='my_attendance'))
        sm.add_widget(TeachersScreen(name='teachers'))
        sm.add_widget(StudentsScreen(name='students'))
        sm.add_widget(StaffScreen(name='staff'))
        sm.add_widget(ScheduleScreen(name='schedule'))
        sm.add_widget(AboutSchoolScreen(name='school_admin_about'))
        return sm

if __name__ == '__main__':
    MyApp().run()