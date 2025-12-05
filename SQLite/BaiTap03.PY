from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import sqlite3
import time
import pandas as pd
import re
import os # Thêm thư viện để kiểm tra/xóa file DB (tùy chọn)

###  KẾT NỐI SQLITE + TẠO BẢNG
# Thiết lập tên file DB và Bảng
DB_FILE = 'longchau_db.sqlite'
TABLE_NAME = 'products'
all_links = []

# Tùy chọn cho Chrome (có thể chạy ẩn nếu cần, nhưng để dễ debug thì không dùng)
# chrome_options = Options()
# chrome_options.add_argument("--headless") 

# Nếu muốn bắt đầu với DB trống, có thể xóa file cũ (Tùy chọn)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Đã xóa file DB cũ: {DB_FILE}")
    
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

create_table_sql = """
CREATE TABLE IF NOT EXISTS products(
    product_id TEXT,
    product_name TEXT,
    price REAL,
    original_price REAL,
    unit TEXT,
    product_url TEXT PRIMARY KEY
)
"""
cursor.execute(create_table_sql)
conn.commit()
print(f"Đã kết nối và chuẩn bị bảng '{TABLE_NAME}' trong '{DB_FILE}'.")

# Hàm đóng driver an toàn
def safe_quit_driver(driver):
    try:
        if driver:
            driver.quit()
    except:
        pass

### KHỞI TẠO WEBDRIVER FIREFOX

gecko_path = r"C:/Users/User/OneDrive/Desktop/Ma Nguon Mo/Selenium/project2/geckodriver.exe"
ser = Service(gecko_path)

options = webdriver.firefox.options.Options()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
options.headless = False

driver = webdriver.Firefox(options=options, service=ser)

### BƯỚC 1 – CÀO TẤT CẢ LINK SẢN PHẨM

url = "https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat"
driver.get(url)
time.sleep(3)

body = driver.find_element(By.TAG_NAME, "body")

# Nhấn “Xem thêm” nhiều lần
for _ in range(5):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "Xem thêm" in btn.text and "sản phẩm" in btn.text:
                btn.click()
                time.sleep(2)
                break
    except:
        pass

    body.send_keys(Keys.END)
    time.sleep(2)

time.sleep(3)

# Lấy link sản phẩm
product_links = []
all_a = driver.find_elements(By.CSS_SELECTOR, "a[href*='/thuc-pham-chuc-nang/']")

for a in all_a:
    href = a.get_attribute("href")
    if href and href.endswith(".html") and href not in product_links:
        product_links.append(href)

print(f"TỔNG SỐ LINK sản phẩm tìm được: {len(product_links)}")

###  BƯỚC 2 – TRUY CẬP TỪNG LINK → CÀO DỮ LIỆU
for idx, link in enumerate(product_links, start=1):
    try:
        driver.get(link)
        time.sleep(1)
        #  LẤY MÃ SẢN PHẨM 
        try:
            product_id = driver.find_element(By.CSS_SELECTOR, "span[data-test-id='sku']").text.strip()
        except:
            product_id = f"auto_{idx}"

        #  LẤY TÊN SẢN PHẨM 
        try:
            product_name = driver.find_element(By.CSS_SELECTOR, "h1[data-test='product_name']").text.strip()
        except:
            product_name = ""

        #  LẤY GIÁ BÁN 
        try:
            price = driver.find_element(By.CSS_SELECTOR, "span[data-test='price']").text
            price = price.replace("đ", "").replace(".", "").strip()
            price = float(price)
        except:
            price = None

        # LẤY GIÁ GỐC 
        try:
            original_price = driver.find_element(By.CSS_SELECTOR, "div[data-test='strike_price']").text
            original_price = original_price.replace("đ", "").replace(".", "").strip()
            original_price = float(original_price)
        except:
            original_price = None

        #  LẤY ĐƠN VỊ TÍNH 
        try:
            unit = driver.find_element(By.CSS_SELECTOR, "div[data-test='unit_lv1']").text.strip()
        except:
            unit = ""

        # LƯU TỨC THỜI VÀO SQLITE 
        cursor.execute(f"""
            INSERT OR IGNORE INTO {TABLE_NAME}
            (product_id, product_name, price, original_price, unit, product_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """, 
            (product_id, product_name, price, original_price, unit, link))

        conn.commit()

        print(f"Đã lưu sản phẩm {idx}/{len(product_links)}")

    except Exception as e:
        print(f"Lỗi khi xử lý {link} | {e}")

### ĐÓNG DRIVER 
driver.quit()
print("\nHoàn tất quá trình cào và lưu dữ liệu tức thời")

# Yêu Cầu Phân Tích Dữ Liệu
print("\n===== NHÓM 1: KIỂM TRA CHẤT LƯỢNG DỮ LIỆU =====\n")

# 1. Kiểm tra TRÙNG LẶP theo product_url hoặc product_name
cursor.execute(f"""
SELECT product_name, product_url, COUNT(*) AS so_lan
FROM {TABLE_NAME}
GROUP BY product_name, product_url
HAVING COUNT(*) > 1
""")
duplicates = cursor.fetchall()
print("1. Các bản ghi trùng lặp (theo product_url hoặc product_name):")
print(duplicates, "\n")

# 2. Kiểm tra dữ liệu thiếu giá (price NULL hoặc = 0)
cursor.execute(f"""
SELECT COUNT(*)
FROM {TABLE_NAME}
WHERE price IS NULL OR price = 0
""")
missing_price = cursor.fetchone()[0]
print(f"2. Số sản phẩm thiếu giá bán (price NULL hoặc 0): {missing_price}\n")

# 3. Kiểm tra giá bất thường (price > original_price)
cursor.execute(f"""
SELECT product_name, price, original_price
FROM {TABLE_NAME}
WHERE price IS NOT NULL AND original_price IS NOT NULL
  AND price > original_price
""")
wrong_price = cursor.fetchall()
print("3. Sản phẩm có giá bất thường (price > original_price):")
print(wrong_price, "\n")

# 4. Kiểm tra định dạng – danh sách unit duy nhất
cursor.execute(f"SELECT DISTINCT unit FROM {TABLE_NAME}")
units = cursor.fetchall()
print("4. Các đơn vị tính (unit) duy nhất:")
print(units, "\n")

# 5. Tổng số lượng bản ghi trong bảng
cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
total = cursor.fetchone()[0]
print(f"5. Tổng số sản phẩm đã được cào: {total}\n")

print("\n===== NHÓM 2: KHẢO SÁT & PHÂN TÍCH =====\n")

# 1. 10 sản phẩm có mức giảm giá lớn nhất
cursor.execute(f"""
SELECT product_name, price, original_price,
       (original_price - price) AS giam_gia
FROM {TABLE_NAME}
WHERE price IS NOT NULL AND original_price IS NOT NULL
ORDER BY giam_gia DESC
LIMIT 10
""")
top_discount = cursor.fetchall()
print("1. Top 10 sản phẩm giảm giá nhiều nhất:")
print(top_discount, "\n")

# 2. Sản phẩm đắt nhất
cursor.execute(f"""
SELECT *
FROM {TABLE_NAME}
WHERE price IS NOT NULL
ORDER BY price DESC
LIMIT 1
""")
highest_price = cursor.fetchone()
print("2. Sản phẩm có giá bán cao nhất:")
print(highest_price, "\n")

# 3. Thống kê số lượng sản phẩm theo đơn vị tính (unit)
cursor.execute(f"""
SELECT unit, COUNT(*) AS so_luong
FROM {TABLE_NAME}
GROUP BY unit
ORDER BY so_luong DESC
""")
unit_stat = cursor.fetchall()
print("3. Số lượng sản phẩm theo từng đơn vị (unit):")
print(unit_stat, "\n")

# 4. Tìm sản phẩm chứa từ khóa 'Vitamin C'
cursor.execute(f"""
SELECT *
FROM {TABLE_NAME}
WHERE product_name LIKE '%Vitamin C%'
""")
vitamin_c_products = cursor.fetchall()
print("4. Sản phẩm có tên chứa 'Vitamin C':")
print(vitamin_c_products, "\n")

# 5. Lọc sản phẩm có giá từ 100k đến 200k
cursor.execute(f"""
SELECT *
FROM {TABLE_NAME}
WHERE price BETWEEN 100000 AND 200000
""")
filtered_price = cursor.fetchall()
print("5. Sản phẩm có giá trong khoảng 100.000 – 200.000 VNĐ:")
print(filtered_price, "\n")

print("\n===== NHÓM 3: CÁC TRUY VẤN NÂNG CAO =====\n")

# 1. Sắp xếp tất cả sản phẩm theo giá bán từ thấp đến cao
cursor.execute(f"""
SELECT product_name, price
FROM {TABLE_NAME}
WHERE price IS NOT NULL
ORDER BY price ASC
""")
sorted_price = cursor.fetchall()
print("1. Danh sách sản phẩm (sắp xếp theo giá tăng dần):")
print(sorted_price[:20], "... (hiển thị 20 dòng đầu)\n")

# 2. Top 5 sản phẩm có phần trăm giảm giá cao nhất
cursor.execute(f"""
SELECT product_name, price, original_price,
       ROUND((original_price - price) * 100.0 / original_price, 2) AS percent_discount
FROM {TABLE_NAME}
WHERE price IS NOT NULL 
  AND original_price IS NOT NULL 
  AND original_price > 0
ORDER BY percent_discount DESC
LIMIT 5
""")
discount_percent = cursor.fetchall()
print("2. Top 5 sản phẩm có phần trăm giảm giá cao nhất:")
print(discount_percent, "\n")

# 3. Xóa bản ghi trùng lặp (chỉ giữ 1 bản ghi cho mỗi product_name)
# --- Bước 1: xem trùng lặp (không bắt buộc nhưng hữu ích)
cursor.execute(f"""
SELECT product_name, COUNT(*)
FROM {TABLE_NAME}
GROUP BY product_name
HAVING COUNT(*) > 1
""")
dups_check = cursor.fetchall()
print("3.1. Các product_name bị trùng trước khi xóa:")
print(dups_check, "\n")

# --- Bước 2: xóa trùng bằng CTE (chỉ giữ bản ghi có product_url nhỏ nhất)
cursor.execute(f"""
WITH ranked AS (
    SELECT rowid AS rid, 
           product_name,
           ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY product_url) AS rn
    FROM {TABLE_NAME}
)
DELETE FROM {TABLE_NAME}
WHERE rowid IN (SELECT rid FROM ranked WHERE rn > 1);
""")
conn.commit()

print("3.2. Đã xóa các bản ghi trùng lặp (giữ lại 1 bản ghi mỗi product_name).\n")

# 4. Phân tích nhóm giá
cursor.execute(f"""
SELECT
    CASE
        WHEN price < 50000 THEN 'Dưới 50k'
        WHEN price BETWEEN 50000 AND 100000 THEN '50k - 100k'
        WHEN price BETWEEN 100000 AND 200000 THEN '100k - 200k'
        ELSE 'Trên 200k'
    END AS nhom_gia,
    COUNT(*) AS so_luong
FROM {TABLE_NAME}
GROUP BY nhom_gia
ORDER BY so_luong DESC
""")
price_group = cursor.fetchall()
print("4. Phân tích số lượng sản phẩm theo nhóm giá:")
print(price_group, "\n")

# 5. Liệt kê các bản ghi có product_url NULL hoặc rỗng
cursor.execute(f"""
SELECT *
FROM {TABLE_NAME}
WHERE product_url IS NULL OR product_url = ''
""")
bad_urls = cursor.fetchall()
print("5. Các bản ghi có URL không hợp lệ:")
print(bad_urls, "\n")

# Dong ket noi
conn.close()


