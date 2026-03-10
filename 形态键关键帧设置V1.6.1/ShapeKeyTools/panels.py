# ShapeKeyAnimator/panels.py
import bpy

from .translations import translate_shape_key_name, get_shape_key_category
from .utils import filter_shape_keys_by_category


# ==================== UIList支持多选显示 ====================
class SHAPEKEY_UL_list( bpy.types.UIList ):
    """自定义形态键列表 - 支持多选显示"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        obj = context.active_object
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            return

        ctrl_settings = context.scene.shape_key_control_settings

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # 检查是否被选中
            is_selected = any( sel.name == item.name for sel in ctrl_settings.selected_shape_keys )
            is_multiple_selected = len( ctrl_settings.selected_shape_keys ) > 1
            is_anchor = (item.name == ctrl_settings.selection_anchor_name)

            row = layout.row()

            # 🔧 优化：更明确的选择状态显示
            if is_selected:
                if is_multiple_selected:
                    row.label( text="", icon='CHECKBOX_HLT' )  # 多选中的一项
                else:
                    row.label( text="", icon='RESTRICT_SELECT_OFF' )  # 单选状态
            else:
                row.label( text="", icon='CHECKBOX_DEHLT' )

            # 如果是锚点，显示特殊图标
            if is_anchor:
                row.label( text="", icon='PIVOT_CURSOR' )

            if item.name.startswith( "---" ):
                row.label( text=item.name, icon='NONE' )
            else:
                # 根据设置显示翻译或原始名称
                display_name = translate_shape_key_name( item.name, ctrl_settings.show_translation )
                # 创建可点击的名称标签
                op = row.operator( "shape_key.select_item", text=display_name, emboss=False, icon='SHAPEKEY_DATA' )
                op.item_index = list( obj.data.shape_keys.key_blocks ).index( item )

                # 如果启用了翻译，在底部显示原始名称
                if ctrl_settings.show_translation:
                    sub_row = layout.row()
                    sub_row.scale_y = 0.7
                    sub_row.label( text=f"({item.name})", icon='NONE' )

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label( text="", icon='SHAPEKEY_DATA' )

    def filter_items(self, context, data, propname):
        search_string = context.scene.shape_key_control_settings.search_string.lower()
        category_filter = context.scene.shape_key_control_settings.category_filter
        shape_keys = getattr( data, propname )

        flt_flags = []
        flt_neworder = []

        if not search_string and category_filter == 'ALL':
            flt_flags = [self.bitflag_filter_item] * len( shape_keys )
            return flt_flags, flt_neworder

        for item in shape_keys:
            # 检查分类过滤
            if category_filter != 'ALL':
                item_category = get_shape_key_category( item.name )
                if item_category != category_filter:
                    flt_flags.append( 0 )
                    continue

            # 检查搜索字符串
            if search_string:
                # 同时搜索原始名称和翻译名称
                translated_name = translate_shape_key_name( item.name, True ).lower()
                if (search_string in item.name.lower() or
                        search_string in translated_name):
                    flt_flags.append( self.bitflag_filter_item )
                else:
                    flt_flags.append( 0 )
            else:
                flt_flags.append( self.bitflag_filter_item )

        return flt_flags, flt_neworder


# ==================== 更新：组合面板 ====================
class CombinedShapeKeyPanel( bpy.types.Panel ):
    bl_label = "形态键工具V1.6.1"
    bl_idname = "VIEW3D_PT_combined_shape_key_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MMD"
    bl_order = 1

    @staticmethod
    def get_used_shape_keys(obj):
        """获取已使用的形态键列表（值不为0的形态键）"""
        used_shape_keys = []

        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            return used_shape_keys

        shape_keys = obj.data.shape_keys.key_blocks
        for shape_key in shape_keys:
            if shape_key == obj.data.shape_keys.reference_key:
                continue

            if shape_key.value > 0.0:
                used_shape_keys.append( shape_key )

        return used_shape_keys

    def draw_shape_key_monitor(self, context, layout, obj):
        """绘制形态键监测面板"""
        monitor_box = layout.box()

        header_row = monitor_box.row()
        header_row.label( text="形态键监测", icon='VIEWZOOM' )

        settings_row = header_row.row( align=True )
        settings_row.prop( context.scene.shape_key_control_settings, "show_monitor_panel",
                           text="",
                           icon='DISCLOSURE_TRI_DOWN' if context.scene.shape_key_control_settings.show_monitor_panel else 'DISCLOSURE_TRI_RIGHT' )
        settings_row.prop( context.scene.shape_key_control_settings, "monitor_auto_refresh",
                           text="", icon='FILE_REFRESH' )

        if not context.scene.shape_key_control_settings.show_monitor_panel:
            return

        used_shape_keys = self.get_used_shape_keys( obj )

        if not used_shape_keys:
            monitor_box.label( text="没有正在使用的形态键" )
            return

        refresh_row = monitor_box.row()
        refresh_row.operator( "animation.refresh_shape_key_monitor", text="手动刷新" )
        refresh_row.operator( "shape_key.reset_all_monitor_shape_keys", text="一键调0值" )
        refresh_row.label( text=f"使用中: {len( used_shape_keys )}" )

        scroll_area = monitor_box.column()

        header = scroll_area.row()
        header.label( text="名称" )
        header.label( text="当前值" )
        header.label( text="状态" )
        header.label( text="操作" )

        scroll_area.separator()

        action = obj.data.shape_keys.animation_data.action if obj.data.shape_keys.animation_data else None

        for shape_key in used_shape_keys:
            if shape_key.name.startswith( "---" ):
                continue

            row = scroll_area.row()

            # 根据设置显示翻译或原始名称
            ctrl_settings = context.scene.shape_key_control_settings
            display_name = translate_shape_key_name( shape_key.name, ctrl_settings.show_translation )
            name_col = row.column()
            name_col.label( text=display_name[:15] + "..." if len( display_name ) > 15 else display_name )

            value_col = row.column()
            value_col.label( text=f"{shape_key.value:.2f}" )

            status_col = row.column()

            has_keyframe_current = False
            has_animation = False

            if action:
                current_frame = context.scene.frame_current
                for fcurve in action.fcurves:
                    if fcurve.data_path == f'key_blocks["{shape_key.name}"].value':
                        has_animation = True
                        for kp in fcurve.keyframe_points:
                            if abs( kp.co.x - current_frame ) < 0.1:
                                has_keyframe_current = True
                                break

            if has_keyframe_current:
                status_col.label( text="", icon='KEY_HLT' )
            elif has_animation:
                status_col.label( text="", icon='KEYFRAME_HLT' )
            else:
                status_col.label( text="", icon='SHAPEKEY_DATA' )

            ops_col = row.column( align=True )
            ops_row = ops_col.row( align=True )

            # 修复：确保操作符正确传递参数
            op_0 = ops_row.operator( "object.set_shape_key_value", text="0" )
            op_0.shape_key = shape_key.name
            op_0.value = 0.0

            op_1 = ops_row.operator( "object.set_shape_key_value", text="1" )
            op_1.shape_key = shape_key.name
            op_1.value = 1.0

            op_insert = ops_row.operator( "animation.insert_shape_key_keyframe", text="", icon='KEY_HLT' )
            op_insert.shape_key_name = shape_key.name

            op_delete = ops_row.operator( "animation.delete_current_shape_key_keyframe", text="", icon='KEY_DEHLT' )
            op_delete.shape_key_name = shape_key.name

    def get_preset_description(self, preset_mode):
        """获取预设模式的详细描述"""
        descriptions = {
            'SIMPLE': "基础振荡模式 - 在指定范围内进行简单的开关切换\n推荐值: 振荡次数 1-5",
            'SINE': "平滑的正弦波 - 适合自然的周期性动画\n推荐值: 频率 0.5-2.0",
            'SQUARE': "方波模式 - 创建机械式的开关效果\n推荐值: 占空比 0.3-0.7",
            'TRIANGLE': "三角波 - 线性渐变效果\n适合扫描或渐变动画",
            'SAW': "锯齿波 - 单向递增然后重置\n适合累积效果",
            'RANDOM': "随机变化 - 自然的随机动画\n推荐值: 平滑度 0.3-0.7",
            'EASE_IN_OUT': "缓入缓出 - 平滑的加速减速\n适合自然的过渡动画",
            'BOUNCE': "弹跳效果 - 模拟物理弹跳\n推荐值: 弹跳次数 2-5, 衰减 0.5-0.8",
            'BREATH': "呼吸节奏 - 模拟自然的呼吸模式\n推荐值: 强度 0.6-1.0, 屏息时间 0.1-0.3"
        }
        return descriptions.get( preset_mode, "无描述" )

    def get_preset_icon(self, preset_mode):
        """获取预设模式的图标"""
        icons = {
            'SIMPLE': 'IPO_CONSTANT',
            'SINE': 'IPO_SINE',
            'SQUARE': 'IPO_QUAD',
            'TRIANGLE': 'IPO_LINEAR',
            'SAW': 'IPO_BACK',
            'RANDOM': 'QUIT',
            'EASE_IN_OUT': 'IPO_EASE_IN_OUT',
            'BOUNCE': 'RNDCURVE',
            'BREATH': 'FORCE_HARMONIC'
        }
        return icons.get( preset_mode, 'SETTINGS' )

    def draw_preset_parameters(self, context, layout, settings):
        """根据选择的预设模式显示相应的参数"""
        preset_mode = settings.preset_mode

        desc_box = layout.box()
        desc_row = desc_box.row()
        desc_row.label( text="模式说明:", icon=self.get_preset_icon( preset_mode ) )
        description = self.get_preset_description( preset_mode )

        lines = description.split( '\n' )
        for line in lines:
            desc_box.label( text=line )

        if preset_mode == 'SIMPLE':
            layout.prop( settings, "oscillations" )
            layout.label( text="提示: 0=从最小值渐变到最大值", icon='INFO' )
        elif preset_mode == 'SINE':
            layout.prop( settings, "sine_frequency" )
            layout.label( text="频率: 值越大波形越密集", icon='INFO' )
            layout.prop( settings, "sine_phase" )
            layout.label( text="相位: 调整波形起始位置", icon='INFO' )
        elif preset_mode == 'SQUARE':
            layout.prop( settings, "square_duty_cycle" )
            layout.label( text="占空比: 控制高低电平比例", icon='INFO' )
        elif preset_mode == 'RANDOM':
            layout.prop( settings, "random_seed" )
            layout.label( text="种子: 相同种子产生相同随机序列", icon='INFO' )
            layout.prop( settings, "random_smoothness" )
            layout.label( text="平滑度: 值越大变化越平缓", icon='INFO' )
        elif preset_mode == 'BOUNCE':
            layout.prop( settings, "bounce_count" )
            layout.label( text="弹跳次数: 值越大弹跳越多", icon='INFO' )
            layout.prop( settings, "bounce_decay" )
            layout.label( text="衰减: 值越小弹跳衰减越快", icon='INFO' )
        elif preset_mode == 'BREATH':
            layout.prop( settings, "breath_intensity" )
            layout.label( text="强度: 控制呼吸深浅", icon='INFO' )
            layout.prop( settings, "breath_hold" )
            layout.label( text="屏息时间: 吸气后的停顿时间", icon='INFO' )
        elif preset_mode in ['TRIANGLE', 'SAW', 'EASE_IN_OUT']:
            layout.label( text="此模式无需额外参数", icon='INFO' )

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        kf_settings = scene.shape_key_keyframe_settings
        ctrl_settings = scene.shape_key_control_settings

        # 作者信息
        info_col = layout.column()
        info_col.label( text="by_FK" )
        info_col.label( text="插件如有问题欢迎各位大佬反馈" )

        qq_row = info_col.row( align=True )
        qq_row.label( text="Q群：1042375616" )
        qq_row.operator( "shape_key.copy_qq_group", text="", icon='COPYDOWN' )

        info_col.separator()

        obj = context.active_object

        # 检查对象是否支持形态键（网格对象）
        if not obj or not obj.data or not hasattr(obj.data, 'shape_keys') or not obj.data.shape_keys:
            warning_box = layout.box()
            warning_box.alert = True
            warning_row = warning_box.row()
            warning_row.label( text="", icon='ERROR' )
            warning_row.label( text="请选择一个具有形态键的对象", icon='SHAPEKEY_DATA' )
            warning_row.label( text="", icon='ERROR' )
            return

        main_col = layout.column()

        # 1.1 形态键关键帧设置部分
        frame_box = main_col.box()
        header_row = frame_box.row()
        header_row.prop( ctrl_settings, "show_keyframe_settings",
                         text="1.1 形态键动画预设",
                         icon='DISCLOSURE_TRI_DOWN' if ctrl_settings.show_keyframe_settings else 'DISCLOSURE_TRI_RIGHT',
                         emboss=False )

        if ctrl_settings.show_keyframe_settings:
            basic_box = frame_box.box()
            basic_box.label( text="基础设置:", icon='SETTINGS' )
            basic_box.prop_search( kf_settings, "shape_key_name", obj.data.shape_keys, "key_blocks", text="形态键" )

            range_row = basic_box.row()
            range_row.prop( kf_settings, "start_frame" )
            range_row.prop( kf_settings, "end_frame" )

            value_row = basic_box.row()
            value_row.prop( kf_settings, "min_value" )
            value_row.prop( kf_settings, "max_value" )

            preset_box = frame_box.box()
            preset_box.label( text="动画预设:", icon='ACTION' )
            preset_row = preset_box.row()
            preset_row.prop( kf_settings, "preset_mode", text="模式" )

            params_box = frame_box.box()
            params_box.label( text="模式参数:", icon='PROPERTIES' )
            self.draw_preset_parameters( context, params_box, kf_settings )

            action_box = frame_box.box()
            action_box.label( text="操作:", icon='PLAY' )
            row = action_box.row()
            row.operator( "animation.shape_key_keyframe_settings", text="生成动画", icon='FILE_REFRESH' )
            row.operator( "animation.delete_shape_key_keyframes", text="清除动画", icon='TRASH' )

            tip_box = frame_box.box()
            tip_box.label( text="使用提示:", icon='LIGHT' )
            tip_box.label( text="1. 先选择形态键和设置帧范围" )
            tip_box.label( text="2. 选择适合的预设模式" )
            tip_box.label( text="3. 调整参数后点击生成动画" )
            tip_box.label( text="4. 不满意可以清除后重新生成" )

        main_col.separator()

        # 形态键监测面板
        self.draw_shape_key_monitor( context, main_col, obj )

        main_col.separator()

        # 1.2 形态键直接控制部分
        control_box = main_col.box()
        header_row = control_box.row()
        header_row.prop( ctrl_settings, "show_direct_control",
                         text="1.2 形态键直接控制",
                         icon='DISCLOSURE_TRI_DOWN' if ctrl_settings.show_direct_control else 'DISCLOSURE_TRI_RIGHT',
                         emboss=False )

        if not ctrl_settings.show_direct_control:
            return

        shape_keys = obj.data.shape_keys.key_blocks
        all_shape_keys = list( shape_keys )

        if not all_shape_keys:
            control_box.label( text="没有可控制的形态键" )
            return

        # 使用临时变量处理索引，避免在draw方法中修改场景数据
        shape_key_index = ctrl_settings.shape_key_index
        if shape_key_index >= len( all_shape_keys ):
            shape_key_index = 0

        current_shape_key = None
        if 0 <= shape_key_index < len( all_shape_keys ):
            current_shape_key = all_shape_keys[shape_key_index]

        # 1.2.1 搜索区域
        search_section = control_box.box()
        search_section.label( text="搜索形态键:", icon='VIEWZOOM' )

        search_row = search_section.row()
        search_row.prop( ctrl_settings, "search_string", text="", icon='VIEWZOOM' )

        if ctrl_settings.search_string:
            search_row.operator( "shape_key.clear_search", text="", icon='X' )

        if ctrl_settings.search_string:
            filtered_keys = filter_shape_keys_by_category( all_shape_keys, ctrl_settings.category_filter )
            search_count = sum( 1 for sk in filtered_keys if
                                ctrl_settings.search_string.lower() in sk.name.lower() or
                                ctrl_settings.search_string.lower() in translate_shape_key_name( sk.name,
                                                                                                 True ).lower() )
            search_row.label( text=f"找到 {search_count} 个" )

        # ==================== 多选状态显示 ====================
        selection_section = control_box.box()
        selection_row = selection_section.row()

        selected_count = len( ctrl_settings.selected_shape_keys )
        if selected_count > 1:
            selection_row.label( text=f"已选择 {selected_count} 个形态键", icon='CHECKBOX_HLT' )
            selection_row.operator( "shape_key.clear_selection", text="清除选择", icon='X' )
        elif selected_count == 1:
            selection_row.label( text="已选择 1 个形态键", icon='CHECKBOX_HLT' )
            selection_row.operator( "shape_key.clear_selection", text="清除选择", icon='X' )
        else:
            selection_row.label( text="未选择形态键", icon='CHECKBOX_DEHLT' )

        # 1.2.2 当前选择上下文信息
        current_section = control_box.box()
        if current_shape_key:
            display_name = translate_shape_key_name( current_shape_key.name, ctrl_settings.show_translation )
            current_row = current_section.row()
            current_row.label( text=f"当前焦点: {display_name}" )

            category = get_shape_key_category( current_shape_key.name )
            category_display = {
                'MOUTH': '嘴', 'EYEBROW': '眉', 'EYE': '目', 'MATERIAL': '材质变形', 'OTHER': '其他'
            }.get( category, '其他' )

            category_row = current_section.row()
            category_row.label( text=f"分类: {category_display}" )

            # 如果启用了翻译，显示原始名称
            if ctrl_settings.show_translation:
                original_row = current_section.row()
                original_row.scale_y = 0.8
                original_row.label( text=f"原始名称: {current_shape_key.name}" )

            if current_shape_key.name.startswith( "---" ):
                current_row = current_section.row()
                current_row.alert = True
                current_row.label( text="这是分界线，不可操作", icon='ERROR' )
        else:
            current_section.label( text="当前: 未选择" )

        # 1.2.3 分类形态键列表
        list_section = control_box.box()
        list_section.label( text="分类形态键列表:", icon='OUTLINER_DATA_POINTCLOUD' )

        # 翻译开关
        translation_row = list_section.row()
        translation_row.prop( ctrl_settings, "show_translation", text="显示中文翻译" )

        # 1.2.3.1 分类选择器
        category_box = list_section.box()
        category_row = category_box.row( align=True )
        category_row.label( text="分类:" )
        category_row.prop( ctrl_settings, "category_filter", expand=True )

        if ctrl_settings.category_filter != 'ALL':
            filtered_count = len( filter_shape_keys_by_category( all_shape_keys, ctrl_settings.category_filter ) )
            category_row.label( text=f"({filtered_count}个)" )

        # 形态键列表 - 保持原有的拉条界面
        row = list_section.row()
        col = row.column()

        col.template_list(
            "SHAPEKEY_UL_list",
            "shape_key_list",
            obj.data.shape_keys,
            "key_blocks",
            ctrl_settings,
            "shape_key_index",
            rows=6  # 保持合适的显示行数
        )

        nav_col = row.column( align=True )
        nav_col.operator( "shape_key.previous", text="", icon='TRIA_UP' )
        nav_col.operator( "shape_key.next", text="", icon='TRIA_DOWN' )

        # 1.2.4 数值控制区域
        control_box.separator()
        control_section = control_box.box()
        control_section.label( text="控制区域:", icon='TOOL_SETTINGS' )

        selected_count = len( ctrl_settings.selected_shape_keys )

        if selected_count > 1:
            # 多选时的控制界面
            control_section.label( text=f"同时控制 {selected_count} 个形态键", icon='GROUP_BONE' )

            # 多选数值滑块
            slider_row = control_section.row()
            slider_row.prop( ctrl_settings, "multi_select_value", text="精确控制", slider=True )

            # 批量快速设置
            quick_row = control_section.row( align=True )
            quick_row.label( text="快速设置:" )
            op_0 = quick_row.operator( "object.set_multiple_shape_key_values", text="全部设为0" )
            op_0.value = 0.0
            op_1 = quick_row.operator( "object.set_multiple_shape_key_values", text="全部设为1" )
            op_1.value = 1.0

            # 批量关键帧操作
            keyframe_row = control_section.row( align=True )
            keyframe_row.label( text="关键帧:" )
            keyframe_row.operator( "animation.insert_multiple_shape_key_keyframes", text="批量插入", icon='KEY_HLT' )
            keyframe_row.operator( "animation.delete_multiple_shape_key_keyframes", text="批量删除", icon='KEY_DEHLT' )

        elif selected_count == 1 or (current_shape_key and not current_shape_key.name.startswith( "---" )):
            # 单选时的控制界面（保持原有行为）
            shape_key_to_control = current_shape_key
            if selected_count == 1:
                # 如果只有一个选中项，使用选中项
                selected_name = ctrl_settings.selected_shape_keys[0].name
                if selected_name in shape_keys:
                    shape_key_to_control = shape_keys[selected_name]

            if shape_key_to_control:
                control_section.prop( shape_key_to_control, "value", text="数值控制", slider=True )

                quick_row = control_section.row( align=True )
                quick_row.label( text="快速设置:" )
                op_0 = quick_row.operator( "object.set_shape_key_value", text="0" )
                op_0.shape_key = shape_key_to_control.name
                op_0.value = 0.0
                op_1 = quick_row.operator( "object.set_shape_key_value", text="1" )
                op_1.shape_key = shape_key_to_control.name
                op_1.value = 1.0

                keyframe_row = control_section.row( align=True )
                keyframe_row.label( text="关键帧:" )
                op_insert = keyframe_row.operator( "animation.insert_shape_key_keyframe", text="插入", icon='KEY_HLT' )
                op_insert.shape_key_name = shape_key_to_control.name
                op_delete = keyframe_row.operator( "animation.delete_current_shape_key_keyframe", text="删除",
                                                   icon='KEY_DEHLT' )
                op_delete.shape_key_name = shape_key_to_control.name
