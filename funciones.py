import os

import pandas as pd
import numpy as np
import pympi

from PyQt5.QtWidgets import  QFileDialog

def generate_elan_first(self):
    """
    - Selecciona el video.
    - Lee el CSV de segmentación (generado en el proceso anterior).
    - Usa pympi para crear un archivo ELAN (.eaf) agregando las anotaciones.
    """
    video_file, _ = QFileDialog.getOpenFileName(self, "Selecciona el video para ELAN (primer CSV)", "videos/originales", "Video Files (*.mp4 *.avi)")
    if not video_file:
        self.log("No se seleccionó video.")
        return
    video_name = os.path.basename(video_file)
    self.log(f"Generando ELAN desde primer CSV para video: {video_name}")
    
    input_folder = "videos"
    full_video_path = os.path.join("..", "..", input_folder, "originales", video_name)
    correccion_csv_path = os.path.join(input_folder, "metadata", f"{os.path.splitext(video_name)[0]}_seg.csv")
    elan_path = os.path.join(input_folder, "ELAN_files", f"{os.path.splitext(video_name)[0]}.eaf")
    
    eaf = pympi.Elan.Eaf()
    eaf.add_linked_file(full_video_path, full_video_path, "video/mp4", 0)
    
    try:
        df = pd.read_csv(correccion_csv_path, sep=";", encoding="latin1")
        df = df.dropna()
        df = df.sort_values(by="start_frame")
    except Exception as e:
        self.log(f"Error al leer CSV de segmentación: {e}")
        return
    
    annotations = []
    fps = 59.94005994005994  # Este valor puede ajustarse
    
    # Leer la lista de palabras para nombres
    try:
        df_wl = pd.read_csv("wordList.csv", encoding='latin1', sep=";")
        columna_es = df_wl["es"].tolist()
    except Exception as e:
        self.log(f"Error al leer wordList.csv: {e}")
        return
    
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
    
    for start_frame, end_frame, text, tier in annotations:
        start_time = (start_frame / fps) * 1000
        end_time = (end_frame / fps) * 1000
        if tier not in eaf.tiers:
            eaf.add_tier(tier)
        eaf.add_annotation(tier, int(start_time), int(end_time), text)
    
    eaf.to_file(elan_path)
    self.log(f"Archivo ELAN guardado en: {elan_path}")

def generate_elan_corrected(self):
    """
    - Selecciona el video.
    - Lee el CSV corregido desde la carpeta 'correcciones'.
    - Genera un archivo ELAN usando pympi y guarda las anotaciones.
    """
    video_file, _ = QFileDialog.getOpenFileName(self, "Selecciona el video para ELAN (CSV corregido)", "videos/originales", "Video Files (*.mp4 *.avi)")
    if not video_file:
        self.log("No se seleccionó video.")
        return
    video_name = os.path.basename(video_file)
    self.log(f"Generando ELAN desde CSV corregido para video: {video_name}")
    
    input_folder = "videos"
    full_video_path = os.path.join("..", "..", input_folder, "originales", video_name)
    correccion_csv_path = os.path.join(input_folder, "correcciones", f"{os.path.splitext(video_name)[0]}_ok.csv")
    elan_path = os.path.join(input_folder, "ELAN_files", f"{os.path.splitext(video_name)[0]}.eaf")
    
    eaf = pympi.Elan.Eaf()
    eaf.add_linked_file(full_video_path, full_video_path, "video/mp4", 0)
    
    try:
        df = pd.read_csv(correccion_csv_path, sep=";", encoding="latin1")
        df.dropna(inplace=True)
        df = df.sort_values(by="start_frame")
    except Exception as e:
        self.log(f"Error al leer CSV corregido: {e}")
        return
    
    annotations = []
    fps = 59.94005994005994
    
    for idx, row in df.iterrows():
        segment_file = row["segment_file"]
        start_frame = row["start_frame"]
        end_frame = row["end_frame"]
        n_frames = end_frame - start_frame
        
        if '_a_' in segment_file:
            label_extra = 'seña'
            name = segment_file.split("_a_")[0]
            temp_n_frames = end_frame - start_frame
            formula = np.maximum(np.log(100 / temp_n_frames), 0)
        elif '_b_' in segment_file:
            label_extra = 'oración'
            name = segment_file.split("_b_")[0]
            formula = 0  # Ajusta si lo requieres
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
    self.log(f"Archivo ELAN (corregido) guardado en: {elan_path}")

def generar_csv_from_elan_final(self):
    """
    Función que integra el proceso de generar un CSV a partir del archivo ELAN final.
    Se utiliza el video seleccionado para derivar el nombre base y buscar:
        - el archivo ELAN en videos/ELAN_files, y
        - almacenar el CSV en videos/correcciones.
    """
    # Seleccionar el video (se usa para extraer el nombre base)
    video_file, _ = QFileDialog.getOpenFileName(
        self,
        "Selecciona el video para generar CSV a partir del ELAN final",
        "videos/originales",
        "Video Files (*.mp4 *.avi)"
    )
    if not video_file:
        self.log("No se seleccionó video.")
        return
    video_name = os.path.basename(video_file)
    base_name = os.path.splitext(video_name)[0]
    self.log(f"Video seleccionado: {video_name}")
    
    input_folder = "videos"
    fps = 59.94005994005994

    # Construir rutas para ELAN y para guardar el CSV corregido
    elan_path = os.path.join(input_folder, "ELAN_files", f"{base_name}.eaf")
    correccion_csv_path = os.path.join(input_folder, "correcciones", f"{base_name}_ok.csv")
    
    # Cargar el archivo EAF
    try:
        eaf = pympi.Elan.Eaf(elan_path)
    except Exception as e:
        self.log(f"Error al cargar el archivo EAF '{elan_path}': {e}")
        return

    # Obtener los tiers (capas) disponibles en el EAF
    tiers = eaf.get_tier_names()
    self.log("Tiers encontrados en el EAF: " + ", ".join(tiers))

    # Recopilar las anotaciones de todos los tiers
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
        
        # Convertir tiempo de milisegundos a frames
        start_frame = round((start_ms / 1000) * fps)
        end_frame   = round((end_ms / 1000) * fps)
        n_frames = end_frame - start_frame
        
        if tier == "seña":
            segment_file = f"{annotation_text}_a_seña.avi"
            temp_n_frames = n_frames
            formula = np.maximum(np.log(100 / temp_n_frames), 0)
            prev_temp_n_frames = temp_n_frames
        elif tier == "oración":
            segment_file = f"{annotation_text}_b_oración.avi"
            if prev_temp_n_frames is None:
                prev_temp_n_frames = n_frames
            formula = np.maximum(np.log(prev_temp_n_frames / n_frames), 0)
        else:
            segment_file = f"{annotation_text}_{tier}.avi"
            formula = 0
        
        rows.append([segment_file, start_frame, end_frame, n_frames, formula, tier])
    
    df_result = pd.DataFrame(rows, columns=["segment_file", "start_frame", "end_frame", "N_frames", "Error_metric", "Tier"])
    df_result = df_result.sort_values(by="start_frame")
    
    try:
        df_result.to_csv(correccion_csv_path, index=False, encoding="latin1", sep=";")
        self.log(f"CSV generado exitosamente en: {correccion_csv_path}")
    except Exception as e:
        self.log(f"Error al guardar el CSV en '{correccion_csv_path}': {e}")