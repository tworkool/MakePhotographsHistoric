# GUIDE

This is a guide on Make Photographs Historical. This is a python based partly automated environment which aims to convert digital photographs into historical photos by simulating filters and aspect ratio (and whatever else may be important) of cameras which were used back then (please read disclaimer). The core of this task is powered by the blender python API and a scene, which includes predefined filters. Here is a step by step explanation:

1. (optional) converts images from HEIC format to PNG (I use an IPhone and thought it would be good to have a converter implemented)
2. crop images according to the aspect ratio of the film used for the selected historic camera model
3. apply filter according to the selected historic camera model with blender

The filters are applied automatically to all images in a folder.

## SETUP

Setup Conda

`conda env create -f environment.yml`

`conda activate make-images-historical`

Install Blender OR DON'T (read later more on this)
this is specific to your OS: https://docs.blender.org/manual/en/latest/getting_started/installing/linux.html

## RUN

Start Jupyter Lab

`jupyter lab`

Go to `main.ipynb` and go through the cells step by step

In the last cell you have to run a python script from within Blender.
Blender allows arguments to be passed so you can just run the last cell OR if you don't have blender installed in your env (I have it like this due to WSL), then just run:
```
blender "<YOUR_BASE>/make-photographs-historical/blender/main.blend" -b --python "<YOUR_BASE>/make-photographs-historical/blender/scripts/batch_composite.py" -- "Camera: Agfar Isolette (with damage)" "<YOUR_BASE>/make-photographs-historical/data/output_images" "<YOUR_BASE>/make-photographs-historical/data/output_images_filtered"
```

Please replace the `<YOUR_BASE>` in the paths with the path leading up to where you have this repository!

The parameters are:

```
blender <BLENDER_SCENE> -b --python <PYTHON_SCRIPT> -- <FILTER_NAME> <INPUT_FILES_FOLDER> <OUTPUT_FILES_FOLDER>
```

## DISCLAIMER

The filters provided in the scene are trying to simulate cameras. They might and probably do look different than what the actual photography with that camera looks like. I was just looking for reference images with specific models so that I can better understand what the final composition should look like!
