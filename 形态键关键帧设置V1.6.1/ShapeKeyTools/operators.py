# ShapeKeyAnimator/operators.py
import bpy
import math
import random

from .presets import ShapeKeyPresetGenerator
from .translations import translate_shape_key_name, get_shape_key_category
from .utils import filter_shape_keys_by_category


# ==================== 辅助函数 ====================
def get_visible_shape_keys_with_indices(context):
    """获取当前可见的形态键列表及其原始索引"""
    obj = context.active_object
    if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
        return []

    ctrl_settings = context.scene.shape_key_control_settings
    shape_keys = obj.data.shape_keys.key_blocks

    search_string = ctrl_settings.search_string.lower()
    category_filter = ctrl_settings.category_filter

    visible_items = []  # 格式: [(原始索引, 形态键), ...]

    for idx, shape_key in enumerate( shape_keys ):
        # 跳过参考键
        if shape_key == obj.data.shape_keys.reference_key:
            continue

        # 跳过分界线形态键
        if shape_key.name.startswith( "---" ):
            continue

        # 分类过滤
        if category_filter != 'ALL':
            item_category = get_shape_key_category( shape_key.name )
            if item_category != category_filter:
                continue

        # 搜索过滤
        if search_string:
            translated_name = translate_shape_key_name( shape_key.name, True ).lower()
            if (search_string not in shape_key.name.lower() and
                    search_string not in translated_name):
                continue

        visible_items.append( (idx, shape_key) )

    return visible_items


def get_shape_key_by_name(obj, name):
    """通过名称获取形态键"""
    if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
        return None
    return obj.data.shape_keys.key_blocks.get( name )


# ==================== 多选操作符 ====================
class SelectShapeKeyOperator( bpy.types.Operator ):
    """处理形态键选择操作"""
    bl_idname = "shape_key.select_item"
    bl_label = "选择形态键"

    item_index: bpy.props.IntProperty()

    def invoke(self, context, event):
        # 检测Shift和Ctrl键状态
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            return {'CANCELLED'}

        shape_keys = obj.data.shape_keys.key_blocks
        if self.item_index >= len( shape_keys ):
            return {'CANCELLED'}

        selected_shape_key = shape_keys[self.item_index]

        # 跳过分界线形态键
        if selected_shape_key.name.startswith( "---" ):
            return {'CANCELLED'}

        ctrl_settings = context.scene.shape_key_control_settings

        # 获取当前选择状态
        current_is_selected = any( sel.name == selected_shape_key.name
                                   for sel in ctrl_settings.selected_shape_keys )
        has_multiple_selected = len( ctrl_settings.selected_shape_keys ) > 1

        # 🔧 处理连续选择 (Shift) - 基于可见列表的虚拟索引
        if event.shift and ctrl_settings.selection_anchor_name:
            # 获取当前可见的形态键列表
            visible_items = get_visible_shape_keys_with_indices( context )
            visible_shape_keys = [item[1] for item in visible_items]  # 只提取形态键对象

            # 通过名称找到锚点形态键
            anchor_shape_key = get_shape_key_by_name( obj, ctrl_settings.selection_anchor_name )

            if anchor_shape_key and anchor_shape_key in visible_shape_keys and selected_shape_key in visible_shape_keys:
                # 在可见列表中计算虚拟索引范围
                start_virtual_idx = visible_shape_keys.index( anchor_shape_key )
                end_virtual_idx = visible_shape_keys.index( selected_shape_key )

                start_virtual_idx, end_virtual_idx = min( start_virtual_idx, end_virtual_idx ), max( start_virtual_idx,
                                                                                                     end_virtual_idx )

                # 清除当前选择（如果之前没有按Ctrl）
                if not event.ctrl:
                    ctrl_settings.selected_shape_keys.clear()

                # 只选择可见范围内的项
                for virtual_idx in range( start_virtual_idx, end_virtual_idx + 1 ):
                    if virtual_idx < len( visible_shape_keys ):
                        shape_key = visible_shape_keys[virtual_idx]
                        if not shape_key.name.startswith( "---" ):
                            # 添加到选择集
                            existing = next( (item for item in ctrl_settings.selected_shape_keys
                                              if item.name == shape_key.name), None )
                            if not existing:
                                new_item = ctrl_settings.selected_shape_keys.add()
                                new_item.name = shape_key.name
            else:
                # 如果锚点不在当前可见列表中，回退到单选行为
                ctrl_settings.selected_shape_keys.clear()
                new_item = ctrl_settings.selected_shape_keys.add()
                new_item.name = selected_shape_key.name

        # 处理切换选择 (Ctrl) 或普通点击
        else:
            existing = next( (item for item in ctrl_settings.selected_shape_keys
                              if item.name == selected_shape_key.name), None )

            if event.ctrl:  # Ctrl点击：切换选择状态
                if existing:
                    # 取消选择
                    ctrl_settings.selected_shape_keys.remove(
                        ctrl_settings.selected_shape_keys.find( existing.name )
                    )
                else:
                    # 添加到选择集
                    new_item = ctrl_settings.selected_shape_keys.add()
                    new_item.name = selected_shape_key.name
            else:  # 普通点击
                # 🔧 问题2修复：多选状态下点击已选项 → 取消多选，单选该项
                if current_is_selected and has_multiple_selected:
                    # 清除所有选择，只选中当前项
                    ctrl_settings.selected_shape_keys.clear()
                    new_item = ctrl_settings.selected_shape_keys.add()
                    new_item.name = selected_shape_key.name
                else:
                    # 正常单选行为
                    ctrl_settings.selected_shape_keys.clear()
                    new_item = ctrl_settings.selected_shape_keys.add()
                    new_item.name = selected_shape_key.name

                # 设置选择锚点（基于名称，避免索引问题）
                ctrl_settings.selection_anchor_name = selected_shape_key.name
                ctrl_settings.selection_anchor_index = self.item_index  # 保持向后兼容

        # 更新活动形态键和索引
        ctrl_settings.shape_key_index = self.item_index
        ctrl_settings.active_shape_key = selected_shape_key.name

        # 重绘界面
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        return {'FINISHED'}


class SetMultipleShapeKeyValues( bpy.types.Operator ):
    """批量设置多个形态键的值"""
    bl_idname = "object.set_multiple_shape_key_values"
    bl_label = "批量设置形态键值"

    value: bpy.props.FloatProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            self.report( {'WARNING'}, "请先选择一个具有形态键的对象" )
            return {'CANCELLED'}

        ctrl_settings = context.scene.shape_key_control_settings
        shape_keys = obj.data.shape_keys.key_blocks

        updated_count = 0

        for selected_item in ctrl_settings.selected_shape_keys:
            if selected_item.name in shape_keys:
                shape_key = shape_keys[selected_item.name]
                # 跳过分界线形态键
                if not shape_key.name.startswith( "---" ):
                    shape_key.value = self.value
                    updated_count += 1

        if updated_count > 0:
            self.report( {'INFO'}, f"已更新 {updated_count} 个形态键的值为 {self.value}" )
        else:
            # 如果没有多选，使用当前活动形态键
            if ctrl_settings.active_shape_key and ctrl_settings.active_shape_key in shape_keys:
                shape_key = shape_keys[ctrl_settings.active_shape_key]
                if not shape_key.name.startswith( "---" ):
                    shape_key.value = self.value
                    self.report( {'INFO'}, f"已将 {shape_key.name} 设置为 {self.value}" )

        return {'FINISHED'}


class InsertMultipleShapeKeyKeyframes( bpy.types.Operator ):
    """为多个形态键插入关键帧"""
    bl_idname = "animation.insert_multiple_shape_key_keyframes"
    bl_label = "批量插入关键帧"

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            self.report( {'WARNING'}, "请先选择一个具有形态键的对象" )
            return {'CANCELLED'}

        ctrl_settings = context.scene.shape_key_control_settings
        shape_keys = obj.data.shape_keys.key_blocks

        inserted_count = 0

        for selected_item in ctrl_settings.selected_shape_keys:
            if selected_item.name in shape_keys:
                shape_key = shape_keys[selected_item.name]
                # 跳过分界线形态键
                if not shape_key.name.startswith( "---" ):
                    shape_key.keyframe_insert( data_path="value" )
                    inserted_count += 1

        if inserted_count > 0:
            self.report( {'INFO'}, f"已为 {inserted_count} 个形态键插入关键帧" )
        else:
            # 如果没有多选，使用当前活动形态键
            if ctrl_settings.active_shape_key and ctrl_settings.active_shape_key in shape_keys:
                shape_key = shape_keys[ctrl_settings.active_shape_key]
                if not shape_key.name.startswith( "---" ):
                    shape_key.keyframe_insert( data_path="value" )
                    self.report( {'INFO'}, f"已为 {shape_key.name} 插入关键帧" )

        return {'FINISHED'}


class DeleteMultipleShapeKeyKeyframes( bpy.types.Operator ):
    """删除多个形态键的关键帧"""
    bl_idname = "animation.delete_multiple_shape_key_keyframes"
    bl_label = "批量删除关键帧"

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            self.report( {'WARNING'}, "请先选择一个具有形态键的对象" )
            return {'CANCELLED'}

        ctrl_settings = context.scene.shape_key_control_settings
        shape_keys = obj.data.shape_keys.key_blocks
        current_frame = context.scene.frame_current

        deleted_count = 0

        for selected_item in ctrl_settings.selected_shape_keys:
            if selected_item.name in shape_keys:
                shape_key = shape_keys[selected_item.name]
                # 跳过分界线形态键
                if shape_key.name.startswith( "---" ):
                    continue

                # 获取形态键的fcurve
                action = obj.data.shape_keys.animation_data.action if obj.data.shape_keys.animation_data else None
                if action:
                    for fc in action.fcurves:
                        if fc.data_path == f'key_blocks["{shape_key.name}"].value':
                            # 查找当前帧的关键帧
                            for i, kp in enumerate( fc.keyframe_points ):
                                if abs( kp.co.x - current_frame ) < 0.1:  # 允许一定的浮点误差
                                    fc.keyframe_points.remove( kp )
                                    deleted_count += 1
                                    break

        if deleted_count > 0:
            self.report( {'INFO'}, f"已删除 {deleted_count} 个形态键在当前帧的关键帧" )
        else:
            # 如果没有多选，使用当前活动形态键
            if ctrl_settings.active_shape_key and ctrl_settings.active_shape_key in shape_keys:
                shape_key = shape_keys[ctrl_settings.active_shape_key]
                if not shape_key.name.startswith( "---" ):
                    action = obj.data.shape_keys.animation_data.action if obj.data.shape_keys.animation_data else None
                    if action:
                        for fc in action.fcurves:
                            if fc.data_path == f'key_blocks["{shape_key.name}"].value':
                                for i, kp in enumerate( fc.keyframe_points ):
                                    if abs( kp.co.x - current_frame ) < 0.1:
                                        fc.keyframe_points.remove( kp )
                                        self.report( {'INFO'}, f"已删除 {shape_key.name} 在当前帧的关键帧" )
                                        return {'FINISHED'}

        self.report( {'INFO'}, "未找到关键帧" )
        return {'FINISHED'}


class ClearShapeKeySelection( bpy.types.Operator ):
    """清除所有形态键选择"""
    bl_idname = "shape_key.clear_selection"
    bl_label = "清除选择"

    def execute(self, context):
        ctrl_settings = context.scene.shape_key_control_settings
        ctrl_settings.selected_shape_keys.clear()
        ctrl_settings.selection_anchor_index = -1
        ctrl_settings.selection_anchor_name = ""  # 🔧 清除名称锚点

        # 重绘界面
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report( {'INFO'}, "已清除选择" )
        return {'FINISHED'}


# ==================== 保留原有的关键帧操作符 ====================
class ShapeKeyKeyframeSettings( bpy.types.Operator ):
    bl_idname = "animation.shape_key_keyframe_settings"
    bl_label = "生成形态键动画"
    bl_description = "使用预设模式生成形态键动画关键帧"

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report( {'WARNING'}, "请先选择一个对象" )
            return {'CANCELLED'}

        scene = context.scene
        settings = scene.shape_key_keyframe_settings

        start_frame = settings.start_frame
        end_frame = settings.end_frame
        oscillations = settings.oscillations
        shape_key_name = settings.shape_key_name
        min_value = settings.min_value
        max_value = settings.max_value
        preset_mode = settings.preset_mode

        if start_frame >= end_frame:
            self.report( {'WARNING'}, "起始帧必须小于结束帧" )
            return {'CANCELLED'}

        if not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            self.report( {'WARNING'}, "对象没有形态键" )
            return {'CANCELLED'}

        shape_keys = obj.data.shape_keys.key_blocks
        if shape_key_name not in shape_keys:
            self.report( {'WARNING'}, f"未找到名为 '{shape_key_name}' 的形态键" )
            return {'CANCELLED'}

        shape_key = shape_keys[shape_key_name]

        # 清除现有关键帧
        action = obj.data.shape_keys.animation_data.action if obj.data.shape_keys.animation_data else None
        fcurve = None
        if action:
            for fc in action.fcurves:
                if fc.data_path == f'key_blocks["{shape_key_name}"].value':
                    fcurve = fc
                    break

        if fcurve:
            keyframes_to_remove = [kp for kp in fcurve.keyframe_points if start_frame <= kp.co.x <= end_frame]
            for kp in keyframes_to_remove:
                try:
                    fcurve.keyframe_points.remove( kp )
                except RuntimeError:
                    pass

        # 根据预设模式生成关键帧
        generator = ShapeKeyPresetGenerator()

        for frame in range( int( start_frame ), int( end_frame ) + 1 ):
            if preset_mode == 'SIMPLE':
                value = generator.simple_oscillation( frame, start_frame, end_frame, min_value, max_value,
                                                      oscillations )
            elif preset_mode == 'SINE':
                value = generator.sine_wave( frame, start_frame, end_frame, min_value, max_value,
                                             settings.sine_frequency, settings.sine_phase )
            elif preset_mode == 'SQUARE':
                value = generator.square_wave( frame, start_frame, end_frame, min_value, max_value,
                                               settings.square_duty_cycle )
            elif preset_mode == 'TRIANGLE':
                value = generator.triangle_wave( frame, start_frame, end_frame, min_value, max_value )
            elif preset_mode == 'SAW':
                value = generator.sawtooth_wave( frame, start_frame, end_frame, min_value, max_value )
            elif preset_mode == 'RANDOM':
                value = generator.random_wave( frame, start_frame, end_frame, min_value, max_value,
                                               settings.random_seed, settings.random_smoothness )
            elif preset_mode == 'EASE_IN_OUT':
                value = generator.ease_in_out( frame, start_frame, end_frame, min_value, max_value )
            elif preset_mode == 'BOUNCE':
                value = generator.bounce_effect( frame, start_frame, end_frame, min_value, max_value,
                                                 settings.bounce_count, settings.bounce_decay )
            elif preset_mode == 'BREATH':
                value = generator.breathing_effect( frame, start_frame, end_frame, min_value, max_value,
                                                    settings.breath_intensity, settings.breath_hold )
            else:
                value = min_value

            shape_key.value = value
            shape_key.keyframe_insert( data_path="value", frame=frame )

        self.report( {'INFO'}, f"形态键 {preset_mode} 动画生成成功" )
        return {'FINISHED'}


class DeleteShapeKeyKeyframes( bpy.types.Operator ):
    bl_idname = "animation.delete_shape_key_keyframes"
    bl_label = "删除形态键关键帧"
    bl_description = "删除指定帧范围内的形态键关键帧"

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report( {'WARNING'}, "请先选择一个对象" )
            return {'CANCELLED'}

        scene = context.scene
        settings = scene.shape_key_keyframe_settings

        start_frame = settings.start_frame
        end_frame = settings.end_frame
        shape_key_name = settings.shape_key_name

        if start_frame >= end_frame:
            self.report( {'WARNING'}, "起始帧必须小于结束帧" )
            return {'CANCELLED'}

        if not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            self.report( {'WARNING'}, "对象没有形态键" )
            return {'CANCELLED'}

        shape_keys = obj.data.shape_keys.key_blocks
        if shape_key_name not in shape_keys:
            self.report( {'WARNING'}, f"未找到名为 '{shape_key_name}' 的形态键" )
            return {'CANCELLED'}

        action = obj.data.shape_keys.animation_data.action if obj.data.shape_keys.animation_data else None
        if not action:
            self.report( {'WARNING'}, "没有找到动画数据" )
            return {'CANCELLED'}

        fcurve = None
        for fc in action.fcurves:
            if fc.data_path == f'key_blocks["{shape_key_name}"].value':
                fcurve = fc
                break

        if not fcurve:
            self.report( {'WARNING'}, f"未找到形态键 '{shape_key_name}' 的动画曲线" )
            return {'CANCELLED'}

        indices_to_remove = [i for i, kp in enumerate( fcurve.keyframe_points ) if start_frame <= kp.co.x <= end_frame]
        removed_count = 0

        for i in sorted( indices_to_remove, reverse=True ):
            try:
                fcurve.keyframe_points.remove( fcurve.keyframe_points[i] )
                removed_count += 1
            except RuntimeError:
                pass

        if len( fcurve.keyframe_points ) == 0:
            action.fcurves.remove( fcurve )

        self.report( {'INFO'}, f"已删除 {removed_count} 个关键帧" )
        return {'FINISHED'}


class InsertShapeKeyKeyframe( bpy.types.Operator ):
    bl_idname = "animation.insert_shape_key_keyframe"
    bl_label = "插入形态键关键帧"
    bl_description = "在当前帧插入形态键关键帧"

    shape_key_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            self.report( {'WARNING'}, "请先选择一个具有形态键的对象" )
            return {'CANCELLED'}

        shape_keys = obj.data.shape_keys.key_blocks
        if self.shape_key_name not in shape_keys:
            self.report( {'WARNING'}, f"未找到名为 '{self.shape_key_name}' 的形态键" )
            return {'CANCELLED'}

        # 检查是否是分界线形态键
        if self.shape_key_name.startswith( "---" ):
            self.report( {'WARNING'}, "分界线形态键不可操作" )
            return {'CANCELLED'}

        shape_key = shape_keys[self.shape_key_name]
        shape_key.keyframe_insert( data_path="value" )

        # 更新活动形态键
        context.scene.shape_key_control_settings.active_shape_key = self.shape_key_name

        self.report( {'INFO'}, f"已为 {self.shape_key_name} 插入关键帧" )
        return {'FINISHED'}


class DeleteCurrentShapeKeyKeyframe( bpy.types.Operator ):
    bl_idname = "animation.delete_current_shape_key_keyframe"
    bl_label = "删除当前关键帧"
    bl_description = "删除当前帧的形态键关键帧"

    shape_key_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            self.report( {'WARNING'}, "请先选择一个具有形态键的对象" )
            return {'CANCELLED'}

        shape_keys = obj.data.shape_keys.key_blocks
        if self.shape_key_name not in shape_keys:
            self.report( {'WARNING'}, f"未找到名为 '{self.shape_key_name}' 的形态键" )
            return {'CANCELLED'}

        # 检查是否是分界线形态键
        if self.shape_key_name.startswith( "---" ):
            self.report( {'WARNING'}, "分界线形态键不可操作" )
            return {'CANCELLED'}

        shape_key = shape_keys[self.shape_key_name]

        # 获取当前帧
        current_frame = context.scene.frame_current

        # 获取形态键的fcurve
        action = obj.data.shape_keys.animation_data.action if obj.data.shape_keys.animation_data else None
        if action:
            for fc in action.fcurves:
                if fc.data_path == f'key_blocks["{self.shape_key_name}"].value':
                    # 查找当前帧的关键帧
                    for i, kp in enumerate( fc.keyframe_points ):
                        if abs( kp.co.x - current_frame ) < 0.1:  # 允许一定的浮点误差
                            fc.keyframe_points.remove( kp )
                            self.report( {'INFO'}, f"已删除 {self.shape_key_name} 在当前帧的关键帧" )
                            return {'FINISHED'}

        self.report( {'INFO'}, f"未找到 {self.shape_key_name} 在当前帧的关键帧" )
        return {'FINISHED'}


class SetShapeKeyValue( bpy.types.Operator ):
    bl_idname = "object.set_shape_key_value"
    bl_label = "设置形态键值"
    bl_description = "设置形态键的值"

    shape_key: bpy.props.StringProperty()
    value: bpy.props.FloatProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            self.report( {'WARNING'}, "请先选择一个具有形态键的对象" )
            return {'CANCELLED'}

        shape_keys = obj.data.shape_keys.key_blocks
        if self.shape_key in shape_keys:
            # 检查是否是分界线形态键
            if self.shape_key.startswith( "---" ):
                self.report( {'WARNING'}, "分界线形态键不可操作" )
                return {'CANCELLED'}

            shape_key = shape_keys[self.shape_key]
            shape_key.value = self.value

            # 更新活动形态键
            context.scene.shape_key_control_settings.active_shape_key = self.shape_key

            self.report( {'INFO'}, f"已将 {self.shape_key} 设置为 {self.value}" )
        else:
            self.report( {'WARNING'}, f"未找到形态键: {self.shape_key}" )

        return {'FINISHED'}


class RefreshShapeKeyMonitor( bpy.types.Operator ):
    bl_idname = "animation.refresh_shape_key_monitor"
    bl_label = "刷新监测"
    bl_description = "刷新形态键使用状态监测"

    def execute(self, context):
        # 强制重绘界面
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        self.report( {'INFO'}, "形态键监测已刷新" )
        return {'FINISHED'}


class CopyQQGroup( bpy.types.Operator ):
    bl_idname = "shape_key.copy_qq_group"
    bl_label = "复制QQ群号"
    bl_description = "复制QQ群号到剪贴板"

    def execute(self, context):
        context.window_manager.clipboard = "1042375616"
        self.report( {'INFO'}, "QQ群号已复制到剪贴板: 1042375616" )
        return {'FINISHED'}


class PreviousShapeKey( bpy.types.Operator ):
    bl_idname = "shape_key.previous"
    bl_label = "上一个形态键"
    bl_description = "切换到上一个形态键"

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            return {'CANCELLED'}

        shape_keys = obj.data.shape_keys.key_blocks

        # 获取所有形态键（包括分界线）
        all_shape_keys = list( shape_keys )

        # 获取当前索引
        ctrl_settings = context.scene.shape_key_control_settings
        current_index = ctrl_settings.shape_key_index

        # 找到上一个非分界线形态键
        new_index = current_index
        for i in range( 1, len( all_shape_keys ) ):
            prev_index = (current_index - i) % len( all_shape_keys )
            shape_key = all_shape_keys[prev_index]

            # 跳过参考键和分界线
            if shape_key == obj.data.shape_keys.reference_key or shape_key.name.startswith( "---" ):
                continue

            new_index = prev_index
            break

        # 更新索引
        ctrl_settings.shape_key_index = new_index

        # 更新活动形态键
        if 0 <= new_index < len( all_shape_keys ):
            shape_key = all_shape_keys[new_index]
            if not shape_key.name.startswith( "---" ):
                context.scene.shape_key_control_settings.active_shape_key = shape_key.name

        return {'FINISHED'}


class NextShapeKey( bpy.types.Operator ):
    bl_idname = "shape_key.next"
    bl_label = "下一个形态键"
    bl_description = "切换到下一个形态键"

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            return {'CANCELLED'}

        shape_keys = obj.data.shape_keys.key_blocks

        # 获取所有形态键（包括分界线）
        all_shape_keys = list( shape_keys )

        # 获取当前索引
        ctrl_settings = context.scene.shape_key_control_settings
        current_index = ctrl_settings.shape_key_index

        # 找到下一个非分界线形态键
        new_index = current_index
        for i in range( 1, len( all_shape_keys ) ):
            next_index = (current_index + i) % len( all_shape_keys )
            shape_key = all_shape_keys[next_index]

            # 跳过参考键和分界线
            if shape_key == obj.data.shape_keys.reference_key or shape_key.name.startswith( "---" ):
                continue

            new_index = next_index
            break

        # 更新索引
        ctrl_settings.shape_key_index = new_index

        # 更新活动形态键
        if 0 <= new_index < len( all_shape_keys ):
            shape_key = all_shape_keys[new_index]
            if not shape_key.name.startswith( "---" ):
                context.scene.shape_key_control_settings.active_shape_key = shape_key.name

        return {'FINISHED'}


class ClearSearch( bpy.types.Operator ):
    bl_idname = "shape_key.clear_search"
    bl_label = "清除搜索"
    bl_description = "清除搜索框内容"

    def execute(self, context):
        context.scene.shape_key_control_settings.search_string = ""
        return {'FINISHED'}


class ResetAllMonitorShapeKeys( bpy.types.Operator ):
    bl_idname = "shape_key.reset_all_monitor_shape_keys"
    bl_label = "一键调0值"
    bl_description = "将监测区域中所有显示的形态键设置为0值"

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            self.report( {'WARNING'}, "请先选择一个具有形态键的对象" )
            return {'CANCELLED'}

        # 获取监测区域中显示的形态键列表
        from .panels import CombinedShapeKeyPanel
        used_shape_keys = CombinedShapeKeyPanel.get_used_shape_keys( obj )

        if not used_shape_keys:
            self.report( {'INFO'}, "监测区域中没有正在使用的形态键" )
            return {'FINISHED'}

        reset_count = 0
        for shape_key in used_shape_keys:
            # 跳过分界线形态键
            if shape_key.name.startswith( "---" ):
                continue
            
            # 设置形态键值为0
            shape_key.value = 0.0
            reset_count += 1

        self.report( {'INFO'}, f"已将 {reset_count} 个形态键设置为0值" )
        return {'FINISHED'}
