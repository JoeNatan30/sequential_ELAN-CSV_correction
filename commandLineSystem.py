# Standard library imports
import os

# Third party imports

# Local imports
#
def clear_terminal():
    # En Windows se usa 'cls' y en Unix 'clear'
    os.system('cls' if os.name == 'nt' else 'clear')

# To choose just one option
def change_unique_option_state(chosen, ans):

    chosen = {k:False for k, _ in chosen.items()}
    chosen[ans] = True

    return chosen

# To choose just multiple option
def change_options_state(chosen, ans):

    if chosen[ans]:
        chosen[ans] = False
    else:
        chosen[ans] = True

    return chosen

def get_selected_option_names(options,chosen):
    return [name for name, isChosed in zip(options, chosen.values()) if isChosed]

#print in console the options
def show_options(options, name):

    print("##################################")
    print(f"Elige {name}: (solo el número)\n")

    for pos, opt in enumerate(options):
        print(f"{pos+1}) {opt}")

# To select wich dataset are in "datasets" folders
def select_dataset():
    ruta = "./videos/originales"
    options = [archivo for archivo in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, archivo))]
    print(options)
    options = sorted(options, key=lambda x: int(x.split('_')[0]))
    print(options)
    # dictionary of selected options
    chosen = {str(pos+1):False for pos in range(len(options))}

    while(True):

        show_options(options, 'el video')

        print(f"\n{len(options)+1}) continue\n")

        chosen_names = get_selected_option_names(options,chosen)
        
        print("Selected:",*chosen_names)

        ans = input("Escriba una opción: ")

        if ans == str(len(options)+1):
            return chosen_names

        if ans not in chosen.keys():
            continue
        
        chosen = change_options_state(chosen, ans)

# To select the desired keypoint stimator
def select_videoName():

    ruta = "./videos/originales"
    options = [archivo for archivo in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, archivo))]

    options = sorted(options, key=lambda x: int(x.split('_')[0]))

    # dictionary of selected options
    chosen = {str(pos+1):False for pos in range(len(options))}

    while(True):
        clear_terminal()

        show_options(options, 'el video')

        print(f'\n{len(options)+1}) continue\n')

        chosen_names = get_selected_option_names(options,chosen)
        
        print("Selected:",*chosen_names)

        ans = input("write an option: ")

        if ans == str(len(options)+1):
            return chosen_names

        if ans not in chosen.keys():
            continue

        chosen = change_unique_option_state(chosen, ans)


def select_process():

    ruta = "."
    options = [archivo for archivo in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, archivo)) and archivo.split(".")[-1] == "py" and "__" in archivo]

    print(options)

    # dictionary of selected options
    chosen = {str(pos+1):False for pos in range(len(options))}

    while(True):
        clear_terminal()

        show_options(options, 'el proceso')

        print(f'\n{len(options)+1}) continue\n')

        chosen_names = get_selected_option_names(options,chosen)
        
        print("Selected:",*chosen_names)

        ans = input("write an option: ")

        if ans == str(len(options)+1):
            return chosen_names

        if ans not in chosen.keys():
            continue

        chosen = change_unique_option_state(chosen, ans)