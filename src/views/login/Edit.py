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
        self.load_database()
        self.known_face_encodings = []
        self.known_face_names = []
        self.database_path = "face_database.json"
        self.encodings_path = "face_encodings.pkl"
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.alignment.top_center
        self.spacing = 10
        
        
    def load_database(self):
        # Load existing face database if it exists
        try:
            if os.path.exists(self.database_path) and os.path.exists(self.encodings_path):
                with open(self.database_path, 'r') as f:
                    database = json.load(f)
                    self.known_face_names = database.get('names', [])
                with open(self.encodings_path, 'rb') as f:
                    self.known_face_encodings = pickle.load(f)
                print(f"Loaded {len(self.known_face_names)} faces from database")
        except Exception as e:
            print(f"Error loading database: {e}")
            self.known_face_encodings = []
            self.known_face_names = []

        
        try:
            self.recognizer = SimpleFaceRecognition() if SimpleFaceRecognition is not None else None
        except Exception as e:
            self.recognizer = None
            _import_error = e



        # Create widgets first
        self.edit_list()
        
        # Add file picker to page overlay
        try:
            self.page.overlay.append(self.file_dialog)
        except Exception:
            self.page.add(self.file_dialog)
            
        self.status = ft.Text("Ready", size=12)
        # Build complete layout with all widgets
        self.controls = [
            # Title
            ft.Container(
                content=ft.Text("Edit Menu", size=32, weight=ft.FontWeight.BOLD),
                margin=ft.margin.only(bottom=20),
                alignment=ft.alignment.center
            ),
            # Status message
            ft.Container(
                content=self.status,
                margin=ft.margin.only(bottom=10),
                alignment=ft.alignment.center
            ),
            # File selection row
            ft.Row(
                controls=[
                    self.file_picker,
                    self.video_path
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # Name input and Add button row
            ft.Row(
                controls=[
                    self.person_name,
                    self.add_btn
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # List button
            ft.Row(
                controls=[self.list_btn],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # People table
            ft.Container(
                content=self.people_table,
                expand=True,
                height=240,
                margin=ft.margin.only(top=20)
            )
        ]


    def edit_list(self):
        self.video_path = ft.TextField(label="Video path", width=400)
        self.file_dialog = ft.FilePicker(on_result=self._on_file_picked)
        self.file_picker = ft.IconButton(
            icon=ft.icons.FOLDER_OPEN,
            tooltip="Select video file",
            on_click=lambda e: self.page.overlay.append(self.file_dialog)
        )
        self.person_name = ft.TextField(label="Person name", width=200)
        self.add_btn = ft.ElevatedButton(text="Add", on_click=self.on_add_clicked)
        self.list_btn = ft.ElevatedButton(text="Refresh List", on_click=self.on_list_clicked)
        self.people_table = ft.Container()

    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            path = e.files[0].path
            self.video_path.value = path
            self.page.update()

    def on_add_clicked(self, e):
        if not self.recognizer:
            print("Recognizer not available")
            self.page.update()
            return
        path = self.video_path.value.strip()
        name = self.person_name.value.strip()
        if not path or not name:
            print("Provide video path and person name")
            self.page.update()
            return

        print(f"Processing {os.path.basename(path)} for {name}...")
        self.page.update()

        def job():
            try:
                # delegate to the recognizer instance
                ok = False
                if self.recognizer:
                    ok = self.recognizer.add_person(path, name)
                self.status.value = "Added" if ok else "Add failed: video may be invalid"
            except Exception as exc:
                self.status.value = f"Error: {str(exc)}"
                traceback.print_exc()
            finally:
                self.page.update()

        # run in a background thread to avoid blocking the UI
        t = threading.Thread(target=job, daemon=True)
        t.start()

    def add_person(self, video_path: str, person_name: str) -> bool:
        """Instance helper that delegates to the recognizer backend.

        Returns True on success, False on failure. Exceptions are raised to be
        handled by the caller.
        """
        if self.recognizer is None:
            raise RuntimeError("SimpleFaceRecognition backend not available")
        return bool(self.recognizer.add_person(video_path, person_name))
        
    def on_list_clicked(self, e):
        if not self.recognizer:
            self.status.value = "Recognizer not available"
            self.page.update()
            return
        counts = {}
        for n in self.recognizer.known_face_names:
            counts[n] = counts.get(n, 0) + 1

        if not counts:
            self.people_table.content = ft.Text("No people in database.")
            self.page.update()
            return

        # Build DataTable
        columns = [ft.DataColumn(ft.Text("Name")), ft.DataColumn(ft.Text("Count"))]
        rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(name)), ft.DataCell(ft.Text(str(cnt)))]) for name, cnt in sorted(counts.items(), key=lambda x: (-x[1], x[0]))]
        total = sum(counts.values())
        rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("Total", weight=ft.FontWeight.BOLD)), ft.DataCell(ft.Text(str(total), weight=ft.FontWeight.BOLD))]))

        table = ft.DataTable(columns=columns, rows=rows, column_spacing=40)
        self.people_table.content = table
        self.page.update()
