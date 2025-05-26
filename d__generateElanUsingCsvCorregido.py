import os
import pandas as pd
import numpy as np
import pympi

def generateElanUsingCsvCorregido(video_name):

    input_folder = "videos"

    full_video_path = os.sep.join(["..","..",input_folder, "originales", video_name])
    correccion_csv_path = os.sep.join([input_folder, "correcciones",f"{video_name.split(".")[0]}_ok.csv"])
    elan_path = os.sep.join([input_folder, "ELAN_files", f"{video_name.split(".")[0]}.eaf"])

    eaf = pympi.Elan.Eaf()

    eaf.add_linked_file(full_video_path, full_video_path, "video/mp4", 0)

    df = pd.read_csv(correccion_csv_path, sep=";", encoding="latin1")  
    df.dropna(inplace=True)
    df = df.sort_values(by="start_frame")

    annotations = []

    for idx, row in df.iterrows():
        segment_file = row["segment_file"]
        start_frame = row["start_frame"]
        end_frame = row["end_frame"]

        n_frames = end_frame - start_frame

        if '_a_' in segment_file:

            label_extra = 'seña'
            name = segment_file.split("_a_")[0]
            temp_n_frames =  end_frame - start_frame
            formula = np.maximum(np.log(100/temp_n_frames), 0)
        elif '_b_' in segment_file:
            label_extra = 'oración'
            name = segment_file.split("_b_")[0]
            formula = np.maximum(np.log(temp_n_frames/n_frames), 0)

        annotations.append((start_frame, end_frame, name, label_extra))

        fps = 59.94005994005994  

    # Recorrer las anotaciones y agregarlas al archivo EAF
    for start_frame, end_frame, name, tier in annotations:
        # Convertir frames a tiempo en milisegundosp
        start_time = (start_frame / fps) * 1000
        end_time = (end_frame / fps) * 1000
        # Si el tier no existe, se crea
        if tier not in eaf.tiers:
            eaf.add_tier(tier)

        # Agregar la anotación al tier correspondiente
        eaf.add_annotation(tier, int(start_time), int(end_time), name)

    if os.path.exists(elan_path):
        os.remove(elan_path)
    # Guardar el archivo ELAN (EAF)
    eaf.to_file(elan_path)

generateElanUsingCsvCorregido("5_JERSON-FINAL.mp4")