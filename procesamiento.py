import os
from commandLineSystem import select_process, select_videoName
from c__generateElanfromFirstCSV import generateElanfromFirstCSV
from d__generateElanUsingCsvCorregido import generateElanUsingCsvCorregido
from e__generarCsvFromElanFinal import generarCsvFromElanFinal
from f__recortarVideos import recortarVideos

while True:
    process = select_process()
    video_name = select_videoName()[0]
    print(video_name)

    if video_name.split("__")[0] == "c":
        generateElanfromFirstCSV(video_name)
    elif video_name.split("__")[0] == "d":
        generateElanUsingCsvCorregido(video_name)
    elif video_name.split("__")[0] == "e":
        generarCsvFromElanFinal(video_name)
    elif video_name.split("__")[0] == "f":
        recortarVideos(video_name)
    while True:
        respuesta = input("¿Desea continuar? (s/n): ").strip().lower()
        if respuesta == 's':
            break
        elif respuesta == 'n':
            break
    if respuesta == 'n':
        break