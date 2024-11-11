import bpy

from ..Defers.Control import *

from ..App.Datas import EXTENSIONS

class EXTENSION_AddExtensionsOperator(bpy.types.Operator):
    """Register and add extension in template"""
    bl_idname = EXTENSIONS.extensions_add_item.value
    bl_label = "Add Extension"

    name: bpy.props.EnumProperty(name="Scripts", items=getListOfScripts)
    template_index: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        
        CMP_addExtension(context, self.template_index, self.name)        
        EXT_updateTemplateProperties(self, context)
        
        context.scene.CSM_isSave = True

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

class EXTENSION_RemoveExtensionsOperator(bpy.types.Operator):
    """Unregister and remove extension from template"""
    bl_idname = EXTENSIONS.extensions_remove_item.value
    bl_label = "Remove Extension?"

    template_index: bpy.props.IntProperty()
    extension_index: bpy.props.IntProperty()

    def execute(self, context):
        
        template = context.scene.CSM_Database[self.template_index]
        ext = template.extensions[self.extension_index]
        
        CMP_unregisterCurrentExtension(context, ext.name)

        CMP_removeExtension(context, self.template_index, self.extension_index)

        context.scene.CSM_isSave = True

        return {'FINISHED'}
    
    def invoke(self, context, event):

        return context.window_manager.invoke_confirm(self, event)

class EXTENSION_RefreshExtensionsOperator(bpy.types.Operator):
    """Unregister and register again all active extensions"""
    bl_idname = EXTENSIONS.extensions_refresh_item.value
    bl_label = "Refresh Extensions?"

    def execute(self, context):
        
        EXT_updateTemplateProperties(self, context)

        return {'FINISHED'}
    
EXTENSIONS_Classes = [
    EXTENSION_AddExtensionsOperator,
    EXTENSION_RemoveExtensionsOperator,
    EXTENSION_RefreshExtensionsOperator
]