# ShapeKeyAnimator/utils.py
from .translations import get_shape_key_category, translate_shape_key_name

def filter_shape_keys_by_category(shape_keys, category):
    """根据分类过滤形态键"""
    if category == 'ALL':
        return shape_keys

    filtered = []
    for shape_key in shape_keys:
        if get_shape_key_category(shape_key.name) == category:
            filtered.append(shape_key)

    return filtered