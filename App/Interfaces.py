import bpy

def makeTemplateSave(self, context):
    context.scene.CSM.isSave = True

### Classes

class INTERFACE_ExtensionsClasses(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

class INTERFACE_ExtensionsStack(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    
    script = {}
        

class INTERFACE_Args(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    type: bpy.props.StringProperty()
    bool: bpy.props.BoolProperty(options={'ANIMATABLE'})
    bool_toggle: bpy.props.BoolProperty(options={'ANIMATABLE'})
    float: bpy.props.FloatProperty()
    float_slider: bpy.props.FloatProperty()
    string: bpy.props.StringProperty(
        name="Directory",
        default="",
        subtype='NONE'
    )
    integer: bpy.props.IntProperty()
    integer_slider: bpy.props.IntProperty()
    string_path: bpy.props.StringProperty(
        name="Directory",
        default="",
        subtype='DIR_PATH'
    )
    custom: bpy.props.StringProperty()
    custom_self: bpy.props.StringProperty()

class INTERFACE_Scripts(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    icon: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    status: bpy.props.BoolProperty(name="Arguments")
    args: bpy.props.CollectionProperty(type=INTERFACE_Args)

class INTERFACE_Extensions(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    
class INTERFACE_Database(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(update=makeTemplateSave)
    scripts: bpy.props.CollectionProperty(type=INTERFACE_Scripts)
    extensions: bpy.props.CollectionProperty(type=INTERFACE_Extensions)

class INTERFACE_Files(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

INTERFACES_Classes = [
    INTERFACE_Args,
    INTERFACE_ExtensionsClasses,
    INTERFACE_ExtensionsStack,
    INTERFACE_Scripts,
    INTERFACE_Extensions,
    INTERFACE_Database,    
    INTERFACE_Files,
]