from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout


class schoolAdminMyAttendance(App):
    def build(self):
        # Create a BoxLayout for the main layout
        layout = BoxLayout(orientation='vertical')

        # Add a title label
        title = Label(text='About Our School', font_size='24sp', size_hint_y=None, height=50)
        layout.add_widget(title)

        # Create a ScrollView to contain the main content
        scroll_view = ScrollView()
        content_layout = GridLayout(cols=1, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))

        # Add content to the GridLayout
        content = """
        Welcome to Our School, where we are committed to providing a nurturing and stimulating environment for students to grow and thrive. Our school has a rich history of academic excellence and a strong commitment to community involvement.

        Our Mission:
        Our mission is to educate and inspire our students to reach their full potential and become responsible, contributing members of society. We believe in fostering a love of learning and encouraging critical thinking, creativity, and collaboration.

        Our Vision:
        Our vision is to create a safe and supportive environment where every student is valued and challenged to excel. We aim to develop well-rounded individuals who are prepared for the challenges and opportunities of the future.

        Our Values:
        - Respect for all individuals
        - Commitment to excellence
        - Integrity and honesty
        - Responsibility and accountability
        - Collaboration and teamwork

        Our History:
        Founded in 1960, Our School has grown from a small community school to a well-respected institution known for its academic rigor and supportive environment. We are proud of our tradition of excellence and look forward to continuing to serve our community for many years to come.
        """

        # Add content to a label and add the label to the content layout
        content_label = Label(text=content, font_size='16sp', size_hint_y=None, height=500)
        content_layout.add_widget(content_label)

        # Add the content layout to the ScrollView
        scroll_view.add_widget(content_layout)

        # Add the ScrollView to the main layout
        layout.add_widget(scroll_view)

        return layout


if __name__ == '__main__':
    schoolAdminMyAttendance().run()
