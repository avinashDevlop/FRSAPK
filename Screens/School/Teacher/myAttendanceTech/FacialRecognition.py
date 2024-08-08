import cv2
import firebase_admin
import numpy as np
import face_recognition
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from datetime import datetime
from PIL import Image as PILImage
import io
from kivy.uix.camera import Camera
from kivy.graphics import Color, Rectangle, Ellipse, Line, StencilPush, StencilUse, StencilPop, StencilUnUse
from kivy.core.window import Window
import os
from firebase_admin import credentials, initialize_app, storage

# Determine the path to your service account key JSON file
service_account_key_path = os.path.join(os.getcwd(), "serviceAccountKey.json")

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_key_path)
    initialize_app(cred, {
        'databaseURL': 'https://facialrecognitiondb-default-rtdb.firebaseio.com/',
        'storageBucket': 'facialrecognitiondb.appspot.com'
    })

def load_teacher_image_from_firebase(username, school_name, type_of, role):
    try:
        # Fetch the image from Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob(f'{type_of}/{school_name}/{role}/{username}/face_registrationsIMG.png')
        image_bytes = blob.download_as_bytes()

        # Open the image using PIL
        pil_image = PILImage.open(io.BytesIO(image_bytes))

        # Convert to RGB if it's not already
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convert PIL image to numpy array
        np_image = np.array(pil_image)

        # Debug information
        print(f"Image mode: {pil_image.mode}")
        print(f"Image size: {pil_image.size}")
        print(f"Numpy array shape: {np_image.shape}")
        print(f"Numpy array dtype: {np_image.dtype}")

        # Ensure the image is uint8
        if np_image.dtype != np.uint8:
            np_image = np_image.astype(np.uint8)

        # Convert RGB to BGR for OpenCV if needed
        bgr_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

        # Detect and encode faces using face_recognition
        face_encodings = face_recognition.face_encodings(bgr_image)
        if not face_encodings:
            raise ValueError("No face found in the image")
        face_encoding = face_encodings[0]
        return face_encoding

    except Exception as e:
        print(f"Error loading teacher image from Firebase: {str(e)}")
        return None

# Ensure to initialize Firebase Admin SDK before calling this function
# firebase_admin.initialize_app(credential, {'storageBucket': 'your-bucket-name'})


class CircularCamera(Camera):
    def __init__(self, **kwargs):
        super(CircularCamera, self).__init__(**kwargs)
        self.bind(size=self._update_canvas)
        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, instance, width, height):
        self.size = (min(width, height) * 0.8, min(width, height) * 0.8)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.6}

    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            StencilPush()
            Color(1, 1, 1, 1)
            Ellipse(pos=self.pos, size=self.size)
            StencilUse()
            Color(1, 1, 1, 1)
            Rectangle(texture=self.texture, pos=self.pos, size=self.size)
            StencilUnUse()
            StencilPop()
            Color(0, 0.7, 1, 1)
            border_width = dp(4)
            Line(circle=(self.center_x, self.center_y, min(self.width, self.height) / 2), width=border_width)

    def on_texture(self, *args):
        self._update_canvas()


class FacialRecognition(MDScreen):
    def __init__(self, **kwargs):
        super(FacialRecognition, self).__init__(**kwargs)
        self.fields = {"SchoolName": None, "TypeOf": None, "role": None, "userName": None}
        self.camera = None
        self.teacher_face_encoding = None

        self.layout = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        self.top_bar = MDTopAppBar(
            title="Facial Recognition",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            pos_hint={"top": 1},
            elevation=10
        )
        self.add_widget(self.top_bar)

        self.camera_layout = MDBoxLayout(size_hint=(1, 0.7))
        self.layout.add_widget(self.camera_layout)

        self.status_label = MDLabel(
            text="Place your face in the frame",
            halign="center",
            size_hint_y=None,
            height=dp(50)
        )
        self.layout.add_widget(self.status_label)

        self.recognize_button = MDRaisedButton(
            text="Recognize",
            pos_hint={'center_x': 0.5},
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            on_release=self.recognize_face,
            disabled=True
        )
        self.layout.add_widget(self.recognize_button)

        self.add_widget(self.layout)

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def update_fields(self, school_name, type_of, role, username):
        self.fields = {
            "SchoolName": school_name,
            "TypeOf": type_of,
            "role": role,
            "userName": username,
        }
        print(school_name, type_of, role, username)
        self.load_teacher_image(school_name, type_of, role, username)

    def load_teacher_image(self, school_name, type_of, role, username):
        self.teacher_face_encoding = load_teacher_image_from_firebase(username, school_name, type_of, role)
        if self.teacher_face_encoding is not None:
            self.status_label.text = "Teacher's face loaded. You can now recognize."
        else:
            self.status_label.text = "Teacher's image not found or failed to load."

    def go_back(self):
        self.stop_camera()
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'school_teacher_myAttendance'

    def start_camera(self):
        if not self.camera:
            self.camera = CircularCamera(play=True, resolution=(640, 480))
            self.camera.size_hint = (None, None)
            self.camera.size = (dp(300), dp(300))
            self.camera.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
            self.camera_layout.add_widget(self.camera)
        else:
            self.camera.play = True
        Clock.schedule_interval(self.update_camera, 1.0 / 30.0)

    def stop_camera(self):
        if self.camera:
            Clock.unschedule(self.update_camera)
            self.camera.play = False
            self.camera_layout.remove_widget(self.camera)
            self.camera = None

    def update_camera(self, dt):
        if self.camera and self.camera.texture:
            texture = self.camera.texture
            size = texture.size
            pixels = texture.pixels
            pil_image = PILImage.frombytes(mode='RGBA', size=size, data=pixels)
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGBA2BGR)
            faces = self.face_cascade.detectMultiScale(opencv_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                self.status_label.text = "Face detected. You can now capture the image."
                self.recognize_button.disabled = False
                self.recognize_button.md_bg_color = self.theme_cls.primary_color
            else:
                self.status_label.text = "No face detected. Please ensure your face is visible in the camera frame."
                self.recognize_button.disabled = True
                self.recognize_button.md_bg_color = self.theme_cls.disabled_hint_text_color

    def get_frame(self):
        if not self.camera or not self.camera.texture:
            print("Camera or texture not available")
            return None

        try:
            texture = self.camera.texture
            size = texture.size
            pixels = texture.pixels
            pil_image = PILImage.frombytes(mode='RGBA', size=size, data=pixels)

            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            opencv_image = cv2.cvtColor(np.array(pil_image, dtype=np.uint8), cv2.COLOR_RGB2BGR)
            return opencv_image
        except Exception as e:
            print(f"Error getting frame from camera: {str(e)}")
            return None

    def on_enter(self):
        self.start_camera()

    def on_leave(self):
        self.stop_camera()

    def recognize_face(self, instance):
        if self.teacher_face_encoding is None:
            self.status_label.text = "Teacher's face not loaded. Please try again."
            return

        frame = self.get_frame()
        if frame is None:
            self.status_label.text = "Failed to capture the frame from the camera. Please try again."
            return

        try:
            # Convert frame to RGB and ensure it's uint8
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame = np.array(rgb_frame, dtype=np.uint8)

            face_locations = face_recognition.face_locations(rgb_frame)
            if not face_locations:
                self.status_label.text = "No face detected. Please try again."
                return

            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            for face_encoding in face_encodings:
                match = face_recognition.compare_faces([self.teacher_face_encoding], face_encoding, tolerance=0.6)
                if match[0]:
                    self.status_label.text = "Face recognized successfully."
                    return
            self.status_label.text = "Face not recognized."
        except Exception as e:
            print(f"Error during face recognition: {str(e)}")
            self.status_label.text = "An error occurred during face recognition. Please try again."


# Note: You'll need to implement the main app class and screen management
# to use this FacialRecognition screen in your application.

if __name__ == '__main__':
    class TestApp(MDApp):
        def build(self):
            sm = ScreenManager()
            sm.add_widget(FacialRecognition(name='facial_recognition'))
            return sm


    TestApp().run()