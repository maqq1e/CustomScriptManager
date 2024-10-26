import bpy

from .Interfaces import *
from ..Defers.Control import EXT_updateDatabaseProperties, EXT_updateTemplateProperties

def _getTemplatesFiles(self, context):
    Enum_items = []
    for templateFile in context.scene.CSM_TemplatesFilesCollection:
        data = str(templateFile.name)
        item = (data, data, data)
        Enum_items.append(item)
    return Enum_items

def _getTemplateItems(self, context):
    
    Enum_items = []
    
    for template_item in context.scene.CSM_Database:
        
        data = str(template_item.name)
        item = (data, data, data)
        
        Enum_items.append(item)
        
    return Enum_items  

def setProperties():
    # Preferences
    bpy.types.Scene.CSM_Preferences = bpy.context.preferences.addons["CustomScriptManager"].preferences
    
    # Main
    bpy.types.Scene.CSM_TemplateFileName = bpy.props.EnumProperty(name="Templates Files", items=_getTemplatesFiles, update=EXT_updateDatabaseProperties)
    bpy.types.Scene.CSM_TemplatesFilesCollection = bpy.props.CollectionProperty(type=INTERFACE_Files)
    
    # Templates
    bpy.types.WorkSpace.CSM_TemplateName = bpy.props.EnumProperty(name="Template", items=_getTemplateItems, update=EXT_updateTemplateProperties)
    bpy.types.Scene.CSM_Database = bpy.props.CollectionProperty(type=INTERFACE_Database)
    bpy.types.Scene.CSM_isSave = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.CSM_activeObject = bpy.props.PointerProperty(type=bpy.types.Object)
    
    # Stack
    bpy.types.Scene.CSM_Stack = bpy.props.CollectionProperty(type=INTERFACE_ExtensionsStack)
    
        
def delProperties():
    # Preferences
    del bpy.types.Scene.CSM_Preferences
    
    # Main
    del bpy.types.Scene.CSM_TemplateFileName
    del bpy.types.Scene.CSM_TemplatesFilesCollection
    
    # Templates
    del bpy.types.WorkSpace.CSM_TemplateName
    del bpy.types.Scene.CSM_Database
    del bpy.types.Scene.CSM_isSave
    del bpy.types.Scene.CSM_activeObject
    
    # Stack
    del bpy.types.Scene.CSM_Stack