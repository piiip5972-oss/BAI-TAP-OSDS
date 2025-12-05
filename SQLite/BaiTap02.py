import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import re
import os # Thêm thư viện để kiểm tra/xóa file DB (tùy chọn)

## I. Cấu hình và Chuẩn bị
# Thiết lập tên file DB và Bảng
DB_FILE = 'Painters_Data.db'
TABLE_NAME = 'painters_info'
all_links = []

# Tùy chọn cho Chrome (có thể chạy ẩn nếu cần, nhưng để dễ debug thì không dùng)
# chrome_options = Options()
# chrome_options.add_argument("--headless") 

# Nếu muốn bắt đầu với DB trống, có thể xóa file cũ (Tùy chọn)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Đã xóa file DB cũ: {DB_FILE}")

# Mở kết nối SQLite và tạo bảng nếu chưa tồn tại
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tạo bảng
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    name TEXT PRIMARY KEY, -- Sử dụng tên làm khóa chính để tránh trùng lặp
    birth TEXT,
    death TEXT,
    nationality TEXT
);
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

## II. Lấy Đường dẫn (URLs)
print("\n--- Bắt đầu Lấy Đường dẫn ---")
# Lặp qua ký tự 'F' (chr(70))
for i in range(70, 71): 
    driver = None
    try:
        driver = webdriver.Chrome() # Khởi tạo driver cho phần này
        url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22"+chr(i)+"%22"
        driver.get(url)
        time.sleep(3)

        # Lấy tất cả thẻ ul
        ul_tags = driver.find_elements(By.TAG_NAME, "ul")
        
        # Thử chọn chỉ mục (index) 20. Cần kiểm tra lại nếu index này thay đổi.
        if len(ul_tags) > 20:
            ul_painters = ul_tags[19] 
            li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

            # Lọc các đường dẫn hợp lệ (có thuộc tính href)
            links = [tag.find_element(By.TAG_NAME, "a").get_attribute("href") 
                     for tag in li_tags if tag.find_elements(By.TAG_NAME, "a")]
            all_links.extend(links)
        else:
            print(f"Lỗi: Không tìm thấy thẻ ul ở chỉ mục 20 cho ký tự {chr(i)}.")

    except Exception as e:
        print(f"Lỗi khi lấy links cho ký tự {chr(i)}: {e}")
    finally:
        safe_quit_driver(driver) # Đóng driver sau khi xong phần này

print(f"Hoàn tất lấy đường dẫn. Tổng cộng {len(all_links)} links đã tìm thấy.")

## III. Lấy thông tin & LƯU TRỮ TỨC THỜI

print("\n--- Bắt đầu Cào và Lưu Trữ Tức thời ---")
count = 0
for link in all_links:
    # Giới hạn số lượng truy cập để thử nghiệm nhanh
    if (count >= 10): # Đã tăng lên 10 họa sĩ để có thêm dữ liệu mẫu
        break
    count = count + 1

    driver = None
    try:
        driver = webdriver.Chrome() 
        driver.get(link)
        time.sleep(2)

        # 1. Lấy tên họa sĩ
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""
        
        # 2. Lấy dữ liệu BIRTH / DEATH / NATIONALITY theo code bạn của bạn
        try:
            birth_text = driver.find_element(
                By.XPATH, "//th[contains(text(),'Born')]/following-sibling::td"
            ).text

            birth_match = re.findall(r'\d{4}|c\.\s*\d{4}', birth_text)
            birth = birth_match[0] if birth_match else ""
        except:
            birth = ""
            birth_text = ""

        # 3. Năm mất
        try:
            death_text = driver.find_element(
                By.XPATH, "//th[contains(text(),'Died')]/following-sibling::td"
            ).text

            death_match = re.findall(r'\d{4}|c\.\s*\d{4}', death_text)
            death = death_match[0] if death_match else ""
        except:
            death = ""

        # 4. Quốc tịch 
        # Tầng 1: Nationality / Citizenship
        try:
            nationality = driver.find_element(
                By.XPATH,
                "//th[contains(text(),'Nationality') or contains(text(),'Citizenship')]/following-sibling::td"
            ).text
        except:
            nationality = ""

        # Tầng 2: Lấy từ mục Born nếu dạng “City, Country”
        if nationality == "" and birth_text and "," in birth_text:
            possible_country = birth_text.split(",")[-1].strip()
            if len(possible_country) >= 3:
                nationality = possible_country

        # Tầng 3: Lấy từ đoạn văn “born in …”
        if nationality == "":
            try:
                paragraphs = driver.find_elements(By.TAG_NAME, "p")
                if paragraphs:
                    first_p = paragraphs[0].text
                    match = re.search(r"born in ([A-Za-z\s]+)", first_p, re.IGNORECASE)
                    if match:
                        nationality = match.group(1).strip()
            except:
                pass

        safe_quit_driver(driver)
        
        # 5. LƯU TỨC THỜI VÀO SQLITE
        insert_sql = f"""
        INSERT OR IGNORE INTO {TABLE_NAME} (name, birth, death, nationality) 
        VALUES (?, ?, ?, ?);
        """
        # Sử dụng 'INSERT OR IGNORE' để bỏ qua nếu Tên (PRIMARY KEY) đã tồn tại
        cursor.execute(insert_sql, (name, birth, death, nationality))
        conn.commit()
        print(f"  --> Đã lưu thành công: {name}")

    except Exception as e:
        print(f"Lỗi khi xử lý hoặc lưu họa sĩ {link}: {e}")
        safe_quit_driver(driver)
        
print("\nHoàn tất quá trình cào và lưu dữ liệu tức thời.")

## IV. Truy vấn SQL Mẫu và Đóng kết nối
#A. Yêu Cầu Thống Kê và Toàn Cục
# 1. Đếm tổng số họa sĩ đã được lưu trữ trong bảng.
cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
total = cursor.fetchone()[0]
print(f"\n1. Tổng số họa sĩ: {total}")

#2. Hiển thị 5 dòng dữ liệu đầu tiên để kiểm tra cấu trúc và nội dung bảng.
cursor.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 5")
print("\n2. 5 dòng đầu tiên:")
for r in cursor.fetchall():
    print(r)
#3. Liệt kê danh sách các quốc tịch duy nhất có trong tập dữ liệu.
cursor.execute(f"SELECT DISTINCT nationality FROM {TABLE_NAME}")
print("\n3. Quốc tịch duy nhất:")
for n in cursor.fetchall():
    print(n[0])

#B. Yêu Cầu Lọc và Tìm Kiếm
#4. Tìm và hiển thị tên của các họa sĩ có tên bắt đầu bằng ký tự 'F'.
cursor.execute(f"SELECT name FROM {TABLE_NAME} WHERE name LIKE 'F%'")
print("\n4. Họa sĩ tên bắt đầu F:")
for n in cursor.fetchall():
    print(n[0])
#5. Tìm và hiển thị tên và quốc tịch của những họa sĩ có quốc tịch chứa từ khóa 'French' (ví dụ: French, French-American).
cursor.execute(f"SELECT name, nationality FROM {TABLE_NAME} WHERE nationality LIKE '%French%'")
print("\n5. Họa sĩ quốc tịch chứa 'French':")
for n in cursor.fetchall():
    print(n)

#6. Hiển thị tên của các họa sĩ không có thông tin quốc tịch (hoặc để trống, hoặc NULL).
cursor.execute(f"SELECT name FROM {TABLE_NAME} WHERE nationality IS NULL OR nationality = ''")
print("\n6. Họa sĩ không có quốc tịch:")
for n in cursor.fetchall():
    print(n[0])

#7. Tìm và hiển thị tên của những họa sĩ có cả thông tin ngày sinh và ngày mất (không rỗng).
cursor.execute(f"SELECT name FROM {TABLE_NAME} WHERE birth != '' AND death != ''")
print("\n7. Họa sĩ có ngày sinh và ngày mất:")
for n in cursor.fetchall():
    print(n[0])

#8. Hiển thị tất cả thông tin của họa sĩ có tên chứa từ khóa '%Fales%' (ví dụ: George Fales Baker).
cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE name LIKE '%Fales%'")
print("\n8. Họa sĩ tên chứa 'Fales':")
for n in cursor.fetchall():
    print(n)

#C. Yêu Cầu Nhóm và Sắp Xếp
#9. Sắp xếp và hiển thị tên của tất cả họa sĩ theo thứ tự bảng chữ cái (A-Z).
cursor.execute(f"SELECT name FROM {TABLE_NAME} ORDER BY name ASC")
print("\n9. Họa sĩ A-Z:")
for n in cursor.fetchall():
    print(n[0])
    
#10. Nhóm và đếm số lượng họa sĩ theo từng quốc tịch.
cursor.execute(f"SELECT nationality, COUNT(*) FROM {TABLE_NAME} GROUP BY nationality")
print("\n10. Số lượng họa sĩ theo quốc tịch:")
for n in cursor.fetchall():
    print(n)


# Đóng kết nối cuối cùng
conn.close()
print("\nĐã đóng kết nối cơ sở dữ liệu.")