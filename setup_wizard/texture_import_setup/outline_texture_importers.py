
import bpy
import os

from abc import ABC, abstractmethod
from bpy.types import Context, Operator

from setup_wizard.domain.game_types import GameType
from setup_wizard.domain.shader_identifier_service import GenshinImpactShaders, ShaderIdentifierService, \
    ShaderIdentifierServiceFactory
from setup_wizard.domain.shader_material_names import JaredNytsPunishingGrayRavenShaderMaterialNames, V3_BonnyFestivityGenshinImpactMaterialNames, V2_FestivityGenshinImpactMaterialNames, \
    ShaderMaterialNames, Nya222HonkaiStarRailShaderMaterialNames

from setup_wizard.import_order import CHARACTER_MODEL_FOLDER_FILE_PATH, cache_using_cache_key, get_actual_material_name_for_dress, get_cache
from setup_wizard.texture_import_setup.texture_importer_types import TextureImporterFactory, TextureImporterType
from setup_wizard.utils.genshin_body_part_deducer import get_npc_mesh_body_part_name


class OutlineTextureImporter(ABC):
    def __init__(self, blender_operator: Operator, context: Context, material_names: ShaderMaterialNames):
        self.blender_operator: Operator = blender_operator
        self.context: Context = context
        self.material_names = material_names

    @abstractmethod
    def import_textures(self):
        raise NotImplementedError()

    def assign_lightmap_texture(self, character_model_folder_file_path, lightmap_files, body_part_material_name, actual_material_part_name):
        v1_lightmap_node_name = 'Image Texture'
        v2_lightmap_node_name = 'Outline_Lightmap'
        outline_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{body_part_material_name} Outlines')

        # Note: Unable to determine between character/equipment textures for Monsters w/ equipment in same folder
        lightmap_filenames = []
        if body_part_material_name == 'EffectHair':
            lightmap_filenames = [file for file in lightmap_files if 'EffectHair' in file]
        else:
            lightmap_filenames = [file for file in lightmap_files if \
                                 actual_material_part_name in file and 'EffectHair' not in file]
        if not lightmap_filenames:
            self.blender_operator.report({'WARNING'}, f'"{actual_material_part_name}" lightmap not found for material "{outline_material.name}"')
            return
        else:
            lightmap_filename = lightmap_filenames[0]

        lightmap_node = outline_material.node_tree.nodes.get(v2_lightmap_node_name) \
            or outline_material.node_tree.nodes.get(v1_lightmap_node_name)
        self.assign_texture_to_node(lightmap_node, character_model_folder_file_path, lightmap_filename)
        self.blender_operator.report({'INFO'}, f'Imported "{actual_material_part_name}" lightmap onto material "{outline_material.name}"')

    def assign_diffuse_texture(self, character_model_folder_file_path, diffuse_files, body_part_material_name, actual_material_part_name):
        difuse_node_name = 'Outline_Diffuse'
        outline_material = bpy.data.materials.get(f'{self.material_names.MATERIAL_PREFIX}{body_part_material_name} Outlines')
        diffuse_node = outline_material.node_tree.nodes.get(difuse_node_name) \
            or None  # None for backwards compatibility in v1 where it did not exist

        diffuse_filenames = []
        if diffuse_node:
            if body_part_material_name == 'EffectHair':
                diffuse_filenames = [file for file in diffuse_files if 'EffectHair' in file]
            else:
                diffuse_filenames = [file for file in diffuse_files if \
                                    actual_material_part_name in file and 'EffectHair' not in file]
        if not diffuse_filenames:
            self.blender_operator.report({'INFO'}, f'"{actual_material_part_name}" diffuse not found for material "{outline_material.name}"')
            return
        else:
            diffuse_filename = diffuse_filenames[0]

            self.assign_texture_to_node(diffuse_node, character_model_folder_file_path, diffuse_filename)
            self.blender_operator.report({'INFO'}, f'Imported "{actual_material_part_name}" diffuse onto material "{outline_material.name}"')

    def assign_texture_to_node(self, node, character_model_folder_file_path, texture_file_name):
        texture_img_path = character_model_folder_file_path + "/" + texture_file_name
        texture_img = bpy.data.images.load(filepath = texture_img_path, check_existing=True)
        texture_img.alpha_mode = 'CHANNEL_PACKED'
        node.image = texture_img


class OutlineTextureImporterFactory:
    def create(game_type: GameType, blender_operator: Operator, context: Context):
        shader_identifier_service: ShaderIdentifierService = ShaderIdentifierServiceFactory.create(game_type)

        # Because we inject the GameType via StringProperty, we need to compare using the Enum's name (a string)
        if game_type == GameType.GENSHIN_IMPACT.name:
            if shader_identifier_service.identify_shader(bpy.data.materials, bpy.data.node_groups) is GenshinImpactShaders.V3_GENSHIN_IMPACT_SHADER:
                material_names = V3_BonnyFestivityGenshinImpactMaterialNames
            else:
                material_names = V2_FestivityGenshinImpactMaterialNames
            return GenshinImpactOutlineTextureImporter(blender_operator, context, material_names)
        elif game_type == GameType.HONKAI_STAR_RAIL.name:
            return HonkaiStarRailOutlineTextureImporter(blender_operator, context)
        elif game_type == GameType.PUNISHING_GRAY_RAVEN.name:
            return PunishingGrayRavenOutlineTextureImporter(blender_operator, context)
        else:
            raise Exception(f'Unknown {GameType}: {game_type}')


class GenshinImpactOutlineTextureImporter(OutlineTextureImporter):
    def __init__(self, blender_operator, context, material_names):
        super().__init__(blender_operator, context, material_names)
        self.material_names = material_names

    def import_textures(self):
        cache_enabled = self.context.window_manager.cache_enabled
        character_model_folder_file_path = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(CHARACTER_MODEL_FOLDER_FILE_PATH) \
            or os.path.dirname(self.blender_operator.filepath)

        if not character_model_folder_file_path:
            bpy.ops.genshin.import_outline_lightmaps(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}
        
        for name, folder, files in os.walk(character_model_folder_file_path):
            diffuse_files = [file for file in files if 'Diffuse'.lower() in file.lower()]
            lightmap_files = [file for file in files if 'Lightmap'.lower() in file.lower() or 'Ligntmap'.lower() in file.lower()]  # Important typo check for: Wrioth
            outline_materials = [material for material in bpy.data.materials.values() if 'Outlines' in material.name and material.name != self.material_names.OUTLINES]

            for outline_material in outline_materials:
                body_part_material_name = outline_material.name.split(' ')[-2]  # ex. 'miHoYo - Genshin Hair Outlines'
                character_type = None

                if [material for material in bpy.data.materials if material.name.startswith('NPC')]:
                    original_mesh_material = [material for material in bpy.data.materials if material.name.startswith('NPC') and body_part_material_name in material.name][0]
                    character_type = TextureImporterType.NPC
                elif [material for material in bpy.data.materials if material.name.startswith('Monster')]:
                    # Assuming all body parts are Body for now
                    # original_mesh_material = [material for material in bpy.data.materials if material.name.startswith('Monster') and 'Body' in material.name][0]
                    character_type = TextureImporterType.MONSTER
                else:
                    original_mesh_material = [material for material in bpy.data.materials if material.name.endswith(f'Mat_{body_part_material_name}')][0]
                    character_type = TextureImporterType.AVATAR

                if character_type == TextureImporterType.MONSTER:
                    actual_material_part_name = 'Tex'
                elif character_type == TextureImporterType.NPC:
                    actual_material_part_name = get_npc_mesh_body_part_name(original_mesh_material.name)
                else:
                    actual_material_part_name = get_actual_material_name_for_dress(original_mesh_material.name, character_type.name)

                if 'Face' not in actual_material_part_name and 'Face' not in body_part_material_name:
                    self.assign_lightmap_texture(character_model_folder_file_path, lightmap_files, body_part_material_name, actual_material_part_name)
                    self.assign_diffuse_texture(character_model_folder_file_path, diffuse_files, body_part_material_name, actual_material_part_name)
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

        if cache_enabled and character_model_folder_file_path:
            cache_using_cache_key(get_cache(cache_enabled), CHARACTER_MODEL_FOLDER_FILE_PATH, character_model_folder_file_path)


class HonkaiStarRailOutlineTextureImporter(OutlineTextureImporter):
    def __init__(self, blender_operator, context):
        super().__init__(blender_operator, context, Nya222HonkaiStarRailShaderMaterialNames)

    def import_textures(self):
        cache_enabled = self.context.window_manager.cache_enabled
        character_model_folder_file_path = self.blender_operator.file_directory \
            or get_cache(cache_enabled).get(CHARACTER_MODEL_FOLDER_FILE_PATH) \
            or os.path.dirname(self.blender_operator.filepath)

        if not character_model_folder_file_path:
            bpy.ops.genshin.import_outline_lightmaps(
                'INVOKE_DEFAULT',
                next_step_idx=self.blender_operator.next_step_idx, 
                file_directory=self.blender_operator.file_directory,
                invoker_type=self.blender_operator.invoker_type,
                high_level_step_name=self.blender_operator.high_level_step_name,
                game_type=self.blender_operator.game_type,
            )
            return {'FINISHED'}

        for name, folder, files in os.walk(character_model_folder_file_path):
            color_files = [file for file in files if 'Color'.lower() in file.lower()]
            lightmap_files = [file for file in files if 'LightMap'.lower() in file.lower() or 'FaceMap' in file.lower() or 'LigthMap'.lower() in file.lower()]  # that Lightmap typo is on purpose
            outline_materials = [material for material in bpy.data.materials.values() if 'outlines' in material.name.lower() and material.name != Nya222HonkaiStarRailShaderMaterialNames.OUTLINES]

            for outline_material in outline_materials:
                body_part_material_name = outline_material.name.split(' ')[-2]  # ex. 'miHoYo - Genshin Hair Outlines'
                original_mesh_material = [material for material in bpy.data.materials if material.name.endswith(f'Mat_{body_part_material_name}')]

                if original_mesh_material and 'EyeShadow' not in original_mesh_material and 'EyeShadow' not in body_part_material_name:
                    if 'Weapon' in body_part_material_name:
                        actual_material_part_name = 'Weapon'
                    elif 'Body' in body_part_material_name and 'Trans' in body_part_material_name:
                        actual_material_part_name = 'Body'
                    else:
                        actual_material_part_name = body_part_material_name

                    self.assign_diffuse_texture(character_model_folder_file_path, color_files, body_part_material_name, actual_material_part_name)

                    # No Lightmap texture for Face (not sure if Face even needs Color diffuse either...)
                    if 'Face' not in original_mesh_material and 'Face' not in body_part_material_name:
                        self.assign_lightmap_texture(character_model_folder_file_path, lightmap_files, body_part_material_name, actual_material_part_name)
            break  # IMPORTANT: We os.walk which also traverses through folders...we just want the files

        if cache_enabled and character_model_folder_file_path:
            cache_using_cache_key(get_cache(cache_enabled), CHARACTER_MODEL_FOLDER_FILE_PATH, character_model_folder_file_path)

    def assign_lightmap_texture(self, character_model_folder_file_path, lightmap_files, body_part_material_name, actual_material_part_name):
        outline_material = bpy.data.materials.get(
            f'{Nya222HonkaiStarRailShaderMaterialNames.MATERIAL_PREFIX}{body_part_material_name} Outlines')

        # Genshin Note: Unable to determine between character/equipment textures for Monsters w/ equipment in same folder
        lightmap_filename = [file for file in lightmap_files if actual_material_part_name in file][0]

        texture_img_path = character_model_folder_file_path + "/" + lightmap_filename
        texture_img = bpy.data.images.load(filepath = texture_img_path, check_existing=True)
        texture_img.alpha_mode = 'CHANNEL_PACKED'

        hsr_texture_importer = TextureImporterFactory.create(TextureImporterType.HSR_AVATAR, GameType.HONKAI_STAR_RAIL)
        hsr_texture_importer.set_lightmap_texture(None, outline_material, texture_img)

    def assign_diffuse_texture(self, character_model_folder_file_path, diffuse_files, body_part_material_name, actual_material_part_name):
        outline_material = bpy.data.materials.get(
            f'{Nya222HonkaiStarRailShaderMaterialNames.MATERIAL_PREFIX}{body_part_material_name} Outlines')

        diffuse_filename = [file for file in diffuse_files if actual_material_part_name in file][0]

        texture_img_path = character_model_folder_file_path + "/" + diffuse_filename
        texture_img = bpy.data.images.load(filepath = texture_img_path, check_existing=True)
        texture_img.alpha_mode = 'CHANNEL_PACKED'

        hsr_texture_importer = TextureImporterFactory.create(TextureImporterType.HSR_AVATAR, GameType.HONKAI_STAR_RAIL)
        hsr_texture_importer.set_diffuse_texture(None, outline_material, texture_img)


class PunishingGrayRavenOutlineTextureImporter(OutlineTextureImporter):
    def __init__(self, blender_operator, context):
        super().__init__(blender_operator, context, JaredNytsPunishingGrayRavenShaderMaterialNames)

    def import_textures(self):
        return
