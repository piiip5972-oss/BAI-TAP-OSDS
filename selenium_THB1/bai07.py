from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

# I. Tạo nơi chứa dữ liệu + DataFrame rỗng


all_schools = []      # danh sách (mã trường, link)
d = pd.DataFrame({
    'short_name': [], 
    'name': [], 
    'address': [], 
    'rector': [], 
    'website': []
})

# II. CÀO TỪ TRANG DANH SÁCH TRƯỜNG ĐH VN

driver = webdriver.Chrome()
url = "https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_tr%C6%B0%E1%BB%9Dng_%C4%91%E1%BA%A1i_h%E1%BB%8Dc,_h%E1%BB%8Dc_vi%E1%BB%87n_v%C3%A0_cao_%C4%91%E1%BA%B3ng_t%E1%BA%A1i_Vi%E1%BB%87t_Nam"

try:
    driver.get(url)
    time.sleep(3)

    # Lấy tất cả các bảng wikitable
    tables = driver.find_elements(By.CSS_SELECTOR, "table.wikitable")

    for table in tables:
        rows = table.find_elements(By.TAG_NAME, "tr")

        for row in rows[1:]:   # bỏ hàng tiêu đề
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) >= 2:
                try:
                    short = tds[0].text                # Tên viết tắt
                    link = tds[1].find_element(By.TAG_NAME, "a").get_attribute("href")
                    all_schools.append((short, link))
                except:
                    pass

except:
    print("Lỗi lấy danh sách!")

driver.quit()

print("Tổng số link trường tìm thấy:", len(all_schools))


# III. MỞ TỪNG LINK TRƯỜNG → CÀO CHI TIẾT

count = 0
for short_name, link in all_schools:

    print("Đang cào:", short_name, "→", link)
    count += 1

    try:
        driver = webdriver.Chrome()
        driver.get(link)
        time.sleep(2)

        # TÊN TRƯỜNG
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""

        # ĐỊA CHỈ
        try:
            address = driver.find_element(
                By.XPATH, "(//th[contains(text(),'Địa chỉ')]/following::td)[1]"
            ).text
        except:
            address = ""

        # HIỆU TRƯỞNG
        try:
            rector = driver.find_element(
                By.XPATH, "(//th[contains(text(),'Hiệu trưởng')]/following-sibling::td)[1]"
            ).text
        except:
            rector = ""

        # WEBSITE
        try:
            website = driver.find_element(
                By.XPATH, "(//th[contains(text(),'Website')]/following-sibling::td//a)[1]"
            ).get_attribute("href")
        except:
            website = ""

        # Tạo dictionary → đưa vào DataFrame
        school = {
            'short_name': short_name,
            'name': name,
            'address': address,
            'rector': rector,
            'website': website
        }

        school_df = pd.DataFrame([school])
        d = pd.concat([d, school_df], ignore_index=True)

        driver.quit()

    except:
        print("Lỗi cào trường", short_name)
        pass

# IV. IN KẾT QUẢ + LƯU EXCEL
print(d)

file_name = "Danh_sach_truong_DH_VN.xlsx"
d.to_excel(file_name, index=False)

print("Đã lưu file Excel thành công →", file_name)

