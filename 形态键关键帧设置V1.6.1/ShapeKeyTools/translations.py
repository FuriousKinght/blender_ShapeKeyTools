# ShapeKeyAnimator/translations.py
# ==================== 保留原有的辅助函数和分类系统 ====================

import bpy

def get_mmd_model_root(obj):
    """获取MMD模型根对象"""
    if not obj:
        return None
    
    # 检查对象是否直接是根对象
    if hasattr(obj, 'mmd_type') and obj.mmd_type == 'ROOT':
        return obj
    
    # 检查对象是否有mmd_root属性（子对象通常有）
    if hasattr(obj, 'mmd_root'):
        root_obj = obj.mmd_root.id_data
        if hasattr(root_obj, 'mmd_type') and root_obj.mmd_type == 'ROOT':
            return root_obj
    
    # 尝试通过父级查找根对象
    current = obj
    while current.parent:
        current = current.parent
        if hasattr(current, 'mmd_type') and current.mmd_type == 'ROOT':
            return current
    
    return None

def get_material_morph_names(mmd_root):
    """获取模型的所有材质变形名称"""
    material_morph_names = set()
    
    if not mmd_root or not hasattr(mmd_root, 'material_morphs'):
        return material_morph_names
    
    for morph in mmd_root.material_morphs:
        if morph.name:
            material_morph_names.add(morph.name)
    
    return material_morph_names

def is_material_morph_shape_key(shape_key_name):
    """检查形态键是否为材质变形形态键"""
    # 1. 首先检查常见的材质相关形态键命名模式
    material_keywords = [
        # 全身/半身材质相关
        '[FullBody]', '[FullBody', 'FullBody]',
        '[HalfBody]', '[HalfBody', 'HalfBody]',
        '[FlatFoot]', '[FlatFoot', 'FlatFoot]',
        
        # 材质相关关键词
        'Material', 'material', 'Mat', 'mat',
        'Texture', 'texture', 'Tex', 'tex',
        'Color', 'color', 'Col', 'col',
        'Shader', 'shader', 'Shade', 'shade',
        
        # 常见材质变形前缀
        'M_', 'm_', 'MT_', 'mt_',
        'Material_', 'material_',
        
        # 特殊材质变形
        'Skin', 'skin', 'Hair', 'hair',
        'Eye', 'eye', 'Cloth', 'cloth',
        'Metal', 'metal', 'Glass', 'glass'
    ]
    
    # 检查是否包含材质相关关键词
    for keyword in material_keywords:
        if keyword in shape_key_name:
            return True
    
    # 2. 检查方括号格式的材质变形（如[材质名]）
    if shape_key_name.startswith('[') and shape_key_name.endswith(']'):
        return True
    
    # 3. 检查MMD材质变形数据
    obj = bpy.context.active_object
    if not obj:
        return False
    
    # 获取MMD模型根对象
    mmd_root_obj = get_mmd_model_root(obj)
    if not mmd_root_obj or not hasattr(mmd_root_obj, 'mmd_root'):
        return False
    
    # 获取材质变形名称列表
    material_morph_names = get_material_morph_names(mmd_root_obj.mmd_root)
    
    # 检查形态键名称是否在材质变形列表中
    return shape_key_name in material_morph_names

MOUTH_SHAPE_KEYS = {
    # 日语假名嘴型
    'あ', 'あ2', 'ああ', 'い', 'い2', 'う', 'う2', 'え', 'お', 'お2',
    'ワ', 'ん', 'ん2', '∧', '□', 'なんで', '口', 
    
    # 嘴部动作
    '角下げ左', '口角下げ右', '口角上げ左', '口角上げ右', 
    '口横広げ左', '口横広げ右', '口横広げ2右', '口横広げ2左', '口横縮小',
    '口開け', '口閉じ', '口すぼめ', '口尖らせ', '口引き延ばし',
    
    # 英文嘴型关键词
    'mouth', 'Mouth', 'MOUTH', 'lip', 'Lip', 'LIP',
    'ah', 'Ah', 'AH', 'ee', 'Ee', 'EE', 'oh', 'Oh', 'OH',
    'oo', 'Oo', 'OO', 'eh', 'Eh', 'EH', 'uh', 'Uh', 'UH',
    'smile', 'Smile', 'SMILE', 'frown', 'Frown', 'FROWN',
    'pout', 'Pout', 'POUT', 'grin', 'Grin', 'GRIN',
    'open', 'Open', 'OPEN', 'close', 'Close', 'CLOSE',
    'wide', 'Wide', 'WIDE', 'narrow', 'Narrow', 'NARROW',
    
    # 常见嘴型前缀
    'M_', 'm_', 'mouth_', 'Mouth_', 'lip_', 'Lip_'
}

EYEBROW_SHAPE_KEYS = {
    # 日语眉毛表情
    '困る', '困る左', '困る右', 'にこり', 'にこり左', 'にこり右', 'にこり２',
    'にこり２右', 'にこり２左', '怒り', '怒り左', '怒り右', '上', '上左',
    '上右', '下', '下左', '下右', '平行', '平行左', '平行右', '入', '入左', '入右',
    '眉', '眉上', '眉下', '眉上げ', '眉下げ', '眉寄せ', '眉離し',
    
    # 英文眉毛关键词
    'brow', 'Brow', 'BROW', 'eyebrow', 'Eyebrow', 'EYEBROW',
    'up', 'Up', 'UP', 'down', 'Down', 'DOWN',
    'angry', 'Angry', 'ANGRY', 'happy', 'Happy', 'HAPPY',
    'sad', 'Sad', 'SAD', 'surprise', 'Surprise', 'SURPRISE',
    'frown', 'Frown', 'FROWN', 'raise', 'Raise', 'RAISE',
    'lower', 'Lower', 'LOWER', 'furrow', 'Furrow', 'FURROW',
    'arch', 'Arch', 'ARCH', 'flat', 'Flat', 'FLAT',
    'inner', 'Inner', 'INNER', 'outer', 'Outer', 'OUTER',
    
    # 常见眉毛前缀
    'B_', 'b_', 'brow_', 'Brow_', 'eyebrow_', 'Eyebrow_'
}

EYE_SHAPE_KEYS = {
    # 日语眼部表情
    'まばたき', 'ウィンク２', 'ウィンク２右', '笑い', 'ウィンク', 'ウィンク右',
    'ウィンク左', 'じと目', 'じと目左', 'じと目右', 'びっくり', 'びっくり左',
    'びっくり右', 'キリッ', 'キリッ左', 'キリッ右', 'たれ目', 'たれ目左',
    'たれ目右', '笑い目', '笑い目左', '笑い目右', '悲しい目', '悲しい目左',
    '悲しい目右', '瞳小', '瞳小左', '瞳小右', '恐ろしい子！', '恐ろしい子！左',
    '恐ろしい子！右', 'ハイライト消', 'ハイライト消左', 'ハイライト消右',
    'カメラ目', 'Up', 'Down', 'Right', 'Left', '星目', '星目2', 'はぁと', 'はぁと2',
    '目', '目開け', '目閉じ', '目細め', '目大きく', '目寄せ', '目離し',
    
    # 英文眼部关键词
    'eye', 'Eye', 'EYE', 'eyes', 'Eyes', 'EYES',
    'blink', 'Blink', 'BLINK', 'wink', 'Wink', 'WINK',
    'close', 'Close', 'CLOSE', 'open', 'Open', 'OPEN',
    'wide', 'Wide', 'WIDE', 'narrow', 'Narrow', 'NARROW',
    'happy', 'Happy', 'HAPPY', 'sad', 'Sad', 'SAD',
    'angry', 'Angry', 'ANGRY', 'surprise', 'Surprise', 'SURPRISE',
    'sleepy', 'Sleepy', 'SLEEPY', 'cry', 'Cry', 'CRY',
    'squint', 'Squint', 'SQUINT', 'stare', 'Stare', 'STARE',
    'look', 'Look', 'LOOK', 'gaze', 'Gaze', 'GAZE',
    'pupil', 'Pupil', 'PUPIL', 'iris', 'Iris', 'IRIS',
    'tear', 'Tear', 'TEAR', 'highlight', 'Highlight', 'HIGHLIGHT',
    'shine', 'Shine', 'SHINE', 'glow', 'Glow', 'GLOW',
    
    # 眼部方向
    'up', 'Up', 'UP', 'down', 'Down', 'DOWN',
    'left', 'Left', 'LEFT', 'right', 'Right', 'RIGHT',
    
    # 常见眼部前缀
    'E_', 'e_', 'eye_', 'Eye_', 'eyes_', 'Eyes_'
}

SHAPE_KEY_TRANSLATIONS = {
    # 嘴部形态键
    'あ': '啊', 'あ2': '啊2', 'ああ': '啊啊',
    'い': '伊', 'い2': '伊2',
    'う': '乌', 'う2': '乌2',
    'え': '诶', 'お': '哦', 'お2': '哦2',
    'ワ': '哇', 'ん': '嗯', 'ん2': '嗯2',
    '∧': '∧型', '□': '□型', 'なんで': '为什么',
    '口': '嘴', '角下げ左': '嘴角下左', '口角下げ右': '嘴角下右',
    '口角上げ左': '嘴角上左', '口角上げ右': '嘴角上右',
    '口横広げ左': '嘴角扩展左', '口横広げ右': '嘴角扩展右',
    '口横広げ2右': '嘴角扩展2右', '口横広げ2左': '嘴角扩展2左',
    '口横縮小': '嘴角缩小',

    # 眉毛形态键
    '困る': '困惑', '困る左': '困惑左', '困る右': '困惑右',
    'にこり': '微笑', 'にこり左': '微笑左', 'にこり右': '微笑右',
    'にこり２': '微笑2', 'にこり２右': '微笑2右', 'にこり２左': '微笑2左',
    '怒り': '生气', '怒り左': '生气左', '怒り右': '生气右',
    '上': '眉毛上', '上左': '眉毛上左', '上右': '眉毛上右',
    '下': '眉毛下', '下左': '眉毛下左', '下右': '眉毛下右',
    '平行': '眉毛平行', '平行左': '眉毛平行左', '平行右': '眉毛平行右',
    '入': '眉毛内', '入左': '眉毛内左', '入右': '眉毛内右',

    # 眼部形态键
    'まばたき': '眨眼',
    'ウィンク２': '眨眼2', 'ウィンク２右': '眨眼2右',
    '笑い': '笑眼', 'ウィンク': '眨眼', 'ウィンク右': '眨眼右', 'ウィンク左': '眨眼左',
    'じと目': '湿润眼', 'じと目左': '湿润眼左', 'じと目右': '湿润眼右',
    'びっくり': '惊讶', 'びっくり左': '惊讶左', 'びっくり右': '惊讶右',
    'キリッ': '锐利', 'キリッ左': '锐利左', 'キリッ右': '锐利右',
    'たれ目': '下垂眼', 'たれ目左': '下垂眼左', 'たれ目右': '下垂眼右',
    '笑い目': '笑眼', '笑い目左': '笑眼左', '笑い目右': '笑眼右',
    '悲しい目': '悲伤眼', '悲しい目左': '悲伤眼左', '悲しい目右': '悲伤眼右',
    '瞳小': '瞳孔小', '瞳小左': '瞳孔小左', '瞳小右': '瞳孔小右',
    '恐ろしい子！': '可怕', '恐ろしい子！左': '可怕左', '恐ろしい子！右': '可怕右',
    'ハイライト消': '取消高光', 'ハイライト消左': '取消高光左', 'ハイライト消右': '取消高光右',
    'カメラ目': '镜头眼', 'Up': '上', 'Down': '下', 'Right': '右', 'Left': '左',
    '星目': '星星眼', '星目2': '星星眼2', 'はぁと': '心形眼', 'はぁと2': '心形眼2',

    # 通用翻译
    'blink': '眨眼', 'blink_left': '左眨眼', 'blink_right': '右眨眼',
    'wink': '眨眼', 'wink_left': '左眨眼', 'wink_right': '右眨眼',
    'surprise': '惊讶', 'happy': '高兴', 'sad': '悲伤', 'angry': '生气',
    'eye_close': '闭眼', 'eye_open': '睁眼', 'eye_wide': '瞪眼',
    'mouth_ah': '啊型', 'mouth_ee': '伊型', 'mouth_oh': '哦型',
    'mouth_smile': '微笑', 'mouth_frown': '皱眉', 'mouth_pout': '噘嘴',
    'brow_up': '眉毛上', 'brow_down': '眉毛下', 'brow_angry': '怒眉',
}

def get_shape_key_category(shape_key_name):
    """基于参考表和关键词匹配获取形态键的精确分类"""
    
    # 0. 首先检查是否为分割线形态键（如果是分割线，直接返回OTHER）
    if is_separator_shape_key(shape_key_name):
        return 'OTHER'
    
    # 1. 检查精确匹配
    if shape_key_name in MOUTH_SHAPE_KEYS:
        return 'MOUTH'
    elif shape_key_name in EYEBROW_SHAPE_KEYS:
        return 'EYEBROW'
    elif shape_key_name in EYE_SHAPE_KEYS:
        return 'EYE'
    
    # 2. 检查关键词包含关系（提高识别率）
    shape_key_lower = shape_key_name.lower()
    
    # 嘴部关键词检查
    mouth_keywords = ['mouth', 'lip', 'ah', 'ee', 'oh', 'oo', 'eh', 'uh', 
                     'smile', 'frown', 'pout', 'grin', 'open', 'close', 'wide', 'narrow']
    for keyword in mouth_keywords:
        if keyword in shape_key_lower:
            return 'MOUTH'
    
    # 眉毛关键词检查
    eyebrow_keywords = ['brow', 'eyebrow', 'angry', 'happy', 'sad', 'surprise',
                       'frown', 'raise', 'lower', 'furrow', 'arch', 'flat', 'inner', 'outer']
    for keyword in eyebrow_keywords:
        if keyword in shape_key_lower:
            return 'EYEBROW'
    
    # 眼部关键词检查
    eye_keywords = ['eye', 'blink', 'wink', 'close', 'open', 'wide', 'narrow',
                   'happy', 'sad', 'angry', 'surprise', 'sleepy', 'cry',
                   'squint', 'stare', 'look', 'gaze', 'pupil', 'iris', 'tear']
    for keyword in eye_keywords:
        if keyword in shape_key_lower:
            return 'EYE'
    
    # 3. 检查材质变形
    if is_material_morph_shape_key(shape_key_name):
        return 'MATERIAL'
    
    # 4. 检查常见前缀
    if shape_key_name.startswith(('M_', 'm_', 'mouth_', 'lip_')):
        return 'MOUTH'
    elif shape_key_name.startswith(('B_', 'b_', 'brow_', 'eyebrow_')):
        return 'EYEBROW'
    elif shape_key_name.startswith(('E_', 'e_', 'eye_', 'eyes_')):
        return 'EYE'
    
    # 5. 默认分类
    return 'OTHER'

def is_separator_shape_key(shape_key_name):
    """检查形态键是否为分割线形态键"""
    # 1. 传统的三破折号分割线
    if shape_key_name.startswith("---"):
        return True
    
    # 2. 双破折号包围格式（如 --衣服消失--、--BDSM--）
    if shape_key_name.startswith("--") and shape_key_name.endswith("--"):
        # 确保中间有内容（不是单纯的 "----"）
        if len(shape_key_name) > 4 and shape_key_name[2:-2].strip():
            return True
    
    # 3. 其他常见分割线格式
    separator_patterns = [
        # 等号格式
        '=====', '======', '=======',
        # 星号格式
        '*****', '******', '*******',
        # 下划线格式
        '_____', '______', '_______',
        # 中文字符分割线
        '分割线', '分隔线', '分界线',
        # 英文分割线
        'separator', 'Separator', 'SEPARATOR',
        'divider', 'Divider', 'DIVIDER'
    ]
    
    for pattern in separator_patterns:
        if pattern in shape_key_name:
            return True
    
    # 4. 检查是否包含分割线关键词
    separator_keywords = [
        'line', 'Line', 'LINE', 'bar', 'Bar', 'BAR',
        'section', 'Section', 'SECTION', 'group', 'Group', 'GROUP',
        'category', 'Category', 'CATEGORY', 'menu', 'Menu', 'MENU'
    ]
    
    for keyword in separator_keywords:
        if keyword in shape_key_name:
            return True
    
    return False

def translate_shape_key_name(name, use_translation=False):
    """翻译形态键名称"""
    if use_translation:
        return SHAPE_KEY_TRANSLATIONS.get(name, name)
    else:
        return name