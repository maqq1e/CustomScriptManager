import bpy
from enum import Enum

### Datas Variables

def getIcons(self, context):
    icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()
    return [(icon, icon, "", icon, idx) for idx, icon in enumerate(icons)]

PROPERTY_var_types = [
    ("BOOL", "Bool", "bool"),
    ("BOOL_TOGGLE", "Bool Toggle", "bool_toggle"),
    ("FLOAT", "Float", "float"),
    ("FLOAT_SLIDER", "Float Slider", "float_slider"),
    ("INTEGER", "Integer", "integer"),
    ("INTEGER_SLIDER", "Integer Slider", "integer_slider"),
    ("STRING", "String", "string"),
    ("STRING_PATH", "Directory Path", "string_path"),
    ("CUSTOM", "Custom Data", "custom"),
    ("CUSTOM_SELF", "Active Object Custom Data", "custom_self"),
]

PROPERTY_var_default_value = [
    False,
    False,
    1.5,
    1.5,
    0,
    0,
    "String",
    "C:\\",
    "",
    ""
]

PROPERTY_var_types_options = [
    {
        "hideName": True,
        "slider":False,
        "toggle":False,
        "icon_only":False,
    },
    {
        "hideName": False,
        "slider":False,
        "toggle":True,
        "icon_only":False,
    },
    {
        "hideName": False,
        "slider":False,
        "toggle":True,
        "icon_only":False,
    },
    {
        "hideName": True,
        "slider":True,
        "toggle":False,
        "icon_only":False,
    },
    {
        "hideName": True,
        "slider":False,
        "toggle":False,
        "icon_only":False,
    },
    {
        "hideName": True,
        "slider":True,
        "toggle":False,
        "icon_only":False,
    },
    {
        "hideName": True,
        "slider":False,
        "toggle":False,
        "icon_only":False,
    },
    {
        "hideName": True,
        "slider":False,
        "toggle":False,
        "icon_only":False,
    },
    {
        "hideName": True,
        "slider":False,
        "toggle":False,
        "icon_only":False,
    },
    {
        "hideName": True,
        "slider":False,
        "toggle":False,
        "icon_only":False,
    },
]

### Class id_names

class EXTENSIONS(Enum):
    extensions_add_item = "extensions.add_item"
    extensions_remove_item = "extensions.remove_item"
    extensions_refresh_item = "extensions.refresh_item"

class TEMPLATES(Enum):
    templates_add_item = "templates.add_item"
    templates_remove_item = "templates.remove_item"
    templates_edit_item = "templates.edit_item"
    scripts_add_item = "scripts.add_item"
    scripts_remove_item = "scripts.remove_item"
    scripts_edit_item = "scripts.edit_item"
    args_add_item = "args.add_item"
    args_edit_item = "args.edit_item"
    args_remove_item = "args.remove_item"

class OPERATORS(Enum):
    open_addon_prefs = "operators.open_addon_prefs"
    create_json_file = "operators.create_json_file"
    delete_json_file = "operators.delete_json_file"
    load_templates = "operators.load_templates"
    save_templates = "operators.save_templates"
    run_scripts = "operators.run_scripts"
    register_script = "operators.register_script"
    unregister_script = "operators.unregister_script"
    edit_template_file = "operators.edit_template_file"
