# Based on Tiled_ZoeDepth,_v3.ipynb

import numpy as np
import cv2
import torch
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.ndimage import gaussian_filter
import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import sys
import shutil
import threading
import time
import re
from idlelib.tooltip import Hovertip
import atexit
import requests
import zipfile
import io
import math 

contents_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
torch_cache = '.\\torch\\cache'

if not os.path.exists(torch_cache):
    os.makedirs(torch_cache, exist_ok=True)

torch.hub.set_dir(torch_cache)

import locale
def getpreferredencoding(do_setlocale = True):
    return "UTF-8"
locale.getpreferredencoding = getpreferredencoding

dependencies = {}

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = width  
    window_height = height
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2  
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position-35}")
    
root = TkinterDnD.Tk()
root.withdraw()

splash_screen = tk.Toplevel(root)
splash_screen.overrideredirect(1)
splash_screen.attributes('-topmost', True)  # Keep the window on top
splash_screen.attributes("-transparentcolor", "black")
splash_geo_x = 490
splash_geo_y = 490
center_window(splash_screen, splash_geo_x, splash_geo_y)

icon = 'ZoeDepth2.ico'
splash_img = './/assets//ZoeDepth2.png'
if hasattr(sys, '_MEIPASS'):
    splash_img = './/splash//ZoeDepth2.png'
    splash_img = os.path.join(sys._MEIPASS, splash_img)
    icon = os.path.join(contents_dir, icon)

splash_img = ImageTk.PhotoImage(file=splash_img)
splash_label = tk.Label(splash_screen, image=splash_img, bg='black')
splash_label.pack()

def make_non_resizable(window):
    window.resizable(False, False)

def choose_file(event):
    global file_path
    file_path = filedialog.askopenfilenames(
        title="Select Image File",
        filetypes=(("Image files", "*" + " *".join(image_ext_upper)), ("All files", "*.*"))
    )
    files_selected(file_path)

image_ext = [
'.bmp','.dib','.eps','.gif','.icns','.ico','.im','.jpeg','.jpg','.jfif','.jpe',
'.jpf','.jp2','.j2c','.j2k','.jpc','.msp','.pcx', '.png','.ppm','.sgi','.spider',
'.tga','.tiff','.tif','.webp','.xbm','.xpm'
]

image_ext_upper = [ext.upper() for ext in image_ext]

def is_image_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() in image_ext

def files_selected(file_path):
    if file_path:
        for file in file_path:
            if not is_image_file(file):
                print(f'File "{file}" is not a supported image file.')
                return
        threading.Thread(target=Tiled_ZoeDepth_process, args=(file_path, ), daemon=True).start()
    else:
        print('No image File dropped.')


def main():
    global ZD_N_var, ZD_K_var, ZD_NK_var, ZD_N_Check, ZD_K_Check, ZD_NK_Check, Batch_mode_var, Batch_mode_Check
    global canvas, drop_label, settings_frame
    global drag_enter, on_drop, drag_leave
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def drag_enter(event):
        drop_label.config(bg="lightgray")
        label.config(bg="lightgray")

    def drag_leave(event):
        drop_label.config(bg="white")
        label.config (bg="white")
        
    def on_drop(event):
        global file_path
        drop_label.config(bg="white")
        label.config (bg="white")
        
        file_path = re.findall(r'\{.*?\}|\S+', event.data)
        file_path = [re.sub(r'[{}]', '', file) for file in file_path]

        files_selected(file_path)
        
    geo_width= 900
    center_window(root, geo_width, 950)
    root.iconbitmap(icon)
    make_non_resizable(root)
    root.title('Tiled ZoeDepth')

    canvas = tk.Canvas(root, bd=2, relief="ridge")
    canvas.pack(expand=True, fill="both")
    canvas.pack_propagate(0)

    # Create a Label for the drop area
    drop_label = tk.Label(canvas, text="Drag and drop image files Here\nor\nClick this area to select file\s", padx=20, pady=20, bg="white")
    drop_label.pack(expand=True, fill="both")

    # Bind the drop event to the on_drop function
    drop_label.bind("<Enter>", drag_enter)
    drop_label.bind("<Leave>", drag_leave)
    drop_label.bind('<Button-1>', choose_file)
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', on_drop)
    canvas.bind("<Enter>", drag_enter)
    canvas.bind("<Leave>", drag_leave)
    canvas.bind('<Button-1>', choose_file)
    canvas.dnd_bind('<<Drop>>', on_drop)
    canvas.drop_target_register(DND_FILES)

    label = tk.Label(canvas, bd=0, bg="white")

    settings_frame = tk.Frame(root)
    settings_frame.pack(side=tk.BOTTOM, pady=10)

    def update_checkbox_state(var, widget, var2, var3):
        if var.get() == 1:
            var2.set(0)
            var3.set(0)
            widget['state'] = 'normal'

    # You can choose to use ZoeD_N for indoor scenes, ZoeD_K for outdoor road scenes, and ZoeD_NK for generic scenes
    # - shariqfarooq123 (https://github.com/isl-org/ZoeDepth/issues/10#issuecomment-1475260262)

    ZD_N_var = tk.IntVar(value=1)
    ZD_N_Check = tk.Checkbutton(settings_frame, text= 'ZoeD_N', variable=ZD_N_var, command=lambda: update_checkbox_state(ZD_N_var, ZD_N_Check, ZD_NK_var, ZD_K_var))
    ZD_N_Check.pack(side=tk.LEFT)
    Hovertip(ZD_N_Check, "Model ZoeD_N: Best for Indoor scenes.")

    ZD_K_var = tk.IntVar()
    ZD_K_Check = tk.Checkbutton(settings_frame, text= 'ZoeD_K', variable=ZD_K_var, command=lambda: update_checkbox_state(ZD_K_var, ZD_N_Check, ZD_NK_var, ZD_N_var))
    ZD_K_Check.pack(side=tk.LEFT)
    Hovertip(ZD_K_Check, "Model ZoeD_K: Best for Outdoor scenes.")

    ZD_NK_var = tk.IntVar()
    ZD_NK_Check = tk.Checkbutton(settings_frame, text= 'ZoeD_NK', variable=ZD_NK_var, command=lambda: update_checkbox_state(ZD_NK_var, ZD_N_Check, ZD_N_var, ZD_K_var))
    ZD_NK_Check.pack(side=tk.LEFT)
    Hovertip(ZD_K_Check, "Model ZoeD_NK: Best for generic scenes.")
    
    Batch_mode_var = tk.IntVar()
    Batch_mode_Check = tk.Checkbutton(settings_frame, text='Batch Mode', variable=Batch_mode_var)
    Batch_mode_Check.pack(padx= 10, side=tk.RIGHT)
    Hovertip(Batch_mode_Check, "Enable this if you don't want a \'Save as\' prompt and just assumes to save right next to the image.")
    
    

    print("Current working directory:", os.getcwd())
    print("Executable path:", sys.executable)
    
    if not os.path.exists('.\\ZoeDepth'):
        #Repo.clone_from('https://github.com/isl-org/ZoeDepth.git', 'ZoeDepth')
        dlzip_unzip("https://github.com/isl-org/ZoeDepth/archive/refs/heads/main.zip")
        extracted_folder = "ZoeDepth-main"
        new_folder_name = "ZoeDepth"
        os.rename(extracted_folder, new_folder_name)
    
    splash_screen.destroy()
    root.deiconify()

def dlzip_unzip(repo_url, extract_path = '.'):
    response = requests.get(repo_url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    zip_file.extractall(extract_path)

def ongoing_process():
    global progress_label, progress_bar
    
    drop_label.pack_forget()
    ZD_N_Check.pack_forget()
    ZD_K_Check.pack_forget()
    ZD_NK_Check.pack_forget()
    Batch_mode_Check.pack_forget()
    
    canvas.unbind("<Enter>")
    canvas.unbind("<Leave>")
    canvas.unbind('<Button-1>')
    canvas.drop_target_unregister()
    
    settings_frame.update_idletasks()
    
    progress_label = tk.Label(settings_frame, text='Starting Depth Map process...')
    progress_label.pack(pady=10)
    
    progress_bar = ttk.Progressbar(settings_frame, mode='determinate', length=550)
    progress_bar.pack(fill=tk.X, padx=10, pady=0)
    
    settings_frame.update_idletasks()

def restore_main():
    progress_label.pack_forget()
    progress_bar.pack_forget()
    canvas.bind("<Enter>", drag_enter)
    canvas.bind("<Leave>", drag_leave)
    canvas.bind('<Button-1>', choose_file)
    canvas.dnd_bind('<<Drop>>', on_drop)
    canvas.drop_target_register(DND_FILES)
    drop_label.pack(expand=True, fill="both")
    ZD_N_Check.pack(side=tk.LEFT)
    ZD_K_Check.pack(side=tk.LEFT)
    ZD_NK_Check.pack(side=tk.LEFT)
    Batch_mode_Check.pack(padx= 10, side=tk.RIGHT)
    root.update_idletasks()
    settings_frame.update_idletasks()

def update_pbar(texthere, progress, filenum=0, filestotal=0, infLoad=False):
    r'''
    **update_pbar(texthere, progress, filenum=0, filestotal=0, infLoad=False)**

Updates a progress bar with the provided information.

This function updates the value and text of a progress bar based on the given parameters. The `texthere` parameter is used to set the text displayed on the progress bar. The `progress` parameter represents the progress value, which is used to update the progress bar's value. The `filenum` and `filestotal` parameters are optional and used to display the current file number and total number of files being processed. The `infLoad` parameter is a flag indicating whether the progress bar should be in indeterminate mode or not.

Args:
    texthere (str): The text to be displayed on the progress bar.
    progress (float): The progress value, ranging from 0 to 100.
    filenum (int, optional): The current file number. Defaults to 0.
    filestotal (int, optional): The total number of files being processed. Defaults to 0.
    infLoad (bool, optional): Flag indicating whether the progress bar should be in indeterminate mode. Defaults to False.

Returns:
    None

Raises:
    None
    '''
    progress_bar["value"] = progress
    progress = round(progress,2)
    if filenum == 0 and filestotal == 0 or filestotal == 1:
        progress_label.config(text=f'{texthere} {progress}%')
    else:
        progress_label.config(text=f'({filenum}/{filestotal}) - {texthere} {progress}%')
    if infLoad == True:
        progress_bar.config(mode='indeterminate')
        progress_label.config(text=f'{texthere}')
        progress_bar.start()
    else:
        progress_bar.stop()
        progress_bar.config(mode='determinate')
        progress_bar["value"] = progress

def suppress_outputs():
    sys.stderr = open(os.devnull, 'w')
    sys.__stderr__ = open(os.devnull, 'w')
    sys.stdout = open(os.devnull, 'w')
    sys.__stdout__ = open(os.devnull, 'w')

def format_time(seconds):
    '''Formats the given time duration in seconds into a string representation.

This function takes a time duration in seconds and formats it into a string representation in the format "HH:MM:SS". If the input is `None`, not a number, or infinite, it returns "00:00:00" or "Infinity" respectively.

Args:
    seconds (int or float): The time duration in seconds.

Returns:
    str: The formatted time duration in the format "HH:MM:SS".

Raises:
    None'''
    if seconds is None or not isinstance(seconds, (int, float)):
        return "00:00:00" 
    elif math.isinf(seconds):
        return "Infinity"
    
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def format_bytes(bytes, decimal_places=2):
    for unit in ['', 'KB', 'MB', 'GB']:
        if abs(bytes) < 1024.0:
            return f"{bytes:.{decimal_places}f} {unit}"
        bytes /= 1024.0

def download_file(url, path='.'):
    r'''Downloads a file from the specified URL and saves it to the given path.

This function downloads a file from the specified URL and saves it to the specified path. If no path is provided, the file is saved in the current directory. The function supports resuming partial downloads.

Args:
    url (str): The URL of the file to download.
    path (str, optional): The path where the file should be saved. Defaults to '.' (current directory).

Returns:
    None

Raises:
    None
    '''
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    filename = os.path.basename(url)
    file_path = os.path.join(path, filename)
    partial_file_path = f"{file_path}.partial"

    bytes_so_far = 0
    resume = False

    if os.path.exists(file_path):
        if os.path.exists(partial_file_path):
            os.remove(partial_file_path)
        total_size = os.path.getsize(file_path)
    elif os.path.exists(partial_file_path):
        bytes_so_far = os.path.getsize(partial_file_path)
        resume = True

    response = requests.get(url, stream=True, headers={"Range": f"bytes={bytes_so_far}-"})
    if response.status_code == 416:
        response = requests.get(url, stream=True)
    elif response.status_code not in [200, 206]:
        progress_label.config(text=f'Response Code: {response.status_code}\n Please check your internet connection. This application will now close.')
        progress_bar.pack_forget()
        time.sleep(5)
        on_closing()

    total_size = int(response.headers.get('content-length', 0))
    total_size_existing_file = bytes_so_far + total_size if resume else 0
    
    start_time = time.time()
    if bytes_so_far == total_size:
        os.rename(partial_file_path, file_path)
        progress_label.config(text=f"Download complete: {filename}")
    else:
        resumed_bytes = 0
        with open(partial_file_path, "ab") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    bytes_so_far += len(chunk)
                    resumed_bytes += len(chunk)

                    elapsed_time = time.time() - start_time
                    if resume:
                        download_speed = resumed_bytes / elapsed_time if elapsed_time > 0 else 0
                        remaining_bytes = total_size_existing_file - bytes_so_far
                        time_remaining = remaining_bytes / download_speed if download_speed > 0 else float('inf')
                        progress = int(bytes_so_far * 100 / total_size_existing_file)
                        progress_bar["value"] = progress
                        progress_label.config(text=f"Resuming {filename} | "
                                                    f"{progress}% \n"
                                                    f"{format_bytes(bytes_so_far)} / {format_bytes(total_size_existing_file)} " 
                                                    f"[{format_time(elapsed_time)} > {format_time(time_remaining)}, "
                                                    f"{format_bytes(download_speed)}/s]")
                    else:
                        download_speed = bytes_so_far / elapsed_time if elapsed_time > 0 else 0
                        remaining_bytes = total_size - bytes_so_far
                        time_remaining = remaining_bytes / download_speed if download_speed > 0 else float('inf')   
                        progress = int(bytes_so_far * 100 / total_size)
                        progress_bar["value"] = progress
                        progress_label.config(text=f"Downloading {filename} | "
                                                    f"{progress}% \n"
                                                    f"{format_bytes(bytes_so_far)} / {format_bytes(total_size)} " 
                                                    f"[{format_time(elapsed_time)} > {format_time(time_remaining)}, "
                                                    f"{format_bytes(download_speed)}/s]")
                    root.update_idletasks()
        f.close()
        if (
            total_size_existing_file == 0 and bytes_so_far == total_size
            or 
            total_size_existing_file != 0 and bytes_so_far == total_size_existing_file
        ):
            os.rename(partial_file_path, file_path)
            progress_label.config(text=f"Download complete: {filename}")

    root.update_idletasks()

def Tiled_ZoeDepth_process(file_path):
    from ZoeDepth.zoedepth.utils.misc import get_image_from_url, colorize
    # Unpack widgets
    ongoing_process()
    # Disable verbose on exe (verbose=verbose on torch does not work, so we're forcing to supress.)
    suppress_outputs()
    
    # Load model
    model_path = '.\\torch\\cache\\checkpoints'
    ZDN_pt = 'https://github.com/isl-org/ZoeDepth/releases/download/v1.0/ZoeD_M12_N.pt'
    ZDK_pt = 'https://github.com/isl-org/ZoeDepth/releases/download/v1.0/ZoeD_M12_K.pt'
    ZDNK_pt = 'https://github.com/isl-org/ZoeDepth/releases/download/v1.0/ZoeD_M12_NK.pt'
    if ZD_N_var.get():
        if os.path.exists(f'{model_path}\\ZoeD_M12_N.pt'):
            update_pbar('Loading ZoeD_N Model... |', 1)
        else:
            download_file(ZDN_pt,model_path)
            update_pbar('Loading ZoeD_N Model... |', 1)
        # Load ZoeD_N Model
        zoe = torch.hub.load(".\\ZoeDepth", "ZoeD_N", source="local", pretrained=True, trust_repo=True)
        model = 'Model: ZoeD_N'
    elif ZD_K_var.get():
        if os.path.exists(f'{model_path}\\ZoeD_M12_K.pt'):
            update_pbar('Loading ZoeD_K Model... |', 1)
        else:
            download_file(ZDK_pt,model_path)
            update_pbar('Loading ZoeD_K Model... |', 1)

        # Load ZoeD_K Model    
        zoe = torch.hub.load(".\\ZoeDepth", "ZoeD_K", source="local", pretrained=True, trust_repo=True)
        model = 'Model: ZoeD_K'
    elif ZD_NK_var.get():
        if os.path.exists(f'{model_path}\\ZoeD_M12_NK.pt'):
            update_pbar('Loading ZoeD_NK Model... |', 1)
        else:
            download_file(ZDNK_pt,model_path)
            update_pbar('Loading ZoeD_NK Model... |', 1)

        # Load ZoeD_NK Model
        zoe = torch.hub.load(".\\ZoeDepth", "ZoeD_NK", source="local", pretrained=True, trust_repo=True)
        model = 'Model: ZoeD_NK'

    # Load CUDA dependency
    if torch.cuda.is_available() == True:
        update_pbar('Cuda is available! Starting process... ', 10, infLoad=True) 
    else:
        update_pbar('Cuda not available! Using CPU instead. Starting process... ', 10, infLoad=True)

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    dependencies['zoe'] = zoe.to(DEVICE)

    # Load and process the image/s
    save_filter_images = True

    for filenum, file in enumerate(file_path, start=1):
        #create temp folder
        os.makedirs('.\\temp', exist_ok=True)

        image_file = os.path.basename(file)

        img = Image.open(file)
        
        if img.mode != 'RGB':
            img = img.convert("RGB")

        # Generate low resolution image
        low_res_depth = dependencies['zoe'].infer_pil(img)
        low_res_scaled_depth = 2**16 - (low_res_depth - np.min(low_res_depth)) * 2**16 / (np.max(low_res_depth) - np.min(low_res_depth))

        update_pbar(f'{image_file}: Generating low-res depth map\n', 20, filenum, len(file_path))

        low_res_depth_map_image = Image.fromarray((0.999 * low_res_scaled_depth).astype("uint16"))
        low_res_depth_map_image.save('temp\\zoe_depth_map_16bit_low.png')
        
        # Display depth map on window
        fig = plt.Figure()
        ax1 = fig.add_subplot(111)

        ax1.imshow(low_res_scaled_depth, cmap='magma')
        ax1.axis('off')
        ax1.set_title('Low Quality Depth Map')

        fig.text(0.5, 0.03, model, horizontalalignment='center', fontsize=12)

        magma_images = FigureCanvasTkAgg(fig, master=canvas)
        magma_images.draw()

        plt_canvas = magma_images.get_tk_widget()
        plt_canvas.pack(fill=tk.BOTH, expand=True)

        # Generate filters

        # store filters in lists
        pbar_value = 30
        update_pbar(f'{image_file}: Generating filters\n', pbar_value, filenum, len(file_path))

        im = np.asarray(img)
        tile_sizes = [[4, 4], [8, 8]]
        filters = []

        for tile_size in tile_sizes:
            num_x = tile_size[0]
            num_y = tile_size[1]

            M = im.shape[0]//num_x
            N = im.shape[1]//num_y

            filter_dict = {'right_filter': np.zeros((M, N))}
            filter_dict['left_filter'] = np.zeros((M, N))
            filter_dict['top_filter'] = np.zeros((M, N))
            filter_dict['bottom_filter'] = np.zeros((M, N))
            filter_dict['top_right_filter'] = np.zeros((M, N))
            filter_dict['top_left_filter'] = np.zeros((M, N))
            filter_dict['bottom_right_filter'] = np.zeros((M, N))
            filter_dict['bottom_left_filter'] = np.zeros((M, N))
            filter_dict['filter'] = np.zeros((M, N))

            for i in range(M):
                pbar_value += .008
                update_pbar(f'{image_file}: Generating filters\n', pbar_value, filenum, len(file_path))
                for j in range(N):

                    x_value = 0.998*np.cos((abs(M/2-i)/M)*np.pi)**2
                    y_value = 0.998*np.cos((abs(N/2-j)/N)*np.pi)**2

                    filter_dict['right_filter'][i,j] = x_value if j > N/2 else x_value * y_value
                    filter_dict['left_filter'][i,j] = x_value if j < N/2 else x_value * y_value
                    filter_dict['top_filter'][i,j] = y_value if i < M/2 else x_value * y_value
                    if i > M/2:
                        filter_dict['bottom_filter'][i,j] = y_value
                    else:
                        filter_dict['bottom_filter'][i,j] = x_value * y_value

                    if j > N/2 and i < M/2:
                        filter_dict['top_right_filter'][i,j] = 0.998
                    elif j > N/2:
                        filter_dict['top_right_filter'][i,j] = x_value
                    elif i < M/2:
                        filter_dict['top_right_filter'][i,j] = y_value
                    else:
                        filter_dict['top_right_filter'][i,j] = x_value * y_value

                    if j < N/2 and i < M/2:
                        filter_dict['top_left_filter'][i,j] = 0.998
                    elif j < N/2:
                        filter_dict['top_left_filter'][i,j] = x_value
                    elif i < M/2:
                        filter_dict['top_left_filter'][i,j] = y_value
                    else:
                        filter_dict['top_left_filter'][i,j] = x_value * y_value

                    if j > N/2 and i > M/2:
                        filter_dict['bottom_right_filter'][i,j] = 0.998
                    elif j > N/2:
                        filter_dict['bottom_right_filter'][i,j] = x_value
                    elif i > M/2:
                        filter_dict['bottom_right_filter'][i,j] = y_value
                    else:
                        filter_dict['bottom_right_filter'][i,j] = x_value * y_value

                    if j < N/2 and i > M/2:
                        filter_dict['bottom_left_filter'][i,j] = 0.998
                    elif j < N/2:
                        filter_dict['bottom_left_filter'][i,j] = x_value
                    elif i > M/2:
                        filter_dict['bottom_left_filter'][i,j] = y_value
                    else:
                        filter_dict['bottom_left_filter'][i,j] = x_value * y_value

                    filter_dict['filter'][i,j] = x_value * y_value

            filters.append(filter_dict)
            if save_filter_images:
                update_pbar(f'{image_file}: Saving filters\n', 60, filenum, len(file_path))

                for filter in list(filter_dict.keys()):
                    filter_image = Image.fromarray((filter_dict[filter]*2**16).astype("uint16"))
                    filter_image.save(f'temp\\mask_{filter}_{num_x}_{num_y}.png')

        # Compile tiles and create depth maps
        pbar_value = 60
        update_pbar(f'{image_file}: Compiling tiles & creating depth maps\n', pbar_value, filenum, len(file_path))

        compiled_tiles_list = []

        for i in range(len(filters)):

            num_x = tile_sizes[i][0]
            num_y = tile_sizes[i][1]

            M = im.shape[0]//num_x
            N = im.shape[1]//num_y

            compiled_tiles = np.zeros((im.shape[0], im.shape[1]))

            x_coords = list(range(0,im.shape[0],im.shape[0]//num_x))[:num_x]
            y_coords = list(range(0,im.shape[1],im.shape[1]//num_y))[:num_y]

            x_coords_between = list(range((im.shape[0]//num_x)//2, im.shape[0], im.shape[0]//num_x))[:num_x-1]
            y_coords_between = list(range((im.shape[1]//num_y)//2,im.shape[1],im.shape[1]//num_y))[:num_y-1]

            x_coords_all = x_coords + x_coords_between
            y_coords_all = y_coords + y_coords_between

            for x in x_coords_all:
                for y in y_coords_all:
                    pbar_value += .04
                    update_pbar(f'{image_file}: Compiling tiles & creating depth maps\n', pbar_value, filenum, len(file_path))
                    # depth = zoe.infer_pil(Image.fromarray(np.uint8(im[x:x+M,y:y+N])))
                    depth = dependencies['zoe'].infer_pil(Image.fromarray(np.uint8(im[x:x+M,y:y+N])))


                    scaled_depth = 2**16 - (depth - np.min(depth)) * 2**16 / (np.max(depth) - np.min(depth))

                    if y == min(y_coords_all) and x == min(x_coords_all):
                        selected_filter = filters[i]['top_left_filter']
                    elif y == min(y_coords_all) and x == max(x_coords_all):
                        selected_filter = filters[i]['bottom_left_filter']
                    elif y == max(y_coords_all) and x == min(x_coords_all):
                        selected_filter = filters[i]['top_right_filter']
                    elif y == max(y_coords_all) and x == max(x_coords_all):
                        selected_filter = filters[i]['bottom_right_filter']
                    elif y == min(y_coords_all):
                        selected_filter = filters[i]['left_filter']
                    elif y == max(y_coords_all):
                        selected_filter = filters[i]['right_filter']
                    elif x == min(x_coords_all):
                        selected_filter = filters[i]['top_filter']
                    elif x == max(x_coords_all):
                        selected_filter = filters[i]['bottom_filter']
                    else:
                        selected_filter = filters[i]['filter']

                    compiled_tiles[x:x+M, y:y+N] += selected_filter * (np.mean(low_res_scaled_depth[x:x+M, y:y+N]) + np.std(low_res_scaled_depth[x:x+M, y:y+N]) * ((scaled_depth - np.mean(scaled_depth)) /  np.std(scaled_depth)))

            compiled_tiles[compiled_tiles < 0] = 0
            compiled_tiles_list.append(compiled_tiles)

            tiled_depth_map = Image.fromarray((2**16 * 0.999 * compiled_tiles / np.max(compiled_tiles)).astype("uint16"))

            update_pbar(f'{image_file}: Saving tiles\n', 80, filenum, len(file_path))

            tiled_depth_map.save(f'temp\\tiled_depth_{i}.png')

        update_pbar(f'{image_file}: Combining depth maps\n', 90, filenum, len(file_path))
        # Combine depth maps
        grey_im = np.mean(im, axis=2)
        tiles_blur = gaussian_filter(grey_im, sigma=20)
        tiles_difference = tiles_blur - grey_im
        tiles_difference = tiles_difference / np.max(tiles_difference)
        tiles_difference = gaussian_filter(tiles_difference, sigma=40)
        tiles_difference *= 5
        tiles_difference = np.clip(tiles_difference, 0, 0.999)

        update_pbar(f'{image_file}: Generating High-quality depth map\n', 95, filenum, len(file_path))

        mask_image = Image.fromarray((tiles_difference*2**16).astype("uint16"))
        mask_image.save('temp\\mask_image.png')

        combined_result = (tiles_difference * compiled_tiles_list[1] + (1-tiles_difference) * ((compiled_tiles_list[0] + low_res_scaled_depth)/2))/(2)

        # Display results
        plt_canvas.destroy()
        fig.clear()

        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        ax1.imshow(low_res_scaled_depth, cmap='magma')
        ax1.axis('off')
        ax1.set_title('Low Quality Depth Map')

        ax2.imshow(combined_result, cmap='magma')
        ax2.axis('off')
        ax2.set_title('Hiqh Quality Depth Map')

        fig.text(0.5, 0.03, model, horizontalalignment='center', fontsize=12)

        magma_images = FigureCanvasTkAgg(fig, master=canvas)
        magma_images.draw()

        plt_canvas = magma_images.get_tk_widget()
        plt_canvas.pack(fill=tk.BOTH, expand=True)

        combined_image = Image.fromarray((2**16 * 0.999* combined_result / np.max(combined_result)).astype("uint16"))

        time.sleep(3)

        # Save image
        update_pbar(f'{image_file}: Saving low quality and high quality depth maps...\n', 99, filenum, len(file_path))
        if Batch_mode_var.get():
            combined_image.save(f"{os.path.splitext(file)[0]}_TiledZoeDepth.png")
            low_res_depth_map_image.save(f"{os.path.splitext(file)[0]}_ZoeDepth.png")
            update_pbar(f'{image_file}: Saved!\n', 100, filenum, len(file_path))
        else:   
            if output_file := filedialog.asksaveasfile(
                defaultextension=".png",
                initialfile=f"{os.path.splitext(os.path.basename(file))[0]}_TiledZoeDepth.png",
                filetypes=[("PNG files", "*.png")],
            ):
                combined_image.save(output_file.name)
                low_res_depth_map_image.save(output_file.name.replace("_TiledZoeDepth.png", "_ZoeDepth.png"))
                update_pbar(f'{image_file}: Saved!\n', 100, filenum, len(file_path))
                output_file.close()

        # print('Original low resolution result')
        # plt.imshow(low_res_scaled_depth, 'magma')
        # plt.axis("off")
        # plt.show()

        # print('\nNew high resolution result')
        # plt.imshow(combined_result, 'magma')
        # plt.axis("off")
        # plt.show()

        print("Processing ended")
        print("Removing temporary files...")
        if os.path.exists('temp'):
            shutil.rmtree('temp') 
            print("temp removed successfully.")
        else:
            print("temp does not exist.")

        plt_canvas.destroy()

    restore_main()

def on_closing():
    if os.path.exists('temp'):
        shutil.rmtree('temp')
        print("temp removed successfully.")
    else:
        print("temp does not exist.")
        
    print("Closing the application.")
    
    atexit.unregister(on_closing)  # Unregister the atexit callback
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
atexit.register(on_closing)

splash_screen.after(1000, main)
root.mainloop()