import bpy

from .Interfaces import *
from ..Defers.Control import *

from .Datas import OPERATORS

# Operator to open the add-on preferences
class OPERATOR_OpenAddonPreferencesOperator(bpy.types.Operator):
    """Open addon properties tab"""
    bl_idname = OPERATORS.open_addon_prefs.value
    bl_label = "Open Addon Preferences"
    
    addon_name: bpy.props.StringProperty(default="")
    
    def execute(self, context):
        # Open the Add-ons preferences tab
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        bpy.context.preferences.active_section = 'ADDONS'
        bpy.data.window_managers['WinMan'].addon_search = context.scene.CSM_Preferences.addon_name
        bpy.ops.preferences.addon_expand(module = self.addon_name)
        return {'FINISHED'}

class OPERATOR_CreateJsonFile(bpy.types.Operator):
    """Create .json file with templates data"""
    bl_idname = OPERATORS.create_json_file.value
    bl_label = "Create new .json template file?"
    
    path: bpy.props.StringProperty(name="Path", default="")
    name: bpy.props.StringProperty(name="Name", default="")
    
    def execute(self, context):
        
        data = {
            "templates": [],
            "extensions": []
        }
        
        if not EXT_checkFileExist(self.path, self.name):
            EXT_jsonExport(self.path, self.name, data, True)
        else:
            EXT_jsonExport(self.path, "1_" + self.name, data, True)
            
    
        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)

class OPERATOR_DeleteJsonFile(bpy.types.Operator):
    """Delete .json file with templates data"""
    bl_idname = OPERATORS.delete_json_file.value
    bl_label = "Delete current .json template file?"
    
    path: bpy.props.StringProperty(name="Path", default="")
    name: bpy.props.StringProperty(name="Name", default="")
    
    def execute(self, context):
        
        EXT_deleteFile(self.path, self.name)
        
        if len(context.scene.CSM_TemplatesFilesCollection) > 0:
            context.scene.CSM_TemplateFileName = context.scene.CSM_TemplatesFilesCollection[0].name
        
        return {'FINISHED'}

    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)

class OPERATOR_LoadTemplates(bpy.types.Operator):
    """Load template data from .json file"""
    bl_idname = OPERATORS.load_templates.value
    bl_label = "Load Template"
    
    def execute(self, context):
        
        EXT_updateAllProperties(self, context)        

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)

class OPERATOR_SaveTemplates(bpy.types.Operator):
    """Save template data in .json file"""
    bl_idname = OPERATORS.save_templates.value
    bl_label = "Save Template"
    
    def execute(self, context):
        # Get the file name from the addon preferences
        PREFERENCES = context.scene.CSM_Preferences
        
        templates = context.scene.CSM_Database
        
        file = context.scene.CSM_TemplateFileName

        EXT_jsonExport(PREFERENCES.script_dir, file, EXT_serializeDict(templates))

        context.scene.CSM_isSave = False

        return {'FINISHED'}

class OPERATOR_RunScriptsOperator(bpy.types.Operator):
    """Execute custom script .py file"""
    bl_idname = OPERATORS.run_scripts.value
    bl_label = "Run Scripts in Directory"

    script_dir: bpy.props.StringProperty(name="Script Dir", default="")
    script_name: bpy.props.StringProperty(name="Script Name", default="")
    
    props: bpy.props.CollectionProperty(type=INTERFACE_Args)
    
    def execute(self, context):
        filepath = self.script_dir + self.script_name

        status = EXT_executeScript(self.props, filepath)
        
        self.report(status[0], status[1])
        return {'FINISHED'}

class OPERATOR_EditTemplateFileOperator(bpy.types.Operator):
    """Edit .json file with template data"""
    bl_idname = OPERATORS.edit_template_file.value
    bl_label = "Edit Template File"
    
    template_file_name: bpy.props.StringProperty()

    new_name: bpy.props.StringProperty()

    path: bpy.props.StringProperty()
    
    def execute(self, context):
        
        EXT_renameFile(self.path, self.template_file_name, self.new_name, ".json")
        
        context.scene.CSM_TemplatesFilesCollection[self.template_file_name].name = self.new_name

        return {'FINISHED'}
    
    def draw(self, context):
        
        layout = self.layout
        
        disbox = layout.box()
        disbox.prop(self, "template_file_name", text="Old Name")
        disbox.enabled = False
        
        box = layout.box()        
        box.prop(self, "new_name", text="New name")        
    
    def invoke(self, context, event):
        self.new_name = ""
        return context.window_manager.invoke_props_dialog(self)

OPERATORS_Classes = [
    OPERATOR_OpenAddonPreferencesOperator,
    OPERATOR_LoadTemplates,
    OPERATOR_SaveTemplates,
    OPERATOR_RunScriptsOperator,
    OPERATOR_CreateJsonFile,
    OPERATOR_DeleteJsonFile,
    OPERATOR_EditTemplateFileOperator
]