import bpy

from ..Defers.Control import *
from ..App.Interfaces import *

from ..App.Datas import TEMPLATES

class TEMPLATE_AddTemplateOperator(bpy.types.Operator):
    """Add new template"""
    bl_idname = TEMPLATES.templates_add_item.value
    bl_label = "Add Template"

    def execute(self, context):

        CMP_addTemplate(context)

        context.scene.CSM.isSave = True

        return {'FINISHED'}

class TEMPLATE_RemoveTemplateOperator(bpy.types.Operator):
    """Remove current template"""
    bl_idname = TEMPLATES.templates_remove_item.value
    bl_label = "Remove Template?"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        
        CMP_removeTemplate(context, self.index)

        context.scene.CSM.isSave = True

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)

class TEMPLATE_EditTemplateOperator(bpy.types.Operator):
    """Edit current template"""
    bl_idname = TEMPLATES.templates_edit_item.value
    bl_label = "Edit Template"
    
    template_index: bpy.props.IntProperty(options={'HIDDEN'})

    old_name: bpy.props.StringProperty(name="Old Name")
    
    name: bpy.props.StringProperty(name="New Name")
    
    def execute(self, context):
        
        CMP_editTemplate(context, self.template_index, self.name)
        
        context.scene.CSM.isSave = True

        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        
        disbox = layout.box()
        disbox.prop(self, "old_name", text="Old Name")
        disbox.enabled = False
        
        box = layout.box()        
        box.prop(self, "name", text="New name")   
        
    
    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)
 
class TEMPLATE_AddScriptOperator(bpy.types.Operator):
    """Add Script in current template"""
    bl_idname = TEMPLATES.scripts_add_item.value
    bl_label = "Add Script"

    template_index: bpy.props.IntProperty(options={'HIDDEN'})

    name: bpy.props.StringProperty(name="Button Name")

    description: bpy.props.StringProperty(name="Description")

    icon: bpy.props.EnumProperty(name="Icons", items=icons)

    path: bpy.props.EnumProperty(name="Scripts", items=getListOfScripts)

    def execute(self, context):
        
        CMP_addScript(context, self.template_index, self.name, self.description, self.icon, self.path)

        context.scene.CSM.isSave = True

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)
    
class TEMPLATE_RemoveScriptOperator(bpy.types.Operator):
    """Remove Script from current template"""
    bl_idname = TEMPLATES.scripts_remove_item.value
    bl_label = "Remove Script from Template?"
    
    template_index: bpy.props.IntProperty()
    script_index: bpy.props.IntProperty()
    
    def execute(self, context):
        
        CMP_removeScript(context, self.template_index, self.script_index)
        
        context.scene.CSM.isSave = True

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)
    
class TEMPLATE_EditScriptOperator(bpy.types.Operator):
    """Edit current Script"""
    bl_idname = TEMPLATES.scripts_edit_item.value
    bl_label = "Edit Script"
    
    template_index: bpy.props.IntProperty(options={'HIDDEN'})
    script_index: bpy.props.IntProperty(options={'HIDDEN'})

    name: bpy.props.StringProperty(name="Button Name")

    description: bpy.props.StringProperty(name="Description")

    icon: bpy.props.EnumProperty(name="Icons", items=icons)

    path: bpy.props.EnumProperty(name="Scripts", items=getListOfScripts)
    
    def execute(self, context):
        
        CMP_editScript(context, self.template_index, self.script_index, self.name, self.description, self.icon, self.path)
        
        context.scene.CSM.isSave = True

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

class TEMPLATE_AddArgsOperator(bpy.types.Operator):
    """Add arguments in current Script"""
    bl_idname = TEMPLATES.args_add_item.value
    bl_label = "Add Arg Item"

    template_index: bpy.props.IntProperty(options={'HIDDEN'})
    script_index: bpy.props.IntProperty(options={'HIDDEN'})

    name: bpy.props.StringProperty(name="Name")

    description: bpy.props.StringProperty(name="Args Description")

    type: bpy.props.EnumProperty(name="Type", items=PROPERTY_var_types)
    
    value: bpy.props.StringProperty(name="Object Name", default="0")

    def execute(self, context):
        if self.type == "CUSTOM":
            self.value = bpy.context.scene.CSM.activeObject.name
        if self.type == "CUSTOM_SELF":
            self.value = ""
        
        CMP_addArgs(context, self.template_index, self.script_index, self.type, self.name, self.description, self.value)

        context.scene.CSM.isSave = True

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

class TEMPLATE_EditArgsOperator(bpy.types.Operator):
    """Edit arguments in current Script"""
    bl_idname = TEMPLATES.args_edit_item.value
    bl_label = "Edit Arg Item"
    
    template_index: bpy.props.IntProperty(options={'HIDDEN'})
    script_index: bpy.props.IntProperty(options={'HIDDEN'})
    arg_index: bpy.props.IntProperty(options={'HIDDEN'})

    name: bpy.props.StringProperty(name="Name")

    description: bpy.props.StringProperty(name="Description")

    type: bpy.props.EnumProperty(name="Type", items=PROPERTY_var_types)
    
    value: bpy.props.CollectionProperty(type=INTERFACE_Args, options={'HIDDEN'})
    
    def execute(self, context):
        if self.type == "CUSTOM":
            self.value[0].custom = bpy.context.scene.CSM.activeObject.name
        if self.type == "CUSTOM_SELF":
            self.value[0].custom = ""
        
        CMP_editArgs(context, self.template_index, self.script_index, self.arg_index, self.type, self.name, self.description, self.value[0])
        
        context.scene.CSM.isSave = True

        return {'FINISHED'}
    
    def draw(self, context):
        
        layout = self.layout
        box = layout.box()
        
        if "CUSTOM" in self.type:
            box.prop(self, "name", text="Ignore Properties", placeholder="Prop1;Prop2;Prop3;")
        else:
            box.prop(self, "name", text="Name")
        box.prop(self, "description", text="Description")
        disbox = layout.box()
        disbox.prop(self, "type", text="Type")
        disbox.enabled = False
        
        if self.type == "CUSTOM":
            box.prop(context.scene.CSM, "activeObject", text="Object")
    
    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)
    
class TEMPLATE_RemoveArgsOperator(bpy.types.Operator):
    """Remove arguments from current Script"""
    bl_idname = TEMPLATES.args_remove_item.value
    bl_label = "Remove Argument from Script?"
    
    template_index: bpy.props.IntProperty(options={'HIDDEN'})
    script_index: bpy.props.IntProperty(options={'HIDDEN'})
    arg_index: bpy.props.IntProperty(options={'HIDDEN'})
    
    def execute(self, context):
        
        CMP_removeArgs(context, self.template_index, self.script_index, self.arg_index)
        
        context.scene.CSM.isSave = True

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)
    
TEMPLATES_Classes = [
    TEMPLATE_AddTemplateOperator,
    TEMPLATE_RemoveTemplateOperator,
    TEMPLATE_EditTemplateOperator,
    TEMPLATE_AddScriptOperator,
    TEMPLATE_RemoveScriptOperator,
    TEMPLATE_EditScriptOperator,
    TEMPLATE_AddArgsOperator,
    TEMPLATE_EditArgsOperator,
    TEMPLATE_RemoveArgsOperator
]
