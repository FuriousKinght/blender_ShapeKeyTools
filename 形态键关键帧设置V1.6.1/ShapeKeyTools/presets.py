# ShapeKeyAnimator/presets.py
import math
import random

# ==================== 保留原有的预设生成器 ====================
class ShapeKeyPresetGenerator:
    @staticmethod
    def simple_oscillation(frame, start_frame, end_frame, min_val, max_val, oscillations):
        """简单振荡模式"""
        if oscillations == 0:
            return min_val if frame == start_frame else max_val

        total_frames = end_frame - start_frame
        total_points = oscillations * 2 + 1
        t = (frame - start_frame) / total_frames

        segment = int(t * (total_points - 1))
        if segment % 2 == 0:
            return min_val
        else:
            return max_val

    @staticmethod
    def sine_wave(frame, start_frame, end_frame, min_val, max_val, frequency, phase):
        """正弦波模式"""
        t = (frame - start_frame) / (end_frame - start_frame)
        sine_val = math.sin(2 * math.pi * frequency * t + phase)
        normalized = (sine_val + 1) / 2
        return normalized * (max_val - min_val) + min_val

    @staticmethod
    def square_wave(frame, start_frame, end_frame, min_val, max_val, duty_cycle):
        """方波模式"""
        t = (frame - start_frame) / (end_frame - start_frame)
        cycle_pos = t % 1.0
        if cycle_pos < duty_cycle:
            return max_val
        else:
            return min_val

    @staticmethod
    def triangle_wave(frame, start_frame, end_frame, min_val, max_val):
        """三角波模式"""
        t = (frame - start_frame) / (end_frame - start_frame)
        triangle_val = 2 * abs(2 * (t - math.floor(t + 0.5))) - 1
        normalized = (triangle_val + 1) / 2
        return normalized * (max_val - min_val) + min_val

    @staticmethod
    def sawtooth_wave(frame, start_frame, end_frame, min_val, max_val):
        """锯齿波模式"""
        t = (frame - start_frame) / (end_frame - start_frame)
        saw_val = t % 1.0
        return saw_val * (max_val - min_val) + min_val

    @staticmethod
    def random_wave(frame, start_frame, end_frame, min_val, max_val, seed, smoothness):
        """随机模式"""
        random.seed(seed + int(frame - start_frame))

        if smoothness < 0.1:
            return random.uniform(min_val, max_val)
        else:
            base_random = random.uniform(min_val, max_val)
            if frame > start_frame:
                prev_value = getattr(ShapeKeyPresetGenerator, f"_last_random_{seed}", base_random)
                smoothed = prev_value * smoothness + base_random * (1 - smoothness)
                setattr(ShapeKeyPresetGenerator, f"_last_random_{seed}", smoothed)
                return smoothed
            return base_random

    @staticmethod
    def ease_in_out(frame, start_frame, end_frame, min_val, max_val):
        """缓入缓出模式"""
        t = (frame - start_frame) / (end_frame - start_frame)
        if t < 0.5:
            ease_t = 4 * t * t * t
        else:
            ease_t = 1 - math.pow(-2 * t + 2, 3) / 2
        return ease_t * (max_val - min_val) + min_val

    @staticmethod
    def bounce_effect(frame, start_frame, end_frame, min_val, max_val, bounce_count, decay):
        """弹跳模式"""
        t = (frame - start_frame) / (end_frame - start_frame)

        bounce_height = 1.0
        current_bounce = 0
        time_per_bounce = 1.0 / bounce_count

        while current_bounce < bounce_count:
            bounce_start = current_bounce * time_per_bounce
            bounce_end = (current_bounce + 1) * time_per_bounce

            if bounce_start <= t <= bounce_end:
                bounce_t = (t - bounce_start) / time_per_bounce
                bounce_val = 4 * bounce_t * (1 - bounce_t) * bounce_height
                return bounce_val * (max_val - min_val) + min_val

            current_bounce += 1
            bounce_height *= decay

        return min_val

    @staticmethod
    def breathing_effect(frame, start_frame, end_frame, min_val, max_val, intensity, hold_ratio):
        """呼吸模式"""
        t = (frame - start_frame) / (end_frame - start_frame)

        adjusted_t = t * (1 + hold_ratio)

        if adjusted_t <= 1.0:
            breath_t = adjusted_t
            breath_val = (math.sin(breath_t * math.pi - math.pi / 2) + 1) / 2
        else:
            breath_val = 1.0

        return (min_val + (max_val - min_val) * breath_val * intensity)