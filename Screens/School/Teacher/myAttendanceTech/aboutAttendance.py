from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton

from datetime import datetime, timedelta
import calendar


class CircularImage(Widget):
    source = StringProperty(None)
    color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super(CircularImage, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, source=self.update_canvas, color=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self.color)
            Ellipse(pos=self.pos, size=self.size)
            Color(1, 1, 1, 1)
            Ellipse(pos=(self.pos[0] + dp(2), self.pos[1] + dp(2)),
                    size=(self.size[0] - dp(4), self.size[1] - dp(4)),
                    source=self.source)


class CircularDateLabel(Label):
    def __init__(self, text, is_highlighted=False, **kwargs):
        super(CircularDateLabel, self).__init__(**kwargs)
        self.text = text
        self.color = (0.3, 0.3, 0.3, 1) if not is_highlighted else (1, 1, 1, 1)
        self.is_highlighted = is_highlighted
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_highlighted:
                Color(1, 0.5, 0, 1)  # Orange color for highlight
                Ellipse(pos=self.pos, size=self.size)
            else:
                Color(1, 1, 1, 1)  # White background
                Rectangle(pos=self.pos, size=self.size)


class CalendarWidget(MDBoxLayout):
    current_date = ObjectProperty(datetime.now())

    def __init__(self, **kwargs):
        super(CalendarWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(16), dp(0), dp(16), dp(0)  # Add padding to the sides
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.create_calendar()
        Window.bind(on_resize=self.on_window_resize)

    def create_calendar(self):
        self.clear_widgets()

        # Header with month, year, and navigation arrows
        header = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        left_arrow = MDIconButton(icon="chevron-left", on_release=self.previous_month)
        right_arrow = MDIconButton(icon="chevron-right", on_release=self.next_month)
        month_year_label = MDLabel(
            text=f"{self.current_date.strftime('%B %Y')}",
            halign='center',
            theme_text_color="Primary",
            font_style="H6"
        )
        header.add_widget(left_arrow)
        header.add_widget(month_year_label)
        header.add_widget(right_arrow)
        self.add_widget(header)

        # Calendar grid
        calendar_grid = GridLayout(cols=7, spacing=dp(2), size_hint_y=None)
        calendar_grid.bind(minimum_height=calendar_grid.setter('height'))

        # Weekday labels
        for day in ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]:
            weekday_label = MDLabel(
                text=day,
                halign='center',
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint_y=None,
                height=dp(30)
            )
            calendar_grid.add_widget(weekday_label)

        # Date cells
        month_calendar = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        for week in month_calendar:
            for day in week:
                if day == 0:
                    calendar_grid.add_widget(Widget(size_hint_y=None, height=dp(40)))
                else:
                    is_highlighted = (day == self.current_date.day and
                                      self.current_date.month == datetime.now().month and
                                      self.current_date.year == datetime.now().year)
                    date_label = CircularDateLabel(
                        text=str(day),
                        is_highlighted=is_highlighted,
                        size_hint=(None, None),
                        size=self.get_date_label_size(),
                        font_size=self.get_date_label_font_size()
                    )
                    calendar_grid.add_widget(date_label)

        self.add_widget(calendar_grid)

    def previous_month(self, *args):
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.create_calendar()

    def next_month(self, *args):
        next_month = self.current_date.replace(day=28) + timedelta(days=4)
        self.current_date = next_month.replace(day=1)
        self.create_calendar()

    def on_window_resize(self, window, width, height):
        self.create_calendar()  # Recreate the calendar on window resize

    def get_date_label_size(self):
        return (Window.width / 10, Window.width / 10)  # Adjusted size for better responsiveness

    def get_date_label_font_size(self):
        return str(int(Window.width / 32)) + 'sp'  # Adjusted font size for better readability


class AttendanceScreen(MDScreen):
    def __init__(self, **kwargs):
        super(AttendanceScreen, self).__init__(**kwargs)
        self._setup_ui()
        
    def update_fields(self, school_name, type_of, role, username):
        self.fields = {
            "SchoolName": school_name,
            "TypeOf": type_of,
            "role": role,
            "userName": username,
        }   
        print(type_of, school_name,role,username)    

    def on_enter(self, *args):
        # Update the layout manually when the screen is entered
        self._setup_ui()

    def _setup_ui(self):
        self.clear_widgets()  # Clear any existing widgets to avoid duplicates

        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=(dp(0), dp(0), dp(0), dp(0)))  # Remove padding here

        top_bar = MDTopAppBar(
            title="About Attendance",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            pos_hint={"top": 1},
            elevation=0
        )
        main_layout.add_widget(top_bar)

        scroll_content = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=(dp(0), dp(0), dp(0), dp(0)),
                                     size_hint_y=None)  # Remove padding here
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        profile_card = MDCard(
            orientation='horizontal',
            size_hint=(None, None),
            height=dp(100),
            width=Window.width - dp(40),  # Adjust width to fit screen width with some margin
            padding=dp(10),
            pos_hint={"center_x": 0.5}  # Center the profile card horizontally
        )

        circular_img = CircularImage(
            source="path/to/profile_image.png",  # Replace with actual image path
            size_hint=(None, None),
            size=(dp(80), dp(80)),
            color=(0.2, 0.7, 0.3, 1)
        )
        profile_card.add_widget(circular_img)

        text_layout = BoxLayout(orientation='vertical', padding=(dp(10), 0, 0, 0), size_hint_x=1)
        name_label = MDLabel(
            text="Name: John Doe",
            theme_text_color="Primary",
            font_style="Subtitle1",
            halign='left',
        )
        subject_label = MDLabel(
            text="Subject: Mathematics",
            theme_text_color="Secondary",
            font_style="Body2",
            halign='left',
        )
        text_layout.add_widget(name_label)
        text_layout.add_widget(subject_label)
        profile_card.add_widget(text_layout)

        scroll_content.add_widget(profile_card)
        scroll_content.add_widget(CalendarWidget())
        scroll = ScrollView()
        scroll.add_widget(scroll_content)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "school_teacher_myAttendance" 


class AttendanceApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AttendanceScreen(name="attendance_screen"))
        return sm

if __name__ == '__main__':
    AttendanceApp().run()