bl_info = {
    "name": "Genshin Setup Wizard",
    "author": "Mken, M4urlcl0, Modder4869, Zekium",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar > Genshin Impact Setup Wizard",
    "description": "An addon to streamline the character model setup when using Festivity's Shaders",
    "warning": "",
    "doc_url": "",
    "support": 'COMMUNITY',
    "category": "miHoYo",
    "tracker_url": "",
    "doc_url": ""
}

import bpy
import importlib
import setup_wizard.cache_operator
from setup_wizard.cache_operator import ClearCacheOperator

import setup_wizard.ui_setup_wizard_menu
from setup_wizard.ui_setup_wizard_menu import UI_Properties, GI_PT_Setup_Wizard_UI_Layout, GI_PT_UI_Character_Model_Menu, GI_PT_UI_Materials_Menu, GI_PT_UI_Outlines_Menu, GI_PT_UI_Misc_Setup_Menu, GI_PT_UI_Misc_Menu

import setup_wizard.genshin_setup_wizard
from setup_wizard.genshin_setup_wizard import register as register_genshin_setup_wizard, setup_dependencies

register_genshin_setup_wizard()
setup_dependencies()

modules = [
    setup_wizard.ui_setup_wizard_menu,
    setup_wizard.genshin_setup_wizard,
    setup_wizard.cache_operator
]

classes = [
    GI_PT_Setup_Wizard_UI_Layout, 
    GI_PT_UI_Character_Model_Menu, 
    GI_PT_UI_Materials_Menu, 
    GI_PT_UI_Outlines_Menu, 
    GI_PT_UI_Misc_Setup_Menu,
    GI_PT_UI_Misc_Menu,
    ClearCacheOperator
]

for module in modules:
    try:
        importlib.reload(module)
    except ModuleNotFoundError:
        pass  # likely new class

register, unregister = bpy.utils.register_classes_factory(classes)
UI_Properties.create_custom_ui_properties()


'''
For auto_loading, but right now we're doing simple loading to have
direct control for the order of class registration.
'''
'''
# from setup_wizard import auto_load
# auto_load.init()


# def register():
#     # auto_load.register()


# def unregister():
#     # auto_load.unregister()
'''
