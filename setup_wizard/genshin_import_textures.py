# Author: michael-gh1
# Originally contributed by Zekium and Modder4869 from Discord

import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import os

from setup_wizard.import_order import CHARACTER_MODEL_FOLDER_FILE_PATH, NextStepInvoker, cache_using_cache_key, get_cache
from setup_wizard.import_order import get_actual_material_name_for_dress
from setup_wizard.models import CustomOperatorProperties


class GI_OT_GenshinImportTextures(Operator, ImportHelper, CustomOperatorProperties):
    """Select the folder with the model's textures to import"""
    bl_idname = "genshin.import_textures"  # important since its how we chain file dialogs
    bl_label = "Genshin: Import Textures - Select Character Model Folder"

    # ImportHelper mixin class uses this
    filename_ext = "*.*"
    
    import_path: StringProperty(
        name = "Path",
        description = "Path to the folder containing the files to import",
        default = "",
        subtype = 'DIR_PATH'
        )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        cache_enabled = context.window_manager.cache_enabled
        directory = self.file_directory \
            or get_cache(cache_enabled).get(CHARACTER_MODEL_FOLDER_FILE_PATH) \
            or os.path.dirname(self.filepath)

        if not directory:
            bpy.ops.genshin.import_textures(
                'INVOKE_DEFAULT',
                next_step_idx=self.next_step_idx, 
                file_directory=self.file_directory,
                invoker_type=self.invoker_type,
                high_level_step_name=self.high_level_step_name
            )
            return {'FINISHED'}
        
        for name, folder, files in os.walk(directory):
            for file in files:
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                hair_material = bpy.data.materials.get('miHoYo - Genshin Hair')
                face_material = bpy.data.materials.get('miHoYo - Genshin Face')
                body_material = bpy.data.materials.get('miHoYo - Genshin Body')
                
                # Implement the texture in the correct node
                self.report({'INFO'}, f'Importing texture {file}')
                if "Hair_Diffuse" in file and "Eff" not in file:
                    hair_material.node_tree.nodes['Hair_Diffuse_UV0'].image = img
                    hair_material.node_tree.nodes['Hair_Diffuse_UV1'].image = img
                    self.setup_dress_textures('Hair_Diffuse', img)
                elif "Hair_Lightmap" in file:
                    img.colorspace_settings.name='Non-Color'
                    hair_material.node_tree.nodes['Hair_Lightmap_UV0'].image = img
                    hair_material.node_tree.nodes['Hair_Lightmap_UV1'].image = img
                    self.setup_dress_textures('Hair_Lightmap', img)
                elif "Hair_Normalmap" in file:
                    img.colorspace_settings.name='Non-Color'
                    hair_material.node_tree.nodes['Hair_Normalmap_UV0'].image = img
                    hair_material.node_tree.nodes['Hair_Normalmap_UV1'].image = img
                    self.setup_dress_textures('Hair_Normalmap', img)
                    self.plug_normal_map('miHoYo - Genshin Hair', 'MUTE IF ONLY 1 UV MAP EXISTS')
                elif "Hair_Shadow_Ramp" in file:
                    bpy.data.node_groups['Hair Shadow Ramp'].nodes['Hair_Shadow_Ramp'].image = img
                elif "Body_Diffuse" in file:
                    body_material.node_tree.nodes['Body_Diffuse_UV0'].image = img
                    body_material.node_tree.nodes['Body_Diffuse_UV1'].image = img
                    self.setup_dress_textures('Body_Diffuse', img)
                elif "Body_Lightmap" in file:
                    img.colorspace_settings.name='Non-Color'
                    body_material.node_tree.nodes['Body_Lightmap_UV0'].image = img
                    body_material.node_tree.nodes['Body_Lightmap_UV1'].image = img
                    self.setup_dress_textures('Body_Lightmap', img)
                elif "Body_Normalmap" in file:
                    img.colorspace_settings.name='Non-Color'
                    body_material.node_tree.nodes['Body_Normalmap_UV0'].image = img
                    body_material.node_tree.nodes['Body_Normalmap_UV1'].image = img
                    self.setup_dress_textures('Body_Normalmap', img)
                    self.plug_normal_map('miHoYo - Genshin Body', 'MUTE IF ONLY 1 UV MAP EXISTS')
                    self.plug_normal_map('miHoYo - Genshin Dress', 'MUTE IF ONLY 1 UV MAP EXISTS')
                elif "Body_Shadow_Ramp" in file:
                    bpy.data.node_groups['Body Shadow Ramp'].nodes['Body_Shadow_Ramp'].image = img
                elif "Body_Specular_Ramp" in file or "Tex_Specular_Ramp" in file :
                    img.colorspace_settings.name='Non-Color'
                    bpy.data.node_groups['Body Specular Ramp'].nodes['Body_Specular_Ramp'].image = img
                elif "Face_Diffuse" in file:
                    face_material.node_tree.nodes['Face_Diffuse'].image = img
                elif "Face_Shadow" in file:
                    img.colorspace_settings.name='Non-Color'
                    face_material.node_tree.nodes['Face_Shadow'].image = img
                elif "FaceLightmap" in file:
                    img.colorspace_settings.name='Non-Color'
                    bpy.data.node_groups['Face Lightmap'].nodes['Face_Lightmap'].image = img
                elif "MetalMap" in file:
                    bpy.data.node_groups['Metallic Matcap'].nodes['MetalMap'].image = img
                else:
                    pass
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

        self.report({'INFO'}, 'Imported textures')
        if cache_enabled and directory:
            cache_using_cache_key(get_cache(cache_enabled), CHARACTER_MODEL_FOLDER_FILE_PATH, directory)

        NextStepInvoker().invoke(
            self.next_step_idx,
            self.invoker_type,
            file_path_to_cache=directory,
            high_level_step_name=self.high_level_step_name
        )
        super().clear_custom_properties()
        return {'FINISHED'}

    '''
    Deprecated: No longer needed after shader rewrite because normal map is plugged by default
    Still maintains backward compatibility by only trying this if `label_name` is found in the node tree.
    '''
    def plug_normal_map(self, shader_material_name, label_name):
        shader_group_material_name = 'Group.001'
        shader_material = bpy.data.materials.get(shader_material_name)

        if shader_material:
            normal_map_node_color_outputs = [node.outputs.get('Color') for node in shader_material.node_tree.nodes \
                if node.label == label_name and not node.outputs.get('Color').is_linked]
            
            if normal_map_node_color_outputs:
                normal_map_node_color_output = normal_map_node_color_outputs[0]
                normal_map_input = shader_material.node_tree.nodes.get(shader_group_material_name).inputs.get('Normal Map')

                bpy.data.materials.get(shader_material_name).node_tree.links.new(
                    normal_map_node_color_output,
                    normal_map_input
                )
    
    def setup_dress_textures(self, texture_name, texture_img):
        shader_dress_materials = [material for material in bpy.data.materials if 'Genshin Dress' in material.name]
        shader_cloak_materials = [material for material in bpy.data.materials
                                  if 'Genshin Arm' in material.name or 'Genshin Cloak' in material.name]

        # TODO: Refactor this for sure!
        # Specific case for Xiao (the only character with an Arm material)
        # Specific case for Dainsleif (the only character with a Cloak material)
        # Technically Paimon has one, but we ignore it
        if shader_cloak_materials:
            original_cloak_material = [material for material in bpy.data.materials if material.name.endswith(
                shader_cloak_materials[0].name.split(' ')[-1]
            )][0]  # the material that ends with 'Dress', 'Dress1', 'Dress2'
            actual_cloak_material = get_actual_material_name_for_dress(original_cloak_material.name)
            if actual_cloak_material in texture_name:
                material_shader_nodes = bpy.data.materials.get(shader_cloak_materials[0].name).node_tree.nodes
                material_shader_nodes.get(f'{texture_name}_UV0').image = texture_img
                material_shader_nodes.get(f'{texture_name}_UV1').image = texture_img

        for shader_dress_material in shader_dress_materials:
            original_dress_material = [material for material in bpy.data.materials if material.name.endswith(
                shader_dress_material.name.split(' ')[-1]
            )][0]  # the material that ends with 'Dress', 'Dress1', 'Dress2'

            actual_material = get_actual_material_name_for_dress(original_dress_material.name)
            if actual_material in texture_name:
                self.report({'INFO'}, f'Importing texture "{texture_name}" onto material "{shader_dress_material.name}"')
                material_shader_nodes = bpy.data.materials.get(shader_dress_material.name).node_tree.nodes
                material_shader_nodes.get(f'{texture_name}_UV0').image = texture_img
                material_shader_nodes.get(f'{texture_name}_UV1').image = texture_img
                return


register, unregister = bpy.utils.register_classes_factory(GI_OT_GenshinImportTextures)
