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
try:
    import pandas as pd
except Exception:
    pd = None


#================================================================================================================================================
#----------------------------------------------------------------------Main----------------------------------------------------------------------
#================================================================================================================================================





face_recognition = None
try:
    face_recognition = importlib.import_module('face_recognition')
except Exception:
    print("Install all the required modules first!\nPlease install 'face_recognition' and its dependencies (dlib, cmake, etc.).")
    raise SystemExit(1)
        


class SimpleFaceRecognition:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.database_path = "face_database.json"
        self.encodings_path = "face_encodings.pkl"
        self.load_database()

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

    def save_database(self):
        # Save face database
        try:
            with open(self.database_path, 'w') as f:
                json.dump({'names': self.known_face_names}, f)
            with open(self.encodings_path, 'wb') as f:
                pickle.dump(self.known_face_encodings, f)
            print("Database saved successfully")
        except Exception as e:
            print(f"Error saving database: {e}")

    def process_video(self, video_path, frames_to_extract=20):
        # Process video and extract face encodings
        print(f"Processing video from: {video_path}")
        face_encodings = []
        
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            return []
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Could not open video file")
            return []
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Total frames in video: {total_frames}")
        interval = max(1, total_frames // frames_to_extract)
        
        frames_processed = 0
        while frames_processed < frames_to_extract:
            ret, frame = cap.read()
            if not ret:
                print("Could not read frame from video")
                break
                
            # Skip frames according to interval
            for _ in range(interval - 1):
                cap.read()
            
            # Convert to RGB (face_recognition uses RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces and get encodings
            face_locations = face_recognition.face_locations(rgb_frame)
            if face_locations:
                # Get face encodings
                encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                if encodings:
                    face_encodings.extend(encodings)
                    frames_processed += 1
                    print(f"Processed frame {frames_processed}/{frames_to_extract}")
        
        cap.release()
        return face_encodings

    def add_person(self, video_path, person_name):
        # Add a new person from video
        print(f"\nAttempting to add person: {person_name}")
        print(f"Video path: {video_path}")
        
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return False

        print(f"Processing video for {person_name}...")
        face_encodings = self.process_video(video_path)
        
        if not face_encodings:
            print("No faces found in the video")
            return False
            
        print(f"Found {len(face_encodings)} face encodings in the video")
        
        # Add the person to our database
        for encoding in face_encodings:
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(person_name)
        
        # Save updated database
        self.save_database()
        print(f"Successfully added {person_name} with {len(face_encodings)} face variations")
        return True

    def remove_person(self, person_name):
        # Remove all entries for a person from the database
        if person_name not in self.known_face_names:
            print(f"Person '{person_name}' not found in database")
            return False

        # Find all indices for this person and remove them
        indices = [i for i, n in enumerate(self.known_face_names) if n == person_name]
        removed = 0
        for idx in reversed(indices):
            try:
                del self.known_face_names[idx]
                del self.known_face_encodings[idx]
                removed += 1
            except Exception as excpt:
                print("Error reason: ", excpt)

        # Save updated database
        self.save_database()
        print(f"Removed {removed} encoding(s) for '{person_name}' from the database")
        return True

    def list_people(self):
        # Print a summary list of people in the database with counts
        if not self.known_face_names:
            print("No people in the database.")
            return

        counts = {}
        for name in self.known_face_names:
            counts[name] = counts.get(name, 0) + 1

        print("\nPeople in database:")
        for name, cnt in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
            print(f" - {name}: {cnt} encoding(s)")

    def recognize_face(self, frame):

        # Returns a list of tuples: (face_location, name, confidence, distance)
        # where distance is the face_distance for the chosen candidate (or None).
        
        # Convert to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        results = []

        if not face_locations:
            return results

        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Keep track of which registered NAMES were already assigned to detected faces
        # in this frame so we don't repeatedly label different faces with the same person.
        used_names = set()

        for face_location, face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            confidence = 0.0
            candidate_distance = None

            if self.known_face_encodings:
                # Compare face with known faces
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                if len(distances) > 0:
                    # Sort candidate indices by distance (best first)
                    candidate_idxs = np.argsort(distances)

                    # Debug info counter
                    if not hasattr(self, 'debug_counter'):
                        self.debug_counter = 0
                    self.debug_counter += 1

                    chosen = False
                    for idx in candidate_idxs:
                        candidate_name = self.known_face_names[idx]
                        d = float(distances[idx])

                        # Skip names already assigned to another face in this frame
                        if candidate_name in used_names:
                            continue

                        # Debug print occasionally (best remaining candidate)
                        if self.debug_counter % 30 == 0:
                            print(f"\nDebug - Known faces: {len(self.known_face_encodings)}")
                            print(f"Candidate: {candidate_name} (idx={idx})")
                            print(f"Distance: {d}")

                        # Reject if distance too large (stricter cutoff)
                        if d > 0.50:
                            # No suitable known candidate for this face
                            name = "Unknown"
                            confidence = 0.0
                            candidate_distance = None
                            chosen = True
                            break

                        # Accept this candidate
                        candidate_distance = d
                        confidence = max(0.0, min(100.0, (1.0 - d) * 100.0))
                        name = candidate_name
                        used_names.add(candidate_name)
                        chosen = True
                        break

                    if not chosen:
                        # No candidate found (all candidates were already used or distances too big)
                        name = "Unknown"
                        confidence = 0.0

            # append numeric candidate distance (None when unknown)
            results.append((face_location, name, confidence, candidate_distance))

        return results

    def run_recognition(self):
        # Run real-time face recognition
        print("Starting face recognition... Press 'q' to quit")
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        # Track recognized candidates for this session
        # _session_recognized: set of names (for backward compatibility)
        # _session_recognitions: dict mapping name -> first recognition datetime
        self._session_recognized = set()
        self._session_recognitions = {}
        # _session_logs: dict name -> list of all recognition timestamps in this session
        self._session_logs = {}

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Get face recognition results
            results = self.recognize_face(frame)

            # Draw results on frame
            for (top, right, bottom, left), name, confidence, distance in results:
                # Determine status and color based on confidence and registration
                # confidence is percentage (0-100)
                if not self.known_face_encodings:
                    # No faces in database yet
                    color = (0, 0, 255)        # Red (BGR)
                    status = "Unknown"
                    name = "Unknown"
                elif name == "Unknown" or confidence == 0.0:
                    # Face detected but not matching any registered face
                    color = (0, 0, 255)        # Red (BGR)
                    status = "Unknown"
                    name = "Unknown"
                elif confidence >= 30:
                    color = (0, 200, 0)        # Green (BGR)
                    status = "Recognized"
                else:
                    color = (0, 215, 255)      # Yellow-ish (BGR)
                    status = "Low Confidence"

                thickness = 2

                # Draw face box
                cv2.rectangle(frame, (left, top), (right, bottom), color, thickness)

                # Decide what to display: only show the person's name when confidence is high
                display_name = name if confidence >= 80 else ""

                # Main label (name/status). If we don't have a confident name, show only status.
                if display_name:
                    main_label = f"{display_name} | {status}"
                else:
                    main_label = status

                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                font_thickness = 2
                main_text_size = cv2.getTextSize(main_label, font, font_scale, font_thickness)[0]
                main_bg_left = left
                main_bg_top = max(0, top - main_text_size[1] - 15)
                main_bg_right = left + main_text_size[0] + 10
                main_bg_bottom = main_bg_top + main_text_size[1] + 12
                cv2.rectangle(frame, (main_bg_left, main_bg_top), (main_bg_right, main_bg_bottom), color, cv2.FILLED)
                cv2.putText(frame, main_label, (main_bg_left + 5, main_bg_bottom - 4), font, font_scale, (255, 255, 255), font_thickness)

                # Show numeric distance overlay for debugging (if available)
                if distance is not None:
                    dbg_label = f"dist: {distance:.2f}"
                    dbg_font = cv2.FONT_HERSHEY_SIMPLEX
                    dbg_scale = 0.5
                    dbg_thick = 1
                    cv2.putText(frame, dbg_label, (left, top - 5), dbg_font, dbg_scale, (200, 200, 200), dbg_thick)

                # Record for per-session summary when confidently recognized
                if status == "Recognized" and name != "Unknown":
                    # Add to simple set for compatibility
                    try:
                        self._session_recognized.add(name)
                    except Exception:
                        pass

                    # Record first recognition timestamp for this candidate
                    if name not in self._session_recognitions:
                        try:
                            self._session_recognitions[name] = datetime.now()
                        except Exception:
                            # If datetime isn't available for any reason, ignore
                            pass

                    # Record all recognition timestamps for export
                    try:
                        self._session_logs.setdefault(name, []).append(datetime.now())
                    except Exception:
                        pass

                # If we didn't show the name on the top (low confidence) and the candidate is a registered person, show candidate and percentage below the box
                if not display_name and name != "Unknown":
                    cand_label = f"Candidate: {name} ({confidence:.1f}%)"
                    cand_font = cv2.FONT_HERSHEY_SIMPLEX
                    cand_scale = 0.5
                    cand_thick = 1
                    cand_size = cv2.getTextSize(cand_label, cand_font, cand_scale, cand_thick)[0]
                    # Position below the box
                    cand_x = left
                    cand_y = min(frame.shape[0] - 1, bottom + cand_size[1] + 8)
                    # Draw background for candidate
                    cv2.rectangle(frame, (cand_x, bottom + 4), (cand_x + cand_size[0] + 8, bottom + 4 + cand_size[1] + 6), (50, 50, 50), cv2.FILLED)
                    cv2.putText(frame, cand_label, (cand_x + 4, bottom + cand_size[1] + 6), cand_font, cand_scale, (255, 255, 255), cand_thick)

                # If we have a recorded recognition timestamp for this name, display it
                if name != "Unknown" and name in getattr(self, '_session_recognitions', {}):
                    ts = self._session_recognitions[name]
                    try:
                        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        ts_str = str(ts)

                    time_label = f"seen: {ts_str}"
                    time_font = cv2.FONT_HERSHEY_SIMPLEX
                    time_scale = 0.45
                    time_thick = 1
                    time_size = cv2.getTextSize(time_label, time_font, time_scale, time_thick)[0]

                    # Prefer to draw the time just below candidate label if present, otherwise below the box
                    if not display_name and name != "Unknown":
                        tx = cand_x
                        ty = bottom + cand_size[1] + 14 + time_size[1]
                    else:
                        # position below the face box
                        tx = left
                        ty = min(frame.shape[0] - 1, bottom + time_size[1] + 8)

                    # Draw background for time and render
                    cv2.rectangle(frame, (tx, ty - time_size[1] - 4), (tx + time_size[0] + 8, ty + 2), (60, 60, 60), cv2.FILLED)
                    cv2.putText(frame, time_label, (tx + 4, ty), time_font, time_scale, (220, 220, 220), time_thick)

            # (No extra overlay when no faces are found)

            # Show frame
            cv2.imshow('Face Recognition', frame)

            # Check for quit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # End of session - print recognized candidates list and total (with timestamps when available)
        rec_dict = getattr(self, '_session_recognitions', {})
        if not rec_dict:
            # Fallback to the simple set if timestamps weren't recorded
            recognized = sorted(getattr(self, '_session_recognized', set()))
            print("\nSession summary - recognized candidates:")
            if not recognized:
                print("  None recognized this session.")
            else:
                print("  Recognized (list):")
                for n in recognized:
                    print(f"   - {n}")
                print(f"  Total recognized candidates: {len(recognized)}")
        else:
            # Print names with their first-seen timestamp, sorted by time
            items = sorted(rec_dict.items(), key=lambda x: x[1])
            print("\nSession summary - recognized candidates (first seen):")
            for name, ts in items:
                try:
                    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    ts_str = str(ts)
                print(f"  - {name} at {ts_str}")
            print(f"  Total recognized candidates: {len(items)}")

        cap.release()
        cv2.destroyAllWindows()

    def export_session(self, out_path: str):
        """Export current session recognitions to an Excel file (or CSV fallback).

        Columns:
          - Name
          - First Seen
          - Last Seen
          - Seen Count
          - All Timestamps (comma-separated)

        Returns (ok: bool, message: str).
        """
        logs = getattr(self, '_session_logs', None)
        rec_first = getattr(self, '_session_recognitions', None)

        if logs and any(logs.values()):
            rows = []
            for name, ts_list in logs.items():
                if not ts_list:
                    continue
                try:
                    ts_list_sorted = sorted(ts_list)
                except Exception:
                    ts_list_sorted = ts_list
                first_seen = ts_list_sorted[0]
                last_seen = ts_list_sorted[-1]
                seen_cnt = len(ts_list_sorted)
                all_ts = ", ".join([t.strftime("%Y-%m-%d %H:%M:%S") if hasattr(t, 'strftime') else str(t) for t in ts_list_sorted])
                rows.append({
                    "Name": name,
                    "First Seen": first_seen.strftime("%Y-%m-%d %H:%M:%S") if hasattr(first_seen, 'strftime') else str(first_seen),
                    "Last Seen": last_seen.strftime("%Y-%m-%d %H:%M:%S") if hasattr(last_seen, 'strftime') else str(last_seen),
                    "Seen Count": seen_cnt,
                    "All Timestamps": all_ts,
                })
        elif rec_first and len(rec_first) > 0:
            # Fallback: only first-seen timestamps
            rows = []
            for name, ts in rec_first.items():
                ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, 'strftime') else str(ts)
                rows.append({
                    "Name": name,
                    "First Seen": ts_str,
                    "Last Seen": ts_str,
                    "Seen Count": 1,
                    "All Timestamps": ts_str,
                })
        else:
            return False, "No session data to export. Start camera and recognize someone first."

        # Write to Excel (preferred) or CSV
        try:
            if out_path.lower().endswith('.csv') or pd is None:
                import csv
                with open(out_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=["Name", "First Seen", "Last Seen", "Seen Count", "All Timestamps"])
                    writer.writeheader()
                    writer.writerows(rows)
                return True, f"Exported CSV: {out_path}"
            else:
                df = pd.DataFrame(rows)
                df.to_excel(out_path, index=False)
                return True, f"Exported Excel: {out_path}"
        except Exception as exc:
            traceback.print_exc()
            return False, f"Failed to export: {exc}"

    def edit_list(self):
        self.video_path = ft.TextField(label="Video path", width=400)
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
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
            self.status.value = "Recognizer not available"
            self.page.update()
            return
        path = self.video_path.value.strip()
        name = self.person_name.value.strip()
        if not path or not name:
            self.status.value = "Provide video path and person name"
            self.page.update()
            return

        self.status.value = f"Processing {os.path.basename(path)} for {name}..."
        self.page.update()

        def job():
            try:
                ok = self.recognizer.add_person(path, name)
                self.status.value = "Added" if ok else "Add failed"
            except Exception:
                self.status.value = "Error while adding"
                traceback.print_exc()
            self.page.update()

        self.run_in_thread(job)

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


class LoginSuccess(ft.Column):

    def Start_camera(self, e):
        self.recognizer.run_recognition()


    def Edit_List(self, e):
        self.page.clean()
        self.recognizer.edit_list()
        self.page.update()

    def Download_List(self, e):
        # Prompt for a file path and then export current session data
        try:
            suggested = f"recognitions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            # Ensure picker exists
            if not hasattr(self, 'save_picker'):
                self.save_picker = ft.FilePicker(on_result=self._on_save_result)
                try:
                    self.page.overlay.append(self.save_picker)
                except Exception:
                    self.page.add(self.save_picker)
            # Open save dialog
            self.save_picker.save_file(file_name=suggested)
        except Exception as exc:
            self._notify(f"Save dialog error: {exc}")

    def _on_save_result(self, e: ft.FilePickerResultEvent):
        path = getattr(e, 'path', None)
        if not path:
            self._notify("Export cancelled.")
            return
        ok, msg = self.recognizer.export_session(path)
        self._notify(msg)

    def _notify(self, message: str):
        try:
            self.page.snack_bar = ft.SnackBar(ft.Text(message))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception:
            print(message)



    def __init__(self, page: ft.Page):
        super().__init__()
        page.title = 'Face Recognition'
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        page.window_resizable = True
        page.window_maximized = False
        page.update()
        self.recognizer = SimpleFaceRecognition()
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.alignment.top_center
        self.spacing = 10
        # File save picker for downloads
        self.save_picker = ft.FilePicker(on_result=self._on_save_result)
        try:
            page.overlay.append(self.save_picker)
        except Exception:
            page.add(self.save_picker)

        self.controls = [
                ft.Container(
                content=ft.Text(
                    "Select One Item From The Menu",
                    weight=ft.FontWeight.W_900,
                    size=30,
                ),
                margin=ft.margin.only(bottom=20),
                alignment=ft.alignment.center
            ),
                ft.FilledButton(
                text="Start camera",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=16),
                ),
                width=250,
                height=50,
                on_click=self.Start_camera
            ),
                ft.FilledButton(
                text="Add/View List",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=16),
                ),
                width=250,
                height=50,
                on_click=lambda _: page.go("/Edit")
                ),
                ft.FilledButton(
                text="Remove From List",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=16),
                ),
                width=250,
                height=50,
                on_click=lambda _: page.go("/Remove")
            ),
                ft.FilledButton(
                text="Download List",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=16),
                ),
                width=250,
                height=50,
                on_click=self.Download_List
            ),
                ft.FilledButton(
                text="Logout",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=16),
                ),
                width=250,
                height=50,
                on_click=lambda _: page.go("/Login")
            )
        ]