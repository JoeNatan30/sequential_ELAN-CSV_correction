import os
import sys

import pandas as pd
import numpy as np
import pympi

import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTextEdit, QLabel, QComboBox, QGroupBox
)

from PyQt5.QtGui import QIcon

def resource_path(relative_path):
    """
    To obtain the absolute path to the resource, necessary for PyInstaller in onefile mode.
    """
    try:
        # sys._MEIPASS is established by PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.create_required_folders()

        # Default language: Spanish.
        self.language = "es"
        self.video_file = None  # Almacena el video seleccionado

        # Dictionary for translations
        # Keys are language codes, values are dictionaries with UI texts.
        self.translations = {
            "es": {
                "title": "Integración: Video, CSV y ELAN",
                "btn_select_video": "Seleccionar Video",
                "lbl_video_selected": "Video seleccionado: {}",
                "btn_elan_corr": "CSV → ELAN",
                "btn_csv_from_elan_final": "ELAN → CSV",
                "btn_open_csv": "Abrir archivo CSV",
                "btn_open_elan": "Abrir archivo ELAN",
                "tip_generate_elan": "Toma el archivo CSV de segmentación y genera o reemplaza el archivo ELAN",
                "tip_generate_csv":  "Toma el archivo ELAN y genera o reemplaza el archivo CSV",
                "group_procesamiento": "Procesamiento",
                "group_abrir_archivos": "Abrir Archivos",
                "select_video_elan_corr": "Selecciona el video para ELAN",
                "select_video_csv_from_elan_final": "Selecciona el video para generar CSV",
                "no_video_selected": "No se seleccionó video. Por favor, selecciónalo en 'Seleccionar Video'.",
                "generating_elan_corr": "Generando ELAN Corregido para video: {}",
                "video_selected": "Video seleccionado: {}",
                "tiers_found": "Tiers encontrados en el EAF: {}",
                "elan_file_saved": "Archivo ELAN guardado en: {}",
                "elan_corrected_saved": "Archivo ELAN corregido guardado en: {}",
                "csv_generated_success": "CSV final generado exitosamente en: {}",
                "error_read_csv_segmentation": "Error al leer CSV de segmentación: {}",
                "error_read_csv_corrected": "Error al leer CSV corregido: {}",
                "error_loading_eaf": "Error al cargar el archivo EAF '{}' : {}"
            },
            "en": {
                "title": "Integration: Video, CSV and ELAN",
                "btn_select_video": "Select Video",
                "lbl_video_selected": "Selected video: {}",
                "btn_elan_corr": "CSV → ELAN",
                "btn_csv_from_elan_final": "ELAN → CSV",
                "btn_open_csv": "Open CSV File",
                "btn_open_elan": "Open ELAN File",
                "tip_generate_elan": "Takes the segmentation CSV file and generates or replaces the ELAN file",
                "tip_generate_csv":  "Takes the ELAN file and generates or replaces the CSV file",
                "group_procesamiento": "Processing",
                "group_abrir_archivos": "Open Files",
                "select_video_elan_corr": "Select video for corrected ELAN",
                "select_video_csv_from_elan_final": "Select video to generate final CSV",
                "no_video_selected": "No video selected. Please select a video using 'Select Video'.",
                "generating_elan_corr": "Generating corrected ELAN for video: {}",
                "video_selected": "Selected video: {}",
                "tiers_found": "Tiers found in EAF: {}",
                "elan_file_saved": "ELAN file saved at: {}",
                "elan_corrected_saved": "Corrected ELAN file saved at: {}",
                "csv_generated_success": "Final CSV successfully generated at: {}",
                "error_read_csv_segmentation": "Error reading segmentation CSV: {}",
                "error_read_csv_corrected": "Error reading corrected CSV: {}",
                "error_loading_eaf": "Error loading EAF file '{}' : {}"
            }
        }

        self.init_ui()
        self.update_ui_texts()

    def init_ui(self):
        layout = QVBoxLayout()

        #  ComboBox for language selection (with icons if available)
        self.language_combo = QComboBox()

        t = self.translations[self.language]

        try:
            icon_es = QIcon(resource_path(os.path.join("icons", "flag_es.jpg")))
            icon_en = QIcon(resource_path(os.path.join("icons", "flag_en.png")))
            self.language_combo.addItem(icon_es, "Español", userData="es")
            self.language_combo.addItem(icon_en, "English", userData="en")
        except Exception:
            self.language_combo.addItem("Español", userData="es")
            self.language_combo.addItem("English", userData="en")
        self.language_combo.currentIndexChanged.connect(self.change_language)
        layout.addWidget(self.language_combo)

        # botom to select video
        self.btn_select_video = QPushButton()
        self.btn_select_video.clicked.connect(self.select_video)
        layout.addWidget(self.btn_select_video)

        # Label to show selected video
        self.lbl_video_selected = QLabel()
        layout.addWidget(self.lbl_video_selected)

        # processing group functions
        self.procesar_group = QGroupBox()  # To update the tile in the user interface update_ui_texts
        procesar_layout = QVBoxLayout()
        self.btn_elan_corr = QPushButton()
        self.btn_elan_corr.clicked.connect(self.generate_elan)
        self.btn_elan_corr.setToolTip(t["tip_generate_elan"])
        
        procesar_layout.addWidget(self.btn_elan_corr)
        self.btn_csv_from_elan_final = QPushButton()
        self.btn_csv_from_elan_final.clicked.connect(self.generar_csv)
        self.btn_csv_from_elan_final.setToolTip(t["tip_generate_csv"])
        procesar_layout.addWidget(self.btn_csv_from_elan_final)

        self.procesar_group.setLayout(procesar_layout)
        layout.addWidget(self.procesar_group)

        # Grupo de acciones para abrir archivos
        self.abrir_group = QGroupBox()  # Título se actualizará en update_ui_texts
        abrir_layout = QVBoxLayout()
        self.btn_open_csv = QPushButton()
        self.btn_open_csv.clicked.connect(self.abrir_csv)
        abrir_layout.addWidget(self.btn_open_csv)
        self.btn_open_elan = QPushButton()
        self.btn_open_elan.clicked.connect(self.abrir_elan)
        abrir_layout.addWidget(self.btn_open_elan)
        self.abrir_group.setLayout(abrir_layout)
        layout.addWidget(self.abrir_group)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_required_folders(self):
        """
        to create the required folders for the application. 
        if these folders already exist, it does nothing.
        """
        base_folder = "videos"
        subfolders = ["correcciones", "originales", "ELAN_files"]
        os.makedirs(base_folder, exist_ok=True)
        for folder in subfolders:
            os.makedirs(os.path.join(base_folder, folder), exist_ok=True)

    def update_ui_texts(self):
        t = self.translations[self.language]
        self.setWindowTitle(t["title"])
        self.btn_select_video.setText(t["btn_select_video"])
        self.btn_elan_corr.setText(t["btn_elan_corr"])
        self.btn_csv_from_elan_final.setText(t["btn_csv_from_elan_final"])
        self.btn_open_csv.setText(t["btn_open_csv"])
        self.btn_open_elan.setText(t["btn_open_elan"])
        # to update QGroupBox titles
        self.procesar_group.setTitle(t["group_procesamiento"])
        self.abrir_group.setTitle(t["group_abrir_archivos"])
        if self.video_file:
            self.lbl_video_selected.setText(t["lbl_video_selected"].format(os.path.basename(self.video_file)))
        else:
            self.lbl_video_selected.setText("")

    def change_language(self):
        self.language = self.language_combo.currentData()
        self.update_ui_texts()

    def log(self, message):
        self.log_area.append(message)

    def select_video(self):
        t = self.translations[self.language]
        video_file, _ = QFileDialog.getOpenFileName(self, t["btn_select_video"], "videos/originales", "Video Files (*.mp4 *.avi)")
        if not video_file:
            self.log(t["no_video_selected"])
            return
        self.video_file = video_file
        self.log(t["video_selected"].format(os.path.basename(video_file)))
        self.update_ui_texts()

    def generate_elan(self):
        """
        to generate an ELAN file from the selected video and the CSV file.
        The ELAN file is saved in the "videos/ELAN_files" folder with the same name as the video.
        """
        t = self.translations[self.language]
        if not self.video_file:
            self.log(t["no_video_selected"])
            return

        video_name = os.path.basename(self.video_file)
        self.log(t["generating_elan_corr"].format(video_name))

        input_folder = "videos"
        full_video_path = os.path.abspath(os.path.join("..", "..", input_folder, "originales", video_name))
        correccion_csv_path = os.path.join(input_folder, "correcciones", f"{os.path.splitext(video_name)[0]}_ok.csv")
        elan_path = os.path.join(input_folder, "ELAN_files", f"{os.path.splitext(video_name)[0]}.eaf")

        eaf = pympi.Elan.Eaf()
        eaf.add_linked_file(full_video_path, full_video_path, "video/mp4", 0)

        try:
            df = pd.read_csv(correccion_csv_path, sep=";", encoding="latin1")
            df.dropna(inplace=True)
            df = df.sort_values(by="start_frame")
        except Exception as e:
            self.log(t["error_read_csv_corrected"].format(e))
            return

        annotations = []
        fps = 59.94005994005994
        for idx, row in df.iterrows():
            segment_file = row["segment_file"]
            start_frame = row["start_frame"]
            end_frame = row["end_frame"]
            if '_a_' in segment_file:
                label_extra = 'seña'
                name = segment_file.split("_a_")[0]
            elif '_b_' in segment_file:
                label_extra = 'oración'
                name = segment_file.split("_b_")[0]
            else:
                label_extra = 'desconocido'
                name = segment_file.split("_")[0]
            annotations.append((start_frame, end_frame, name, label_extra))
        for start_frame, end_frame, name, tier in annotations:
            start_time = (start_frame / fps) * 1000
            end_time = (end_frame / fps) * 1000
            if tier not in eaf.tiers:
                eaf.add_tier(tier)
            eaf.add_annotation(tier, int(start_time), int(end_time), name)
        if os.path.exists(elan_path):
            os.remove(elan_path)
        eaf.to_file(elan_path)
        self.log(t["elan_corrected_saved"].format(elan_path))

    def generar_csv(self):
        t = self.translations[self.language]
        if not self.video_file:
            self.log(t["no_video_selected"])
            return
        video_name = os.path.basename(self.video_file)
        base_name = os.path.splitext(video_name)[0]
        self.log(t["video_selected"].format(video_name))

        input_folder = "videos"
        fps = 59.94005994005994

        elan_path = os.path.join(input_folder, "ELAN_files", f"{base_name}.eaf")
        correccion_csv_path = os.path.join(input_folder, "correcciones", f"{base_name}_ok.csv")

        try:
            eaf = pympi.Elan.Eaf(elan_path)
        except Exception as e:
            self.log(t["error_loading_eaf"].format(elan_path, e))
            return

        tiers = eaf.get_tier_names()
        self.log(t["tiers_found"].format(", ".join(tiers)))

        temp_rows = []
        for tier_name in tiers:
            annotations = eaf.get_annotation_data_for_tier(tier_name)
            for (start_ms, end_ms, annotation_text) in annotations:
                temp_rows.append([start_ms, end_ms, annotation_text, tier_name])
        df = pd.DataFrame(temp_rows, columns=["start_ms", "end_ms", "annotation_text", "Tier"])
        df = df.sort_values(by="start_ms")

        rows = []
        prev_temp_n_frames = None
        for _, row in df.iterrows():
            start_ms = row["start_ms"]
            end_ms = row["end_ms"]
            annotation_text = row["annotation_text"]
            tier = row["Tier"]
            start_frame = round((start_ms / 1000) * fps)
            end_frame = round((end_ms / 1000) * fps)
            n_frames = end_frame - start_frame
            if tier == "seña":
                segment_file = f"{annotation_text}_a_seña.avi"
                temp_n_frames = n_frames
                formula = np.maximum(np.log(50 / temp_n_frames), 0)#*100
                prev_temp_n_frames = temp_n_frames
            elif tier == "oración":
                segment_file = f"{annotation_text}_b_oración.avi"
                if prev_temp_n_frames is None:
                    prev_temp_n_frames = n_frames
                formula = np.maximum(np.log(prev_temp_n_frames / n_frames), 0)#*100
            else:
                segment_file = f"{annotation_text}_{tier}.avi"
                formula = 0
            rows.append([segment_file, start_frame, end_frame, n_frames, formula, tier])
        df_result = pd.DataFrame(rows, columns=["segment_file", "start_frame", "end_frame", "N_frames", "Error_metric", "Tier"])
        df_result = df_result.sort_values(by="start_frame")

        try:
            df_result.to_csv(correccion_csv_path, index=False, encoding="latin1", sep=";")
            self.log(t["csv_generated_success"].format(correccion_csv_path))
        except Exception as e:
            self.log(t["error_loading_eaf"].format(correccion_csv_path, e))

    # functions to open external files
    def abrir_csv(self):
        t = self.translations[self.language]
        if not self.video_file:
            self.log(t["no_video_selected"])
            return
        base_name = os.path.splitext(os.path.basename(self.video_file))[0]
        csv_path = os.path.join("videos", "correcciones", f"{base_name}_ok.csv")
        if not os.path.exists(csv_path):
            self.log(f"El archivo CSV {csv_path} no existe.")
            return
        self.open_file(csv_path)

    def abrir_elan(self):
        t = self.translations[self.language]
        if not self.video_file:
            self.log(t["no_video_selected"])
            return
        base_name = os.path.splitext(os.path.basename(self.video_file))[0]
        elan_path = os.path.join("videos", "ELAN_files", f"{base_name}.eaf")
        if not os.path.exists(elan_path):
            self.log(f"El archivo ELAN {elan_path} no existe.")
            return
        self.open_file(elan_path)

    def open_file(self, file_path):
        try:
            if sys.platform.startswith('win'):
                os.startfile(file_path)
            elif sys.platform.startswith('darwin'):
                subprocess.call(['open', file_path])
            else:
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            self.log(f"Error al abrir {file_path}: {e}")

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
