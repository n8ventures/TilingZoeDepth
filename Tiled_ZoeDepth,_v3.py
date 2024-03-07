import numpy as np
import cv2
import torch
from ZoeDepth.zoedepth.utils.misc import get_image_from_url, colorize
from PIL import Image
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import tkinter as tk
from tkinter import filedialog
import os
from git import Repo
 
if not os.path.exists('.\\ZoeDepth'):
    Repo.clone_from('https://github.com/isl-org/ZoeDepth.git', 'ZoeDepth')

import locale
def getpreferredencoding(do_setlocale = True):
    return "UTF-8"
locale.getpreferredencoding = getpreferredencoding

dependencies = {}


# Load ZoeD_N model
zoe = torch.hub.load(".\\ZoeDepth", "ZoeD_N", source="local", pretrained=True)
dependencies['zoe'] = zoe.to('cuda')



# Load and process the image
filename = 'test\\test.jpg'
img = Image.open(filename)

# Generate low resolution image
low_res_depth = dependencies['zoe'].infer_pil(img)
low_res_scaled_depth = 2**16 - (low_res_depth - np.min(low_res_depth)) * 2**16 / (np.max(low_res_depth) - np.min(low_res_depth))

low_res_depth_map_image = Image.fromarray((0.999 * low_res_scaled_depth).astype("uint16"))
low_res_depth_map_image.save('zoe_depth_map_16bit_low.png')

# Generate filters

# store filters in lists
im = np.asarray(img)
tile_sizes = [[4, 4], [8, 8]]
filters = []
save_filter_images = True
for tile_size in tile_sizes:

    num_x = tile_size[0]
    num_y = tile_size[1]

    M = im.shape[0]//num_x
    N = im.shape[1]//num_y

    filter_dict = {}
    filter_dict['right_filter'] = np.zeros((M, N))
    filter_dict['left_filter'] = np.zeros((M, N))
    filter_dict['top_filter'] = np.zeros((M, N))
    filter_dict['bottom_filter'] = np.zeros((M, N))
    filter_dict['top_right_filter'] = np.zeros((M, N))
    filter_dict['top_left_filter'] = np.zeros((M, N))
    filter_dict['bottom_right_filter'] = np.zeros((M, N))
    filter_dict['bottom_left_filter'] = np.zeros((M, N))
    filter_dict['filter'] = np.zeros((M, N))

    for i in range(M):
        for j in range(N):
            x_value = 0.998*np.cos((abs(M/2-i)/M)*np.pi)**2
            y_value = 0.998*np.cos((abs(N/2-j)/N)*np.pi)**2

            if j > N/2:
                filter_dict['right_filter'][i,j] = x_value
            else:
                filter_dict['right_filter'][i,j] = x_value * y_value

            if j < N/2:
                filter_dict['left_filter'][i,j] = x_value
            else:
                filter_dict['left_filter'][i,j] = x_value * y_value

            if i < M/2:
                filter_dict['top_filter'][i,j] = y_value
            else:
                filter_dict['top_filter'][i,j] = x_value * y_value

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
        for filter in list(filter_dict.keys()):
            filter_image = Image.fromarray((filter_dict[filter]*2**16).astype("uint16"))
            filter_image.save(f'mask_{filter}_{num_x}_{num_y}.png')

# Compile tiles and create depth maps
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
    tiled_depth_map.save(f'tiled_depth_{i}.png')

# Combine depth maps
from scipy.ndimage import gaussian_filter
grey_im = np.mean(im, axis=2)
tiles_blur = gaussian_filter(grey_im, sigma=20)
tiles_difference = tiles_blur - grey_im
tiles_difference = tiles_difference / np.max(tiles_difference)
tiles_difference = gaussian_filter(tiles_difference, sigma=40)
tiles_difference *= 5
tiles_difference = np.clip(tiles_difference, 0, 0.999)

mask_image = Image.fromarray((tiles_difference*2**16).astype("uint16"))
mask_image.save('mask_image.png')

combined_result = (tiles_difference * compiled_tiles_list[1] + (1-tiles_difference) * ((compiled_tiles_list[0] + low_res_scaled_depth)/2))/(2)

combined_image = Image.fromarray((2**16 * 0.999* combined_result / np.max(combined_result)).astype("uint16"))
# combined_image.save('combined_image.png')

# output_file = filedialog.asksaveasfile(
#     defaultextension=".gif",
# initialfile=os.path.splitext(os.path.basename(filename))[0] + ".png",
# filetypes=[("PNG files", "*.png")]
# )
# if output_file:
#     output_file.close()
    
combined_image.save(filename.split('.')[0] + '_depth.png')

# display output images

print('Original low resolution result')
plt.imshow(low_res_scaled_depth, 'magma')
plt.axis("off")
plt.show()

print('\nNew high resolution result')
plt.imshow(combined_result, 'magma')
plt.axis("off")
plt.show()

print("Processing ended")
print("Removing temporary files...")