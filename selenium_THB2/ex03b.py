from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import time
import getpass

gecko_path = r"C:/Users/User/OneDrive/Desktop/Ma Nguon Mo/Selenium/project2/geckodriver.exe"
service = Service(gecko_path)

options = webdriver.firefox.options.Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
options.headless = False

driver = webdriver.Firefox(service=service, options=options)

url = "https://daotao.hutech.edu.vn/default.aspx?page=dangnhap"
driver.get(url)
time.sleep(2)

# Nhập thông tin
mssv = input("Nhập MSSV: ")
matkhau = getpass.getpass("Nhập mật khẩu: ")

print("Đang đăng nhập...")

# TÌM 2 Ô INPUT
username = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ctl00_txtTaiKhoa")
password = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ctl00_txtMatKhau")

# Gửi dữ liệu
username.send_keys(mssv)
password.send_keys(matkhau)

time.sleep(1)

# Nút đăng nhập
login_button = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ctl00_btnDangNhap")
login_button.click()

time.sleep(5)   # chờ trang load

# Sau khi bấm đăng nhập
time.sleep(2)

if "Sai thông tin đăng nhập" in driver.page_source:
    print(" Sai MSSV hoặc mật khẩu! Vui lòng thử lại.")
else:
    print(" Đăng nhập thành công!")




