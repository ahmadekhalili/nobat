from django.conf import settings

from user.models import Customer

import cv2
import os
import time
import random
import jdatetime
import numpy as np
from PIL import Image
from scipy.special import expit
from paddleocr import PaddleOCR       # pip install paddlepaddle paddleocr
ocr = PaddleOCR(use_angle_cls=True, lang='en')


class HumanMouseMove:
    @staticmethod
    def generate_bezier_curve(start, control, end, num_points=40):
        """تولید مسیر منحنی Bézier برای حرکت طبیعی موس"""
        t_values = np.linspace(0, 1, num_points)
        curve = np.array([
            (1 - t) ** 2 * np.array(start) +
            2 * (1 - t) * t * np.array(control) +
            t ** 2 * np.array(end)
            for t in t_values
        ])
        return curve

    @staticmethod
    def sigmoid_speed_curve(num_points):
        """ایجاد لیستی از زمان‌بندی‌های حرکت بر اساس تابع سیگموئید"""
        x = np.linspace(-5, 5, num_points)
        y = expit(x)  # خروجی تابع سیگموئید
        return np.diff(y) * 2  # تبدیل به اختلاف زمانی برای حرکت نرم‌تر

    @staticmethod
    def add_random_noise(path, max_noise=2):
        """افزودن نویز تصادفی برای شبیه‌سازی لرزش‌های طبیعی دست انسان"""
        noise = np.random.randint(-max_noise, max_noise + 1, path.shape)
        return np.clip(path + noise, 0, None)  # جلوگیری از مقدار منفی

    @staticmethod
    def human_mouse_move(actions, start, end, duration=2, window_width=1920, window_height=1080):
        """Simulate human-like mouse movement while ensuring the mouse stays within bounds."""
        control = (
            (start[0] + end[0]) // 2 + random.randint(-100, 100),
            (start[1] + end[1]) // 2 + random.randint(-100, 100)
        )

        path = HumanMouseMove.generate_bezier_curve(start, control, end)
        path = HumanMouseMove.add_random_noise(path, max_noise=3)
        speed_curve = HumanMouseMove.sigmoid_speed_curve(len(path) + 1)
        actions.move_by_offset(0, 0)
        x,y = 0,0
        for i in range(1, len(path)):
            # Clamp the coordinates to ensure they stay within window bounds
            step1, step2 = path[i-1], path[i]
            step1_x, step1_y = min(max(0, int(step1[0])), window_width),  min(max(0, int(step1[1])), window_height)
            step2_x, step2_y = min(max(0, int(step2[0])), window_width), min(max(0, int(step2[1])), window_height)
            x += step2_x - step1_x
            y += step2_y - step1_y
            actions.move_by_offset(step2_x - step1_x, step2_y - step1_y)  # Move relative to start
            delay = (speed_curve[i] * duration / sum(speed_curve)) + random.uniform(0.001, 0.01)
            time.sleep(delay)

            if random.random() < 0.05:
                time.sleep(random.uniform(0.05, 0.2))
        return actions


def processed_img2(image_path, tolerance=20, background_color=(255, 255, 255, 0)):
    # image_path is like 'captcha.png' in root of project
    target_colors = {'dark': '#333333', 'light': '#C0C0C0'}
    try:
        img = Image.open(os.path.join(settings.BASE_DIR, image_path)).convert("RGBA") # Ensure RGBA for transparency
        pixels = img.load()
        width, height = img.size
        target_rgb_colors = {}
        for name, hex_color in target_colors.items():
            hex_color = hex_color.lstrip('#')
            target_rgb_colors[name] = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        for x in range(width):
            for y in range(height):
                pixel_color = pixels[x, y][:3] # Get RGB, ignore alpha if present

                is_target_color = False
                for color_name, target_rgb in target_rgb_colors.items():
                    r_diff = abs(pixel_color[0] - target_rgb[0])
                    g_diff = abs(pixel_color[1] - target_rgb[1])
                    b_diff = abs(pixel_color[2] - target_rgb[2])

                    if r_diff <= tolerance and g_diff <= tolerance and b_diff <= tolerance:
                        is_target_color = True
                        break # Pixel matches one of the target colors, no need to check others

                if not is_target_color:
                    pixels[x, y] = background_color # Set to transparent background

        return img

    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def image_to_text(image_path):
    processed = processed_img2(image_path)
    processed.save('h.png')     # cv2.imwrite('h.png', processed)

    processed = Image.open("h.png")
    processed = processed.convert('RGB')  # Optionally, ensure the image is in RGB format (helps with consistency)
    processed = np.array(processed)  # convert the PIL image to a numpy array

    result = ocr.ocr(processed, det=False, rec=True)  # ocr.ocr(processed, cls=True)

    if result[0]:
        return result[0][0][0]
    else:
        return None


# convert jalali "YYYY-MM-DD HH:MM" for gregorian datetime object
def convert_jalali_to_gregorian(j_date_str, j_time_str):
    # Parse the Jalali datetime; adjust the format if needed
    if j_date_str and j_time_str:
        try:
            # Expecting format "YYYY-MM-DD HH:MM"
            j_dt = jdatetime.datetime.strptime(f"{j_date_str} {j_time_str}", "%Y/%m/%d %H:%M")
        except ValueError as e:
            raise ValueError(f"Invalid date/time format: {e}")
        # Convert to Gregorian datetime
        gregorian_dt = j_dt.togregorian()
        return gregorian_dt
    return None


def add_square(customer_id, color_class='green'):
    if not customer_id:
        customer_id = customer_id
    customer = Customer.objects.get(id=customer_id)  # sent via ajax not form post
    if customer.color_classes:
        customer.color_classes = customer.color_classes + f",{color_class}"
    else:
        customer.color_classes = color_class
    customer.save()
