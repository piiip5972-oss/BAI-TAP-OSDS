from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
import getpass
from openpyxl import Workbook

# SETUP
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)
actions = ActionChains(driver)

# 1. MỞ TRANG QUOTES TRƯỚC
quotes_url = "https://www.goodreads.com/quotes/tag/inspirational"
driver.get(quotes_url)
time.sleep(2)

# 2. NHẤN SIGN IN
btn_sign_in = wait.until(
    EC.element_to_be_clickable((By.LINK_TEXT, "Sign In"))
)
btn_sign_in.click()
time.sleep(2)

# 3. NHẤN “SIGN IN WITH EMAIL”
btn_email = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign in with email')]"))
)
btn_email.click()
time.sleep(2)

# 4. NHẬP EMAIL + PASSWORD 
my_email = input("Nhập email Goodreads: ")
my_password = getpass.getpass("Nhập password: ")

email_box = wait.until(
    EC.presence_of_element_located((By.ID, "ap_email"))
)
email_box.send_keys(my_email)

pass_box = wait.until(
    EC.presence_of_element_located((By.ID, "ap_password"))
)
pass_box.send_keys(my_password)

# Bấm Sign In
driver.find_element(By.ID, "signInSubmit").click()
print("Đang đăng nhập…")
time.sleep(3)

# 6. KIỂM TRA ĐĂNG NHẬP THÀNH CÔNG
try:
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quoteText")))
    print("Đăng nhập thành công! Bắt đầu cào dữ liệu…")
except:
    print("Đăng nhập thất bại!")
    driver.quit()
    exit()

# 7. BẮT ĐẦU CÀO QUOTES TRÊN TRANG HIỆN TẠI
quotes = driver.find_elements(By.CLASS_NAME, "quote")

data = []

for q in quotes:
    quote_text = q.find_element(By.CLASS_NAME, "quoteText").text.strip()
    author = q.find_element(By.CLASS_NAME, "authorOrTitle").text.strip()

    # Lấy tags 
    tag_elements = q.find_elements(By.CSS_SELECTOR, ".greyText.smallText a")
    tag_list = ", ".join([t.text for t in tag_elements])

    data.append([quote_text, author, tag_list])

driver.quit()

# 8. LƯU EXCEL
wb = Workbook()
ws = wb.active
ws.title = "Goodreads Quotes"
ws.append(["Quote", "Author", "Tags"])

for row in data:
    ws.append(row)

file_name = "goodreads_quotes.xlsx"
wb.save(file_name)

print(f" Đã lưu file Excel: {file_name}")

