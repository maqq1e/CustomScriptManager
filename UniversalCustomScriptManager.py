import importlib
import bpy
import os
import json
import sys

# Addon Info
bl_info = {
    "name": "Universal Custom Script Manager",
    "author": "https://github.com/maqq1e/CustomScriptManager",
    "description": "Easy way manage your custom scripts",
    "blender": (5, 0, 0),
    "version": (2, 1, 0),
}

# Datas


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
        "hideName": False,
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


# Def

def dataToJson(scripts, extensions):

    result = {
        "extensions": [],
        "scripts": []
    }

    extensions_data = []
    scripts_data = []
    
    if len(extensions) > 0:
        for ext in extensions:
            extensions_data.append({
                    "name": ext.name,
                    "path": ext.path,
                    "data_block": ext.data_block
                })

    if len(scripts) > 0:
        for scr in scripts:

            args_data = []

            for arg in scr.args:
                        
                key = getVarType(PROPERTY_var_types, arg.type)[0]
                
                value = arg[key]      

                args_data.append({
                        "name": arg.name,
                        "description": arg.description,
                        "type": arg.type,
                        "value": value,
                    })

            scripts_data.append({
                    "name": scr.name,
                    "description": scr.description,
                    "icon": scr.icon,
                    "path": scr.path,
                    "data_block": scr.data_block,
                    "args": args_data
                })

    result["extensions"].extend(extensions_data)
    result["scripts"].extend(scripts_data)


    return result

def importJson(folder, file_name, ):
    # set output path and file name (set your own)
    file = os.path.join(folder, file_name + ".json")

    # 2 - Import data from JSON file
    variable = {}

    # read JSON file
    with open(file, 'r') as f:
        variable = json.load(f)

    return variable

def exportJson(context, data, filename, is_new = False):
    global_ucsm = context.window_manager.ucsm

    # encode dict as JSON
    payload = json.dumps(data, indent=1, ensure_ascii=True)

    # set output path and file name (set your own)
    save_path = global_ucsm.preferences.folder
    file = os.path.join(save_path, filename + ".json")

    if is_new:
        counter = 1
        # Loop until we find a non-existing file
        while os.path.exists(file):
            file = os.path.join(save_path, filename + "_" + str(counter) + ".json")
            counter += 1

    # write JSON file
    with open(file, 'w') as outfile:
        outfile.write(payload + '\n')

def loadScriptAsString(filepath):
        
    try:
        # Open the file and read its content
        with open(filepath, 'r', encoding='utf-8') as file:
            script_content = file.read()
    except ImportError as e:
        print(f"Error importing module: {e}")
        script_content = None
        
    
    return script_content

def loadScriptAsTextFile(filepath):
    filename = os.path.basename(filepath)

    is_exist = bpy.data.texts.get(filename)

    if is_exist:
        return is_exist

    # Load the file into Blender's Text datablocks
    text_block = bpy.data.texts.load(filepath)

    return text_block

def registerCurrentExtension(self, context, path, filename, new=True):
    global_ucsm = context.window_manager.ucsm

    # if filename in global_ucsm.extensions_list:
    #     if self:
    #         self.report({'ERROR'}, "You have already assigned addon with same name")
    #     return None
        
    script_context = {}
    if path == "":
        _temp = bpy.data.texts.get(filename) # Load local script
        if _temp == None:
            if self:
                self.report({'ERROR'}, 'There is no local extensions with name' + filename)
            else:
                correct_name = filename.replace(".py", "")
                item = global_ucsm.extensions_list.add()
                item.name = correct_name
                item.path = path
                item.is_missing = True
            return None
        else:
            script = _temp.as_string()
    else:
        # script = loadScriptAsTextFile(path)
        script = loadScriptAsString(path) # Load global script
    

    exec(script, script_context)


    if script_context.get("register") == None or script_context.get("unregister") == None:
        if self:
            self.report({'ERROR'}, 'You have no register and unregister functions inside ' + filename)
        return None
    else:
        correct_name = filename.replace(".py", "")
        if new:
            item = global_ucsm.extensions_list.add()
        else:
            item = global_ucsm.extensions_list.get(correct_name)

            
        item.name = correct_name
        item.path = path

        if path == "":
            item.data_block = filename

        stack = global_ucsm.extensions_stack
        
        stack[item.name] = script_context['unregister']

        try:
            script_context['register']()
        except Exception as e:
            if self:
                self.report({'ERROR'}, f"Error running register in {filename}: {e}")
            else:
                print(e)

    
        return item

def unregisterCurrentExtension(self, context, filename, clear=True):
        
    global_ucsm = context.window_manager.ucsm
    stack = global_ucsm.extensions_stack
    index = global_ucsm.extensions_list.find(filename)
        
    ext = global_ucsm.extensions_list[index]
    # For cases when script context broke 
    if stack == {}:

        script_context = {}

        if ext.path == "":
            _temp = bpy.data.texts.get(filename) # Load local script
            if _temp == None:
                if self:
                    self.report({'ERROR'}, 'There is no local extensions with name' + filename)
                return None
            else:
                script = _temp.as_string()
        else:
            script = loadScriptAsString(ext.path) # Load global script
        
        exec(script, script_context)

        try:
            script_context['register']()
        except Exception as e:
            if self:
                self.report({'ERROR'}, f"Error running register in {filename}: {e}")
            else:
                print(e)

        stack[ext.name] = script_context['unregister']

    try:
        stack[ext.name]()
    except Exception as e:
        if self:
            self.report({'ERROR'}, f"Error while unregister in {filename}: {e}")
        else:
            print(e)
    else:
        if self:
            self.report({'INFO'}, "Success unregister " + filename + " extension.")
    
    if clear:
        global_ucsm.extensions_list.remove(index)
    
def reloadCurrentExtension(self, context, path, filename):

    unregisterCurrentExtension(self, context, filename, False)

    registerCurrentExtension(self, context, path, filename, False)

def reloadAllExtensions(self, context):

    global_ucsm = context.window_manager.ucsm

    for item in global_ucsm.extensions_list:
        reloadCurrentExtension(self, context, item.path, item.name)

def getVarType(types, id_type):
    value = ""
    index = 0
    # I need to find only whole name, ignore substrings
    str1 = " " + id_type + " "
    
    for vt in types:
        str2 = " " + vt[0] + " "
        if str1 in str2:
            value = vt[2]
            break
        index = index + 1
    return [value, index]

def executeInternal(name, args=None):
    text = bpy.data.texts.get(name)
    if not text:
        return [{'ERROR'}, f"No text datablock named '{name}'"]

    try:
        # Create a temporary namespace for execution
        namespace = {}
        exec(text.as_string(), namespace)

        if "main" in namespace and callable(namespace["main"]):
            namespace["main"](args)
            return [{'INFO'}, f"Text datablock '{name}' executed"]
        else:
            return [{'WARNING'}, f"No main() function in text datablock '{name}'"]
    except Exception as e:
        return [{'ERROR'}, f"Error running main() in text datablock '{name}': {e}"]

def executeExternal(filepath, args=None):

    spec = importlib.util.spec_from_file_location("module.name", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
        
    # Assuming there's a function named 'main' in each script
    if hasattr(module, "main"):
        try:                
            module.main(args)  # Execute the 'main' function
            return [{'INFO'}, "Scripts executed"]
        except Exception as e:
            return [{'ERROR'}, f"Error running main() in {filepath}: {e}"]

def executeScript(props, filepath, filename):

    # Init Props value for script
    args = {}
    for prop in props:
        # Basic Properties or Cusom Object Properties
        key = getVarType(PROPERTY_var_types, prop.type)[0]
        
        value = prop[key]
        
        prop_name = prop.name
        
        if "CUSTOM" in prop.type:
            sub_args = {}
            
            if prop.type == "CUSTOM":
                target_object = bpy.context.scene.objects.get(value)
            if prop.type == "CUSTOM_SELF":
                target_object = bpy.context.active_object
                
            for prop_item in target_object.keys():
                ignore_mask = prop_item + ";"
                if ignore_mask not in prop.name:
                    if prop_item != "_RNA_UI":
                        sub_args.update({prop_item: target_object[prop_item]})
            
            value = sub_args
            prop_name = target_object.name
            
        
        args.update({prop_name: value})\
        
    if filepath == "":
        return executeInternal(filename, args)
    else:
        return executeExternal(filepath, args)

# Preferences Panel
class UCSM_ManagerPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    addon_name: bpy.props.StringProperty(default=__name__)
    
    links_hide: bpy.props.BoolProperty(default=False)

    folder: bpy.props.StringProperty(
        name="Path",
        description="Path to scripts",
        default="",
        subtype='DIR_PATH',
    )
    
    def draw(self, context):
        layout = self.layout

        layout.prop(self, "folder")

        row = layout.row()
        if self.links_hide:
            row.prop(self, "links_hide", text="Links:", icon="TRIA_DOWN", toggle=True)
        else:
            row.prop(self, "links_hide", text="Links:", icon="TRIA_LEFT", toggle=True)
            
        if self.links_hide:
            op = layout.operator('wm.url_open', text="Project Git", icon="URL")
            op.url = "https://github.com/maqq1e/CustomScriptManager"        
            row = layout.row()
            op = row.operator('wm.url_open', text="Github", icon="URL")
            op.url = "https://github.com/maqq1e"
            op = row.operator('wm.url_open', text="Gumroad", icon="URL")
            op.url = "https://maqq1e.gumroad.com/"
            op = row.operator('wm.url_open', text="ArtStation", icon="URL")
            op.url = "https://www.artstation.com/jellystuff"
  
# Properties

def _callSave(self, context):
    global_ucsm = context.window_manager.ucsm

    global_ucsm.is_save = True

class UCSM_ScriptsArguments(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(update=_callSave)
    description: bpy.props.StringProperty(update=_callSave)
    type: bpy.props.StringProperty(update=_callSave)
    bool: bpy.props.BoolProperty(options={'ANIMATABLE'}, update=_callSave)
    bool_toggle: bpy.props.BoolProperty(options={'ANIMATABLE'}, update=_callSave)
    float: bpy.props.FloatProperty(update=_callSave)
    float_slider: bpy.props.FloatProperty(update=_callSave)
    string: bpy.props.StringProperty(
        name="Directory",
        default="",
        subtype='NONE'
    , update=_callSave)
    integer: bpy.props.IntProperty(update=_callSave)
    integer_slider: bpy.props.IntProperty(update=_callSave)
    string_path: bpy.props.StringProperty(
        name="Directory",
        default="",
        subtype='DIR_PATH'
    )
    custom: bpy.props.StringProperty()
    custom_self: bpy.props.StringProperty()

class UCSM_ExecutionGroup(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="")
    description: bpy.props.StringProperty(default="")
    icon: bpy.props.StringProperty(default="")

    path: bpy.props.StringProperty(
        name="Path",
        description="Path to script",
        default="",
        subtype='FILE_PATH',
    )

    data_block: bpy.props.StringProperty()

    is_missing: bpy.props.BoolProperty(default=False)

    status: bpy.props.BoolProperty(default=False)

    args: bpy.props.CollectionProperty(type=UCSM_ScriptsArguments)
 

def _getTemplatesFiles(self, context):
    global_ucsm = context.window_manager.ucsm
    Enum_items = [("NONE", "None", "Not use any of templates")]
    
    if global_ucsm.preferences.folder:
        for filename in os.listdir(global_ucsm.preferences.folder):
            # Check if the file ends with .py (Python files)
            if filename.endswith(".json"):
                data = filename.replace(".json", "")
                item = (data, data, data)
                # Print the file name
                Enum_items.append(item)
            
    return Enum_items

def _updateCurrentTemplateScripts(self, context):

    global_ucsm = context.window_manager.ucsm

    for item in global_ucsm.extensions_list:
        unregisterCurrentExtension(None, context, item.name)

    global_ucsm.extensions_list.clear()
    global_ucsm.scripts_list.clear()

    if global_ucsm.templates == "NONE":
        return None

    data = importJson(global_ucsm.preferences.folder, global_ucsm.templates)


    for ext in data["extensions"]:
        item = registerCurrentExtension(None, context, ext["path"], ext["name"])
        if item:
            if ext["data_block"]:
                item.data_block = ext["data_block"]

    for script in data["scripts"]:

        script_item = global_ucsm.scripts_list.add()

        script_item.name = script["name"]
        script_item.description = script["description"]
        script_item.path = script["path"]
        script_item.icon = script["icon"]

        if script["data_block"]:
            script_item.data_block = script["data_block"]
                
        for arg in script["args"]:
            if arg["type"] == "CUSTOM":
                arg["value"] = context.scene.active_object.name
            if arg["type"] == "CUSTOM_SELF":
                arg["value"] = ""

            args = script_item.args
            
            arg_item = args.add()
            
            arg_item.name = arg["name"]
            arg_item.description = arg["description"]
            arg_item.type = arg["type"]
            
            varType = getVarType(PROPERTY_var_types, arg["type"])
            key = varType[0]
            index = varType[1]

            value = arg["value"]
            
            if value == 0 or value == "0":
                value = PROPERTY_var_default_value[index]
            
            arg_item[key] = value

    
    return None
    
class UCSM_GlobalProperties(bpy.types.PropertyGroup):

    @property
    def preferences(self):
        # Dynamically access the addon preferences
        return bpy.context.preferences.addons[__name__].preferences

    is_save: bpy.props.BoolProperty(default=False)

    templates: bpy.props.EnumProperty(name="Templates", items=_getTemplatesFiles, update=_updateCurrentTemplateScripts)

    use_script_tab: bpy.props.BoolProperty(default=True)
    use_extension_tab: bpy.props.BoolProperty(default=True)
    use_list: bpy.props.BoolProperty(default=False)

    extensions_stack = {}
    # global_extensions_list: bpy.props.PointerProperty(type=UCSM_ExecutionGroup)
    extensions_list: bpy.props.CollectionProperty(type=UCSM_ExecutionGroup)
    active_extensions_list: bpy.props.IntProperty()
    local_extensions_list: bpy.props.CollectionProperty(type=UCSM_ExecutionGroup)

    scripts_list: bpy.props.CollectionProperty(type=UCSM_ExecutionGroup)
    active_scripts_list: bpy.props.IntProperty()
    local_script_list: bpy.props.PointerProperty(type=UCSM_ExecutionGroup)
    active_local_script_list: bpy.props.IntProperty()

class UCSM_Properties(bpy.types.PropertyGroup):

    temp_local_extension = bpy.props.PointerProperty(type=bpy.types.Object)


def setProperties():
    bpy.types.Scene.ucsm = bpy.props.PointerProperty(type=UCSM_Properties)
    bpy.types.WindowManager.ucsm = bpy.props.PointerProperty(type=UCSM_GlobalProperties)
        
def delProperties():
    del bpy.types.Scene.ucsm
    del bpy.types.WindowManager.ucsm


PropsClasses = [
    UCSM_ManagerPreferences,
    UCSM_ScriptsArguments,
    UCSM_ExecutionGroup,
    UCSM_GlobalProperties,
    UCSM_Properties
]

# Panels

def EXTENSIONS_LIST(layout, item):
    if item.is_missing:
        layout.alert = True
        layout.label(text=item.name)
    else:
        op = layout.operator(UCSM_ExtensionsReloadSingle.bl_idname, text=item.name, icon="FILE_REFRESH")
        op.name = item.name
    op = layout.operator(UCSM_ExtensionsRemove.bl_idname, text="", icon="TRASH")
    op.name = item.name

def SCRIPTS_LIST(layout, item):  
    icon = "NONE"
    if item.icon:
        icon = item.icon
    op = layout.operator(UCSM_ScriptExecute.bl_idname, text=item.name, icon=icon)
    op.data_block = item.data_block
    op.path = item.path  
    op.name = item.name
    
    op = layout.operator(UCSM_ScriptsEdit.bl_idname, text="", icon="GREASEPENCIL")
    op.name = item.name
    op.description = item.description
    op.path = item.path
    op.icon = item.icon
    if item.data_block:
        op.temp = item.data_block
    else:
        op.is_global = True
    op = layout.operator(UCSM_ScriptsDelete.bl_idname, text="", icon="REMOVE")
    op.name = item.name

def ARGUMENTS_LIST(context, _layout, script):
    for arg in script.args:

        layout = _layout.box()
            
        args_row = layout.row()
                                                        
        varType = getVarType(PROPERTY_var_types, arg.type)
        key = varType[0]
        index = varType[1]
        option = PROPERTY_var_types_options[index]
        
        ### ---   CUSTOM OBJECT PROPERTIES   --- ###
        
        if "CUSTOM" in arg.type:
            
            if arg.type == "CUSTOM":
                target_object = context.scene.objects.get(arg.custom)
            if arg.type == "CUSTOM_SELF":
                target_object = context.active_object
                if target_object == None:
                    continue
            
            prop_box = args_row.box()
            prop_row = prop_box.grid_flow()
            
            _props_count = 0
                                        
            for prop in target_object.keys():
                ignore_mask = prop + ";"
                if ignore_mask not in arg.name:
                    if prop != "_RNA_UI":  # Ignore the '_RNA_UI' entry
                        prop_row.prop(target_object, f'["{prop}"]', text=prop)
                        _props_count = _props_count + 1
            
            if (_props_count == 0):
                prop_row.label(text="You have no any properties.")
        ###############################################
        else:
            args_row.prop(arg, key, text="" if option['hideName'] else arg.name, 
                        slider=option['slider'],
                        toggle=option['toggle'],
                        icon_only=option['icon_only']
                        )

        op = args_row.operator(UCSM_ScriptsArgsEdit.bl_idname, text="", icon="TOOL_SETTINGS")
        op.current_script = script.name
        op.current_argument = arg.name
        op.name = arg.name
        op.description = arg.description
        op.type = arg.type
        _value = op.value.add()
        _value[key] = arg[key]
        
        op = args_row.operator(UCSM_ScriptsArgsDelete.bl_idname, text="", icon="REMOVE")
        op.current_script = script.name
        op.current_argument = arg.name

class UCSM_ExtensionsList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data

        row = layout.row(align=True)
        EXTENSIONS_LIST(row, item)

class UCSM_ScriptsList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data

        row = layout.row(align=True)
        SCRIPTS_LIST(row, item)
        


class UCSM_SetupPanel(bpy.types.Panel):
    bl_label = "Universal Custom Script Manager"
    bl_idname = "UCSM_PT_setup_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Script Manager' # You may edit this field

    def draw_header(self, context):
        """Optional: Draw the header of the panel."""
        self.layout.label(icon='KEY_COMMAND')  # Example header icon
    
    def draw(self, context):
        global_ucsm = context.window_manager.ucsm
        
        layout = self.layout

        layout.prop(global_ucsm.preferences, "folder", text="")
        box = layout.box()
        box.enabled = global_ucsm.is_save
        _row = box.row()
        _row.operator(UCSM_ExtensionsReload.bl_idname, text="Revert Changes", icon="LOOP_BACK")
        _row.operator(UCSM_TemplateSave.bl_idname, text="Save Changes", icon="EXPORT")
        
        box = layout.box()
        row = box.row()
        row.prop(global_ucsm, "templates", text="")
        if global_ucsm.templates != "NONE":
            row.operator(UCSM_TemplateRename.bl_idname, text="", icon="TOOL_SETTINGS")

        row.operator(UCSM_TemplateAdd.bl_idname, text="", icon="ADD")

        if global_ucsm.templates != "NONE":
            row.operator(UCSM_TemplateDelete.bl_idname, text="", icon="REMOVE")

        if global_ucsm.use_extension_tab:
            icon = "HIDE_OFF"
        else:
            icon = "HIDE_ON"
        box.prop(global_ucsm, "use_extension_tab", text="Extensions Tab", toggle=True, icon=icon)
        if global_ucsm.use_script_tab:
            icon = "HIDE_OFF"
        else:
            icon = "HIDE_ON"
        box.prop(global_ucsm, "use_script_tab", text="Scripts Tab", toggle=True, icon=icon)
        box.prop(global_ucsm, "use_list", text="Use List", toggle=True, icon="ALIGN_LEFT")

class UCSM_Extensions(bpy.types.Panel):
    bl_parent_id = "UCSM_PT_setup_panel"
    bl_label = "Extensions"
    bl_idname = "UCSM_PT_extensions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw_header(self, context):
        """Optional: Draw the header of the panel."""
        self.layout.label(icon='SYSTEM')  # Example header icon

    @classmethod
    def poll(cls, context):
        global_ucsm = context.window_manager.ucsm

        return global_ucsm.use_extension_tab
    
    
    def draw(self, context):
        global_ucsm = context.window_manager.ucsm
        
        layout = self.layout
        if global_ucsm.templates == "NONE":
            layout.enabled = False

        layout.operator(UCSM_ExtensionsReload.bl_idname, text="Forced Reload All Extensions", icon="FILE_REFRESH")
        
        if global_ucsm.use_list:
            layout.template_list("UCSM_ExtensionsList", "", global_ucsm, "extensions_list", global_ucsm, "active_extensions_list")
        else:
            for ext in global_ucsm.extensions_list:
                box = layout.box()
                row = box.row(align=True)
                EXTENSIONS_LIST(row, ext)
        if global_ucsm.templates == "NONE":
            layout.enabled = False
        layout.operator(UCSM_ExtensionsAdd.bl_idname, text="Add Extension", icon="ADD")


class UCSM_Scripts(bpy.types.Panel):
    bl_parent_id = "UCSM_PT_setup_panel"
    bl_label = "Scripts"
    bl_idname = "UCSM_PT_scripts"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw_header(self, context):
        """Optional: Draw the header of the panel."""
        self.layout.label(icon='SCRIPT')  # Example header icon

    @classmethod
    def poll(cls, context):
        global_ucsm = context.window_manager.ucsm

        return global_ucsm.use_script_tab
    
    def draw(self, context):
        global_ucsm = context.window_manager.ucsm
        
        layout = self.layout

        if global_ucsm.use_list:
            layout.template_list("UCSM_ScriptsList", "", global_ucsm, "scripts_list", global_ucsm, "active_scripts_list")
        else:
            for script in global_ucsm.scripts_list:
                box = layout.box()
                row = box.row(align=True)
                if script.status:
                    row.prop(script, "status", text="", icon="TRIA_DOWN")
                else:
                    row.prop(script, "status", text="", icon="TRIA_RIGHT")
                SCRIPTS_LIST(row, script)
                
                if script.status:
                    ARGUMENTS_LIST(context, box, script)
                    
                    op = box.operator(UCSM_ScriptsArgsAdd.bl_idname, text="Add Argument", icon="ADD")
                    op.current_script = script.name


        if global_ucsm.templates == "NONE":
            layout.enabled = False
        layout.operator(UCSM_ScriptsAdd.bl_idname, text="Add Script", icon="ADD")

PanelClasses = [
    UCSM_ExtensionsList,
    UCSM_ScriptsList,
    UCSM_SetupPanel,
    UCSM_Extensions,
    UCSM_Scripts
]

# Operators

class UCSM_Test(bpy.types.Operator):
    bl_idname = "ucsm.test"
    bl_label = "Test"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        return {'FINISHED'}
    
class UCSM_TemplateAdd(bpy.types.Operator):
    """Add New Template File"""
    bl_idname = "ucsm.template_add"
    bl_label = "Add New Template"
    bl_options = {'REGISTER'}

    name: bpy.props.StringProperty(default="New Template")

    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        if global_ucsm.preferences.folder == "":
            self.report({'ERROR'}, "You have to set templates folder path!")
            return {'FINISHED'}
        
        data = {
            "scripts": [],
            "extensions": []
        }

        exportJson(context, data, self.name, is_new = True)

        global_ucsm.templates = self.name

        return {'FINISHED'}
    
    def draw(self, context):
        
        layout = self.layout

        layout.prop(self, "name", text="Name")

    
    def invoke(self, context, event):
        global_ucsm = context.window_manager.ucsm

        text_files = bpy.data.texts
        global_ucsm.local_extensions_list.clear()
        for tf in text_files:
            # Make sure it have correct format
            if "def main" in tf.as_string():
                item = global_ucsm.local_extensions_list.add()
                item.name = tf.name
                item.data_block = tf.name

        return context.window_manager.invoke_props_dialog(self)
 
class UCSM_TemplateDelete(bpy.types.Operator):
    """Delete Current Template File"""
    bl_idname = "ucsm.template_delete"
    bl_label = "Delete Current Template"
    bl_options = {'REGISTER'}

    name: bpy.props.StringProperty(default="New Template")

    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        if global_ucsm.preferences.folder == "":
            self.report({'ERROR'}, "You have to set templates folder path!")
            return {'FINISHED'}
        
        # set output path and file name (set your own)
        save_path = global_ucsm.preferences.folder
        file = os.path.join(save_path, global_ucsm.templates + ".json")

        # for item in global_ucsm.extensions_list:
        #     unregisterCurrentExtension(None, context, item.name)

        os.remove(file)

        global_ucsm.templates = "NONE"

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)

class UCSM_TemplateRename(bpy.types.Operator):
    """Rename Current Template File"""
    bl_idname = "ucsm.template_rename"
    bl_label = "Rename Current Template"
    bl_options = {'REGISTER'}

    current_name: bpy.props.StringProperty(default="Old Template")
    new_name: bpy.props.StringProperty(default="New Template")

    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        if global_ucsm.preferences.folder == "":
            self.report({'ERROR'}, "You have to set templates folder path!")
            return {'FINISHED'}
        
        save_path = global_ucsm.preferences.folder
        old_file = os.path.join(save_path, self.current_name + ".json")
        new_file = os.path.join(save_path, self.new_name + ".json")

        try:
            os.rename(old_file, new_file)
        except FileExistsError as e:
            self.report({'ERROR'}, "You have same name in other template! Use different name")

        return {'FINISHED'}
    
    def draw(self, context):
        
        layout = self.layout

        layout.prop(self, "new_name", text="New name")

    
    def invoke(self, context, event):
        global_ucsm = context.window_manager.ucsm

        self.current_name = global_ucsm.templates

        self.new_name = self.current_name

        return context.window_manager.invoke_props_dialog(self)

class UCSM_TemplateSave(bpy.types.Operator):
    """Save Current Template Changes"""
    bl_idname = "ucsm.template_save"
    bl_label = "Save Current Template Changes"
    
    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        if global_ucsm.templates != "NONE":

            data = dataToJson(global_ucsm.scripts_list, global_ucsm.extensions_list)

            exportJson(context, data, global_ucsm.templates)

        global_ucsm.is_save = False

        return {'FINISHED'}

class UCSM_ExtensionsAdd(bpy.types.Operator):
    """Add new extension"""
    bl_idname = "ucsm.extensions_add"
    bl_label = "Add new extension"

    is_global: bpy.props.BoolProperty(default=False)
    path: bpy.props.StringProperty(
        name="Path",
        description="Path to script",
        default="",
        subtype='FILE_PATH',
    )

    make_local: bpy.props.BoolProperty(default=False)

    temp: bpy.props.StringProperty()
    
    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        if self.path == "":
            self.report({'ERROR'}, "You need to choose path for your extension")
            return {'FINISHED'}

        if self.is_global:
            filename = os.path.basename(self.path)

            if ".py" not in filename:
                self.report({'ERROR'}, "You can use only .py files as extensions!")
                return {'FINISHED'}
            
            registerCurrentExtension(self, context, self.path, filename)
        else:
            filename = self.temp
            registerCurrentExtension(self, context, "", filename)
       
        global_ucsm.is_save = True

        return {'FINISHED'}
    
    def draw(self, context):
        global_ucsm = context.window_manager.ucsm
        local_ucsm = context.scene.ucsm
        
        layout = self.layout
        
        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "is_global", text="Local", toggle=True, invert_checkbox=True)
        row.prop(self, "is_global", text="Global",  toggle=True)

        if self.is_global:
            box = layout.box()        
            box.prop(self, "path", text="Path")
            box.prop(self, "make_local", text="Make this script local")
        else:
            box = layout.box()
            box.prop_search(self, "temp", global_ucsm ,"local_extensions_list")
            box.label(text=self.temp)

    def invoke(self, context, event):
        global_ucsm = context.window_manager.ucsm

        self.path = global_ucsm.preferences.folder

        text_files = bpy.data.texts
        global_ucsm.local_extensions_list.clear()
        for tf in text_files:
            # Make sure it have correct format
            if "def register" and "def unregister" in tf.as_string():
                item = global_ucsm.local_extensions_list.add()
                item.name = tf.name
                item.data_block = tf.name

        return context.window_manager.invoke_props_dialog(self)
   
class UCSM_ExtensionsRemove(bpy.types.Operator):
    """Remove Current Extension"""
    bl_idname = "ucsm.extensions_remove"
    bl_label = "Remove Current Extension"

    name: bpy.props.StringProperty(default="")
    
    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        unregisterCurrentExtension(self, context, self.name)

        global_ucsm.is_save = True
        return {'FINISHED'}

    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)
   
class UCSM_ExtensionsReload(bpy.types.Operator):
    """Forced Reload All Extension"""
    bl_idname = "ucsm.extensions_reload"
    bl_label = "Reload All Extension"
    
    def execute(self, context):
        global_ucsm = context.window_manager.ucsm
        
        _updateCurrentTemplateScripts(self, context)


        global_ucsm.is_save = False


        return {'FINISHED'}
   
class UCSM_ExtensionsReloadSingle(bpy.types.Operator):
    """Forced Reload Current Extension"""
    bl_idname = "ucsm.extensions_reload_single"
    bl_label = "Reload Current Extension"

    name: bpy.props.StringProperty(default="")
    
    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        item = global_ucsm.extensions_list.get(self.name)

        if item:
            reloadCurrentExtension(self, context, item.path, item.name)
        return {'FINISHED'}
    
class UCSM_ScriptsAdd(bpy.types.Operator):
    """Add New Script"""
    bl_idname = "ucsm.scripts_add"
    bl_label = "Add New Script"

    name: bpy.props.StringProperty(name="Button Name")

    description: bpy.props.StringProperty(name="Description")

    icon: bpy.props.StringProperty(name="Icon")

    is_global: bpy.props.BoolProperty(default=False)
    path: bpy.props.StringProperty(
        name="Path",
        description="Path to script",
        default="",
        subtype='FILE_PATH',
    )

    make_local: bpy.props.BoolProperty(default=False)

    temp: bpy.props.StringProperty()

    
    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        item = global_ucsm.scripts_list.add()

        item.name = self.name
        item.description = self.description
        if self.is_global:
            item.path = self.path
        else:
            item.path = ""

        item.icon = self.icon

        if not self.is_global:
            _temp = bpy.data.texts.get(self.temp)
            if _temp:
                item.data_block = _temp.name
            
        global_ucsm.is_save = True
        
        return {'FINISHED'}

    
    def draw(self, context):
        global_ucsm = context.window_manager.ucsm
        local_ucsm = context.scene.ucsm
        
        layout = self.layout
        box = layout.box()
        box.operator("iv.icons_show")
        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "is_global", text="Local", toggle=True, invert_checkbox=True)
        row.prop(self, "is_global", text="Global",  toggle=True)

        if self.is_global:
            box = layout.box()        
            box.prop(self, "path", text="Path")
            box.prop(self, "make_local", text="Make this script local")
        else:
            box = layout.box()
            box.prop_search(self, "temp", global_ucsm ,"local_extensions_list")
            box.label(text=self.temp)\
        
        box.prop(self, "name")
        box.prop(self, "description")
        box.prop(self, "icon")

    def invoke(self, context, event):
        global_ucsm = context.window_manager.ucsm

        self.path = global_ucsm.preferences.folder

        text_files = bpy.data.texts
        global_ucsm.local_extensions_list.clear()
        for tf in text_files:
            # Make sure it have correct format
            if "def main" in tf.as_string():
                item = global_ucsm.local_extensions_list.add()
                item.name = tf.name
                item.data_block = tf.name

        return context.window_manager.invoke_props_dialog(self)

class UCSM_ScriptsDelete(bpy.types.Operator):
    """Delete Current Script"""
    bl_idname = "ucsm.scripts_delete"
    bl_label = "Delete Current Script"

    name: bpy.props.StringProperty()

    def execute(self, context):
        
        global_ucsm = context.window_manager.ucsm

        index = global_ucsm.scripts_list.find(self.name)

        global_ucsm.scripts_list.remove(index)

        global_ucsm.is_save = True

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)

class UCSM_ScriptsEdit(bpy.types.Operator):
    """Edit Current Script"""
    bl_idname = "ucsm.scripts_edit"
    bl_label = "Edit Current Script"

    name: bpy.props.StringProperty(name="Button Name")

    description: bpy.props.StringProperty(name="Description")

    icon: bpy.props.StringProperty(name="Icon")

    is_global: bpy.props.BoolProperty(default=False)
    path: bpy.props.StringProperty(
        name="Path",
        description="Path to script",
        default="",
        subtype='FILE_PATH',
    )

    make_local: bpy.props.BoolProperty(default=False)

    temp: bpy.props.StringProperty()

    
    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        item = global_ucsm.scripts_list.get(self.name)

        if item:

            item.name = self.name
            item.description = self.description
            if self.is_global:
                item.path = self.path
            else:
                item.path = ""
            item.icon = self.icon

            if not self.is_global:
                _temp = bpy.data.texts.get(self.temp)
                if _temp:
                    item.data_block = _temp.name
                
            global_ucsm.is_save = True
        
        return {'FINISHED'}

    
    def draw(self, context):
        global_ucsm = context.window_manager.ucsm
        local_ucsm = context.scene.ucsm
        
        layout = self.layout
        box = layout.box()
        box.operator("iv.icons_show")

        if self.is_global:
            box = layout.box()        
            box.prop(self, "path", text="Path")
            box.prop(self, "make_local", text="Make this script local")
        else:
            box = layout.box()
            box.prop_search(self, "temp", global_ucsm ,"local_extensions_list")
            box.label(text=self.temp)\
        
        box.prop(self, "name")
        box.prop(self, "description")
        box.prop(self, "icon")

    def invoke(self, context, event):
        global_ucsm = context.window_manager.ucsm

        self.path = global_ucsm.preferences.folder

        text_files = bpy.data.texts
        global_ucsm.local_extensions_list.clear()
        for tf in text_files:
            # Make sure it have correct format
            if "def main" in tf.as_string():
                item = global_ucsm.local_extensions_list.add()
                item.name = tf.name
                item.data_block = tf.name
                
        return context.window_manager.invoke_props_dialog(self)

class UCSM_ScriptsArgsAdd(bpy.types.Operator):
    """Add Arguments to Current Script"""
    bl_idname = "ucsm.scripts_arguments_add"
    bl_label = "Add Arguments to Current Script"
    
    current_script: bpy.props.StringProperty()

    name: bpy.props.StringProperty(name="Name")

    description: bpy.props.StringProperty(name="Args Description")

    type: bpy.props.EnumProperty(name="Type", items=PROPERTY_var_types)
    
    value: bpy.props.StringProperty(name="Object Name", default="0")

    
    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        if self.type == "CUSTOM":
            self.value = context.active_object.name
        if self.type == "CUSTOM_SELF":
            self.value = ""
                
        script = global_ucsm.scripts_list.get(self.current_script)
        args = script.args
        
        arg = args.add()
        
        arg.name = self.name
        arg.description = self.description
        arg.type = self.type
        
        varType = getVarType(PROPERTY_var_types, self.type)
        key = varType[0]
        index = varType[1]

        value = self.value
        
        if value == 0 or value == "0":
            value = PROPERTY_var_default_value[index]
        
        arg[key] = value


        global_ucsm.is_save = True
        
        return {'FINISHED'}

    
    def draw(self, context):
        
        layout = self.layout
        box = layout.box()
        
        if "CUSTOM" in self.type:
            box.prop(self, "name", text="Ignore Properties", placeholder="Prop1;Prop2;Prop3;")
        else:
            box.prop(self, "name", text="Name")
        box.prop(self, "description", text="Description")
        box.prop(self, "type", text="Type")
        
        if self.type == "CUSTOM":
            box.prop(context.scene.CSM, "activeObject", text="Object")

    def invoke(self, context, event):
                
        return context.window_manager.invoke_props_dialog(self)

class UCSM_ScriptsArgsEdit(bpy.types.Operator):
    """Edit Argument of Current Script"""
    bl_idname = "ucsm.scripts_arguments_edit"
    bl_label = "Edit Argument of Current Script"
    
    current_script: bpy.props.StringProperty()
    current_argument: bpy.props.StringProperty()

    name: bpy.props.StringProperty(name="Name")

    description: bpy.props.StringProperty(name="Args Description")

    type: bpy.props.EnumProperty(name="Type", items=PROPERTY_var_types)
    
    value: bpy.props.CollectionProperty(type=UCSM_ScriptsArguments, options={'HIDDEN'})
    
    def execute(self, context):
        global_ucsm = context.window_manager.ucsm

        if self.type == "CUSTOM":
            self.value[0].custom = context.active_object.name
        if self.type == "CUSTOM_SELF":
            self.value[0].custom = ""
                
        script = global_ucsm.scripts_list.get(self.current_script)
        args = script.args
        
        arg = args.get(self.current_argument)
        
        arg.name = self.name
        arg.description = self.description
        arg.type = self.type
        
        varType = getVarType(PROPERTY_var_types, self.type)
        key = varType[0]
        index = varType[1]

        value = self.value[0]
        
        if value == 0 or value == "0":
            value = PROPERTY_var_default_value[index]
        
        arg[key] = value[key]


        global_ucsm.is_save = True
        
        return {'FINISHED'}

    
    def draw(self, context):
        
        layout = self.layout
        box = layout.box()
        
        if "CUSTOM" in self.type:
            box.prop(self, "name", text="Ignore Properties", placeholder="Prop1;Prop2;Prop3;")
        else:
            box.prop(self, "name", text="Name")
        box.prop(self, "description", text="Description")
        box.prop(self, "type", text="Type")
        
        if self.type == "CUSTOM":
            box.prop(context.scene.CSM, "activeObject", text="Object")

    def invoke(self, context, event):
                
        return context.window_manager.invoke_props_dialog(self)

class UCSM_ScriptsArgsDelete(bpy.types.Operator):
    """Delete Current Arg"""
    bl_idname = "ucsm.scripts_args_delete"
    bl_label = "Delete Current Arg"

    current_script: bpy.props.StringProperty()
    current_argument: bpy.props.StringProperty()

    def execute(self, context):
        
        global_ucsm = context.window_manager.ucsm

        script = global_ucsm.scripts_list.get(self.current_script)

        index = script.args.find(self.current_argument)

        script.args.remove(index)

        global_ucsm.is_save = True

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)


class UCSM_ScriptExecute(bpy.types.Operator):
    """Execute Current Script"""
    bl_idname = "ucsm.script_execute"
    bl_label = "Execute Current Script"



    name: bpy.props.StringProperty()
    data_block: bpy.props.StringProperty()

    path: bpy.props.StringProperty(
        name="Path",
        description="Path to script",
        default="",
        subtype='FILE_PATH',
    )

    props: bpy.props.CollectionProperty(type=UCSM_ScriptsArguments)

    def execute(self, context):

        global_ucsm = context.window_manager.ucsm

        current_save_status = global_ucsm.is_save
                
        script = global_ucsm.scripts_list.get(self.name)
        
        for arg in script.args:
            ap = self.props.add()
            ap.name = arg.name
            ap.description = arg.description
            ap.type = arg.type
            
            key = getVarType(PROPERTY_var_types, arg.type)[0]
            
            ap[key] = arg[key]
        
        status = executeScript(self.props, self.path, self.data_block)

         
        self.report(status[0], status[1])
        self.props.clear()

        global_ucsm.is_save = current_save_status

        return {'FINISHED'}


OperatorClasses = [
    UCSM_Test,
    UCSM_TemplateAdd,
    UCSM_TemplateDelete,
    UCSM_TemplateRename,
    UCSM_TemplateSave,
    UCSM_ExtensionsAdd,
    UCSM_ExtensionsRemove,
    UCSM_ExtensionsReload,
    UCSM_ExtensionsReloadSingle,
    UCSM_ScriptsAdd,
    UCSM_ScriptsDelete,
    UCSM_ScriptsEdit,
    UCSM_ScriptsArgsAdd,
    UCSM_ScriptsArgsEdit,
    UCSM_ScriptsArgsDelete,
    UCSM_ScriptExecute,
]


# Initialization Classes
UsesClasses = []

UsesClasses.extend(PropsClasses)
UsesClasses.extend(OperatorClasses)
UsesClasses.extend(PanelClasses)



# Handler for Event
event_handler = object()

def subscribe_window_manager():
    
    # Triggers when window's workspace is changed
    subscribe_to = bpy.types.Window, "workspace"

    def change_template(context):
        _updateCurrentTemplateScripts(None, bpy.context)
        return None
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=event_handler,
        args=(bpy.context,),
        notify=change_template,
    )
    bpy.msgbus.publish_rna(key=subscribe_to)

# Register Classes
def register():

    for useClass in UsesClasses:
        bpy.utils.register_class(useClass)
    
    setProperties()

    # subscribe_window_manager()

def unregister():    
    
    for useClass in UsesClasses:
        bpy.utils.unregister_class(useClass)

    delProperties()

