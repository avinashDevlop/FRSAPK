import cv2
import numpy as np
import face_recognition
import firebase_admin
from firebase_admin import credentials, initialize_app, storage, db
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
from kivy.uix.camera import Camera
from kivy.graphics import Color, Rectangle, Ellipse, Line, StencilPush, StencilUse, StencilPop, StencilUnUse
from kivy.core.window import Window
from PIL import Image as PILImage
import os
import tempfile
import logging
import requests
import io

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Firebase
service_account_key_path = os.path.join(os.getcwd(), "serviceAccountKey.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_key_path)
    initialize_app(cred, {
        'databaseURL': 'https://facialrecognitiondb-default-rtdb.firebaseio.com/',
        'storageBucket': 'facialrecognitiondb.appspot.com'
    })

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
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self._setup_ui()

    def _setup_ui(self):
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
            on_release=self.perform_frs,
            disabled=True
        )
        self.layout.add_widget(self.recognize_button)

        self.add_widget(self.layout)

    def update_fields(self, school_name, type_of, role, username):
        self.fields = {
            "SchoolName": school_name,
            "TypeOf": type_of,
            "role": role,
            "userName": username,
        }
        logger.info(f"Fields updated: {self.fields}")

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
            frame = self.get_frame()
            if frame is not None:
                faces = self.face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
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
            logger.warning("Camera or texture not available")
            return None

        try:
            texture = self.camera.texture
            size = texture.size
            pixels = texture.pixels
            pil_image = PILImage.frombytes(mode='RGBA', size=size, data=pixels)
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGBA2BGR)
            return opencv_image
        except Exception as e:
            logger.error(f"Error getting frame from camera: {str(e)}")
            return None

    def on_enter(self):
        self.start_camera()

    def on_leave(self):
        self.stop_camera()

    def compare_faces(self, stored_img_url, live_img):
        try:
            response = requests.get(stored_img_url)
            stored_image = PILImage.open(io.BytesIO(response.content))
            logger.debug(f"Stored image mode before conversion: {stored_image.mode}")
            if stored_image.mode != 'RGB':
                stored_image = stored_image.convert('RGB')
            stored_image = np.array(stored_image)
            
            live_img_rgb = cv2.cvtColor(live_img, cv2.COLOR_BGR2RGB)
            
            stored_encoding = face_recognition.face_encodings(stored_image)[0]
            live_encoding = face_recognition.face_encodings(live_img_rgb)[0]
            
            results = face_recognition.compare_faces([stored_encoding], live_encoding)
            return results[0]
        except Exception as e:
            logger.error(f"Error in face comparison: {str(e)}")
            return False

    def perform_frs(self, instance):
        frame = self.get_frame()
        if frame is None:
            self.status_label.text = "Failed to capture the frame from the camera. Please try again."
            return

        faces = self.face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            self.status_label.text = "No face detected. Please try again."
            return

        self.stop_camera()

        typeof = self.fields['TypeOf']
        schoolName = self.fields["SchoolName"]
        role = self.fields["role"]
        username = self.fields["userName"]
        
        try:
            ref = db.reference(f'{typeof}/{schoolName}/{role}s/{username}')
            user_data = ref.get()
            if user_data is None:
                raise ValueError("User data not found in the database")
            stored_img_url = user_data.get('image_url')
            if stored_img_url is None:
                raise ValueError("Image URL not found in user data")

            match = self.compare_faces(stored_img_url, frame)
            if match:
                self.status_label.text = "FRS Successful!"
                logger.info("FRS Successful!")
                # Here you can add code to update attendance or perform other actions
            else:
                self.status_label.text = "Face does not match. Please try again."
                logger.warning("Face does not match")
        except Exception as e:
            self.status_label.text = f"An error occurred: {str(e)}"
            logger.error(f"Error in FRS process: {str(e)}")
        finally:
            self.start_camera()

class FacialRecognitionApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        sm = ScreenManager()
        sm.add_widget(FacialRecognition(name='facial_recognition'))
        return sm

if __name__ == '__main__':
    FacialRecognitionApp().run()