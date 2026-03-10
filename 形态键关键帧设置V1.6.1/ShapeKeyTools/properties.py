# ShapeKeyAnimator/properties.py
import bpy
import math


# ==================== 多选支持属性组 ====================
class ShapeKeySelectionItem(bpy.types.PropertyGroup):
    """单个形态键选择项"""
    name: bpy.props.StringProperty(name="形态键名称")


# ==================== 更新：控制属性组 ====================
class ShapeKeyControlProperties(bpy.types.PropertyGroup):
    active_shape_key: bpy.props.StringProperty(
        name="活动形态键",
        description="当前选择的形态键",
        default="",
    )

    # 分类选择
    category_filter: bpy.props.EnumProperty(
        name="分类过滤",
        description="按类别过滤形态键",
        items=[
            ('ALL', "全部", "显示所有形态键"),
            ('MOUTH', "嘴", "嘴巴相关的形态键"),
            ('EYEBROW', "眉", "眉毛相关的形态键"),
            ('EYE', "目", "眼睛相关的形态键"),
            ('MATERIAL', "材质变形", "材质相关的形态键"),
            ('OTHER', "其他形态键", "其他类型的形态键"),
        ],
        default='ALL'
    )

    # 翻译开关
    show_translation: bpy.props.BoolProperty(
        name="显示中文翻译",
        description="显示形态键的中文翻译名称",
        default=False,
    )

    # 监测面板显示设置
    show_monitor_panel: bpy.props.BoolProperty(
        name="显示监测面板",
        description="显示形态键使用状态监测面板",
        default=True,
    )
    monitor_auto_refresh: bpy.props.BoolProperty(
        name="自动刷新",
        description="自动刷新形态键状态监测",
        default=True,
    )

    # 形态键列表索引
    shape_key_index: bpy.props.IntProperty(
        name="形态键索引",
        description="当前选择的形态键在列表中的索引",
        default=0,
        min=0,
    )

    # 搜索字符串
    search_string: bpy.props.StringProperty(
        name="搜索",
        description="搜索形态键名称",
        default="",
        options={'TEXTEDIT_UPDATE'}
    )

    # 1.1部分折叠状态
    show_keyframe_settings: bpy.props.BoolProperty(
        name="显示关键帧设置",
        description="显示1.1形态键关键帧设置部分",
        default=False,
    )

    # 1.2部分折叠状态
    show_direct_control: bpy.props.BoolProperty(
        name="显示直接控制",
        description="显示1.2形态键直接控制部分",
        default=True,
    )

    # ==================== 多选相关属性 ====================
    selection_anchor_index: bpy.props.IntProperty(
        name="选择锚点索引",
        description="连续选择的起始索引",
        default=-1,
    )

    # 🔧 新增：基于名称的锚点（解决索引混乱问题）
    selection_anchor_name: bpy.props.StringProperty(
        name="选择锚点名称",
        description="连续选择的起始形态键名称",
        default="",
    )

    selected_shape_keys: bpy.props.CollectionProperty(
        type=ShapeKeySelectionItem,
        name="选中的形态键"
    )

    # 新增：多选时的统一数值控制
    multi_select_value: bpy.props.FloatProperty(
        name="多选数值",
        description="同时设置所有选中形态键的数值",
        default=0.5,
        min=0.0,
        max=1.0,
        precision=3,
        update=lambda self, context: self.update_multi_select_values(context)
    )

    def update_multi_select_values(self, context):
        """当多选数值改变时更新所有选中的形态键"""
        obj = context.active_object
        if not obj or not obj.data.shape_keys:
            return

        shape_keys = obj.data.shape_keys.key_blocks
        value = self.multi_select_value

        # 更新所有选中的形态键
        for selected_item in self.selected_shape_keys:
            if selected_item.name in shape_keys:
                shape_key = shape_keys[selected_item.name]
                if not shape_key.name.startswith("---"):
                    shape_key.value = value


# ==================== 关键帧设置属性组 ====================
class ShapeKeyKeyframeSettingsProperties(bpy.types.PropertyGroup):
    shape_key_name: bpy.props.StringProperty(
        name="形态键名称",
        description="要设置关键帧的形态键名称",
        default=""
    )

    start_frame: bpy.props.IntProperty(
        name="起始帧",
        description="动画起始帧",
        default=0
    )

    end_frame: bpy.props.IntProperty(
        name="结束帧",
        description="动画结束帧",
        default=50
    )

    oscillations: bpy.props.IntProperty(
        name="振荡次数",
        description="振荡次数",
        default=1,
        min=0
    )

    min_value: bpy.props.FloatProperty(
        name="最小值",
        description="最小值",
        default=0.0,
        min=0.0,
        max=1.0
    )

    max_value: bpy.props.FloatProperty(
        name="最大值",
        description="最大值",
        default=1.0,
        min=0.0,
        max=1.0
    )

    preset_mode: bpy.props.EnumProperty(
        name="预设模式",
        description="动画预设模式",
        items=[
            ('SIMPLE', "简单振荡", "基础振荡模式"),
            ('SINE', "正弦波", "平滑的周期性变化"),
            ('SQUARE', "方波", "开关式变化"),
            ('TRIANGLE', "三角波", "线性渐变"),
            ('SAW', "锯齿波", "单向渐变"),
            ('RANDOM', "随机变化", "随机值变化"),
            ('EASE_IN_OUT', "缓入缓出", "平滑加速减速"),
            ('BOUNCE', "弹跳", "模拟弹跳效果"),
            ('BREATH', "呼吸", "模拟呼吸节奏"),
        ],
        default='SIMPLE'
    )

    sine_frequency: bpy.props.FloatProperty(
        name="频率",
        description="正弦波频率",
        default=1.0,
        min=0.1,
        max=10.0
    )

    sine_phase: bpy.props.FloatProperty(
        name="相位",
        description="正弦波相位",
        default=0.0,
        min=0.0,
        max=2.0 * math.pi
    )

    square_duty_cycle: bpy.props.FloatProperty(
        name="占空比",
        description="方波占空比",
        default=0.5,
        min=0.1,
        max=0.9
    )

    random_seed: bpy.props.IntProperty(
        name="随机种子",
        description="随机种子",
        default=0
    )

    random_smoothness: bpy.props.FloatProperty(
        name="平滑度",
        description="随机变化平滑度",
        default=0.5,
        min=0.0,
        max=1.0
    )

    bounce_count: bpy.props.IntProperty(
        name="弹跳次数",
        description="弹跳次数",
        default=3,
        min=1,
        max=10
    )

    bounce_decay: bpy.props.FloatProperty(
        name="衰减",
        description="弹跳衰减",
        default=0.6,
        min=0.1,
        max=0.9
    )

    breath_intensity: bpy.props.FloatProperty(
        name="强度",
        description="呼吸强度",
        default=0.8,
        min=0.1,
        max=1.0
    )

    breath_hold: bpy.props.FloatProperty(
        name="屏息时间",
        description="呼吸屏息时间",
        default=0.2,
        min=0.0,
        max=0.5
    )
