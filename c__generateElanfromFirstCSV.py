import os
import pandas as pd
import pympi

def generateElanfromFirstCSV(video_name):
    input_folder = "videos"
    #video_name = "JERSON-FINAL.MP4"

    full_video_path = os.sep.join(["..","..",input_folder, "originales", video_name])
    correccion_csv_path = os.sep.join([input_folder, "metadata",f"{video_name.split(".")[0]}_seg.csv"])
    elan_path = os.sep.join([input_folder, "ELAN_files", f"{video_name.split(".")[0]}.eaf"])

    eaf = pympi.Elan.Eaf()

    eaf.add_linked_file(full_video_path, full_video_path, "video/mp4", 0)

    df = pd.read_csv(correccion_csv_path, sep=";", encoding="latin1")
    df = df.dropna()
    df = df.sort_values(by="start_frame")

    annotations = []

    for idx, row in df.iterrows():
        segment_file = row["segment_file"]
        start_frame = row["start_frame"]
        end_frame = row["end_frame"]
        print(segment_file, end_frame)
        if '_a_' in segment_file:
            label_extra = 'seña'
            name = segment_file.split("_a_")[0]
        elif '_b_' in segment_file:
            label_extra = 'oración'
            name = segment_file.split("_b_")[0]


        annotations.append((start_frame, end_frame, name, label_extra))

        fps = 59.94005994005994  # Ejemplo de FPS del video

    # Recorrer las anotaciones y agregarlas al archivo EAF
    for start_frame, end_frame, text, tier in annotations:
        # Convertir frames a tiempo en milisegundosp
        start_time = (start_frame / fps) * 1000
        end_time = (end_frame / fps) * 1000
        # Si el tier no existe, se crea
        if tier not in eaf.tiers:
            eaf.add_tier(tier)
        # Agregar la anotación al tier correspondiente
        eaf.add_annotation(tier, int(start_time), int(end_time), text)

    # Guardar el archivo ELAN (EAF)
    eaf.to_file(elan_path)


generateElanfromFirstCSV("4. JUNIOR-FINAL.mp4")