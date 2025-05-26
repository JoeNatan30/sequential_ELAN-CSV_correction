import pympi
import pandas as pd
import numpy as np
import os


def generarCsvFromElanFinal(video_name):

    input_folder = "videos"

    fps = 59.94005994005994

    elan_path = os.sep.join([input_folder, "ELAN_files", f"{video_name.split(".")[0]}.eaf"])
    correccion_csv_path = os.sep.join([input_folder, "correcciones",f"{video_name.split(".")[0]}_ok.csv"])
    # Carga el archivo EAF con pympi
    eaf = pympi.Elan.Eaf(elan_path)

    # Obtenemos los nombres de los tiers (capas) en el archivo
    tiers = eaf.get_tier_names()
    print("Tiers encontrados en el EAF:", tiers)

    temp_row = []

    for tier_name in tiers:
        # Obtenemos las anotaciones de ese tier.
        # Cada anotación tiene la forma: (tiempo_inicio_ms, tiempo_fin_ms, texto_anotacion)
        annotations = eaf.get_annotation_data_for_tier(tier_name)
        
        for (start_ms, end_ms, annotation_text) in annotations:
            temp_row.append([start_ms, end_ms, annotation_text, tier_name])

    df = pd.DataFrame(temp_row, columns=["start_frame", "end_frame", "annotation_text", "Tier"])
    df = df.sort_values(by="start_frame")
    # Preparamos una lista para ir guardando la información

    rows = []

    for _, (start_ms, end_ms, annotation_text, tier) in df.iterrows():
        # Convertimos ms a frames (redondeando al entero más cercano)
        start_frame = round((start_ms / 1000) * fps)
        end_frame   = round((end_ms / 1000) * fps)
        
        # Construimos el nombre del archivo segmentado.
        # Aquí puedes adaptar la lógica para generar algo como 
        # "1_BEBÉ_a_sena.avi", "1_BEBÉ_b_oracion.avi", etc.
        #
        # Por ejemplo, supongamos que la anotación (annotation_text) 
        # indica parte de ese nombre y el tier_name indica "a_sena" o "b_oracion".
        
        n_frames = end_frame- start_frame

        if tier == "seña":
            segment_file = f"{annotation_text}_a_{tier}.avi"
            temp_n_frames = end_frame- start_frame
            formula = np.maximum(np.log(100/temp_n_frames), 0)
        elif tier == "oración":
            segment_file = f"{annotation_text}_b_{tier}.avi"
            formula = np.maximum(np.log(temp_n_frames/n_frames), 0)

        rows.append([segment_file, start_frame, end_frame, n_frames, formula, tier])

    # Creamos un DataFrame con la información recolectada
    df = pd.DataFrame(rows, columns=["segment_file", "start_frame", "end_frame", "N_frames", "Error_metric", "Tier"])
    df = df.sort_values(by="start_frame")

    # Exportamos a CSV
    df.to_csv(correccion_csv_path, index=False, encoding="latin1", sep=";")


generarCsvFromElanFinal("5_JERSON-FINAL.mp4")