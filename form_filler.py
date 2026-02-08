from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def fill_form(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)

    inputs = driver.find_elements(By.TAG_NAME, "input")

    for field in inputs:
        name = field.get_attribute("type")
        if name == "text":
            field.send_keys("Test User")
        elif name == "email":
            field.send_keys("test@email.com")

    time.sleep(5)
    driver.quit()
