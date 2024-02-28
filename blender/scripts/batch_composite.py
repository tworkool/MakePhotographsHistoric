import bpy
import os
import time
import sys
import random

bpy.context.scene.use_nodes = True

## CONSTANTS
IMAGE_INPUT_DIRECTORY = (
    "D:\\dev\\python\\make-photographs-historical\\data\\3_preprocessed_images"
)
IMAGE_OUTPUT_DIRECTORY = (
    "D:\\dev\\python\\make-photographs-historical\\data\\4_output_images\\"
)
FILTER_NAME = "Camera: Hasselblad 500 C/M"
# apply dynamic filter effects (like damage) to every nth image!
DAMAGE_RANDOMIZER = None  # None = off
CLEANUP = True
NODE_OFFSET = 200
# value from 0 to 1
RANDOMNESS_WEIGHT = 1.0

## BPY CONSTANTS
tree = bpy.context.scene.node_tree
links = tree.links
scoped_images = []
scoped_image_nodes = []

# Set the render resolution
# bpy.context.scene.render.resolution_x = 1080
# bpy.context.scene.render.resolution_y = 1080


def evaluate_args():
    global FILTER_NAME
    global IMAGE_INPUT_DIRECTORY
    global IMAGE_OUTPUT_DIRECTORY
    global DAMAGE_RANDOMIZER
    global RANDOMNESS_WEIGHT

    # list of arguments passed after '--'
    # call like that 'python test.py -- <FILTER_NAME> <INPUT_PATH> <OUTPUT_PATH>
    argv = sys.argv[sys.argv.index("--") + 1 :]

    if len(argv) < 0:
        raise Exception(
            "ERROR: pass at least one argument(-- <FILTER_NAME> <OPTIONAL: INPUT_PATH> <OPTIONAL: OUTPUT_PATH>)"
        )

    FILTER_NAME = argv[0]

    if len(argv) > 1:
        IMAGE_INPUT_DIRECTORY = argv[1]

    if len(argv) > 2:
        IMAGE_OUTPUT_DIRECTORY = argv[2]

    if len(argv) > 3:
        DAMAGE_RANDOMIZER = int(argv[3])

    if len(argv) > 4:
        RANDOMNESS_WEIGHT = float(argv[4])

    return


def apply_filters():
    if len(image_files) == 0:
        print("INFO: found 0 images in input folder. Cancelling script.")
        return

    print(f"INFO: applying filters to {len(image_files)} images")

    # INSTANTIATE NODE PIPELINE
    file_output_node = tree.nodes.new("CompositorNodeOutputFile")
    file_output_node.base_path = IMAGE_OUTPUT_DIRECTORY
    file_output_node.format.file_format = "PNG"
    file_output_node.location = 1000, 200 * (len(image_files) / 2)
    # Clear all existing file slots (because in the beginning one already exists)
    file_output_node.file_slots.clear()
    # Create unique file slots for each image
    file_slots = [
        file_output_node.file_slots.new(f"{os.path.splitext(fl)[0]}_###")
        for fl in image_files
    ]
    scoped_image_nodes.append(file_output_node)

    active_filter_group = bpy.data.node_groups.get(FILTER_NAME)
    damage_filter_group = bpy.data.node_groups.get("CameraFilmDamageFilter")

    # Loop through each image file
    for i, (image_file, file_slot) in enumerate(zip(image_files, file_slots)):
        # Construct the full path to the image file
        image_path = os.path.join(IMAGE_INPUT_DIRECTORY, image_file)

        # Load the image
        img = bpy.data.images.load(image_path)

        # Create an image node and set the image for it
        image_node = tree.nodes.new("CompositorNodeImage")
        image_node.image = img
        image_node.hide = True
        image_node.location = 0, i * NODE_OFFSET

        active_filter_node = tree.nodes.new("CompositorNodeGroup")
        active_filter_node.node_tree = active_filter_group
        active_filter_node.location = 200, i * NODE_OFFSET

        links.new(image_node.outputs[0], active_filter_node.inputs[0])

        # general randomization
        # active_filter_node.inputs["Randomness Seed"].default_value = random.uniform(0.0, 1.0)
        # active_filter_node.inputs["Randomness Weight"].default_value = RANDOMNESS_WEIGHT
        for n in active_filter_node.node_tree.nodes:
            if "randomness map" in n.name.lower():
                randomness_seed = random.uniform(0.0, 1.0)
                n.inputs["Range Value"].default_value = randomness_seed
                print(
                    f"INFO: Randomness Seed for image {image_file} randomness node {n.label} with weight {RANDOMNESS_WEIGHT} and seed {randomness_seed}"
                )

        if DAMAGE_RANDOMIZER and DAMAGE_RANDOMIZER != 0 and i % DAMAGE_RANDOMIZER == 0:
            damage_filter_node = tree.nodes.new("CompositorNodeGroup")
            damage_filter_node.node_tree = damage_filter_group
            damage_filter_node.location = 600, i * NODE_OFFSET
            damage_filter_node.inputs["Amount"].default_value = 1.0
            damage_filter_node.inputs["Offset"].default_value = random.uniform(
                0.0, 25.0
            )  # times 1.0 to normalize as float!

            # Link nodes
            links.new(
                damage_filter_node.outputs[0],
                file_output_node.inputs[i],
            )  # link to every slot in the output node
            links.new(
                active_filter_node.outputs[0],
                damage_filter_node.inputs[0],
            )  # link to every slot in the output node
            scoped_image_nodes.append(damage_filter_node)
        else:
            # Link nodes
            links.new(
                active_filter_node.outputs[0],
                file_output_node.inputs[i],
            )  # link to every slot in the output node

        scoped_images.append(img)
        scoped_image_nodes.append(image_node)
        scoped_image_nodes.append(active_filter_node)


def unlink_image(img):
    if img.users == 0:
        # The image is not used by any other data block
        bpy.data.images.remove(img)
    else:
        print(
            f"WARN: could not remove the following image because it is still used somewhere: {img}"
        )
    return


def cleanup():
    ### CLEANUP ###
    if CLEANUP:
        # remove users of images first!
        for img_node in scoped_image_nodes:
            tree.nodes.remove(img_node)

        for img in scoped_images:
            unlink_image(img)

        time.sleep(2)


# evaluate script args first
evaluate_args()

print(f"INFO: executing script with the following params: ")
print(f"IMAGE_INPUT_DIRECTORY: {IMAGE_INPUT_DIRECTORY}")
print(f"IMAGE_OUTPUT_DIRECTORY: {IMAGE_OUTPUT_DIRECTORY}")
print(f"FILTER_NAME: {FILTER_NAME}")
print(f"DAMAGE_RANDOMIZER: {DAMAGE_RANDOMIZER}")

# get all images from folder
image_files = [
    f
    for f in os.listdir(IMAGE_INPUT_DIRECTORY)
    if f.lower().endswith((".png", ".jpg", ".jpeg"))
]
print(image_files)

# apply composition node workflow filters
apply_filters()

# render the frame
bpy.ops.render.render(write_still=True)

# cleanup
cleanup()
