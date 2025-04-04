
import bpy
import sys
import os

# Helper: parse command-line args after "--"
argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]
else:
    argv = []

# Default paths
input_path = "Teddy_Face_0330031823_texture.glb"
output_path = "rigged_teddy.glb"

# Override if args provided
if len(argv) >= 1:
    input_path = argv[0]
if len(argv) >= 2:
    output_path = argv[1]

print(f"Loading model: {input_path}")
print(f"Will export rigged model to: {output_path}")

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import the .glb model
bpy.ops.import_scene.gltf(filepath=input_path)

# Select imported object
obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj

# Create armature for facial rig
bpy.ops.object.armature_add(enter_editmode=True)
armature = bpy.context.object
armature.name = 'FaceRig'

# Edit bones
bpy.ops.object.mode_set(mode='EDIT')
edit_bones = armature.data.edit_bones

# Define basic facial bones
bones_info = {
    'Head': ((0, 0, 1.6), (0, 0, 1.8)),
    'Jaw': ((0, 0, 1.5), (0, 0, 1.6)),
    'LeftEye': ((0.05, 0.05, 1.75), (0.05, 0.05, 1.8)),
    'RightEye': ((-0.05, 0.05, 1.75), (-0.05, 0.05, 1.8)),
    'Mouth': ((0, 0.05, 1.5), (0, 0.05, 1.55)),
}

for name, (head, tail) in bones_info.items():
    bone = edit_bones.new(name)
    bone.head = head
    bone.tail = tail

# Exit edit mode
bpy.ops.object.mode_set(mode='OBJECT')

# Parent mesh to armature with automatic weights
obj.select_set(True)
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# Export the rigged model
bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
print("Export complete.")
