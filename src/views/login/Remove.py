#================================================================================================================================================
#---------------------------------------------------------------------Import---------------------------------------------------------------------
#================================================================================================================================================


import flet as ft
import os
import cv2
import numpy as np
import importlib
from datetime import datetime
import pickle
import json
import traceback
import threading
import sys


#================================================================================================================================================
#----------------------------------------------------------------------Main----------------------------------------------------------------------
#================================================================================================================================================



face_recognition = None
try:
    face_recognition = importlib.import_module('face_recognition')
except Exception:
    print("Install all the required modules first!\nPlease install 'face_recognition' and its dependencies (dlib, cmake, etc.).")
    raise SystemExit(1)


HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.append(HERE)

try:
    from Login_Success import SimpleFaceRecognition
except Exception as e:
    SimpleFaceRecognition = None
    _import_error = e
else:
    _import_error = None


class Edit(ft.Column):

    def __init__(self, page: ft.Page):
        super().__init__()
        page.title = 'Face Recognition'
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        page.window_resizable = True
        page.window_maximized = False
        page.update()
        self.page = page
        # Minimal remove-only screen
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.alignment.top_center
        self.spacing = 12

        # Backend recognizer instance
        try:
            self.recognizer = SimpleFaceRecognition() if SimpleFaceRecognition is not None else None
        except Exception as e:
            self.recognizer = None
            _import_error = e

        # Widgets
        self.status = ft.Text("Ready", size=12)
        self.remove_name = ft.TextField(label="Name to remove", width=300)
        self.remove_btn = ft.ElevatedButton(text="Remove", on_click=self.on_remove_clicked)

        # Layout
        self.controls = [
            ft.Container(
                content=ft.Text("Remove Person", size=28, weight=ft.FontWeight.BOLD),
                alignment=ft.alignment.center,
                margin=ft.margin.only(bottom=10),
            ),
            ft.Container(self.status, alignment=ft.alignment.center),
            ft.Row([self.remove_name, self.remove_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ]

    def on_remove_clicked(self, e):
        if not self.recognizer:
            self.status.value = "Recognizer not available"
            self.page.update()
            return
        name = (self.remove_name.value or "").strip()
        if not name:
            self.status.value = "Enter a name to remove"
            self.page.update()
            return
        # Perform removal (fast enough to do inline)
        try:
            ok = self.recognizer.remove_person(name)
            self.status.value = "Removed" if ok else "Name not found"
        except Exception as exc:
            self.status.value = f"Error: {exc}"
            traceback.print_exc()
        self.page.update()
