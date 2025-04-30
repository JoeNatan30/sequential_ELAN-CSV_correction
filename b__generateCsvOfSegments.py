import os
import cv2

from tqdm import tqdm
from collections import deque
import pandas as pd
import numpy as np

input_folder = "videos"
from commandLineSystem import select_videoName

video_name = select_videoName()[0]

full_video_path = os.sep.join([input_folder, "originales", video_name])
output_folder = os.sep.join([input_folder, "segmentados", video_name.split(".")[0]])
metadata_csv_path = os.sep.join([input_folder, "metadata",f"{video_name.split(".")[0]}_dec.csv"])


os.makedirs(output_folder, exist_ok=True)
print("segmented:", output_folder)

metadata_path = os.sep.join([input_folder, "metadata"])
print("metadata:", metadata_path)

correciones_path = os.sep.join([input_folder, "correcciones"])
print("correcciones:", correciones_path)

cap = cv2.VideoCapture(full_video_path)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

end_tolerance_frames = 25      # Tolerancia para finalizar segmento cuando se pierden x frames consecutivos sin detección.
min_buffer_length = 75        # Mínimo número de frames para considerar un segmento válido.
pre_buffer_length = 20        # Cantidad de frames previos a incluir al inicio del segmento.
video_count = 0

# Buffer para el segmento activo y pre-buffer para guardar los últimos frames siempre
segment_buffer = []
pre_buffer = deque(maxlen=pre_buffer_length)
segment_active = False
no_hands_counter = 0
frame_counter = 0

metadata_rows = []

df_md = pd.read_csv(metadata_csv_path, encoding='latin1', sep=";")
metadata_dict = df_md.set_index("frame")["hand_detected"].to_dict()

df_wl = pd.read_csv("wordList.csv", encoding='latin1', sep=";")
columna_es = df_wl["es"]

for i in tqdm(range(total_frames), total=total_frames):
    if not cap.isOpened():
        break
    ret, frame = cap.read()
    if not ret:
        break

    pre_buffer.append((frame_counter, frame))

    timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
    frame_counter += 1 

    hands_detected = bool(metadata_dict.get(frame_counter, 0))

    if hands_detected:
        # Si se detecta la mano y el segmento aún no se ha iniciado, iniciarlo
        if not segment_active:
            segment_active = True
            # Iniciar el buffer del segmento con el contenido del pre-buffer
            segment_buffer = list(pre_buffer)
            no_hands_counter = 0
        else:
            no_hands_counter = 0  # Reinicia el contador si ya está activo
    else:
        # Si ya estamos en un segmento, aumentar el contador
        if segment_active:
            no_hands_counter += 1

    # Si el segmento está activo, añadimos el frame actual al buffer del segmento
    if segment_active:
        segment_buffer.append((frame_counter, frame))

    # Si el segmento está activo y se alcanza la tolerancia final, se finaliza el segmento
    if segment_active and no_hands_counter >= end_tolerance_frames:
        if len(segment_buffer) > (min_buffer_length + end_tolerance_frames):
            # Se eliminan los últimos frames de tolerancia para recortar el final
            segment_frames = segment_buffer[:-end_tolerance_frames]

            numeracion = video_count//2+1
            n_frames = segment_frames[-1][0] - segment_frames[0][0]
            
            if numeracion-1 < len(columna_es):
                seña_name = columna_es[numeracion-1]
            else:
                seña_name = "__Nombre__"

            if video_count % 2 == 0:
                print(f"Segmento de seña {numeracion} completo, guardado (from: {segment_frames[0][0]}, frames: {len(segment_frames)})")
                final_path = f'{numeracion}_{seña_name}_a_sena.avi'
                out_path = os.sep.join([output_folder, final_path])
                temp_n_frames =  segment_frames[-1][0] - segment_frames[0][0]
                formula = np.maximum(np.log(100/temp_n_frames), 0)
                tier = "seña"
            else:
                print(f"Segmento de oración {numeracion} completo, guardado (from: {segment_frames[0][0]}, frames: {len(segment_frames)})")
                final_path = f'{numeracion}_{seña_name}_b_oracion.avi'
                out_path = os.sep.join([output_folder, final_path])
                formula = np.maximum(np.log(temp_n_frames/n_frames), 0)
                tier = "oración"
            
            height, width, _ = segment_frames[0][1].shape

            out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

            video_count += 1

            for (_, frm) in segment_frames:
                out.write(frm)
            out.release()

            metadata_rows.append({
                "segment_file": final_path,
                "start_frame": segment_frames[0][0],
                "end_frame": segment_frames[-1][0],
                "N_frames": n_frames,
                "Error_metric": formula,
                "tier": tier
            })

        else:
            print("Segmento descartado por no tener suficientes frames.", len(segment_buffer))

        segment_active = False
        segment_buffer = []
        no_hands_counter = 0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


metadata_df = pd.DataFrame(metadata_rows)
metadata_csv_path = os.sep.join([metadata_path, f"{video_name.split('.')[0]}_seg.csv"])
metadata_df.to_csv(metadata_csv_path, index=False, sep=";", encoding="latin1")
print("Metadata guardada en:", metadata_csv_path)

correciones_csv_path = os.sep.join([correciones_path, f"{video_name.split('.')[0]}_ok.csv"])
metadata_df.to_csv(correciones_csv_path, index=False, sep=";", encoding="latin1")
print("correciones guardada en:", correciones_csv_path)