# Sequential ELAN-CSV Correction

This software was created to assist in correcting sign language annotations when using two interleaved tiers. In our case, "seña" (sign) and "oración" (sentence) are annotated in a single record that follows a predefined list of signs in order.

## Goal

The main goal is to reduce the repetitive task of manually editing ELAN files to correct annotations.

## How to Use

1. Download the `hand_landmarker.task` model from MediaPipe using this [link](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task), and place it in the main folder of the repository.

2. *(Optional)* Modify the `wordList.csv` file depending on the words and the order of the signs you want to annotate in the GUI. The structure of the file should be:

    ```
    en;es
    BABY;BEBÉ
    HOUSE;CASA
    GROW;CRECER
    SMOKE;FUMAR
    WORM;GUSANO
    WATCH;RELOJ
    EGG;HUEVO
    SIT;SENTARSE
    SHAMPOO;SHAMPOO
    ```

    > For our project, the words are needed in both English and Spanish.

3. Run `prepare_folders.sh` using the command `sh prepare_folders.sh` to create all necessary folders in the repository.

### Folder Descriptions

- `videos/correcciones`: Files automatically created after running `b_....py` and `gui.py`. These CSVs are used to correct the ELAN annotations.
- `videos/ELAN_files`: Files automatically created after running `c_....py`, `d_....py`, and `gui.py`.
- `videos/metadata`: Files created after running `a_....py` and `b_....py`.
- `videos/originales`: Place all raw videos you want to process here.
- `videos/segmentados`: Folders and files created after running `f_....py`.

4. Place your raw videos into the `videos/originales` folder.

5. Run the `a_....py` and `b_....py` scripts, and select the videos you want to process.

6. Finally, run `gui.py` or use the `GUI.exe` to start correcting the annotations through the graphical interface.