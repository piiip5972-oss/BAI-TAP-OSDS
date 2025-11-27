from selenium import webdriver
from selenium.webdriver.common.by import By
import time
#Khởi tạo
driver = webdriver.Chrome()

#Mở trang web
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22P%22"
driver.get(url)

#Đợi trang tải
time.sleep(2)

#Lấy tất cả thẻ <ul>
ul_tags = driver.find_elements(By.TAG_NAME, "ul")
print(len(ul_tags))

#Chọn thẻ <ul> thứ 21 
ul_painters = ul_tags[20]

#Lấy tất cả thẻ <li> thuộc ul_painters
li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

#Tạo danh sách URL của từng painter
links = [tag.find_element(By.TAG_NAME, "a").get_attribute("href") for tag in li_tags]

#Tạo danh sách Title (tên painter)
titles = [tag.find_element(By.TAG_NAME, "a").get_attribute("title") for tag in li_tags]

#In ra url
for link in links:
    print(link)

#In ra title
for title in titles:
    print(title)

# Đóng webdriver
driver.quit()