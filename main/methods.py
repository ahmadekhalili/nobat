import logging

from django.conf import settings

from user.models import Customer

import cv2
import os
import time
import pytz
import signal
import random
import logging
import psutil
import win32con
import win32gui
import win32process
import jdatetime
import numpy as np
from PIL import Image
from pathlib import Path
from scipy.special import expit
from paddleocr import PaddleOCR       # pip install paddlepaddle paddleocr
ocr = PaddleOCR(use_angle_cls=True, lang='en')
BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger('web')


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


def convert_str_jdatetime(date_str, time_str):  # convert date like: "1403-03-12" and "07:12" to its jdatetime (one digit supports)
    try:
        year, month, day = map(int, date_str.split('-'))
        hour, minute = map(int, time_str.split(':'))
        # Create a jdatetime object directly
        return jdatetime.datetime(year, month, day, hour, minute)
    except:
        return None


def get_datetime(jdate, time):  # date is like: 1404/04/05, time is like: 07:33  returns awared datetime object
    year, month, day = map(int, jdate.split("/"))
    hour, minute = map(int, time.split(":"))

    # 2. Create a jdatetime object
    jdt = jdatetime.datetime(year, month, day, hour, minute)

    # 3. Convert to Gregorian datetime
    gregorian_dt = jdt.togregorian()  # Naive datetime (no timezone yet)

    # 4. Make it timezone-aware (Asia/Tehran)
    tehran_tz = pytz.timezone("Asia/Tehran")
    return tehran_tz.localize(gregorian_dt)


def add_square(customer_id, color_class='green'):
    if not customer_id:
        customer_id = customer_id
    customer = Customer.objects.get(id=customer_id)  # sent via ajax not form post
    if customer.color_classes:
        customer.color_classes = customer.color_classes + f",{color_class}"
    else:
        customer.color_classes = color_class
    customer.save()


import pygetwindow as gw
from pywinauto.application import Application


def maximize_chrome_window(title_keyword="1a"):
    try:
        # Find window that matches title
        window = next((w for w in gw.getWindowsWithTitle(title_keyword) if w.title and title_keyword in w.title), None)
        if not window:
            return "Window not found"

        app = Application(backend="uia").connect(handle=window._hWnd)
        app_window = app.window(handle=window._hWnd)

        app_window.set_focus()
        app_window.maximize()

        return "Window maximized"
    except Exception as e:
        return f"Error: {e}"


def minimize_chrome_window(title_keyword="1a"):
    try:
        # Find window that matches title
        window = next((w for w in gw.getWindowsWithTitle(title_keyword) if w.title and title_keyword in w.title), None)
        if not window:
            return "Window not found"

        app = Application(backend="uia").connect(handle=window._hWnd)
        app_window = app.window(handle=window._hWnd)

        app_window.set_focus()
        app_window.minimize()

        return "Window minimized"
    except Exception as e:
        return f"Error: {e}"


class WindowsHandler:     # handle via AutoHotkey software
    path = r'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
    bridge_file = os.path.join(BASE_DIR, 'scripts', 'bridge_django_autokey.txt')

    @staticmethod
    def _minimize_hwnds(hwnds, delay: float = 0.0):
        """
        Minimizes each window handle in `hwnds`.
        If `delay` > 0, sleeps that many seconds between windows.
        """
        for hwnd in hwnds:
            # SW_MINIMIZE = 6
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            if delay:
                time.sleep(delay)

    @classmethod
    def minimize_by_driver_id(cls, chromedriver_pid):
        """
        1) Finds all Chrome window HWNDs for given Chromedriver PID
        2) Minimizes them
        Returns the list of HWNDs it tried to minimize (empty if none found).
        """
        hwnds = cls.get_hwnds_by_pid(chromedriver_pid)
        if hwnds:
            cls._minimize_hwnds(hwnds)
        return hwnds

    @staticmethod
    def _maximise_hwnds(hwnds, delay: float = 0.0):
        """
        Minimizes each window handle in `hwnds`.
        If `delay` > 0, sleeps that many seconds between windows.
        """
        for hwnd in hwnds:
            # SW_MINIMIZE = 6
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            if delay:
                time.sleep(delay)

    @classmethod
    def maximise_by_driver_id(cls, chromedriver_pid):
        """
        1) Finds all Chrome window HWNDs for given Chromedriver PID
        2) Minimizes them
        Returns the list of HWNDs it tried to minimize (empty if none found).
        """
        hwnds = cls.get_hwnds_by_pid(chromedriver_pid)
        if hwnds:
            cls._minimize_hwnds(hwnds)
        return hwnds

    @staticmethod
    def _hide_hwnds(hwnds):
        """
        Completely hides each window handle in `hwnds` (SW_HIDE).
        If `delay` > 0, pauses between each.
        """
        for hwnd in hwnds:
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

    @staticmethod
    def _show_hwnds(hwnds):
        """
        Restores each hidden window handle in `hwnds` (SW_SHOW).
        If `delay` > 0, pauses between each.
        """
        for hwnd in hwnds:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

    @classmethod
    def hide_by_driver_id(cls, chromedriver_pid):
        hwnds = cls.get_hwnds_by_pid(chromedriver_pid)
        if hwnds:
            cls._hide_hwnds(hwnds)
        return hwnds

    @classmethod
    def show_by_driver_id(cls, chromedriver_pid):
        hwnds = cls.get_hwnds_by_pid(int(chromedriver_pid))
        if hwnds:
            cls._show_hwnds(hwnds)
        return hwnds

    @staticmethod
    def _move_hwnd(hwnd, x: int, y: int):
        """
        Moves the window to (x,y), keeping its current width/height.
        """
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width  = right - left
        height = bottom - top
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            x, y, width, height,
            win32con.SWP_NOZORDER
        )

    @classmethod
    def _move_offscreen(cls, hwnds, x: int = -32000, y: int = 0):
        """
        Slides each hwnd to (x,y), which defaults to far off the left of your screen.
        """
        for hwnd in hwnds:
            cls._move_hwnd(hwnd, x, y)

    @classmethod
    def _restore_on_screen(cls, hwnds, x: int = 100, y: int = 100):
        """
        Moves each hwnd back to (x,y) on your primary screen.
        You can customize x/y or track original positions if you need.
        """
        for hwnd in hwnds:
            cls._move_hwnd(hwnd, x, y)


    @classmethod
    def move_off_chromedriver_pid(cls, chromedriver_pid, **kwargs): # show hide browser (while can crawl in background)
        """
        Finds Chrome HWNDs and either moves them offscreen or back onscreen.
        `hide=True` → move_offscreen, else restore_on_screen.
        """
        hwnds = cls.get_hwnds_by_pid(chromedriver_pid)
        logger.info(f"hwnds in move_off: {hwnds}")
        if not hwnds:
            return []
        cls._move_offscreen(hwnds, **kwargs)
        return hwnds

    @classmethod
    def restore_on_chromedriver_pid(cls, chromedriver_pid, **kwargs): # show hide browser (while can crawl in background)
        """
        Finds Chrome HWNDs and either moves them offscreen or back onscreen.
        `hide=True` → move_offscreen, else restore_on_screen.
        """
        hwnds = cls.get_hwnds_by_pid(chromedriver_pid)
        logger.info(f"hwnds in restore_on: {hwnds}")
        if not hwnds:
            return []
        cls._restore_on_screen(hwnds, **kwargs)
        return hwnds

    def get_window(title):
        window = next((w for w in gw.getWindowsWithTitle(title) if w.title and title in w.title), None)
        if not window:
            return None
        return window

    def save_hwnd(self, thread_id, hwnd):
        # Ensure the directory exists, create it if it doesn't
        os.makedirs(os.path.dirname(self.bridge_file), exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            line = f"{thread_id} {hwnd}\n"
            f.write(line)

    @classmethod
    def get_hwnds_by_pid(cls, target_pid):
        hwnds = []
        chrome_pids = cls._get_chrome_child_pids(target_pid)
        if not chrome_pids:
            return []

        def callback(hwnd, _):
            # get pid
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid not in chrome_pids:
                return True

            # ۱. عنوان پنجره
            title = win32gui.GetWindowText(hwnd).strip()
            if not title:
                return True

            # ۲. کلاس پنجره
            cls_name = win32gui.GetClassName(hwnd)
            if cls_name != "Chrome_WidgetWin_1":
                return True

            # ۳. سبک پنجره: باید پنجره‌ی معمولی (با نوار عنوان) باشد
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            if not (style & win32con.WS_OVERLAPPEDWINDOW):
                return True

            # اگر به اینجا رسید، یک پنجره‌ی واقعی/مربوط است
            hwnds.append(hwnd)
            return True

        win32gui.EnumWindows(callback, None)
        return hwnds

    @staticmethod
    def _get_chrome_child_pids(chromedriver_pid):
        # Chromedriver itself has no visible window, so chrome_pid returns blank hwnd (because didnt see any windows)
        # chrome_pid = driver.service.process.pid,  get_hwnds_by_pid(chrome_pid) returns none always
        parent = psutil.Process(chromedriver_pid)
        # Look for chrome.exe children
        return [c.pid for c in parent.children(recursive=True) if 'chrome.exe' in c.name().lower()]


def is_chrome_alive(driver_id):  # return False if chrome windows closed
    # each driver can have several sub process manages chrome windows. they can be terminate (close windows) while driver process exist alive!
    try:
        child_driver_ids = WindowsHandler._get_chrome_child_pids(driver_id)
        if child_driver_ids:       # it can be blank list if windows closed via close button (only driver process itself available)
            return any(is_driver_alive(child_driver_id) for child_driver_id in child_driver_ids)  # 'or' between all items
        else:
            return False
    except Exception as e:
        logger.info(f"failed getting chrome processes status. error: {e}")
        return False


def is_driver_alive(driver_id):  # return true if related process tp driver_id is alive
    try:
        p = psutil.Process(driver_id)
        logger.info(f"driver id {driver_id} p.is_running(): {p.is_running()}")
        logger.info(f"driver id {driver_id} p.status() != psutil.STATUS_ZOMBIE: {p.is_running()}")
        return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        logger.info(f"driver id not alive")
        return False


def kill_driver_and_windows(driver_id):
    try:
        driver_id = int(driver_id)
        child_driver_ids = WindowsHandler._get_chrome_child_pids(driver_id)
        if child_driver_ids:
            for process_id in child_driver_ids:
                process_id = int(process_id)
                try:
                    os.kill(process_id, signal.SIGTERM)  # quite drive too (driver.quite)
                except:       # process not exits or stoped before
                    pass
        try:
            os.kill(driver_id, signal.SIGTERM)
        except:       # process not exits or stopped before
            pass
        logger.info(f"driver and all its process successfully killed")
    except Exception as e:
        logger.info(f"Error raise during stop driver and all its process: {e}")


class JobStatus:
    @staticmethod
    def close(driver_id):
        if not is_chrome_alive(driver_id):    # all windows of the driver closed
            os.kill(driver_id, signal.SIGTERM)
