import os
import pandas as pd
import pympi

from moviepy.video.io.VideoFileClip import VideoFileClip
from commandLineSystem import select_videoName

def recortarVideos(video_name):
    video_name = select_videoName()[0]
    input_folder = "videos"


    full_video_path = os.sep.join([input_folder, "originales", video_name])
    correccion_csv_path = os.sep.join([input_folder, "correcciones",f"{video_name.split(".")[0]}_ok.csv"])
    output_csv_path = os.sep.join([input_folder,"segmentados",video_name.split(".")[0]])

    eaf = pympi.Elan.Eaf()

    eaf.add_linked_file(full_video_path, full_video_path, "video/mp4", 0)

    df = pd.read_csv(correccion_csv_path, sep=";", encoding="latin1")

    df = df.dropna()
    annotations = []

    fps = 59.94005994005994

    for idx, row in df.iterrows():
        segment_file = row["segment_file"]
        start_frame = row["start_frame"]
        end_frame = row["end_frame"]

        eafFileName = segment_file.replace(".MP4", ".eaf")

        if 'seña' in segment_file:
            name = segment_file.split("_a_")[0]
        elif 'oración' in segment_file:
            name = segment_file.split("_b_")[0]


        annotations.append((start_frame, end_frame, name))

    video = VideoFileClip(full_video_path)

    for start_frame, end_frame, label in annotations:
        start_time = start_frame / fps
        end_time = end_frame / fps
        subclip = video.subclipped(start_time, end_time)
        output_filename = os.sep.join([output_csv_path, f"{label}.mp4"])
        subclip.write_videofile(output_filename, codec="libx264")