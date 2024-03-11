# Based on Tiled_ZoeDepth,_v3.ipynb

import numpy as np
import cv2
import torch
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.ndimage import gaussian_filter
import os
from git import Repo
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import sys
import shutil
import threading
import time
import re
from idlelib.tooltip import Hovertip

if not os.path.exists('.\\torch\\cache'):
    os.makedirs('.\\torch\\cache', exist_ok=True)

torch.hub.set_dir('.\\torch\\cache')

if not os.path.exists('.\\ZoeDepth'):
    Repo.clone_from('https://github.com/isl-org/ZoeDepth.git', 'ZoeDepth')
    
from ZoeDepth.zoedepth.utils.misc import get_image_from_url, colorize

import locale
def getpreferredencoding(do_setlocale = True):
    return "UTF-8"
locale.getpreferredencoding = getpreferredencoding

dependencies = {}

root = TkinterDnD.Tk()

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = width  
    window_height = height
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2  
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position-35}")

def make_non_resizable(window):
    window.resizable(False, False)

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

def img_preview(image):
    img = Image.open(image)
    aspect_ratio = img.width / img.height
    
    if img.width > img.height:  # Landscape
        target_width = min(img.width, 450)
        target_height = int(target_width / aspect_ratio)
    else:  # Portrait or square
        target_height = min(img.height, 300)
        target_width = int(target_height * aspect_ratio)
    
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    return img

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

image_ext_upper = [ext.upper() for ext in image_ext]
icon = 'ZoeDepth2.ico'
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
Hovertip(ZD_N_Check, "Model ZD_N: Best for Indoor scenes.")

ZD_K_var = tk.IntVar()
ZD_K_Check = tk.Checkbutton(settings_frame, text= 'ZoeD_K', variable=ZD_K_var, command=lambda: update_checkbox_state(ZD_K_var, ZD_N_Check, ZD_NK_var, ZD_N_var))
ZD_K_Check.pack(side=tk.LEFT)
Hovertip(ZD_K_Check, "Model ZD_K: Best for Outdoor scenes.")

ZD_NK_var = tk.IntVar()
ZD_NK_Check = tk.Checkbutton(settings_frame, text= 'ZoeD_NK', variable=ZD_NK_var, command=lambda: update_checkbox_state(ZD_NK_var, ZD_N_Check, ZD_N_var, ZD_K_var))
ZD_NK_Check.pack(side=tk.LEFT)
Hovertip(ZD_K_Check, "Model ZD_NK: Best for generic scenes.")

print("Current working directory:", os.getcwd())
print("Executable path:", sys.executable)

def ongoing_process():
    global progress_label, progress_bar
    
    drop_label.pack_forget()
    ZD_N_Check.pack_forget()
    ZD_K_Check.pack_forget()
    ZD_NK_Check.pack_forget()
    
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
    root.update_idletasks()
    settings_frame.update_idletasks()
    

def update_pbar(texthere, progress, filenum=0, filestotal=0, infLoad=False):
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

def Tiled_ZoeDepth_process(file_path):
    # Unpack widgets
    ongoing_process()
    # Load model
    if ZD_N_var.get():
        if os.path.exists('.\\torch\\cache\\checkpoints\\ZoeD_M12_N.pt'):
            update_pbar('Loading ZoeD_N Model... |', 1)
        else:
            update_pbar('Downloading ZoeD_N Model... ', 0, infLoad=True)
            
        zoe = torch.hub.load(".\\ZoeDepth", "ZoeD_N", source="local", pretrained=True, trust_repo=True)
    elif ZD_K_var.get():
        if os.path.exists('.\\torch\\cache\\checkpoints\\ZoeD_M12_K.pt'):
            update_pbar('Loading ZoeD_K Model... |', 1)
        else:
            update_pbar('Downloading ZoeD_K Model... ', 0, infLoad=True)
            
        zoe = torch.hub.load(".\\ZoeDepth", "ZoeD_K", source="local", pretrained=True, trust_repo=True)
    elif ZD_NK_var.get():
        if os.path.exists('.\\torch\\cache\\checkpoints\\ZoeD_M12_NK.pt'):
            update_pbar('Loading ZoeD_NK Model... |', 1)
        else:
            update_pbar('Downloading ZoeD_NK Model... ', 0, infLoad=True)
            
        zoe = torch.hub.load(".\\ZoeDepth", "ZoeD_NK", source="local", pretrained=True, trust_repo=True)

    # Load CUDA dependency
    cuda_True = update_pbar('Cuda is available! Starting process... ', 10, infLoad=True) 
    cude_False = update_pbar('Cuda not available! Using CPU instead. Starting process... ', 10, infLoad=True)
    
    DEVICE = "cuda" if torch.cuda.is_available() and cuda_True else "cpu" and cude_False
    dependencies['zoe'] = zoe.to(DEVICE)

    # Load and process the image/s
    save_filter_images = True
    
    for filenum, file in enumerate(file_path, start=1):
        #create temp folder
        os.makedirs('.\\temp', exist_ok=True)
        
        image_file = os.path.basename(file)
        
        img = Image.open(file)

        # Generate low resolution image
        low_res_depth = dependencies['zoe'].infer_pil(img)
        low_res_scaled_depth = 2**16 - (low_res_depth - np.min(low_res_depth)) * 2**16 / (np.max(low_res_depth) - np.min(low_res_depth))
        
        update_pbar(f'{image_file}: Generating low-res depth map\n', 20, filenum, len(file_path))
        
        low_res_depth_map_image = Image.fromarray((0.999 * low_res_scaled_depth).astype("uint16"))
        low_res_depth_map_image.save('temp\\zoe_depth_map_16bit_low.png')
        
        fig = plt.Figure()
        ax1 = fig.add_subplot(111)

        ax1.imshow(low_res_scaled_depth, cmap='magma')
        ax1.axis('off')
        ax1.set_title('Low Quality Depth Map')
        

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
        update_pbar(f'{image_file}: compiling tiles & creating depth maps\n', pbar_value, filenum, len(file_path))
        
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
                    update_pbar(f'{image_file}: compiling tiles & creating depth maps\n', pbar_value, filenum, len(file_path))
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

            update_pbar(f'{image_file}: saving tiles\n', 80, filenum, len(file_path))
            
            tiled_depth_map = Image.fromarray((2**16 * 0.999 * compiled_tiles / np.max(compiled_tiles)).astype("uint16"))
            tiled_depth_map.save(f'temp\\tiled_depth_{i}.png')
        
        update_pbar(f'{image_file}: combining depth maps\n', 90, filenum, len(file_path))
        # Combine depth maps
        grey_im = np.mean(im, axis=2)
        tiles_blur = gaussian_filter(grey_im, sigma=20)
        tiles_difference = tiles_blur - grey_im
        tiles_difference = tiles_difference / np.max(tiles_difference)
        tiles_difference = gaussian_filter(tiles_difference, sigma=40)
        tiles_difference *= 5
        tiles_difference = np.clip(tiles_difference, 0, 0.999)

        update_pbar(f'{image_file}: generating High-quality depth map\n', 95, filenum, len(file_path))
        
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
        magma_images = FigureCanvasTkAgg(fig, master=canvas)
        magma_images.draw()
        
        plt_canvas = magma_images.get_tk_widget()
        plt_canvas.pack(fill=tk.BOTH, expand=True)

        combined_image = Image.fromarray((2**16 * 0.999* combined_result / np.max(combined_result)).astype("uint16"))
        
        time.sleep(3)
        
        # Save image
        if output_file := filedialog.asksaveasfile(
            defaultextension=".gif",
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
        progress_bar.stop()
        print("Removing temporary files...")
        if os.path.exists('temp'):
            shutil.rmtree('temp') 
            print("temp removed successfully.")
        else:
            print("temp does not exist.")

        plt_canvas.destroy()
    
    restore_main()

root.mainloop()