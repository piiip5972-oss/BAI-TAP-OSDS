from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Khoi tao
driver = webdriver.Chrome()

#mo trang
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name"
driver.get(url)

#mo toan man hinh
driver.maximize_window()

#doi 2 giay
time.sleep(2)

#lay tat ca the <a>
tags = driver.find_elements(By.XPATH, "//a[contains(@title, 'List of painters')]")
#tao ds cac l.ket
links = [tag.get_attribute("href") for tag in tags]

for link in links:
    print(link)

driver.quit()