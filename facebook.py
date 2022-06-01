import json
from random import uniform
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_webdriver(headless, page_load_strategy="eager", WEBDRIVER_TIMEOUT=25):
    """Function that returns a Selenium WebDriver

    Args:
        headless (bool): True if webdriver should be in headless mode

    Returns:
        selenium.webdriver: webdriver
    """
    options = Options()
    options.page_load_strategy = page_load_strategy

    if not headless:
        driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(),
            options=options)

    else:
        options.add_argument("--headless")
        driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(),
            options=options)

    driver.set_page_load_timeout(WEBDRIVER_TIMEOUT)

    return driver


class FACEBOOK_AUDIENCE:

    def __init__(self, driver):
        self.driver = driver
        self.base_url = "https://www.facebook.com/"

    @staticmethod
    def check_elements_exists(xpath, driver):
        try:
            driver.find_elements(by=By.XPATH, value=xpath)
        except NoSuchElementException:
            return False
        return True

    def get_audience(self, name_fb_page):
        facebook_url = self.base_url + name_fb_page
        facebook_about = facebook_url + "/about"

        self.driver.get(facebook_about)
        wait = 2 * uniform(0.5, 1.5)
        self.driver.implicitly_wait(wait)

        xpath = "//div[@class='qzhwtbm6 knvmm38d']" +\
                "//span[@class='d2edcug0 hpfvmrgz qv66sw1b " +\
                "c1et5uql oi732d6d ik7dh3pa ht8s03o8 " +\
                "jq4qci2q a3bd9o3v b1v8xokw oo9gr5id']"
        if self.check_elements_exists(xpath, self.driver):
            body_html = self.driver.find_elements(
                by=By.XPATH, value="/html/body")
            body_text = [elem.text for elem in body_html]

            data = {"facebook_page": facebook_url,
                    "likes": self.get_likes(body_text),
                    "followers": self.get_followers(body_text)}
            return data

    def get_likes(self, body_text):
        if body_text[0]:
            text = body_text[0].replace(",", "")
            match = re.search('[0-9]+ people like this', text)
            if match:
                try:
                    return int(match.group().split()[0])
                except Exception:
                    pass

    def get_followers(self, body_text):
        if body_text[0]:
            text = body_text[0].replace(",", "")
            match = re.search('[0-9]+ people follow this', text)
            if match:
                try:
                    return int(match.group().split()[0])
                except Exception:
                    pass


if "__name__" == "__main__":
    driver = get_webdriver(headless=False)
    facebook = FACEBOOK_AUDIENCE(driver)
    facebook_page = "LExpress"
    data = facebook.get_audience(facebook_page)
    print(json.dumps(data, indent=4))
    driver.close()