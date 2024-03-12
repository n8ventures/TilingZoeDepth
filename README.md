# Tiled Zoe Depth GUI
Basic GUI Implimentation based on [BillFSmith's](https://github.com/BillFSmith/) [TilingZoeDepth](https://github.com/BillFSmith/TilingZoeDepth).

## Prequisites
Python 3.10

## Recommended
### CUDA-capable system (Nvidia GPU)
- If you don't have an NVIDIA GPU, you'll be defaulted to use CPU for depth map generation (It's really slow).

## Setup
1. run `pip3 -r requirements.txt` first to download the packages.
2. On first start, run `python Tiled_ZoeDepth.py` to download the ZoeDepth repo.

## How to use
### 1. First, before we import our images. Select your preferred ZoeDepth model

 "You can choose to use ZoeD_N for indoor scenes, ZoeD_K for outdoor road scenes, and ZoeD_NK for generic scenes"

 source: https://github.com/isl-org/ZoeDepth/issues/10#issuecomment-1475260262

 ![Selecting Zoe_D Model](/assets/howtouse/2.gif)

### 2. Drag and drop your images on the drag-and-drop area.
 ![Main Menu](/assets/howtouse/1a.gif)

 alternatively, click on the drag-and-drop area to select your images.
 ![Alternate import](/assets/howtouse/1b.gif)

### 3. During depth map generation, you will be able to see the original version of Zoe Depth already displayed while the High Quality Depth Map (Tiled Zoe Depth) is processing. You can also see the progress bar moving to ensure user does not panic if it's stuck.
 ![Low Quality Depth Map Preview](/assets/howtouse/3.png)

<details>
<summary> How the progress bar works </summary>

The progress bar is more of an indicator on how close the process is done. I placed checkpoints around the code that will closely resemble the process progress. (It's more of a guestimation).

Here are the checkpoints:

 **1%**:     Loading Model
        
- If model is not downloaded, progress bar switches to indeterminate while it's downloading in the background. (At the moment, I have no idea on how to impliment a progressbar download without modifying the torch module.)

 **10%**:    Checking if CUDA is available or not

 **20%**++: Generating low-res depth map

 **30%**++: Generating filters

 **60%**:    Saving filters

 **60%**++: Compiling tiles & creating depth maps

 **80%**:    Saving tiles

 **90%**:    Combining depth maps

 **95%**:    Generating High-quality depth map

 **99%**:    Saving depthmaps...

 **100%**:   Images saved

</details>

### 4. After the high quality depth map has been generated, there will be 3 seconds of preview before you can choose to save the image/s or cancel it.

 ![Low Quality Depth Map Preview](/assets/howtouse/4.gif)

## Notes

- I only tested this on Windows. Not sure if it will work on Linux or MacOS

Images used:

 - [Kazuya Guy](https://knowyourmeme.com/memes/kazuya-guy/)

 - [Ichiban Low Fade art by Jaya](https://twitter.com/grunt727idn/status/1757017781042880702)

# Original README
# Tiling ZoeDepth outputs for higher resolution
v3 has a more reliable upload system for larger files. Can take multiple files at once:

https://colab.research.google.com/drive/1Wi-1Ji_fhcoGpK-drT4dVrl5AjfVUQ5M

v2 has a GUI and STL generation:

https://colab.research.google.com/drive/1wbbXpMC_UUwE3e7Tifq9fYNnd5Rn0zna

v1 is broken into sections:

https://colab.research.google.com/drive/1taTL_8GVx1G93ZXp_o-s4FLL-SY6N8TC

This is an adapted version of https://colab.research.google.com/github/isl-org/ZoeDepth/blob/main/notebooks/ZoeDepth_quickstart.ipynb

Corresponding paper : [ZoeDepth: Zero-shot Transfer by Combining Relative and Metric Depth](https://arxiv.org/abs/2302.12288v1)

Here, higher resolution depth maps are generated from the following process:

1)  Generate a depth map for the overall image    
2)  Split original image into overlapping tiles    
3)  Generate depth maps for the tiles    
4)  Reassemble into a single depth map by applying gradient masks and average weighting from first depth map    
5)  Repeat steps 2-4 at higher resolution
6)  Combine all three depth maps by: <br>
        a) Calculate edge filter from original RGB image<br>
        b) Blur edge filter and use as mask for high resolution depth map<br>
        c) Apply masked high resolution to average of low and medium resolution depth maps

The difference between the low resolution original and the new version can be seen below:    
![zoe_depth_map_16bit_low(4)](https://github.com/BillFSmith/TilingZoeDepth/assets/66475393/64bef7b9-566b-4fbc-8a83-f3d393d13873)
![im0 (copy)_depth](https://github.com/BillFSmith/TilingZoeDepth/assets/66475393/8cebe785-a62c-4193-aa0c-7f90b17435ec)

    
