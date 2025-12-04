from selenium import webdriver
from selenium.webdriver.common.by import By
import time
# tao 1 drive de dieu khien
driver = webdriver.Chrome()
#mo 1 trang 
driver.get("https://gomotungkinh.com/")
time.sleep(5)

try:
    while True:
        driver.find_element(By.ID, "bonk").click()
        #tam dung 1 giay
        time.sleep(1)
except:
    driver.quit()