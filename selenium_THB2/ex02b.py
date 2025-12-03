from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
import time
import pandas as pd

# 1. Khởi tạo Firefox + driver
gecko_path = r"C:/Users/User/OneDrive/Desktop/Ma Nguon Mo/Selenium/project2/geckodriver.exe"
service = Service(gecko_path)

options = webdriver.firefox.options.Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
options.headless = False  # Hiển thị Firefox

driver = webdriver.Firefox(service=service, options=options)

# 2. Truy cập trang GoChek
url = "https://gochek.vn/collections/all"
driver.get(url)
time.sleep(5)

# 3. Cuộn xuống để tải TẤT CẢ sản phẩm 
body = driver.find_element(By.TAG_NAME, "body")

for _ in range(50):         # Cuộn khoảng 50 lần → Load toàn bộ
    body.send_keys(Keys.END)
    time.sleep(0.15)

time.sleep(2)  # Chờ trang load nốt

# 4. XÁC ĐỊNH THẺ SẢN PHẨM
# Thẻ sản phẩm đúng trên GoChek: <div class="product-block ...">
products = driver.find_elements(By.CSS_SELECTOR, "div.product-block")
print("Tổng số sản phẩm tìm thấy:", len(products))

# 5. Tạo LIST để lưu dữ liệu
stt = []
ten_sp = []
gia_sau_giam = []
gia_goc = []
phan_tram_giam = []
hinh_anh = []
link_sp = []
# 6. Duyệt từng sản phẩm và lấy dữ liệu
for i, p in enumerate(products, 1):
    # Tên sản phẩm
    try:
        name = p.find_element(By.CSS_SELECTOR, "h3.pro-name").text
    except:
        name = ""
    #  Khối giá chung (có hoặc không giảm giá) 
    try:
        price_tag = p.find_element(By.CSS_SELECTOR, "p.pro-price.highlight, p.pro-price")
    except:
        price_tag = None
    # Giá sau giảm (hoặc giá duy nhất nếu không giảm)
    if price_tag:
        try:
            gia_moi = price_tag.find_element(By.TAG_NAME, "span").text.strip()
        except:
            gia_moi = ""
        # Giá gốc 
        try:
            gia_cu = price_tag.find_element(By.CSS_SELECTOR, "del.compare-price").text.strip()
        except:
            gia_cu = ""
    else:
        gia_moi = ""
        gia_cu = ""
    # Phần trăm giảm giá 
    try:
        giam = p.find_element(By.CSS_SELECTOR, ".product-sale span").text.strip()
    except:
        giam = ""
    # Hình ảnh
    try:
        img = p.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
    except:
        img = ""
    # Link sản phẩm 
    try:
        link = p.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
    except:
        link = ""
    # Chỉ lưu khi có tên 
    if name != "":
        stt.append(i)
        ten_sp.append(name)
        gia_sau_giam.append(gia_moi)
        gia_goc.append(gia_cu)
        phan_tram_giam.append(giam)
        hinh_anh.append(img)
        link_sp.append(link)
# 7. Xuất dữ liệu ra Excel
df = pd.DataFrame({
    "STT": stt,
    "Tên sản phẩm": ten_sp,
    "Giá sau giảm": gia_sau_giam,
    "Giá gốc": gia_goc,
    "Giảm (%)": phan_tram_giam,
    "Hình ảnh": hinh_anh,
    "Link": link_sp
})

df.to_excel("danh_sach_sp_gochek.xlsx", index=False)
print("Hoàn tất! Đã lưu file")

# Đóng browser
driver.quit()

