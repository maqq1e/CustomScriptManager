import bpy, json, os
from .GLOBAL import var_types,var_default_value

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

def serializeDict(data):

    result = {
        "templates": []
    }

    for el in data:

        scripts_data = []

        if len(el.scripts) > 0:
            for script in el["scripts"]:
                
                arg_data = []
                
                for arg in script['args']:
                    
                    key = getVarType(var_types, arg['type'])[0]
                    
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

        result['templates'].append({
            "name": el["name"],
            "scripts": scripts_data
        })


    return result

def jsonImport(path, file_name):
    # set output path and file name (set your own)
    save_path = path
    file_name = os.path.join(save_path, file_name)

    # 2 - Import data from JSON file
    variable = {}

    # read JSON file
    with open(file_name, 'r') as f:
        variable = json.load(f)

    return variable

def jsonExport(path, file_name, data):
    # encode dict as JSON 
    payload = json.dumps(data, indent=1, ensure_ascii=True)

    # set output path and file name (set your own)
    save_path = path
    file_name = os.path.join(save_path, file_name)

    # write JSON file
    with open(file_name, 'w') as outfile:
        outfile.write(payload + '\n')

def addTemplate(context, new_name = "New Template"):

    if new_name == "New Template":
        if len(context.scene.templates_collection) > 0:
            new_name = context.scene.templates_collection[-1].name + " 1"
        
    template = context.scene.templates_collection.add()

    template.name = new_name

    context.scene.Templates = template.name

def removeTemplate(context, index):
    if len(context.scene.templates_collection) > 0:
            context.scene.templates_collection.remove(index)
            
    if len(context.scene.templates_collection) > 0:
        bpy.context.scene.Templates = bpy.context.scene.templates_collection[0].name

def addScript(context, template_index, name = "Test", description = "Test Do", icon = "PREFERENCES", path = "Test.py", status=False):
    template = context.scene.templates_collection[template_index]
    script = template.scripts.add()

    script.name = name
    script.description = description
    script.icon = icon
    script.path = path
    script.status = status

def removeScript(context, template_index, script_index):

    if len(context.scene.templates_collection[template_index].scripts) > 0:
        context.scene.templates_collection[template_index].scripts.remove(script_index)
 
def editScript(context, template_index, script_index, name = "Test", description = "Test Do", icon = "PREFERENCES", path = "Test.py"):
    template = context.scene.templates_collection[template_index]
    script = template.scripts[script_index]

    script.name = name
    script.description = description
    script.icon = icon
    script.path = path
       
def getListOfScripts(self, context):
    
    preferences = bpy.context.preferences.addons["BlenderScriptManager"].preferences

    directory = preferences.script_dir
    
    Enum_items = []
    
    for filename in os.listdir(directory):
        # Check if the file ends with .py (Python files)
            if filename.endswith(".py"):
                data = filename
                item = (data, data, data)
                # Print the file name
                Enum_items.append(item)
        
    return Enum_items
    
def addArgs(context, template_index, script_index, type, name = "Test Arg", description = "Test Arg Do", value=0):
    template = context.scene.templates_collection[template_index]
    script = template.scripts[script_index]
    args = script.args
    
    arg = args.add()
    
    arg.name = name
    arg.description = description
    arg.type = type
    
    key = getVarType(var_types, type)[0]
    index = getVarType(var_types, type)[1]
    
    if value == 0:
        value = var_default_value[index]
    
    arg[key] = value
    
    
def editArgs(context, template_index, script_index, arg_index, type, name = "Test Arg", description = "Test Arg Do", value=0):
    template = context.scene.templates_collection[template_index]
    script = template.scripts[script_index]
    arg = script.args[arg_index]
    
    arg.name = name
    arg.description = description
    arg.type = type
    
    key = getVarType(var_types, type)[0]
        
    arg[key] = value[key]
    
def removeArgs(context, template_index, script_index, arg_index):
    template = context.scene.templates_collection[template_index]
    script = template.scripts[script_index]
    script.args.remove(arg_index)
    