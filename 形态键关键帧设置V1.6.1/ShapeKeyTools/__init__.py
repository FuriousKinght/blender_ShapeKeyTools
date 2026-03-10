# ShapeKeyAnimator/__init__.py
bl_info = {
    "name": "形态键工具V1.6.1",
    "author": "FK",
    "version": (1, 6, 1),
    "blender": (4, 5, 0),
    "location": "视图3D > 属性面板 > MMD",
    "description": "形态键参数控制和关键帧设置工具 - 支持智能多选操作",
    "category": "Animation",
}

import bpy

from . import properties, operators, panels, presets, translations, utils

classes = (
    # Properties
    properties.ShapeKeySelectionItem,
    properties.ShapeKeyKeyframeSettingsProperties,
    properties.ShapeKeyControlProperties,

    # Operators
    operators.ShapeKeyKeyframeSettings,
    operators.DeleteShapeKeyKeyframes,
    operators.InsertShapeKeyKeyframe,
    operators.DeleteCurrentShapeKeyKeyframe,
    operators.SetShapeKeyValue,
    operators.RefreshShapeKeyMonitor,
    operators.CopyQQGroup,
    operators.PreviousShapeKey,
    operators.NextShapeKey,
    operators.ClearSearch,
    operators.SelectShapeKeyOperator,
    operators.SetMultipleShapeKeyValues,
    operators.InsertMultipleShapeKeyKeyframes,
    operators.DeleteMultipleShapeKeyKeyframes,
    operators.ClearShapeKeySelection,
    operators.ResetAllMonitorShapeKeys,

    # UI
    panels.SHAPEKEY_UL_list,
    panels.CombinedShapeKeyPanel,
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            bpy.utils.unregister_class(cls)
            bpy.utils.register_class(cls)

    bpy.types.Scene.shape_key_keyframe_settings = bpy.props.PointerProperty(
        type=properties.ShapeKeyKeyframeSettingsProperties
    )
    bpy.types.Scene.shape_key_control_settings = bpy.props.PointerProperty(
        type=properties.ShapeKeyControlProperties
    )


def unregister():
    if hasattr(bpy.types.Scene, 'shape_key_keyframe_settings'):
        del bpy.types.Scene.shape_key_keyframe_settings

    if hasattr(bpy.types.Scene, 'shape_key_control_settings'):
        del bpy.types.Scene.shape_key_control_settings

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass


if __name__ == "__main__":
    register()