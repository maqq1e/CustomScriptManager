import bpy

from .main import MAIN_Classes

from .App.Operators import OPERATORS_Classes
from .App.Interfaces import *

from .Components.ExtensionsComponent import EXTENSIONS_Classes
from .Components.TemplatesComponent import TEMPLATES_Classes

from .Defers.Control import CMP_unregisterCurrentExtension, EXT_updateAllProperties, EXT_updateTemplateProperties, EXT_updateDatabaseProperties

# Set information about addon
# Addon Info
bl_info = {
    "name": "CustomScriptManager",
    "author": "https://github.com/maqq1e/CustomScriptManager",
    "description": "Easy way manage your custom scripts",
    "blender": (3, 6, 0),
    "version": (1, 4, 0),
}

# Preferences Panel

class SETTING_ManagerPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    script_dir: bpy.props.StringProperty(
        name="Scripts Directory",
        description="Select the directory containing the Python scripts",
        default="",
        subtype='DIR_PATH',
        update=EXT_updateAllProperties
    ) # type: ignore
    
    globalExtensionsStack: bpy.props.CollectionProperty(type=INTERFACE_GlobalExtensionStack)
    
    addon_name: bpy.props.StringProperty(default=__name__)
    
    links_hide: bpy.props.BoolProperty(default=False)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "script_dir")
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

def _getTemplatesFiles(self, context):
    Enum_items = []
    for templateFile in context.scene.CSM.templatesFilesCollection:
        data = str(templateFile.name)
        item = (data, data, data)
        Enum_items.append(item)
    return Enum_items

def _getTemplateItems(self, context):
    
    Enum_items = []
    
    for template_item in context.scene.CSM.database:
        
        data = str(template_item.name)
        item = (data, data, data)
        
        Enum_items.append(item)
        
    return Enum_items

class Properties(bpy.types.PropertyGroup):
    # Preferences
    @property
    def preferences(self):
        # Dynamically access the addon preferences
        return bpy.context.preferences.addons[__name__].preferences
    # Main
    templateFileName: bpy.props.EnumProperty(name="Templates Files", items=_getTemplatesFiles, update=EXT_updateDatabaseProperties)
    templatesFilesCollection: bpy.props.CollectionProperty(type=INTERFACE_Files)
    # # Templates
    database: bpy.props.CollectionProperty(type=INTERFACE_Database)
    scripts_tab: bpy.props.BoolProperty(default=True)
    extensions_tab: bpy.props.BoolProperty(default=True)
    isSave: bpy.props.BoolProperty(default=False)
    activeObject: bpy.props.PointerProperty(type=bpy.types.Object)
    # Stack
    stack: bpy.props.CollectionProperty(type=INTERFACE_ExtensionsStack)
    

def setProperties():
    
    bpy.types.Scene.CSM = bpy.props.PointerProperty(type=Properties)
        
    bpy.types.WorkSpace.CSM_TemplateName = bpy.props.EnumProperty(name="Template", items=_getTemplateItems, update=EXT_updateTemplateProperties)

        
def delProperties():
    
    del bpy.types.Scene.CSM
    
    del bpy.types.WorkSpace.CSM_TemplateName

# Initialization Classes
UsesClasses = []

UsesClasses.extend(INTERFACES_Classes)
UsesClasses.append(SETTING_ManagerPreferences)
UsesClasses.extend(OPERATORS_Classes)
UsesClasses.extend(EXTENSIONS_Classes)
UsesClasses.extend(TEMPLATES_Classes)
UsesClasses.extend(MAIN_Classes)
UsesClasses.append(Properties)

# After Load
@bpy.app.handlers.persistent
def after_load(context):
    EXT_updateAllProperties(None, bpy.context)

# Handler for Event
event_handler = object()

# Register Classes
def register():

    for useClass in UsesClasses:
        bpy.utils.register_class(useClass)
    
    setProperties()
    
    # Triggers when window's workspace is changed
    subscribe_to = bpy.types.Window, "workspace"

    def change_template(context):
        if len(bpy.context.scene.CSM.database) > 0:
            EXT_updateTemplateProperties(None, bpy.context)
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=event_handler,
        args=(bpy.context,),
        notify=change_template,
    )
    bpy.msgbus.publish_rna(key=subscribe_to)

    bpy.app.handlers.load_post.append(after_load) # Load datas after load blender

def unregister():
    
    stack = bpy.context.scene.CSM.stack
    
    ### Unregister all extensions
    for ext in stack:
        CMP_unregisterCurrentExtension(bpy.context, ext.name)
    
    
    for useClass in UsesClasses:
        bpy.utils.unregister_class(useClass)

    delProperties()
    
    bpy.msgbus.clear_by_owner(event_handler)
    
    bpy.app.handlers.load_post.remove(after_load)

if __name__ == "__main__":
    register()
    
