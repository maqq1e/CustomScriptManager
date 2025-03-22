import bpy, json, os, sys, importlib, inspect

from ..App.Datas import *

####### DATAS #######

def getListOfScripts(self, context):
    """Get all scripts from preferences script directory folder"""
    
    PREFERENCES = context.scene.CSM.preferences

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

# Init in Preferences Changes
def EXT_updateAllProperties(self, context):
    
    PREFERENCES = context.scene.CSM.preferences
    script_dir = PREFERENCES.script_dir
    
    if script_dir == "":
        return None
    
    # Set Json Template Files
    context.scene.CSM.templatesFilesCollection.clear() # Clear list of all .json files
    EXT_loadTemplatesFilesList(context, script_dir) # Load .json template files list
    if len(context.scene.CSM.templatesFilesCollection) > 0:
        context.scene.CSM.templateFileName = context.scene.CSM.templatesFilesCollection[0].name

# Init in Template File Changes
def EXT_updateDatabaseProperties(self, context):
    
    PREFERENCES = context.scene.CSM.preferences
    script_dir = PREFERENCES.script_dir
    
    if script_dir == "":
        return None
    
    context.scene.CSM.database.clear() # Clear list of all templates data
    
    file_name = context.scene.CSM.templateFileName
    data_list = EXT_jsonImport(script_dir, file_name)
    templates_list = data_list['templates']
    
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
    
    if len(context.scene.CSM.database) > 0:
        context.workspace.CSM_TemplateName = context.scene.CSM.database[0].name
    
    context.scene.CSM.isSave = False

def EXT_updateTemplateProperties(self, context):
    
    PREFERENCES = context.scene.CSM.preferences
    script_dir = PREFERENCES.script_dir
    
    stack = context.scene.CSM.stack
    
    ### Unregister all extensions
    for ext in stack:
        result = CMP_unregisterCurrentExtension(context, ext.name)
        try:
            self.report(result[0], result[1])
        except Exception as e:
            continue
    
    stack.clear()
    
    ### Register all extensions
    if len(context.scene.CSM.database) > 0:
        template_index = context.workspace.CSM_TemplateName
        
        template_extensions = context.scene.CSM.database[template_index].extensions
        
        for ext in template_extensions:
            script = EXT_loadScriptAsSctring(script_dir, ext.name) # Load script
            
            
            script_context = {}
            
            exec(script, script_context)
            
            if script_context.get("register") == None or script_context.get("unregister") == None:
                self.report({'ERROR'}, 'You have no register and unregister functions inside ' + ext.name)
                return None
            else:
                extension = context.scene.CSM.stack.add()
                
                extension.name = ext.name
                try:
                    script_context['register']()
                except Exception as e:
                    self.report({'ERROR'}, f"Error running register in {ext.name}: {e}")
                
                extension.script['unregister'] = script_context['unregister']

def EXT_updateGlobalExtensions(self, context):
    
    
    PREFERENCES = context.scene.CSM.preferences
    script_dir = PREFERENCES.script_dir
    
    ### Register all extensions
    if len(PREFERENCES.globalExtensionsStack) > 0:    
        
        for ext in PREFERENCES.globalExtensionsStack:
            script = EXT_loadScriptAsSctring(script_dir, ext.name) # Load script
            
            
            script_context = {}
            
            exec(script, script_context)
            
            if script_context.get("register") == None or script_context.get("unregister") == None:
                self.report({'ERROR'}, 'You have no register and unregister functions inside ' + ext.name)
                return None
            else:
                try:
                    script_context['register']()
                except Exception as e:
                    self.report({'ERROR'}, f"Error running register in {ext.name}: {e}")
                
                ext.script['unregister'] = script_context['unregister']    
            
def EXT_loadTemplatesFilesList(context, script_dir):
    for filename in os.listdir(script_dir):
        # Check if the file ends with .json (Python files)
        if filename.endswith(".json"):
            CMP_addTemplatesFiles(context, filename)

### JSON Data Control
def EXT_serializeDict(templates):

    result = {
        "templates": []
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
            for extension in el["extensions"]:
                
                extensions_data.append({
                    "name": extension["name"],
                })
            


        result['templates'].append({
            "name": el["name"],
            "scripts": scripts_data,
            "extensions": extensions_data
        })


    return result

def EXT_jsonImport(path, file_name):
    # set output path and file name (set your own)
    save_path = path
    file_name = os.path.join(save_path, file_name + ".json")

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
    file = os.path.join(save_path, file_name + ".json")

    # write JSON file
    with open(file, 'w') as outfile:
        outfile.write(payload + '\n')
        
    if isNew:
        context = bpy.context
        CMP_addTemplatesFiles(context, file_name + ".json") # Add in CSM_TemplatesFilesList
        context.scene.CSM.templateFileName = file_name
        
def EXT_deleteFile(path, file_name, format = ".json"):
    file = os.path.join(path, file_name + format)
    
    CMP_removeTemplatesFiles(bpy.context, file_name)
    
    os.remove(file)

def EXT_renameFile(path, file_name, new_name, extension):
    old_name = os.path.join(path, file_name) + extension
    new_name = os.path.join(path, new_name) + extension
    os.rename(old_name, new_name)

def EXT_checkFileExist(path, file_name, format = ".json"):
    file = os.path.join(path, file_name + format)
    
    return os.path.isfile(file)

def EXT_loadScript(filepath):
    # Dynamically import and execute the script
    spec = importlib.util.spec_from_file_location("module.name", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

### Scrirt Execution
def EXT_executeScript(props, filepath):
    
    module = EXT_loadScript(filepath)

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

def EXT_loadScriptAsSctring(filepath, fileName):
    
    # Full path to the .py file
    py_file_path = os.path.join(filepath, fileName)
    # Ensure the path is in Python's system path
    if filepath not in sys.path:
        sys.path.append(filepath)
    
    try:
        # Open the file and read its content
        with open(py_file_path, 'r', encoding='utf-8') as file:
            script_content = file.read()
    except ImportError as e:
        print(f"Error importing module: {e}")
        script_content = None
        
    
    return script_content

def EXT_loadProperties(filepath, fileName):
    # Load the external script
    
    external_module = EXT_loadScript(filepath + fileName)
    
    # Execute the register() method
    if hasattr(external_module, "register"):
        external_module.register()
        print("register() executed.")
    else:
        print("No register() method found in the external script.")
    
    # Store the unregister method as a string in a Blender property
    if hasattr(external_module, "unregister"):
        unregister_string = inspect.getsource(external_module.unregister)
        unregister_string = unregister_string[unregister_string.find("\n") + 1:]
        unregister_string = unregister_string.replace("    ", "")
        return unregister_string
    else:
        print("No unregister() method found in the external script.")

def EXT_registerClass(ext_cls):
    try:
        bpy.utils.register_class(ext_cls)
    except RuntimeError as e:
        print(f"Error unregistering class {ext_cls.bl_idname}: {e}")

def EXT_unregisterClass(ext_cls):
    # Check if the class exists in bpy.types (where all Blender classes are registered)
    
    _cls = getattr(bpy.types, ext_cls, None)
        
    # If the class exists, try to unregister it
    if _cls:
        try:
            bpy.utils.unregister_class(_cls)
        except RuntimeError as e:
            print(f"Error unregistering class {ext_cls}: {e}")
    else:
        print(f"Class {ext_cls} not found in bpy.types")

####### COMPONENTS #######

### Extensions Control
def CMP_addExtension(context, template_index, name):
    template = context.scene.CSM.database[template_index]
    extension = template.extensions.add()
    
    extension.name = name
    
def CMP_addGloablExtension(context, name):
    extension = context.scene.CSM.preferences.globalExtensionsStack.add()
    
    extension.name = name
    
def CMP_removeExtension(context, template_index, extension_index):
    if len(context.scene.CSM.database[template_index].extensions) > 0:
        context.scene.CSM.database[template_index].extensions.remove(extension_index)

def CMP_unregisterCurrentExtension(context, current_extension):
    
    try:
        index = context.scene.CSM.stack.find(current_extension)
        
        extension = context.scene.CSM.stack[index]
    
        extension.script['unregister']()
    except Exception as e:
        context.scene.CSM.stack.remove(index) 
        return [{'ERROR'}, f"Error while unregister in {current_extension}: {e}"]
    
    context.scene.CSM.stack.remove(index)    
    return [{'INFO'}, f"Success unregister " + current_extension + " extension."]


def CMP_unregisterGlobalExtension(context, index):
    PREFERENCES = context.scene.CSM.preferences
    
    extension = PREFERENCES.globalExtensionsStack[index]
    
    try:
    
        extension.script['unregister']()
    except Exception as e:
        PREFERENCES.globalExtensionsStack.remove(index) 
        return [{'ERROR'}, f"Error while unregister in {extension.name}: {e}"]
    
    PREFERENCES.globalExtensionsStack.remove(index)    
    return [{'INFO'}, f"Success unregister " + extension.name + " extension."]

     
### Templates Control
def CMP_addTemplate(context, new_name = "New Template"):

    if new_name == "New Template":
        if len(context.scene.CSM.database) > 0:
            new_name = context.scene.CSM.database[-1].name + " 1"
        
    template = context.scene.CSM.database.add()

    template.name = new_name

    context.workspace.CSM_TemplateName = template.name

def CMP_removeTemplate(context, index):
    if len(context.scene.CSM.database) > 0:
            context.scene.CSM.database.remove(index)
            
    if len(context.scene.CSM.database) > 0:
        bpy.context.workspace.CSM_TemplateName = bpy.context.scene.CSM.database[0].name

def CMP_editTemplate(context, template_index, name):
    template = context.scene.CSM.database[template_index]
    template.name = name

def CMP_addTemplatesFiles(context, new_name):
    templateFile = context.scene.CSM.templatesFilesCollection.add()
    templateFile.name = new_name[0:new_name.find(".json")]

def CMP_removeTemplatesFiles(context, name):
    if len(context.scene.CSM.templatesFilesCollection) > 0:
        index = context.scene.CSM.templatesFilesCollection.find(name)
        context.scene.CSM.templatesFilesCollection.remove(index)

### Scripts Control
def CMP_addScript(context, template_index, name = "Test", description = "Test Do", icon = "PREFERENCES", path = "Test.py", status=False):
    template = context.scene.CSM.database[template_index]
    script = template.scripts.add()

    script.name = name
    script.description = description
    script.icon = icon
    script.path = path
    script.status = status

def CMP_removeScript(context, template_index, script_index):
    if len(context.scene.CSM.database[template_index].scripts) > 0:
        context.scene.CSM.database[template_index].scripts.remove(script_index)
 
def CMP_editScript(context, template_index, script_index, name = "Test", description = "Test Do", icon = "PREFERENCES", path = "Test.py"):
    template = context.scene.CSM.database[template_index]
    script = template.scripts[script_index]

    script.name = name
    script.description = description
    script.icon = icon
    script.path = path

### Arguments Control
def CMP_addArgs(context, template_index, script_index, type, name = "Test Arg", description = "Test Arg Do", value=0):
    template = context.scene.CSM.database[template_index]
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
    template = context.scene.CSM.database[template_index]
    script = template.scripts[script_index]
    arg = script.args[arg_index]
    
    arg.name = name
    arg.description = description
    arg.type = type
    
    key = EXT_getVarType(PROPERTY_var_types, type)[0]
        
    arg[key] = value[key]

def CMP_removeArgs(context, template_index, script_index, arg_index):
    template = context.scene.CSM.database[template_index]
    script = template.scripts[script_index]
    script.args.remove(arg_index)

