import firebase_admin
from firebase_admin import credentials, db, storage
import uuid
import io
from datetime import datetime
from kivy.metrics import dp
from kivy.uix.screenmanager import SlideTransition, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from PIL import Image as PILImage

# Path to your service account key file
SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"

# Initialize Firebase
cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://facialrecognitiondb-default-rtdb.firebaseio.com/',
    'storageBucket': 'facialrecognitiondb.appspot.com'
})

# Get a reference to the storage service
bucket = storage.bucket()


class RegisterWithFace(MDScreen):
    def update_fields(self, school_name, type_of, role, username):
        self.fields["TypeOf"] = type_of
        self.fields["schoolName"] = school_name
        self.fields["role"] = role
        self.fields["userName"] = username

    def __init__(self, **kwargs):
        super(RegisterWithFace, self).__init__(**kwargs)

        self.fields = {
            "SchoolName": None,
            "TypeOf": None,
            "role": None,
            "userName": None
        }

        self.layout = MDBoxLayout(orientation='vertical')

        # Top app bar
        self.top_bar = MDTopAppBar(
            title="Face Registration",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            pos_hint={"top": 1},
        )
        self.layout.add_widget(self.top_bar)

        # Camera widget (not added to layout initially)
        self.camera = None

        # Instructions label
        self.instructions = MDLabel(
            text="Please center your face in the frame",
            halign="center",
            size_hint_y=None,
            height=dp(100)
        )
        self.layout.add_widget(self.instructions)

        # Register button
        self.register_button = MDRaisedButton(
            text="Capture and Register",
            pos_hint={'center_x': 0.5},
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            on_release=self.capture_and_register
        )
        self.layout.add_widget(self.register_button)

        self.add_widget(self.layout)

    def on_enter(self):
        # This method is called when the screen is entered
        if not self.camera:
            self.camera = Camera(play=True, index=0, resolution=(640, 480))
            self.layout.add_widget(self.camera, index=1)
        else:
            self.camera.play = True

    def on_leave(self):
        # This method is called when the screen is left
        if self.camera:
            self.camera.play = False

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'attendance'

    def capture_and_register(self, instance):
        if not self.camera:
            self.instructions.text = "Camera is not initialized. Please try again."
            return

        # Capture the image
        texture = self.camera.texture
        size = texture.size
        pixels = texture.pixels

        # Convert to PIL Image
        pil_image = PILImage.frombytes(mode='RGBA', size=size, data=pixels)

        # Convert to PNG format
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        png_data = buffer.getvalue()


        try:
            # Upload image to Firebase Storage
            typeof = self.fields['TypeOf']
            schoolName = self.fields["schoolName"]
            role = self.fields["role"]
            username = self.fields["userName"]
            blob = bucket.blob(f'{typeof}/{schoolName}/{role}/{username}/face_registrationsIMG.png')
            blob.upload_from_string(png_data, content_type='image/png')

            # Make the blob publicly accessible
            blob.make_public()

            # Get the public URL
            image_url = blob.public_url

            # Get current timestamp
            current_time = datetime.utcnow().isoformat()

            # Create a data structure for the registration
            registration_data = {
                "timestamp": current_time,
                "image_url": image_url,
                # Add any other relevant data here
            }

            # Push the data to Firebase Realtime Database
            ref = db.reference(f'{typeof}/{schoolName}/{role}s/{username}')
            ref.update(registration_data)

            # Update instructions
            self.instructions.text = "Registration successful!"

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            self.instructions.text = f"Error: {str(e)}"


class AttendanceApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(RegisterWithFace(name='register_with_face'))
        return sm


if __name__ == '__main__':
    AttendanceApp().run()