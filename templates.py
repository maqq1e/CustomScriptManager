import bpy
from .operators import *
from .interfaces import *

def getPREFERENCES():
    data = bpy.context.preferences.addons["BlenderScriptManager"].preferences
    return data
    
def CHECKOUT_Preferences(layout):
    
    PREFERENCES = getPREFERENCES()
    
    # Set dir if not exist
    if PREFERENCES.script_dir == "":
        layout.label(text="Please set the script directory in preferences.")
        layout.operator(OpenAddonPreferencesOperator.bl_idname, text="Open Addon Preferences", icon='PREFERENCES')
        return None
        
def SETUP_Templates(context, layout):
    row = layout.row()
    # If Templates changed
    if context.scene.isSave:
        row.enabled = True
    else:
        row.enabled = False
    row.operator(LoadTemplates.bl_idname, text="Revert Changes", icon="LOOP_BACK")
    row.operator(SaveTemplates.bl_idname, text="Save Templates", icon="EXPORT")
    
    row = layout.row(align=True)
    row.prop(context.workspace, "Templates", text="")
    row.operator("templates.add_item", text="", icon="ADD")
    _row = row.row()
    op = _row.operator("templates.remove_item", text="", icon="REMOVE")
    if len(context.scene.templates_collection) == 0:
        _row.enabled = False

    if len(context.scene.templates_collection) == 0:
        layout.label(text="You need to create your first template")
        layout.operator(LoadTemplates.bl_idname, text="Load Templates", icon="IMPORT")
        return None
    
    template_index = context.scene.templates_collection.find(context.workspace.Templates) # Get Current Template Index
    op.index = template_index

    layout.prop(context.scene.templates_collection[context.workspace.Templates], "name", text="Template Name: ")

def DRAW_Arguments(context, script, box, template_index, script_index):
    
    for arg in script.args:
        arg_index = script.args.find(arg.name)
        
        box.separator(factor=0.3, type="LINE")
            
        args_row = box.row()
                                                        
        varType = getVarType(var_types, arg.type)
        key = varType[0]
        index = varType[1]
        option = var_types_options[index]
        
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
        
        op = args_row.operator("args.edit_item", text="", icon="TOOL_SETTINGS")
        op.template_index = template_index
        op.script_index = script_index
        op.arg_index = arg_index
        op.name = arg.name
        op.description = arg.description
        op.type = arg.type
        _value = op.value.add()
        _value[key] = arg[key]
        
        op = args_row.operator("args.remove_item", text="", icon="REMOVE")
        op.template_index = template_index
        op.script_index = script_index
        op.arg_index = arg_index
   
def DRAW_Extensions(context, layout, template_index):
    PREFERENCES = getPREFERENCES()
    templates_collection = context.scene.templates_collection
    
    if len(templates_collection) != 0:
        if len(templates_collection[template_index].extensions) != 0:
            ext_index = 0
            for ext in templates_collection[template_index].extensions:
                box = layout.box()
                row = box.row()
                
                op = row.operator(RegisterScriptOperator.bl_idname, text="", icon="PLAY")
                op.script_dir = PREFERENCES.script_dir
                op.script_name = ext.name
                op.isUnregister = False
                
                pause_op = row.operator(RegisterScriptOperator.bl_idname, text="", icon="PAUSE")
                pause_op.script_dir = PREFERENCES.script_dir
                pause_op.script_name = ext.name
                pause_op.isUnregister = True
                
                
                row.label(text=ext.name)
                
                del_op = row.operator("extensions.remove_item", text="", icon="REMOVE")
                del_op.template_index = template_index
                del_op.extension_index = ext_index
                
                ext_index = ext_index + 1
        else:
            layout.label(text="You have no any extensions.")
        
    add_op = layout.operator("extensions.add_item", text="Add Extension")
    add_op.template_index = template_index 
         
def EXECUTE_Script(panel_row, script):
    PREFERENCES = getPREFERENCES()
    
    op = panel_row.operator(RunScriptsOperator.bl_idname, text=script.name, icon=script.icon)
    op.script_dir = PREFERENCES.script_dir
    op.script_name = script.path # Path is name of script
    for arg in script.args:
        ap = op.props.add()
        ap.name = arg.name
        ap.description = arg.description
        ap.type = arg.type
        
        key = getVarType(var_types, arg.type)[0]
        
        ap[key] = arg[key]
        