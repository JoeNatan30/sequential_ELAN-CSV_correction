import os
import cv2
import mediapipe as mp
from collections import deque
import pandas as pd
from tqdm import tqdm

from commandLineSystem import select_videoName

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Crear instancia del landmarker en modo imagen
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='./hand_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO,
    min_hand_presence_confidence=0.45,
    min_tracking_confidence=0.45,
    num_hands=2
)

input_folder = "videos"
video_name = select_videoName()[0]

full_video_path = os.sep.join([input_folder, "originales", video_name])
print("Video:", full_video_path)

metadata_path = os.sep.join([input_folder, "metadata"])
print("metadata:", metadata_path)

cap = cv2.VideoCapture(full_video_path)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

frame_counter = 0

detection_list = []

with HandLandmarker.create_from_options(options) as landmarker:

    for i in tqdm(range(total_frames), total=total_frames):
        if not cap.isOpened():
            break
        ret, frame = cap.read()
        if not ret:
            break

        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        frame_counter += 1 

        # Crear el objeto de imagen para MediaPipe (se espera SRGB)
        frame_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        results = landmarker.detect_for_video(frame_mp, timestamp)

        # Determinar si se detectaron manos
        hands_detected = (results.hand_landmarks is not None and len(results.hand_landmarks) > 0)
        # if results.hand_landmarks is not None and len(results.hand_landmarks) > 0:
        #     print(results)
        detection_list.append(1 if hands_detected else 0)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

detection_df = pd.DataFrame({
    "frame": list(range(1, frame_counter + 1)),
    "hand_detected": detection_list
})

detection_csv_path = os.sep.join([metadata_path, f"{video_name.split('.')[0]}_dec.csv"]) 
detection_df.to_csv(detection_csv_path, index=False, sep=';')
print("Archivo de detecciones guardado en:", detection_csv_path)