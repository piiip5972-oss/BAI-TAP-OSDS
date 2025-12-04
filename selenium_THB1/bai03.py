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

#Chọn thẻ <ul> thứ 20
ul_painters = ul_tags[19]

#Lấy tất cả thẻ <li> thuộc ul_painters
li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

links = []
titles = []

# Tạo danh sách URL và Title
for tag in li_tags:
    try:
        a = tag.find_element(By.TAG_NAME, "a")   # cố gắng tìm thẻ <a>
        links.append(a.get_attribute("href"))
        titles.append(a.get_attribute("title"))
    except:
        # nếu không có <a> thì bỏ qua
        continue

#In ra url
for link in links:
    print(link)

#In ra title
for title in titles:
    print(title)

#Đóng webdriver
driver.quit()
