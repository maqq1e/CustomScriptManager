import bpy

from .Defers.Control import *
from .Defers.Layouts import LAYOUT_multiline

from .App.Operators import OPERATORS
from .App.Interfaces import *

from .App.Datas import TEMPLATES, EXTENSIONS

def EXCEPTION_isReady(context):
    PREFERENCES = context.scene.CSM_Preferences
    data = PREFERENCES.script_dir
    if data == "":
        return False
    else:
        if len(context.scene.CSM_TemplatesFilesCollection) > 0:
            return True
        else:
            return False

class BlenderScriptManager:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Script Manager"

class TemplatesPanel(BlenderScriptManager, bpy.types.Panel):
    bl_label = "Custom Script Manager"
    bl_idname = "CSM_PT_Templates"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        
        PREFERENCES = context.scene.CSM_Preferences
        
        ### --- GET PREFERENCES --- ###
        ###############################
        
        if PREFERENCES.script_dir == "":
            layout.label(text="Please set the script directory.")
            
            layout.prop(PREFERENCES, "script_dir", text="")
            
            layout.operator(OPERATORS.load_templates.value, text="Load Templates", icon="IMPORT")
            op = layout.operator(OPERATORS.open_addon_prefs.value, text="Open Addon Preferences", icon='PREFERENCES')
            op.addon_name = PREFERENCES.addon_name
            return None
        
        if len(context.scene.CSM_TemplatesFilesCollection) == 0:
            LAYOUT_multiline(context, "Your script folder not contain any .json template file. You must create one.", layout)
            op = layout.operator(OPERATORS.create_json_file.value, text="Create .json file", icon='ADD') ## LOOK OUT
            op.path = PREFERENCES.script_dir
            op.name = "templates"
            layout.operator(OPERATORS.load_templates.value, text="Load Templates", icon="IMPORT")
            layout.operator(OPERATORS.open_addon_prefs.value, text="Open Addon Preferences", icon='PREFERENCES')
            return None
        
        ### --- SETUP TEMPLATES --- ###
        ###############################
        
        ### Save and Load Row
        first_row = layout.row()
        
        # If Templates changed
        if context.scene.CSM_isSave:
            first_row.enabled = True
        else:
            first_row.enabled = False
        
        ### Save and Load Buttons
        first_row.operator(OPERATORS.load_templates.value, text="Revert Changes", icon="LOOP_BACK")
        first_row.operator(OPERATORS.save_templates.value, text="Save Templates", icon="EXPORT")
        
        ### If there is not any of templates
        if len(context.scene.CSM_Database) == 0:
            layout.label(text="You need to create your first template")
            layout.operator(TEMPLATES.templates_add_item.value, text="Create template", icon="ADD")
            return None
        
        ### Templates Enum Row
        second_row = layout.row()
        second_row = second_row.row()
        second_row.prop(context.workspace, "CSM_TemplateName", text="")
        
        edit = second_row.operator(TEMPLATES.templates_edit_item.value, text="", icon="TOOL_SETTINGS")
        edit.old_name = context.workspace.CSM_TemplateName
        
        second_row.operator(TEMPLATES.templates_add_item.value, text="", icon="ADD")
        
        _delete_row = second_row.row()
        delete = _delete_row.operator(TEMPLATES.templates_remove_item.value, text="", icon="REMOVE")
        
        
        template_index = context.scene.CSM_Database.find(context.workspace.CSM_TemplateName) # Get Current Template Index
        delete.index = template_index
        edit.template_index = template_index

class ExtensionPanel(BlenderScriptManager, bpy.types.Panel):
    bl_parent_id = "CSM_PT_Templates"
    bl_idname = "CSM_PT_Extensions"
    bl_label = "Extensions"
    bl_options = {'DEFAULT_CLOSED'}
        
    @classmethod
    def poll(cls, context):
        if len(context.scene.CSM_Database) > 0 and EXCEPTION_isReady(context):
            return True
        else:
            return False
        
    
    def draw(self, context):
        layout = self.layout
        
        current_template = context.workspace.CSM_TemplateName
        template_index = context.scene.CSM_Database.find(current_template)
        extensions_collection = context.scene.CSM_Database[current_template].extensions
        
        ### Iterate Extensions List
        if len(extensions_collection) != 0:
            op = layout.operator(EXTENSIONS.extensions_refresh_item.value, text="Forced Refresh Extensions", icon="FILE_REFRESH")
            
            ext_index = 0
            for ext in extensions_collection:
                box = layout.box()
                row = box.row()
                
                row.label(text=ext.name)
                
                del_op = row.operator(EXTENSIONS.extensions_remove_item.value, text="", icon="REMOVE")
                del_op.template_index = template_index
                del_op.extension_index = ext_index
                
                ext_index = ext_index + 1
        else:
            layout.label(text="You have no any extensions.")
            
        op = layout.operator(EXTENSIONS.extensions_add_item.value, text="Add Extension")
        op.template_index = template_index

class ScriptsPanel(BlenderScriptManager, bpy.types.Panel):
    bl_parent_id = "CSM_PT_Templates"
    bl_idname = "CSM_PT_Scripts"
    bl_label = "Scripts"
        
    @classmethod
    def poll(cls, context):
        return EXCEPTION_isReady(context)

    def draw(self, context):
        
        PREFERENCES = context.scene.CSM_Preferences
        
        template_index = context.scene.CSM_Database.find(context.workspace.CSM_TemplateName)
        
        layout = self.layout
        
        ### Iterate Scripts
        if len(context.scene.CSM_Database) != 0:
            
            template = context.scene.CSM_Database[template_index]
            
            if len(template.scripts) != 0:
                for script in template.scripts:
                    
                    box = layout.box()
                    
                    ### --- SUBPANEL --- ###
                    
                    panel_row = box.row()
                    icon = 'TRIA_DOWN' if script.status else 'TRIA_RIGHT'
                    panel_row.prop(script, "status", icon=icon, icon_only=True)
                    
                    ########################
                    
                    script_index = template.scripts.find(script.name)
                    
                    if script.status: 
                        
                        ### ---   ARGS LAYOUTS  --- ###
                        for arg in script.args:
                            arg_index = script.args.find(arg.name)
                            
                            box.separator(factor=0.3, type="LINE")
                                
                            args_row = box.row()
                                                                            
                            varType = EXT_getVarType(PROPERTY_var_types, arg.type)
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
                            
                            op = args_row.operator(TEMPLATES.args_edit_item.value, text="", icon="TOOL_SETTINGS")
                            op.template_index = template_index
                            op.script_index = script_index
                            op.arg_index = arg_index
                            op.name = arg.name
                            op.description = arg.description
                            op.type = arg.type
                            _value = op.value.add()
                            _value[key] = arg[key]
                            
                            op = args_row.operator(TEMPLATES.args_remove_item.value, text="", icon="REMOVE")
                            op.template_index = template_index
                            op.script_index = script_index
                            op.arg_index = arg_index
                            
                        op = box.operator(TEMPLATES.args_add_item.value, text="Add Argument", icon="ADD")
                        op.template_index = template_index
                        op.script_index = script_index
                        
                        ###############################
                                        
                    op = panel_row.operator(OPERATORS.run_scripts.value, text=script.name, icon=script.icon)
                    op.script_dir = PREFERENCES.script_dir
                    op.script_name = script.path # Path is name of script
                    for arg in script.args:
                        ap = op.props.add()
                        ap.name = arg.name
                        ap.description = arg.description
                        ap.type = arg.type
                        
                        key = EXT_getVarType(PROPERTY_var_types, arg.type)[0]
                        
                        ap[key] = arg[key]
                    
                        
                    op = panel_row.operator(TEMPLATES.scripts_edit_item.value, text="", icon="GREASEPENCIL")
                    op.template_index = template_index
                    op.script_index = script_index
                    op.name = script.name
                    op.description = script.description
                    op.icon = script.icon
                    op.path = script.path
                    
                    op = panel_row.operator(TEMPLATES.scripts_remove_item.value, text="", icon="REMOVE")
                    op.template_index = template_index
                    op.script_index = script_index

            op = layout.operator(TEMPLATES.scripts_add_item.value, text="", icon="ADD")
            op.template_index = template_index
            return None
            
        op = layout.label(text="You need template to add any scripts.")

class Settings(BlenderScriptManager, bpy.types.Panel):
    bl_parent_id = "CSM_PT_Templates"
    bl_idname = "CSM_PT_Settings"
    bl_label = "Settings"
    
    @classmethod
    def poll(cls, context):
        return EXCEPTION_isReady(context)

    def draw(self, context):
        PREFERENCES = context.scene.CSM_Preferences
        
        layout = self.layout
        
        box = layout.box()
        
        row = box.row()
        row.prop(context.scene, "CSM_TemplateFileName", text="")
        
        edit = row.operator(OPERATORS.edit_template_file.value, text="", icon='TOOL_SETTINGS')
        edit.path = PREFERENCES.script_dir
        edit.template_file_name = context.scene.CSM_TemplateFileName
        
        add_new = row.operator(OPERATORS.create_json_file.value, text="", icon='ADD')
        add_new.path = PREFERENCES.script_dir
        add_new.name = "templates"
        
        del_new = row.operator(OPERATORS.delete_json_file.value, text="", icon='REMOVE')
        del_new.path = PREFERENCES.script_dir
        del_new.name = context.scene.CSM_TemplateFileName
        
        # Load manualy if didn't load automaticly
        if len(context.scene.CSM_TemplatesFilesCollection) == 0:
            box.operator(OPERATORS.load_templates.value, text="Load Templates", icon="IMPORT")
        
        layout.prop(PREFERENCES, "script_dir", text="")
        layout.operator(OPERATORS.open_addon_prefs.value, text="Open Addon Preferences", icon='PREFERENCES')

MAIN_Classes = [
    TemplatesPanel,
    Settings,
    ExtensionPanel,
    ScriptsPanel,
]
    