import bpy
import os
import math
import json

current_dir = "/Users/prnth/Documents/GitHub/moviemaker/generation/"
print("Current Directory:", current_dir)

def match_transformations(obj, target_obj, vrm=False):
    print(obj)
    rotation_x = 180  # Rotate 45 degrees around X-axis
    # Convert degrees to radians
    rotation_x_rad = math.radians(rotation_x)
    obj.rotation_mode = 'XYZ'
    # Apply the rotations to the object
    obj.rotation_euler = (rotation_x_rad, 0, 0)
    # Match the location, rotation, and scale of the target object
    if not vrm:
        obj.location = (0, 6, 21)
        obj.scale = (10, 10, 10)   # target_obj.scale
    else:
        obj.location = (0, 0.08, 0.2)
        obj.scale = (0.1, 0.1, 0.1)
    
# Function to attach a helmet/hair to the head bone
def attach_to_head(obj_name, head_bone, vrm=False):
    obj = bpy.data.objects[obj_name]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # Apply rotation and scale transformations
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
    armature = bpy.data.objects['Armature']  # Replace with your armature's name
    obj.parent = armature
    obj.parent_type = 'BONE'
    obj.parent_bone = head_bone
    match_transformations(obj, armature, vrm)

# Replace the image texture of the 'Skin' material
def replace_skin_texture(modelId, json):
    new_image_path = os.path.join(current_dir, f'output/{modelId}.png')
    new_image = bpy.data.images.load(new_image_path)
    
    print(json['mouth'])
    
    mouth_image_path = os.path.join(current_dir, f"image-assets/mouth_{json['mouth'].replace(' ', '_')}.png")
    mouth_image = bpy.data.images.load(mouth_image_path)
    # Iterate over all materials
    for mat in bpy.data.materials:
        if 'Skin' in mat.name and mat.node_tree:
            for node in mat.node_tree.nodes:
                # Find the image texture node
                if node.type == 'TEX_IMAGE':
                    if node.image:
                        bpy.data.images.remove(node.image, do_unlink=True)
                        # Replace the image
                    node.image = new_image
                    node.image.alpha_mode = 'NONE'
                if node.type == 'BSDF_PRINCIPLED':
                    # Disconnect the alpha link if it exists
                    alpha_input = node.inputs['Alpha']
                    # Iterate over the links and remove them
                    for link in alpha_input.links:
                        mat.node_tree.links.remove(link)
        if 'Mouth' in mat.name and mat.node_tree:
            for node in mat.node_tree.nodes:
                # Find the image texture node
                if node.type == 'TEX_IMAGE':
                    print(mat.name)
                    if node.image:
                        bpy.data.images.remove(node.image, do_unlink=True)
                        # Replace the image
                    node.image = mouth_image

def replace_from_json(json, vrm=False):
    if json['hair_style'] is not None and json['hair_style'] != 'bald':
        print(f"adding {json['hair_style']}")
        glb_file_path = f"{current_dir}props/hair_{json['hair_style'].replace(' ', '_')}.glb"
        bpy.ops.import_scene.gltf(filepath=glb_file_path)
        attach_to_head("Hairmodel", 'mixamorig:Head', vrm)

    if json['glasses'] is not None and json['glasses'] != 'none':
        print(f"adding {json['glasses']}")
        glb_file_path = f"{current_dir}props/glasses_{json['glasses'].replace(' ', '_')}.glb"
        bpy.ops.import_scene.gltf(filepath=glb_file_path)
        attach_to_head("Sketchfab_model", 'mixamorig:Head', vrm)
        
    if json['hat'] is not None and json['hat'] != 'none':
        print(f"adding {json['hat']}")
        glb_file_path = f"{current_dir}props/hat_{json['hat'].replace(' ', '_')}.glb"
        bpy.ops.import_scene.gltf(filepath=glb_file_path)
        attach_to_head("Hatmodel", 'mixamorig:Head', vrm)
    
def write_model(modelId):
    for texture in bpy.data.textures:
        # Check if the texture has no users
        if texture.users == 0:
            # Remove the texture
            bpy.data.textures.remove(texture)
    # Export the combined model
    output_model_path = os.path.join(current_dir, f'output/{current_model}.glb')
    export_settings = {
        'use_selection': False,  # Set to True if you want to export only selected objects
        'export_format': 'GLB',  # Specify GLB format
        'export_apply': True,    # Apply modifiers and other settings
        'filepath': output_model_path
    }
    bpy.ops.export_scene.gltf(**export_settings)
    
def write_model_vrm(modelId):
    for texture in bpy.data.textures:
        # Check if the texture has no users
        if texture.users == 0:
            # Remove the texture
            bpy.data.textures.remove(texture)
    # Export the combined model
    output_model_path = os.path.join(current_dir, f'upload/{current_model}.vrm')
    bpy.ops.export_scene.vrm('EXEC_DEFAULT', filepath=output_model_path)
    
def clear_workspace():
    obs = [o for o in bpy.data.objects
        if not o.users_scene]
    bpy.data.batch_remove(obs)
    # Delete all objects, including armatures
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    # Clear unused data blocks (materials, textures, etc.)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.armatures:
        bpy.data.armatures.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.images:
        bpy.data.images.remove(block)
    for block in bpy.data.actions:
        bpy.data.actions.remove(block)
        
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture)

startrange = 1
intervalsize = 1

for current_model in range(startrange, startrange + intervalsize):
    file_path = os.path.join(current_dir, f'output/{current_model}.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
        
    # Load the base model
    clear_workspace()
    model_path = os.path.join(current_dir, 'model.glb')
    bpy.ops.import_scene.gltf(filepath=model_path)
    replace_from_json(data)
    replace_skin_texture(current_model, data)
    write_model(current_model)
    
    clear_workspace()
    model_path = os.path.join(current_dir, 'model.vrm')
    bpy.ops.import_scene.vrm(filepath=model_path)
    replace_from_json(data, True)
    replace_skin_texture(current_model, data)
    write_model_vrm(current_model)

