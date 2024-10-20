import bpy, json, os, sys, importlib, inspect

from ..Defers.Layouts import getPreferences
from ..App.Datas import *

####### DATAS #######

def makeTemplateSave(self, context):
    context.scene.BSM_isSave = True

def getTemplatesFiles(self, context):
    
    Enum_items = []
    for templateFile in context.scene.BSM_TemplatesFilesList_collection:
        data = str(templateFile.name)
        item = (data, data, data)
        Enum_items.append(item)
        
    return Enum_items

def getListOfScripts(self, context):
    """Get all scripts from preferences script directory folder"""
    
    PREFERENCES = getPreferences()

    directory = PREFERENCES.script_dir
    
    Enum_items = []
    
    for filename in os.listdir(directory):
        # Check if the file ends with .py (Python files)
            if filename.endswith(".py"):
                data = filename
                item = (data, data, data)
                # Print the file name
                Enum_items.append(item)
        
    return Enum_items

# Templates Component

def getTemplateItems(self, context):
    
    Enum_items = []
    
    for template_item in context.scene.BSM_Templates_collection:
        
        data = str(template_item.name)
        item = (data, data, data)
        
        Enum_items.append(item)
        
    return Enum_items   

def changeTemplateExtensions(self, context):
    CMP_registerTemplateExtensions(context, self.BSM_Templates)
    
####### EXTERNAL #######

### GLOBALS Variables Control

def EXT_getVarType(types, id_type):
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

def EXT_loadDatas(self, context):
    
    PREFERENCES = getPreferences()
    
    script_dir = PREFERENCES.script_dir
    
    context.scene.BSM_TemplatesFilesList_collection.clear()
    
    for filename in os.listdir(PREFERENCES.script_dir):
        # Check if the file ends with .json (Python files)
        if filename.endswith(".json"):
            CMP_addTemplatesFiles(context, filename)
    
    if len(context.scene.BSM_TemplatesFilesList_collection) > 0:
        if context.scene.BSM_TemplatesFilesList == "":
            context.scene.BSM_TemplatesFilesList = context.scene.BSM_TemplatesFilesList_collection[0]
    else:
        return None
    
    templates_name = context.scene.BSM_TemplatesFilesList
    templates_list = EXT_jsonImport(script_dir, templates_name)
    extensions_list = templates_list['extensions']
    templates_list = templates_list['templates']
    
    context.scene.BSM_Templates_collection.clear()
    context.scene.BSM_Extensions_collection.clear()
    
    # Get List Item Index
    template_index = 0
    script_index = 0
    
    for template in templates_list:
        CMP_addTemplate(context, template['name'])
        for script in template['scripts']:
            status = True if script["status"] == 1 else False
            CMP_addScript(context, template_index, 
                        script['name'], 
                        script['description'], 
                        script['icon'], 
                        script['path'], 
                        status)
            for arg in script['args']:
                CMP_addArgs(context, template_index, script_index,
                        arg['type'], 
                        arg['name'], 
                        arg['description'], 
                        arg['value'])
            
            script_index = script_index + 1 # Increment Index 
        
        for extension in template['extensions']:
            CMP_addExtension(context, template_index,
                            extension['name'])
        
        script_index = 0
        template_index = template_index + 1 # Increment Index 
    
    for ext in extensions_list:
        CMP_addGlobalExtension(context, ext['name'])
    
    context.scene.BSM_isSave = False

def EXT_clearProperties(self, context):
    
    PREFERENCES = getPreferences()
    
    CMP_unregisterExtensions(bpy.context, PREFERENCES.script_dir)
    EXT_loadDatas(self, bpy.context)
    CMP_registerTemplateExtensions(context, context.workspace.BSM_Templates)

### JSON Data Control

def EXT_serializeDict(templates, ext_data):

    result = {
        "templates": [],
        "extensions": []
    }

    for el in templates:

        scripts_data = []

        if len(el.scripts) > 0:
            for script in el["scripts"]:
                
                arg_data = []
                
                if script.get("args") != None:
                    for arg in script['args']:
                        
                        key = EXT_getVarType(PROPERTY_var_types, arg['type'])[0]
                        
                        value = arg[key]      
                        
                        arg_data.append({
                            "name": arg['name'],
                            "description": arg['description'],
                            "type": arg['type'],
                            "value": value
                        })
                
                scripts_data.append({
                    "name": script["name"],
                    "description": script["description"],
                    "icon": script["icon"],
                    "path": script["path"],
                    "status": script['status'],
                    "args": arg_data
                })

        extensions_data = []
        
        if len(el.extensions) > 0:
            for extensions in el["extensions"]:
                
                extensions_data.append({
                    "name": extensions["name"],
                })
            


        result['templates'].append({
            "name": el["name"],
            "scripts": scripts_data,
            "extensions": extensions_data
        })

    for el in ext_data:
        result['extensions'].append({
            "name": el["name"]
        })


    return result

def EXT_jsonImport(path, file_name):
    # set output path and file name (set your own)
    save_path = path
    file_name = os.path.join(save_path, file_name)

    # 2 - Import data from JSON file
    variable = {}

    # read JSON file
    with open(file_name, 'r') as f:
        variable = json.load(f)

    return variable

def EXT_jsonExport(path, file_name, data, isNew = False):
    # encode dict as JSON 
    payload = json.dumps(data, indent=1, ensure_ascii=True)

    # set output path and file name (set your own)
    save_path = path
    file = os.path.join(save_path, file_name)

    # write JSON file
    with open(file, 'w') as outfile:
        outfile.write(payload + '\n')
        
    if isNew:
        CMP_addTemplatesFiles(bpy.context, file_name)

def EXT_deleteFile(path, file_name):
    file = os.path.join(path, file_name)
    
    CMP_removeTemplatesFiles(bpy.context, file_name)
    
    os.remove(file)

def EXT_renameFile(path, file_name, new_name, extension):
    old_name = os.path.join(path, file_name) + extension
    new_name = os.path.join(path, new_name) + extension
    os.rename(old_name, new_name)

def EXT_checkFileExist(path, file_name):
    file = os.path.join(path, file_name)
    
    return os.path.isfile(file)

### Scrirt Execution

def EXT_executeScript(props, filepath):
    # Dynamically import and execute the script
    spec = importlib.util.spec_from_file_location("module.name", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Init Props value for script
    args = {}
    for prop in props:
        # Basic Properties or Cusom Object Properties
        key = EXT_getVarType(PROPERTY_var_types, prop.type)[0]
        
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
            
        
        args.update({prop_name: value})
        
    # Assuming there's a function named 'main' in each script
    if hasattr(module, "main"):
        try:                
            module.main(args)  # Execute the 'main' function
            return [{'INFO'}, "Scripts executed"]
        except Exception as e:
            return [{'ERROR'}, f"Error running main() in {filepath}: {e}"]
        
def EXT_registerClass(filepath, fileName, isUnregister=False):
    # Full path to the .py file
    py_file_path = os.path.join(filepath, fileName)
    # Ensure the path is in Python's system path
    if filepath not in sys.path:
        sys.path.append(filepath)
        
    # Remove the .py extension from the filename to import the module
    module_name = os.path.splitext(fileName)[0]
    
    # Try to import the module dynamically
    try:
        module = importlib.import_module(module_name)
        importlib.reload(module)  # Reload the module in case it was already loaded
    except ImportError as e:
        print(f"Error importing module: {e}")
        module = None
        
    # If the module was successfully imported, inspect it to find all classes
    classes = []
    if module:
        # Iterate through the members of the module and filter out classes
        for name, obj in inspect.getmembers(module):
            # Check if the object is a class and a subclass of bpy.types.Operator or bpy.types.Panel
            if inspect.isclass(obj) and (issubclass(obj, bpy.types.Operator) or issubclass(obj, bpy.types.Panel)):
                classes.append(obj)

    if isUnregister:
        for cls in classes:
            # Check if the class exists in bpy.types (where all Blender classes are registered)
            _cls = getattr(bpy.types, cls.bl_idname, None)
            
            # If the class exists, try to unregister it
            if _cls:
                try:
                    bpy.utils.unregister_class(_cls)
                except RuntimeError as e:
                    print(f"Error unregistering class {cls.bl_idname}: {e}")
            else:
                print(f"Class {cls.bl_idname} not found in bpy.types")
    else:
        for cls in classes:
            bpy.utils.register_class(cls)

####### COMPONENTS #######

### Extensions Control

def CMP_addGlobalExtension(context, name):
    extension = context.scene.BSM_Extensions_collection.add()
    extension.name = name

def CMP_removeGlobalExtension(context, extension_index):
    if len(context.scene.BSM_Extensions_collection) > 0:
        context.scene.BSM_Extensions_collection.remove(extension_index)

def CMP_addExtension(context, template_index, name):
    template = context.scene.BSM_Templates_collection[template_index]
    extension = template.extensions.add()
    
    extension.name = name
    
def CMP_removeExtension(context, template_index, extension_index):
    if len(context.scene.BSM_Templates_collection[template_index].extensions) > 0:
        context.scene.BSM_Templates_collection[template_index].extensions.remove(extension_index)
    
def CMP_changeExtensionStatus(context, template_name, extensions_name):
    extension = context.scene.BSM_Extensions_collection[extensions_name]
    
    extension.status = not extension.status
    
    template = context.scene.BSM_Templates_collection[template_name]
    
    ext_index = template.extensions.find(extensions_name)
    
    if ext_index != -1:
        if not extension.status:
            template.extensions.remove(ext_index)
    else:
        ext = template.extensions.add()
        ext.name = extensions_name

def CMP_registerTemplateExtensions(context, template_index):    
    PREFERENCES = getPreferences()
    
    CMP_unregisterExtensions(context, PREFERENCES.script_dir)
    
    extensions_collection = context.scene.BSM_Extensions_collection
    
    if template_index == "":
        return None
    
    template_extensions = context.scene.BSM_Templates_collection[template_index].extensions
    
    for ext in template_extensions:
        extensions_collection[ext.name].status = True
        EXT_registerClass(PREFERENCES.script_dir, ext.name) # Register Classes

def CMP_unregisterExtensions(context, script_dir):
    
    extensions_collection = context.scene.BSM_Extensions_collection
    
    for ext in extensions_collection:
        ext.status = False
        EXT_registerClass(script_dir, ext.name, True) # Unregister Classes
    
### Templates Control

def CMP_addTemplate(context, new_name = "New Template"):

    if new_name == "New Template":
        if len(context.scene.BSM_Templates_collection) > 0:
            new_name = context.scene.BSM_Templates_collection[-1].name + " 1"
        
    template = context.scene.BSM_Templates_collection.add()

    template.name = new_name

    context.workspace.BSM_Templates = template.name

def CMP_removeTemplate(context, index):
    if len(context.scene.BSM_Templates_collection) > 0:
            context.scene.BSM_Templates_collection.remove(index)
            
    if len(context.scene.BSM_Templates_collection) > 0:
        bpy.context.workspace.BSM_Templates = bpy.context.scene.BSM_Templates_collection[0].name

def CMP_editTemplate(context, template_index, name):
    template = context.scene.BSM_Templates_collection[template_index]
    template.name = name

def CMP_addTemplatesFiles(context, new_name):
        
    templateFile = context.scene.BSM_TemplatesFilesList_collection.add()

    templateFile.name = new_name

def CMP_removeTemplatesFiles(context, name):
    if len(context.scene.BSM_TemplatesFilesList_collection) > 0:
        index = context.scene.BSM_TemplatesFilesList_collection.find(name)
        context.scene.BSM_TemplatesFilesList_collection.remove(index)

### Scripts Control

def CMP_addScript(context, template_index, name = "Test", description = "Test Do", icon = "PREFERENCES", path = "Test.py", status=False):
    template = context.scene.BSM_Templates_collection[template_index]
    script = template.scripts.add()

    script.name = name
    script.description = description
    script.icon = icon
    script.path = path
    script.status = status

def CMP_removeScript(context, template_index, script_index):

    if len(context.scene.BSM_Templates_collection[template_index].scripts) > 0:
        context.scene.BSM_Templates_collection[template_index].scripts.remove(script_index)
 
def CMP_editScript(context, template_index, script_index, name = "Test", description = "Test Do", icon = "PREFERENCES", path = "Test.py"):
    template = context.scene.BSM_Templates_collection[template_index]
    script = template.scripts[script_index]

    script.name = name
    script.description = description
    script.icon = icon
    script.path = path

### Arguments Control
    
def CMP_addArgs(context, template_index, script_index, type, name = "Test Arg", description = "Test Arg Do", value=0):
    template = context.scene.BSM_Templates_collection[template_index]
    script = template.scripts[script_index]
    args = script.args
    
    arg = args.add()
    
    arg.name = name
    arg.description = description
    arg.type = type
    
    varType = EXT_getVarType(PROPERTY_var_types, type)
    key = varType[0]
    index = varType[1]
    
    if value == 0 or value == "0":
        value = PROPERTY_var_default_value[index]
    
    arg[key] = value
    
def CMP_editArgs(context, template_index, script_index, arg_index, type, name = "Test Arg", description = "Test Arg Do", value=0):
    template = context.scene.BSM_Templates_collection[template_index]
    script = template.scripts[script_index]
    arg = script.args[arg_index]
    
    arg.name = name
    arg.description = description
    arg.type = type
    
    key = EXT_getVarType(PROPERTY_var_types, type)[0]
        
    arg[key] = value[key]
    
def CMP_removeArgs(context, template_index, script_index, arg_index):
    template = context.scene.BSM_Templates_collection[template_index]
    script = template.scripts[script_index]
    script.args.remove(arg_index)
