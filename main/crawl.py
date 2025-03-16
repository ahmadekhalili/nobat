from django.conf import settings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException

from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from selenium_stealth import stealth
from urllib.parse import quote
from PIL import Image

import jdatetime
import random
import string
import time
import re
import os

from user.models import Center
from .methods import image_to_text, HumanMouseMove
from user.models import ServiceType, PELAK_LETTER_OPTIONS

#driver_path = ChromeDriverManager().install()


def advance_setup():
    service = Service(driver_path=r"C:\Users\akh\.wdm\drivers\chromedriver\win64\134.0.6998.35\chromedriver-win32/chromedriver.exe")

    options = uc.ChromeOptions()
    options.binary_location = r'C:/chrome/chrome_browser_134.0.6998.35/chrome.exe'
    #options.add_argument(r"user-data-dir=C:/Users/akh/AppData/Local/Google/Chrome/User Data")
    #options.add_argument(r"--profile-directory=Profile 6")
    #profile_path = os.path.join(os.getenv('APPDATA'), 'Local', 'Google', 'Chrome', 'User Data', 'Profile5')
    #options.add_argument(f"user-data-dir={profile_path}")
    #options.add_argument("--disable-extensions")
    options.add_argument('--no-sandbox')
    #options.add_argument('--disable-dev-shm-usage')
    #options.add_argument('--disable-gpu')

    #options.add_argument("--disable-webrtc-encryption")
    #options.add_argument("--disable-ipv6")
    #options.add_argument("--disable-blink-features=AutomationControlled")
    #options.add_argument("--lang=en-US")
    #options.add_argument("--disable-geolocation")

    driver = uc.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    user_agent = UserAgent().ua.random  #"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    #stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True, run_on_insecure_origins=True, hide_webdriver=True)
    # Open a blank page to start with a clean slate
    driver.get("about:blank")

    # Create an ActionChains instance
    actions = ActionChains(driver)
    # Optionally, position the mouse at a central point (this is our starting point)
    start_x, start_y = 1078, 521
    actions.move_by_offset(start_x, start_y).perform()
    time.sleep(0.41)  # a slight pause to mimic natural behavior
    actions = HumanMouseMove.human_mouse_move(actions, (random.randint(0, 500), random.randint(0, 500)), (random.randint(0, 500), random.randint(0, 500)))
    driver.maximize_window()
    return driver


def setup2():
    service = Service(driver_path=r"C:\Users\akh\.wdm\drivers\chromedriver\win64\134.0.6998.35\chromedriver-win32/chromedriver.exe")
    options = uc.ChromeOptions()
    options.binary_location = r'C:/chrome/chrome_browser_134.0.6998.35/chrome.exe'

    options.add_argument("--incognito")  # Enable incognito mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-extensions')
    options.add_argument('--dns-prefetch-disable')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")

    user_agent = UserAgent().random  #"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    options.add_argument(f"--user-agent={user_agent}")

    driver = uc.Chrome(service=service, options=options)
    driver.delete_all_cookies()  # Clear all cookies
    driver.execute_script("window.localStorage.clear();")  # Clear local storage
    driver.execute_script("window.sessionStorage.clear();")  # Clear session storage
    driver.maximize_window()
    return driver


def setup():
    options = Options()
    winpath_driver, winpath_chrome = r"C:\Users\akh\.wdm\drivers\chromedriver\win64\134.0.6998.35\chromedriver-win32/chromedriver.exe", r"C:/chrome/chrome_browser_134.0.6998.35/chrome.exe"
    linuxpath_driver, linuxpath_chrome = r"/home/akh/shared/nobat/chrome/chromedriver-linux64/chromedriver", r"/home/akh/shared/nobat/chrome/chrome-headless-shell-linux64/chrome-headless-shell"
    service = Service(driver_path=linuxpath_driver)
    options.binary_location = linuxpath_chrome  # C:\chrome\chrome_browser_134.0.6998.35
    options.add_argument("--incognito")  # Enable incognito mode
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-extensions')
    options.add_argument('--dns-prefetch-disable')
    options.add_argument("--disable-gpu")
    user_agent = UserAgent().random
    options.add_argument(f"--user-agent={user_agent}")

    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver


def crawl_login(driver, phone, password):
    driver.get("https://nobat.epolice.ir/login")
    wait = WebDriverWait(driver, 10)

    try:
        i, max_iter = 0, 20
        while i < 20:
            # Locate and fill the "شماره موبایل" input (mobile number)
            try:
                mobile_input = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
                mobile_input.send_keys(phone)
                # Locate and fill the "رمز عبور" input (password)
                password_input = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
                password_input.send_keys(password)
            except:
                print("Error finding phone, password elements")
            try:
                captcha_image = wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@class, 'captcha_image')]")))
                captcha_path = os.path.join(settings.BASE_DIR, "captcha.png")
                png_data = captcha_image.screenshot(captcha_path)
                text = image_to_text(captcha_path).replace(' ', '')
            except:
                text = False
                print('Error save and convert captcha to text')
            if not text:
                # Locate the refresh button using XPath (by matching part of the onclick attribute)
                try:
                    refresh_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//i[contains(@onclick, 'refresh_captcha')]")
                    ))
                    refresh_button.click()
                except:
                    print(f'error refreshing the captcha try {max_iter-i} more times')
            else:
                # Locate and fill the "کد کپچا" input (captcha)
                try:
                    captcha_input = wait.until(EC.visibility_of_element_located((By.NAME, "sec_code_login")))
                    captcha_input.send_keys(text)
                    # click submit form
                    submit_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[@type='submit' and contains(@class, 'btn-success') and text()='ورود']")
                    ))
                    ActionChains(driver).move_to_element(submit_button).click().perform()
                    try:  # if find element we are not logged in, continue looping
                        print('search captcha input:')
                        time.sleep(5)  # wait a bit to leave the page and load sec page ((important)
                        # elements = driver.find_elements(By.XPATH, "//span[text()='ورود به حساب کاربری']")
                        captcha_input = wait.until(EC.visibility_of_element_located((By.NAME, "sec_code_login")))
                    except:  # we logged in
                        message = "ورود موفق آمیز بود."
                        print(message)
                        return message
                except:
                    print(f"Error in entering captcha and submit, try {max_iter-i} more times")
            i += 1

        if i == max_iter:
            message = "ورود ناموفق. شماره تفلن/پسورد صحیح نمی باشد یا سیستم کپچا تغییر کرده است."
            print(message)
            return False
        else:
            message = "ورود موفق آمیز بود."
            print(message)
            return True
    except:
        print("Error finding elements of login page")
        return False


def select_dropdown_items(driver):
    wait = WebDriverWait(driver, 10)

    # 1. Locate and click the element based on its text.
    # Using XPath with contains(text(), ...) to ensure we match the visible text.
    select_container = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//span[@class='select2-selection__rendered' and contains(text(),'تمام استان ها')]")
    ))
    select_container.click()

    # 2. Wait for the dropdown (ul element) to become visible.
    # The ul is uniquely identified by its id, ensuring we work with the new UI.
    dropdown_ul = wait.until(EC.visibility_of_element_located(
        (By.ID, "select2-zone_home-results")
    ))

    # 3. Find all li elements within the dropdown that match the given text.
    # Define your target substring (or complete text) here.
    li_text = "آذربایجان"  # Example: adjust as needed.
    # Retrieve all li elements within the ul
    li_elements = dropdown_ul.find_elements(By.TAG_NAME, "li")

    print([li.text for li in li_elements])
    # Filter li elements by checking if their text contains the target string.
    matching_li_elements = [li for li in li_elements if li_text in li.text]
    print([li.text for li in matching_li_elements])
    # Click on each matching li element in order.
    for li in matching_li_elements:
        # Optionally scroll the element into view before clicking.
        driver.execute_script("arguments[0].scrollIntoView(true);", li)
        # Wait until the li element is clickable (best practice to handle dynamic UIs)
        wait.until(EC.element_to_be_clickable((By.XPATH, "."))).click()


# fill state, town, service type and vehicle type in first stage for crawling
class LocationStep:
    def __init__(self, driver, report):
        self.driver = driver
        self.report = report

    def handle_dropdown_location(self, four_section):
        driver, report = self.driver, self.report
        try:
            dropdowns = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.select2-selection__rendered")))
            for i, dropdown in enumerate(dropdowns):
                print(f'Successfully got dropdown {i+1} to click: ', dropdown.get_attribute('outerHTML'))
                value, ul_id = four_section[i]['value'], four_section[i]['ul_id']
                ActionChains(driver).move_to_element(dropdown).click().perform()
                # Locate the state by text
                ul_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//ul[@class='select2-results__options']")))
                try:
                    try:
                        state_li = ul_element.find_element(By.XPATH, f".//li[text()='{value}']")
                    except:
                        print(f"Unable location dropdown {i+1} item: {value}")

                    ActionChains(driver).move_to_element(state_li).click().perform()
                    report.append(('', value))  # example: ba maqadir: ... sabt shod
                except StaleElementReferenceException:
                    # Retry finding elements if stale
                    ul_element = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.ID, f"{ul_id}-results"))
                    )
                    try:
                        state_li = ul_element.find_element(By.XPATH, f".//li[text()='{value}']")
                    except:
                        print(f"Unable location dropdown {i + 1} item: {value}")
                        return False
                    state_li.click()
                # time.sleep(0.5)
            else:
                return True
        except:
            print(f"An error occurred in location step")
            return False

    def run(self, customer):
        time.sleep(2)
        self.driver.get('https://nobat.epolice.ir/')
        # note (optional): in 'select2-vehicle-mz-container', 'mz' part is variable. and in 'select2-specialty-aw-results', 'aw' part
        four_section_data = [{'ul_id': 'select2-zone_home', 'value': customer.state.name}, {'ul_id': 'select2-subzone_home', 'value': customer.town.name}, {'ul_id': 'select2-specialty-aw-results', 'value': customer.service_type.name}, {'ul_id': 'select2-vehicle-mz-container', 'value': customer.get_vehicle_cat_display()}]
        if self.handle_dropdown_location(four_section=four_section_data):
            element = self.driver.find_element(By.XPATH, "//span[@class='caption' and normalize-space(text())='جستجو']")
            element.click()
            return True
        time.sleep(2)


# select center_location in second step (second page)
class CenterStep:
    def __init__(self, driver, report):
        self.driver = driver
        self.report = report

    def handle_center(self, search_text, service_type):
        driver = self.driver
        try:
            # Wait for carts container to be present
            wait = WebDriverWait(self.driver, 20)
            # Get all cart elements
            carts = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.row > div.col-md-4.col-sm-6.col-xs-12")))

            for cart in carts:
                try:
                    # Find cart title element
                    title_element = cart.find_element(By.CSS_SELECTOR, "div.dr_name")
                    if search_text == title_element.text:
                        # Find appointment link within the same cart
                        link = cart.find_element(By.CSS_SELECTOR, "a.linkboxprofile")

                        # Scroll to element for reliability
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)

                        # Wait for link to be clickable
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.linkboxprofile")))

                        # Click the link
                        link.click()
                        message = f"مرکز {search_text} با موفقیت انتخاب شد. مرحله بعد انتخاب روز."
                        self.report.append(('pub', message))
                        print(message)
                        break
                except:
                    continue  # Skip cart if elements not found, handles in else

            else:
                message = f"مرکز {search_text} برای این سرویس و استان وجود در دسترس نیست. لطفا مرکز دیگری را انتخاب نمایید"
                self.report.append(('pub', message))
                print(message)
                return False

            try:
                container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "form-group.row"))
                )

                # 2. Search for the label containing "نقل و انتقال" within the container:
                labels = container.find_elements(By.TAG_NAME, "label")  # Find all labels within the container

                target_input = None
                for label in labels:
                    if service_type == label.text:
                        target_input = label.find_element(By.TAG_NAME, "input")  # Find the input within the label
                        break  # Stop searching once found

                # 3. Check if the input was found and click it:
                if target_input:
                    # Wait for the input to be clickable (best practice)
                    clickable_input = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(target_input)
                    )
                    ActionChains(driver).move_to_element(clickable_input).click().perform()
                    self.report.append(('سرویس', service_type))
                    print(f"Successfully clicked the input for {service_type}")
                    return True
                else:
                    print(f"Label with text {service_type} not found.")
                    return False

            except Exception as e:
                print(f"An error occurred: {e}")
                return False

        except:
            print("Timed out waiting for page elements to load")
            return False

    def run(self, customer):
        return self.handle_center(customer.service_center.title, customer.service_type.name)


# specify date and time in page 3 and page 4 of reserving process in the site
class DateTimeStep:
    def __init__(self, driver, report):
        self.driver = driver
        self.report = report

    def string_to_obj(self, str_date):  # str to date obj, for date
        parts = str_date.split('-')
        jalali_year = int(parts[0])
        jalali_month = int(parts[1])
        jalali_day = int(parts[2])
        return jdatetime.date(jalali_year, jalali_month, jalali_day)

    def convert_to_sec(self, time_str):     # time str like: "12:22" to its secs
        hour_minute = time_str.strip().split(':')
        if len(hour_minute)==2:
            h, m = int(hour_minute[0]), int(hour_minute[1])
            return h*60 + m
        return None

    def date_handler(self, requested_dates=None):
        driver = self.driver
        message, reserveday_links = None, None
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
        try:    # obtain very fast at first, next switch to slow
            print('Fast mode, date finding')
            time.sleep(0.1)
            reserveday_links = driver.find_elements(By.CSS_SELECTOR, "a.reserveday")
            raise  # came to except to continue
        except:
            print('switched slow mode, date finding')
            try:
                # 1. Wait for the presence of 'reserveday' links (Best Practice: Explicit Wait)
                try:
                    if not reserveday_links:
                        reserveday_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.reserveday")))
                        print(f"Found {len(reserveday_links)} 'reserveday' links.")
                except:
                    print(f"Raise error finding date container")
                    raise

                # 2. Iterate through the links and find the one with the specific date
                specific_date_link = None
                if requested_dates:
                    try:
                        for requested_date in requested_dates:
                            for link in reserveday_links:
                                if link.get_attribute("data-load") == requested_date:
                                    try:
                                        ActionChains(driver).move_to_element(link).click().perform()
                                        message = f'نوبت در روز{requested_date} انتخاب شد.'
                                        self.report.append(('pub', 'date', message))
                                        print(message)
                                        return requested_date
                                    except:
                                        message = 'The date element founded, but error in clicking'
                                        self.report.append(('dev', 'date', message))
                                        return False

                            else:
                                message = f"No any match dates founded. your date: {requested_date} founded dates: {[link.get_attribute('data-load') for link in reserveday_links]}"
                                self.report.append(('dev', 'date', message))
                                print(message)
                                return False
                    except:
                        print("Error in getting link elements.")



                else:
                    dates_list = [link.get_attribute("data-load") for link in reserveday_links]
                    print(f"all Founded valid dates: {dates_list}")
                    smallest_date = (0, self.string_to_obj(reserveday_links[0].get_attribute("data-load")))
                    for i, link in enumerate(reserveday_links):
                        current_date = (i, self.string_to_obj(link.get_attribute("data-load")))
                        if current_date[1] < smallest_date[1]:
                            smallest_date = current_date
                    smallest_link = reserveday_links[smallest_date[0]]
                    ActionChains(driver).move_to_element(smallest_link).click().perform()
                    message = f'نوبت در تاریخ {smallest_link.get_attribute("data-load")} ثبت شد.'
                    self.report.append(('روز', message))
                    return smallest_link.get_attribute("data-load")

            except:
                message = '.نوبت در روز تخصیص یافته وجود ندارد'
                print(message)
                self.report.append(('date', message))
                return False

    def get_time_container(self, driver):
        try:
            message = "Fast mode, time finding"
            print(message)
            try:
                time.sleep(0.1)
                buttons = driver.find_elements(By.CSS_SELECTOR, ".reservelist-item a")
                print(f"Founded green time button numbers: {len(buttons)}")
                if len(buttons) < 1:
                    raise    # continue in except

                return buttons

            except:
                message = "Fast mode, Unable|0 to find green time elements, lets try gray color."
                print(message)
                reservelist_items = WebDriverWait(driver, 10).until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.reservelist-item"))
                )
                print(f"Founded gray time reserve links numbers: {len(reservelist_items)}")
                buttons = [item.find_element(By.TAG_NAME, "button") for item in reservelist_items]
                print(f"Founded gray time button numbers: {len(buttons)}")
                return buttons

        except:
            print('switched slow mode, time finding')
            try:
                try:
                    buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".reservelist-item a")))
                    return buttons

                except:
                    message = "Unable to find green time elements, lets try gray color."
                    print(message)
                    self.report.append(('dev', message))
                    buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                        (By.XPATH, "//button[@type='submit' and @class='btn btn-default ltr']")))
                    return buttons
            except:
                message = "Last tried, Unable to find green time elements too."
                print(message)
                self.report.append(('dev', message))
                message = "نوبت در زمان مورد نظر وجود ندارد"
                print(message)
                self.report.append(('pub', message))
                return False

    def time_handler(self, times):
        driver = self.driver
        if times:
            try:
                for time_str in times:
                    # 1. Wait for the buttons to be present (Best Practice: Explicit Wait)
                    buttons = self.get_time_container(driver)
                    if not buttons:  # False
                        return False
                    # 2. Extract text from each button and clean it
                    button_texts = []
                    for button in buttons:
                        button_text = button.text.strip()
                        button_texts.append(button_text)
                        if button_text == time_str:
                            ActionChains(driver).move_to_element(button).click().perform()
                            message = f"با موفقیت زمان {time_str} انتخاب شد"
                            print(message)
                            self.report.append(('pub', message))
                            return time_str
                    else:
                        message = f"نوبت در زمان مورد نظر وجود ندارد"
                        self.report.append(('pub', message))
                        message = f"Selected time not founded. searched times: {button_texts}"
                        print(message)
                        self.report.append(('dev', message))
                        screenshot_folder = os.path.join(settings.BASE_DIR, "media", "log_images")
                        if not os.path.exists(screenshot_folder):
                            os.makedirs(screenshot_folder)
                        screenshot_path = os.path.join(screenshot_folder, f"time_{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}.png")
                        print(f'Screen shots of the times has taken at: {screenshot_path}')
                        self.report.append(('dev', message))
                        driver.save_screenshot(screenshot_path)
                        return False
            except:
                message = f"Error in founding time elements"
                print(message)
                self.report.append(('dev', message))
                return False

        else:
            try:
                buttons = self.get_time_container(driver)
                if not buttons:  # False
                    return False
                # 2. Extract text from each button and clean it
                button_texts = []

                if len(buttons) == 0:
                    message = f"نوبت در زمان مورد نظر وجود ندارد"
                    print(message)
                    self.report.append(('pub', message))
                    screenshot_folder = os.path.join(settings.BASE_DIR, "media", "log_images")
                    if not os.path.exists(screenshot_folder):
                        os.makedirs(screenshot_folder)
                    screenshot_path = os.path.join(screenshot_folder, f"time_{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}.png")
                    print(f'Screen shots of the times has taken at: {screenshot_path}')
                    self.report.append(('dev', message))
                    driver.save_screenshot(screenshot_path)
                    return False

                samallest_in_mins = self.convert_to_sec(buttons[0].text.strip())
                samallest_button = buttons[0]
                samallest_time_str = samallest_button.text.strip()
                for button in buttons:
                    button_text = button.text.strip()
                    if self.convert_to_sec(button_text) < samallest_in_mins:
                        samallest_button = button
                        samallest_time_str = button_text
                        samallest_in_mins = self.convert_to_sec(samallest_time_str)  # after clicking elements could stale (lost reference) so we should obtain smallest time str here

                ActionChains(driver).move_to_element(samallest_button).click().perform()
                message = f"با موفقیت زودترین زمان {samallest_time_str} انتخاب شد"
                print(message)
                self.report.append(('pub', message))
                return samallest_time_str

            except Exception as e:
                message = f"Error in founding time elements {e}"
                print(message)
                self.report.append(('dev', message))
                return False

    def run(self, dates, times):
        valid_dates = [date.replace('/', '-') for date in dates if date]
        date = self.date_handler(valid_dates)
        time_of_date = None
        if date:
            if times[0][0]:  # if there is any time
                valid_times = []
                for time_tuple in times:
                    sub_time = [time_str for time_str in time_tuple if time_str]  # some inputs of time could be blank
                    if sub_time:
                        valid_times.append(sub_time)
                if valid_dates:
                    time_of_date = valid_times[valid_dates.index(date)]
                else:    # if user not selected any date, select all times to reservation
                    valid_times = valid_times
            return self.time_handler(time_of_date)


class LastStep:
    def __init__(self, driver, report):
        self.driver = driver
        self.report = report

    def service_submit(self, vehicle_cat, pelak_nums, cd_meli, test=None):
        driver = self.driver
        try:
            try:
                select_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "type_pelak")))
                dropdown = Select(select_element)
                dropdown.select_by_value(vehicle_cat)  # or .select_by_visible_text for option text
                print(f"successfully selected vehicle_cat: {vehicle_cat}")
            except:
                try:
                    print(f"failed select vehicle_cat: {vehicle_cat}, try with js")
                    select_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "type_pelak")))
                    driver.execute_script(
                        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                        select_element, vehicle_cat)
                    print(f"successfully selected vehicle_cat: {vehicle_cat}, by js")
                except:
                    print(f"failed select vehicle_cat: {vehicle_cat}")
                    return False

            if vehicle_cat == 'موتور سیکلت':
                try:
                    # Wait until divp2 is visible
                    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "divp2")))

                    # Locate the first input field
                    input1 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "txtmotor0"))
                    )

                    # Locate the second input field
                    input2 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "txtmotor1"))
                    )

                    # Clear existing values (if any)
                    input1.clear()
                    input2.clear()

                    # Enter values into the fields
                    input1.send_keys(pelak_nums[0])  # Replace with your desired 3-digit number
                    input2.send_keys(pelak_nums[1])  # Replace with your desired 5-digit number

                except Exception as e:
                    print(f"motor siklet pelak section failed")

            else:
                try:
                    # pelak parts
                    # 1.
                    input_pelak1 = driver.find_element(By.NAME, "txtnation1")  # Locate by ID (best)
                    input_pelak1.send_keys(pelak_nums[0])  # Enter the desired value (e.g., "12")

                    # 2. dropdown pelak (pelak letter)
                    try:
                        pelak2_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "txtnation2")))
                        print(f"pelak letter element: {select_element.get_attribute('outerHTML')}")
                        dropdown = Select(pelak2_element)
                        dropdown.select_by_value(pelak_nums[1])
                        print(f"successfully selected pelak value: {pelak_nums[1]}")
                    except:
                        try:
                            print(f"failed select pelak value: {pelak_nums[1]}, try with js")
                            pelak2_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "txtnation2")))
                            print(f"pelak letter element: {select_element.get_attribute('outerHTML')}")
                            driver.execute_script(
                                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                                pelak2_element, pelak_nums[1]
                            ) # Select dropdown pelak

                            print(f"successfully selected pelak value: {pelak_nums[1]}, by js")
                        except:
                            print(f"failed select pelak value: {pelak_nums[1]}")
                            return False
                    # 3. Input field
                    input_pelak3 = driver.find_element(By.NAME, "txtnation3")  # Locate by name (no ID)
                    input_pelak3.send_keys(pelak_nums[2])  # Enter the desired value (e.g., "123")
                    # 4. Input field
                    input_pelak4 = driver.find_element(By.NAME, "txtnation0")  # Locate by name (no ID)
                    input_pelak4.send_keys(pelak_nums[3])  # Enter the desired value (e.g., "34")
                    print(f"successfully selected and filled pelak (by js): {pelak_nums}")
                except:
                    print(f'car pelak section fails')

            # code meli input
            input_codemeli = driver.find_element(By.NAME, "codemeli_kharidar")
            input_codemeli.send_keys(cd_meli)

            # agreement checkbox
            checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='term'][type='checkbox']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
            checkbox.click()
            print('Successfully clicked on agreement checkbox')
        except:
            message = "raise error in main menu"
            print(message)
            return False

        # Captcha part
        i = 0
        max_lim = 20
        while i < max_lim:
            try:
                # captcha detection
                try:
                    captcha_img = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "img.captcha_image_reserve"))
                    )
                    # Save screenshot of just that <img> to "captcha.png"
                    captcha_path = os.path.join(settings.BASE_DIR, "captcha.png")
                    captcha_img.screenshot(captcha_path)
                    text = image_to_text(captcha_path).replace(' ', '')
                    print('Captcha uploaded to: captcha.png')
                except:
                    text = None
                    print('raised error in captcha image saving: {i}/{max_lim}')
                if not text:
                    print(f'captcha solving was blank: {text}, retry: {i+1}/{max_lim}')
                    continue
                else:
                    # captcha input
                    try:
                        sec_code_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "sec_code_reserve"))
                        )
                        sec_code_input.send_keys(text)  # replace with your code
                        print(f'successfully entered captcha text: {text}')
                    except:
                        print(f'raised error in captcha input finding: {i+1}/{max_lim}')

                # Click the “ثبت نوبت” button
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-success.btn-block"))
                )

                if test:
                    print('reserve received successfully in test')
                    return "کد پیگیری test_cd_gen با موفقیت ثبت شد"   # return true to make button element be 'completion'
                else:   # finalize reservation
                    submit_button.click()
                    print('Pressed reserve receiving submit button')
                time.sleep(5)
                try:
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-success.btn-block"))
                    )
                    if submit_button:
                        pass
                    else:     # form submited successfully
                        raise
                except:     # form submited successfully
                    try:
                        screenshot_folder = os.path.join(settings.BASE_DIR, "media", "saved_nobats")
                        if not os.path.exists(screenshot_folder):
                            os.makedirs(screenshot_folder)
                        screenshot_path = os.path.join(screenshot_folder, f"screenshot_{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}.png")
                        driver.save_screenshot(screenshot_path)
                        print(f'Screen shot of nobat and its cd peigiry has taken at: {screenshot_path}')

                        span_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@class='alert alert-success']/span")))
                        cd_peigiry_message = span_element.text
                        message = f"کاربر با کد ملی {cd_meli} پلاک {pelak_nums} ووسیله نقلی {vehicle_cat} ثبت و نوبت دریافت شد."
                        print(message)
                        self.report(('pub', message))

                        return cd_peigiry_message
                    except:
                        print('nobat reservation ended but in getting the cd_peigiry problem happended')
                        return False

                print(f'retry: {i}/{max_lim} times')    # submits failed, loop again (just captcha input resets)
            except:
                print(f'captcha fails: {i}/{max_lim} times')
            i += 1
        return False

    def run(self, customer, test=None):
        vehicle_cat, pelak = customer.vehicle_cat, customer.pelak.number
        if vehicle_cat == 'motor':
            pelak_nums = [pelak[:3], pelak[3:]]
        else:
            pelak_nums = [pelak[:2], customer.pelak.letter_value, pelak[3:6], pelak[6:]]
            return self.service_submit(vehicle_cat, pelak_nums, customer.username, test)


########################################################################## for developers
# calls after get_all_pre_centers to grab all services of center locations
def get_all_centers_services(driver):  # crawl and get all centers from the site (services need to be fill)
    all_services, labels = [], []
    all_centers = Center.objects.all()
    ln_centers = len(all_centers)

    for i, center in enumerate(all_centers):
        try:
            driver.get(f'https://nobat.epolice.ir/office/{center.code}')
        except:
            print(f'Error raised in opening the site')

        try:
            wait = WebDriverWait(driver, 10)
            container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.selectkhadamat")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
            # Find only label elements inside divs with the specific classes
            labels = container.find_elements(By.CSS_SELECTOR, "div.col-md-3.col-sm-6.col-xs-12 > label")

        except:
            screenshot_folder = "screenshots"
            if not os.path.exists(screenshot_folder):
                os.makedirs(screenshot_folder)
            #.code can be unavailable
            screenshot_name = os.path.join(screenshot_folder, f"error_screenshot_center_{center.title}.png")
            print(f'Error finding label or container elements, for center: {center.title}')
            driver.save_screenshot(screenshot_name)

        if labels:
            try:
                valid_labels = []
                for label in labels:
                    if not ServiceType.objects.filter(name=label.text).exists():
                        print(f'Error invalid label: {label.text}. center: {center.title}')
                    else:
                        valid_labels.append(label.text)
                if len(valid_labels) == len(labels):
                    print(f'Successfully Added {len(labels)} labels for center {i+1}/{ln_centers}')

                all_services.append({'code': center.code, 'title': center.title, 'services': valid_labels})
            except Exception as e:
                print(f'Error in calculating')
    return all_services


# grab all center locations and its related town (state not required)
def get_all_pre_centers(driver):  # crawl and get all centers from the site (services need to be fill)
    centers = []
    all_centers, passed_centers = 0, 0
    towns_counter = 0
    try:
        # Collect all states first
        state_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "select2-zone_home-container"))
        )
        state_dropdown.click()

        states_ul = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "select2-zone_home-results"))
        )
        states = states_ul.find_elements(By.TAG_NAME, "li")
        state_names = [state.text for state in states]

        # Close the state dropdown
        state_dropdown.click()

        # Skip the default "all states" option if present
        # start_index = 1 if state_names[0] == "تمام استان ها" else 0

        start_index = [i for i, state in enumerate(state_names) if state=="تهران"][0]
        last_index = [i for i, state in enumerate(state_names) if state=="چهارمحال و بختیاری"][0]
        for i, state_name in enumerate(state_names[start_index:last_index]):
            print('**')
            print(f"Processing state: {state_name} {i+1}/{(len(state_names)-start_index)}")
            HumanMouseMove.human_mouse_move(ActionChains(driver), (random.randint(0, 500), random.randint(0, 500)), (random.randint(0, 500), random.randint(0, 500)))
            try:
                time.sleep(10)      # to much requesting to https://nobat.epolice.ir/ blocks
                driver.get('https://nobat.epolice.ir/')
            except Exception as e:
                print(f"Error while requesting to 'nobat.epolice.ir' (much request). program will wait and try again. \n{e}")
                time.sleep(30)
                driver = setup()
                driver.get('https://nobat.epolice.ir/')
            # Reopen state dropdown
            try:
                state_dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "select2-zone_home-container"))
                )
                ActionChains(driver).move_to_element(state_dropdown).click().perform()
            except:
                print('Error clicking the state dropdown. referesh the page and try again.')
                driver.get('https://nobat.epolice.ir/')
                state_dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "select2-zone_home-container"))
                )
                state_dropdown.click()

            states_ul = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "select2-zone_home-results"))
            )
            # Locate the state by text
            try:
                state_li = states_ul.find_element(By.XPATH, f".//li[text()='{state_name}']")
                state_li.click()
            except StaleElementReferenceException:
                # Retry finding elements if stale
                states_ul = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "select2-zone_home-results"))
                )
                state_li = states_ul.find_element(By.XPATH, f".//li[text()='{state_name}']")
                state_li.click()

            # Handle town dropdown
            town_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "select2-subzone_home-container"))
            )
            ActionChains(driver).move_to_element(town_dropdown).click().perform()

            towns_ul = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "select2-subzone_home-results"))
            )
            towns = [town.text for town in towns_ul.find_elements(By.TAG_NAME, "li")]
            for j, town in enumerate(towns):
                print(f"  Processing town: {town} {j + 1}/{(len(towns))}")
                try:
                    time.sleep(5)      # to much requesting to https://nobat.epolice.ir/ blocks
                    driver.get('https://nobat.epolice.ir/')
                except Exception as e:
                    print(f"Error while requesting to 'nobat.epolice.ir' (much request). program will wait and try again. \n{e}")
                    time.sleep(10)
                    driver = setup()
                    driver.get('https://nobat.epolice.ir/')
                try:
                    # click state dropdown to open ul
                    state_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "select2-zone_home-container")))
                    ActionChains(driver).move_to_element(state_dropdown).click().perform()
                except:
                    print('Error clicking the state dropdown. referesh the page and try again.')
                    driver.get('https://nobat.epolice.ir/')
                    state_dropdown = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "select2-zone_home-container"))
                    )
                    state_dropdown.click()

                try:
                    # get state ul
                    states_ul = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.ID, "select2-zone_home-results"))
                    )
                    state_li = states_ul.find_element(By.XPATH, f".//li[text()='{state_name}']")
                    state_li.click()
                except StaleElementReferenceException:
                    print('Error clicking on the state item, try again.')
                    states_ul = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.ID, "select2-zone_home-results"))
                    )
                    state_li = states_ul.find_element(By.XPATH, f".//li[text()='{state_name}']")
                    state_li.click()

                ############
                try:
                    # click town dropdown to open ul
                    town_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "select2-subzone_home-container")))
                    ActionChains(driver).move_to_element(town_dropdown).click().perform()
                except:
                    print('Error clicking the town dropdown.')

                try:
                    towns_ul = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.ID, "select2-subzone_home-results"))
                    )
                    town_li = towns_ul.find_element(By.XPATH, f".//li[text()='{town}']")
                    town_li.click()
                except:
                    print("Error clicking the town's item. will referesh and try again.")
                    driver.get('https://nobat.epolice.ir/')
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "select2-zone_home-container"))).click()  # click state dropdown to open ul
                    states_ul = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "select2-zone_home-results")))
                    states_ul.find_element(By.XPATH, f".//li[text()='{state_name}']").click()     # click state li

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "select2-subzone_home-container"))).click()  # click town dropdown to open ul
                    towns_ul = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "select2-subzone_home-results")))
                    towns_ul.find_element(By.XPATH, f".//li[text()='{town}']").click()     # click town li

                try:
                    towns_counter += 1
                    time.sleep(0.5)  # Brief pause to ensure stability
                    submit_element = driver.find_element(By.XPATH,
                                                       "//span[@class='caption' and normalize-space(text())='جستجو']")
                    ActionChains(driver).move_to_element(submit_element).click().perform()
                except:
                    print("Error clicking the submit element (state/town form).")


                ######################
                try:
                    # Get all cart elements
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".matab_container")))

                    carts = driver.find_elements(By.CSS_SELECTOR, ".matab_container")

                    all_centers += len(carts)
                    find_carts = []
                    print(f'    {town} found {len(carts)} carts!')
                    for cart in carts:
                        try:
                            # Find cart title element
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cart)
                            title_txt = cart.find_element(By.CSS_SELECTOR, "div.dr_name").text
                            address = cart.find_element(By.CSS_SELECTOR, "h3.dr_proficiency").text

                            link_element = cart.find_element(By.CSS_SELECTOR, "a.linkboxprofile")
                            href_value = link_element.get_attribute("href")
                            # Use regex to extract the numeric code from the URL (e.g., '/office/87800')
                            match = re.search(r'/office/(\d+)', href_value)
                            office_code = match.group(1) if match else None
                            find_carts.append({'title': title_txt, 'code': office_code, 'address': address})
                            passed_centers += 1
                        except NoSuchElementException:
                            print('Error in grabbing card specs.')
                            continue  # Skip cart if elements not found

                    if find_carts:
                        centers.append({'state': state_name, 'town': town, 'centers': find_carts})
                    else:
                        # If no carts were found, raise an error with a custom message
                        raise Exception("Error in page 2: carts not found.")

                except Exception as e:
                    error_message = (
                            "Error in page 2 (center section). Screenshot saved as error_screenshot.png.")
                    print(error_message)
                    screenshot_name = "error_screenshot.png"
                    driver.save_screenshot(screenshot_name)


        print()
        print(f'Successfully crawled {towns_counter} towns and {len(state_names)-start_index} States -- crawled centers: {passed_centers}/{all_centers}')

    except Exception as e:
        screenshot_name = "error_screenshot.png"
        driver.save_screenshot(screenshot_name)
        print(f"An error occurred. Screenshot saved as {screenshot_name}. \n{e}")
    finally:
        driver.quit()

    return centers




















def get_all_states_towns():  # crawl and get from the site
    driver = setup()  # Assume setup initializes the WebDriver
    driver.get('https://nobat.epolice.ir/')
    state_towns = []

    try:
        # Collect all states first
        state_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "select2-zone_home-container"))
        )
        state_dropdown.click()

        states_ul = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "select2-zone_home-results"))
        )
        states = states_ul.find_elements(By.TAG_NAME, "li")
        state_names = [state.text for state in states]

        # Close the state dropdown
        state_dropdown.click()

        # Skip the default "all states" option if present
        start_index = 1 if state_names[0] == "تمام استان ها" else 0
        for i, state_name in enumerate(state_names[start_index:]):
            print(f"Processing state: {state_name} {i+1}/{(len(state_names)-start_index)}")
            # Reopen state dropdown
            state_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "select2-zone_home-container"))
            )
            state_dropdown.click()

            # Locate the state by text
            states_ul = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "select2-zone_home-results"))
            )
            try:
                state_li = states_ul.find_element(By.XPATH, f".//li[text()='{state_name}']")
                state_li.click()
            except StaleElementReferenceException:
                # Retry finding elements if stale
                states_ul = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "select2-zone_home-results"))
                )
                state_li = states_ul.find_element(By.XPATH, f".//li[text()='{state_name}']")
                state_li.click()

            # Handle town dropdown
            town_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "select2-subzone_home-container"))
            )
            town_dropdown.click()

            towns_ul = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "select2-subzone_home-results"))
            )
            towns = [town.text for town in towns_ul.find_elements(By.TAG_NAME, "li")]

            state_towns.append((state_name, towns))


            # Close town dropdown
            town_dropdown.click()
            time.sleep(0.5)  # Brief pause to ensure stability

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

    return state_towns