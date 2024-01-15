import bpy
import os
import time
import sys

bpy.context.scene.use_nodes = True

IMAGE_INPUT_DIRECTORY = "D:\dev\python\make-photographs-historical\data\output_images"
IMAGE_OUTPUT_DIRECTORY = (
    "D:\\dev\\python\\make-photographs-historical\\data\\output_images2\\"
)
# IMAGE_OUTPUT_DIRECTORY = "D:/dev/python/make-photographs-historical/data/"
FILTER_NAME = "Camera: Agfar Isolette"
CLEANUP = True
tree = bpy.context.scene.node_tree
links = tree.links


def evaluate_args():
    global FILTER_NAME
    global IMAGE_INPUT_DIRECTORY
    global IMAGE_OUTPUT_DIRECTORY

    # list of arguments passed after '--'
    # call like that 'python test.py -- <FILTER_NAME> <INPUT_PATH> <OUTPUT_PATH>
    argv = sys.argv[sys.argv.index("--") + 1 :]

    if len(argv) < 0:
        raise Exception(
            "ERROR: pass at least one argument(-- <FILTER_NAME> <OPTIONAL: INPUT_PATH> <OPTIONAL: OUTPUT_PATH>)"
        )

    FILTER_NAME = argv[0]

    if len(argv) >= 2:
        IMAGE_INPUT_DIRECTORY = argv[1]

    if len(argv) >= 3:
        IMAGE_OUTPUT_DIRECTORY = argv[2]

    return


evaluate_args()


def unlink_image(img):
    if img.users == 0:
        # The image is not used by any other data block
        bpy.data.images.remove(img)
    else:
        print(
            f"WARN: could not remove the following image because it is still used somewhere: {img}"
        )
    return


# Set the render resolution
# bpy.context.scene.render.resolution_x = 1080
# bpy.context.scene.render.resolution_y = 1080

# INSTANTIATE NODE PIPELINE
file_output_node = tree.nodes.new("CompositorNodeOutputFile")
file_output_node.base_path = IMAGE_OUTPUT_DIRECTORY
file_output_node.format.file_format = "PNG"

active_filter_group = bpy.data.node_groups.get(FILTER_NAME)


# CREATE AND CONNECT IMAGE NODES
image_files = [
    f
    for f in os.listdir(IMAGE_INPUT_DIRECTORY)
    if f.lower().endswith((".png", ".jpg", ".jpeg"))
]

# Create unique file slots for each image
file_slots = [
    file_output_node.file_slots.new("Image") for _ in image_files
]  # should be -1 because 1 slot already exists, but whatever

scoped_images = []
scoped_image_nodes = []
NODE_OFFSET = 200

file_output_node.location = 600, 200 * (len(image_files) / 2)

# Loop through each image file
for i, (image_file, file_slot) in enumerate(zip(image_files, file_slots)):
    # Construct the full path to the image file
    image_path = os.path.join(IMAGE_INPUT_DIRECTORY, image_file)

    try:
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

        # Link nodes
        image_link = links.new(image_node.outputs[0], active_filter_node.inputs[0])
        links.new(
            active_filter_node.outputs[0],
            file_output_node.inputs[len(file_slots) - 1 - i],
        )  # link to every slot in the output node

        scoped_images.append(img)
        scoped_image_nodes.append(image_node)
        scoped_image_nodes.append(active_filter_node)

    except Exception as e:
        print(f"ERROR: Failed to load {image_path}: {e}")


# Render the frame
bpy.ops.render.render(write_still=True)


### CLEANUP ###
if CLEANUP:
    # remove users of images first!
    for img_node in scoped_image_nodes:
        tree.nodes.remove(img_node)

    for img in scoped_images:
        unlink_image(img)

    time.sleep(2)
    tree.nodes.remove(file_output_node)
