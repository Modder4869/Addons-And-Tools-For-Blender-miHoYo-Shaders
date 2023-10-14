# Author: michael-gh1

import bpy
from bpy.types import Panel, UILayout

from setup_wizard import bl_info
from setup_wizard.domain.game_types import GameType

class UI_Properties:
    @staticmethod
    def create_custom_ui_properties():
        bpy.types.WindowManager.cache_enabled = bpy.props.BoolProperty(
            name = "Cache Enabled",
            default = True
        )

        bpy.types.WindowManager.setup_wizard_betterfbx_enabled = bpy.props.BoolProperty(
            name = "BetterFBX Enabled",
            default = True
        )


class GI_PT_Setup_Wizard_UI_Layout(Panel):
    bl_label = "Genshin Impact Setup Wizard"
    bl_idname = "GI_PT_Setup_Wizard_UI_Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Genshin Impact"

    def draw(self, context):
        layout = self.layout
        window_manager = context.window_manager

        version_text = layout.row()
        version_text.label(text='v' + '.'.join([str(version_num) for version_num in bl_info.get('version')]))

        sub_layout = layout.box()
        row = layout.row()
        OperatorFactory.create(
            sub_layout,
            'genshin.setup_wizard_ui',
            'Run Entire Setup',
            'PLAY',
            game_type=GameType.GENSHIN_IMPACT.name
        )

        expy_kit_installed = bpy.context.preferences.addons.get('Expy-Kit-main')
        betterfbx_installed = bpy.context.preferences.addons.get('better_fbx')
        rigify_installed = bpy.context.preferences.addons.get('rigify')

        if not expy_kit_installed or not betterfbx_installed or not rigify_installed:
            sub_layout.label(text='Rigging Disabled', icon='ERROR')

        row.prop(window_manager, 'cache_enabled')
        OperatorFactory.create(
            row,
            'genshin.clear_cache_operator',
            'Clear Cache',
            'TRASH',
            game_type=GameType.GENSHIN_IMPACT.name,
        )

        if betterfbx_installed:
            row2 = layout.row()
            row2.prop(window_manager, 'setup_wizard_betterfbx_enabled')


class GI_PT_Basic_Setup_Wizard_UI_Layout(Panel):
    bl_label = 'Basic Setup'
    bl_idname = 'GI_PT_UI_Basic_Setup_Layout'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Genshin Impact"

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.box()

        OperatorFactory.create(
            sub_layout,
            'genshin.set_up_character',
            'Set Up Character',
            icon='OUTLINER_OB_ARMATURE',
            game_type=GameType.GENSHIN_IMPACT.name,
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.set_up_materials',
            'Set Up Materials',
            icon='MATERIAL',
            game_type=GameType.GENSHIN_IMPACT.name,
        )
        if bpy.app.version >= (3,3,0):
            OperatorFactory.create(
                sub_layout,
                'genshin.set_up_outlines',
                'Set Up Outlines',
                icon='GEOMETRY_NODES',
                game_type=GameType.GENSHIN_IMPACT.name,
            )
        else:
            layout.label(text='(Outlines Disabled < v3.3.0)')
        OperatorFactory.create(
            sub_layout,
            'genshin.finish_setup',
            'Finish Setup',
            icon='CHECKMARK',
            game_type=GameType.GENSHIN_IMPACT.name,
        )

        OperatorFactory.create_rig_character_ui(sub_layout)


class GI_PT_Advanced_Setup_Wizard_UI_Layout(Panel):
    bl_label = 'Advanced Setup'
    bl_idname = 'GI_PT_UI_Advanced_Setup_Layout'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Genshin Impact"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout


class GI_PT_UI_Character_Model_Menu(Panel):
    bl_label = 'Set Up Character Menu'
    bl_idname = 'GI_PT_UI_Character_Model_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.column()

        OperatorFactory.create(
            sub_layout,
            'genshin.import_model',
            'Import Character Model',
            'OUTLINER_OB_ARMATURE',
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.delete_empties',
            'Delete Empties',
            'TRASH'
        )


class GI_PT_UI_Materials_Menu(Panel):
    bl_label = 'Set Up Materials Menu'
    bl_idname = 'GI_PT_UI_Materials_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.column()

        OperatorFactory.create(
            sub_layout,
            'genshin.import_materials',
            'Import Genshin Materials',
            'MATERIAL',
            game_type=GameType.GENSHIN_IMPACT.name,
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.replace_default_materials',
            'Replace Default Materials',
            'ARROW_LEFTRIGHT',
            game_type=GameType.GENSHIN_IMPACT.name,
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.import_textures',
            'Import Character Textures',
            'TEXTURE',
            game_type=GameType.GENSHIN_IMPACT.name,
        )


class GI_PT_UI_Outlines_Menu(Panel):
    bl_label = 'Set Up Outlines Menu'
    bl_idname = 'GI_PT_UI_Outlines_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.column()
        scene = context.scene

        if bpy.app.version >= (3,3,0):
            OperatorFactory.create(
                sub_layout,
                'genshin.import_outlines',
                'Import Outlines',
                'FILE_FOLDER',
                game_type=GameType.GENSHIN_IMPACT.name,
            )
            OperatorFactory.create(
                sub_layout,
                'genshin.setup_geometry_nodes',
                'Set Up Geometry Nodes',
                'GEOMETRY_NODES',
                game_type=GameType.GENSHIN_IMPACT.name,
            )
            OperatorFactory.create(
                sub_layout,
                'genshin.import_outline_lightmaps',
                'Import Outline Lightmaps',
                'FILE_FOLDER',
                game_type=GameType.GENSHIN_IMPACT.name,
            )

            sub_layout = layout.box()
            sub_layout.prop_search(scene, 'setup_wizard_material_for_material_data_import', bpy.data, 'materials')
            sub_layout.prop_search(scene, 'setup_wizard_outlines_material_for_material_data_import', bpy.data, 'materials')
            OperatorFactory.create(
                sub_layout,
                'genshin.import_material_data',
                'Import Material Data',
                'FILE',
                game_type=GameType.GENSHIN_IMPACT.name,
            )
        else:
            layout.label(text='(Outlines Disabled < v3.3.0)')


class GI_PT_UI_Finish_Setup_Menu(Panel):
    bl_label = 'Finish Setup Menu'
    bl_idname = 'GI_PT_UI_Misc_Setup_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.column()

        OperatorFactory.create(
            sub_layout,
            'genshin.fix_transformations',
            'Fix Transformations',
            'OBJECT_DATA'
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.setup_head_driver',
            'Set Up Head Driver',
            'CONSTRAINT'
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.set_color_management_to_standard',
            'Set Color Mgmt to Standard',
            'SCENE'
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.delete_specific_objects',
            'Delete EffectMesh',
            'TRASH'
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.set_up_armtwist_bone_constraints',
            'Set Up ArmTwist Bone Constraints',
            'CONSTRAINT_BONE'
        )


class GI_PT_UI_Character_Rig_Setup_Menu(Panel):
    bl_label = 'Character Rig Menu'
    bl_idname = 'GI_PT_Rigify_Setup_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'GI_PT_UI_Advanced_Setup_Layout'

    def draw(self, context):
        layout = self.layout
        sub_layout = layout.column()
        box = sub_layout.box()

        character_rigger_props = context.scene.character_rigger_props

        OperatorFactory.create_rig_character_ui(box)

        box = sub_layout.box()        
        box.label(text='Settings')

        col = box.column()
        OperatorFactory.create(
            col,
            'hoyoverse.rootshape_filepath_setter',
            'Override RootShape Filepath',
            'FILE_FOLDER',
            game_type=GameType.GENSHIN_IMPACT.name,
            operator_context='INVOKE_DEFAULT'
        )
        col = box.column()
        col.prop(character_rigger_props, 'allow_arm_ik_stretch')
        col.prop(character_rigger_props, 'allow_leg_ik_stretch')
        col.prop(character_rigger_props, 'use_arm_ik_poles')
        col.prop(character_rigger_props, 'use_leg_ik_poles')
        col.prop(character_rigger_props, 'add_children_of_constraints')
        col.prop(character_rigger_props, 'use_head_tracker')


class GI_PT_UI_Gran_Turismo_UI_Layout(Panel):
    bl_label = "Gran Turismo Tonemapper"
    bl_idname = "GI_PT_Gran_Turismo_Tonemapper_UI_Layout"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Genshin - Setup Wizard"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        sub_layout = layout.box()
        window_manager = context.window_manager

        row.prop(window_manager, 'cache_enabled')
        OperatorFactory.create(
            row,
            'genshin.clear_cache_operator',
            'Clear Cache',
            'TRASH',
            game_type=GameType.GENSHIN_IMPACT.name,
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.change_bpy_context',
            'Enable Use Nodes',
            'CHECKMARK',
            bpy_context_attr='scene.use_nodes',
            bpy_context_value_bool=True
        )
        OperatorFactory.create(
            sub_layout,
            'genshin.gran_turismo_tonemapper_setup',
            'Set Up GT Tonemapper',
            'PLAY'
        )


'''
    This factory is intended to help create a UI element's operator (or the action it takes) when pressed.
    While it currently doesn't do anything too grand, it may provide future flexibility.
'''
class OperatorFactory:
    @staticmethod
    def create(
        ui_object: UILayout,
        operator: str,
        text: str,
        icon: str,
        operator_context='EXEC_DEFAULT',
        **kwargs
    ):
        ui_object.operator_context = operator_context
        ui_object = ui_object.operator(
            operator=operator,
            text=text,
            icon=icon,
        )

        for key, value in kwargs.items():
            setattr(ui_object, key, value)

    @staticmethod
    def create_rig_character_ui(
        ui_object: UILayout,
    ):
        expy_kit_installed = bpy.context.preferences.addons.get('Expy-Kit-main')
        betterfbx_installed = bpy.context.preferences.addons.get('better_fbx')
        rigify_installed = bpy.context.preferences.addons.get('rigify')

        column = ui_object.column()
        column.enabled = True if expy_kit_installed and betterfbx_installed and rigify_installed else False
        OperatorFactory.create(
            column,
            'hoyoverse.set_up_character_rig',
            'Rig Character',
            'OUTLINER_OB_ARMATURE',
            game_type=GameType.GENSHIN_IMPACT.name,
        )
        if not column.enabled:
            column = ui_object.column()
            if not betterfbx_installed:
                column.label(text='BetterFBX required', icon='ERROR')
            if not expy_kit_installed:
                column.label(text='ExpyKit required', icon='ERROR')
            if not rigify_installed:
                column.label(text='Rigify required', icon='ERROR')
