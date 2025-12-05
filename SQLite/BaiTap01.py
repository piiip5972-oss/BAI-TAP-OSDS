import sqlite3

# 1. ket noi toi co so du lieu
conn = sqlite3.connect("inventory.db")

# tao doi tuong 'cursor' de thuc thi cac cau lenh sql
cursor = conn.cursor()

# 2.Thao tac vs Database va Table
#lenh SQL de tao bang products
sql1 = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price NUMERIC NOT NULL,
    quantity INTEGER
)
"""

# THUC THI CAU LEN TREN
cursor.execute(sql1)
conn.commit()# luu thay doi

# 3.CRUD
# 3.2 THEM INSERT
products_data = [
    ("Laptop A100", 999.99, 15),
    ("Mouse Wireless X", 25.50, 50),
    ("Monitor 27-inch", 249.00, 10)
]
# Lenh SQL de chen du lieu. Dung '?' de tranh loi SQL Injection
sql2 = """
INSERT INTO products(name, price, quantity)
VALUES
(?,?,?)
"""
# Them nhieu ban ghi cung luc
cursor.executemany(sql2, products_data)
conn.commit()

#3.2 READ (SELECT)
sql3 = "SELECT * FROM products"

# Thực thi truy vấn
cursor.execute(sql3)

# Lấy tất cả kết quả
all_products = cursor.fetchall()

# In tiêu đề
print(f"{'ID':<4} | {'Tên Sản Phẩm':<20} | {'Giá':<10} | {'Số Lượng':<10}")
# Lặp và in ra
for p in all_products:
    print(f"{p[0]:<4} | {p[1]:<20} | {p[2]:<10} | {p[3]:<10}")
# 3.3 UPDATE
print("\n--- SAU KHI UPDATE ---")
sql4 = """
    UPDATE products
    SET price = ?
    WHERE name = ?
"""
cursor.execute(sql4, (1099.99, "Laptop A100"))
conn.commit()

# đọc lại bảng
cursor.execute("SELECT * FROM products")
updated_products = cursor.fetchall()

print(f"{'ID':<4} | {'Tên Sản Phẩm':<20} | {'Giá':<10} | {'Số Lượng':<10}")
for p in updated_products:
    print(f"{p[0]:<4} | {p[1]:<20} | {p[2]:<10} | {p[3]:<10}")


# 3.4 DELETE
print("\n--- SAU KHI DELETE (xóa Mouse Wireless X) ---")
sql5 = """
DELETE FROM products
WHERE name = ?
"""
cursor.execute(sql5, ("Mouse Wireless X",))
conn.commit()

# đọc lại bảng
cursor.execute("SELECT * FROM products")
after_delete = cursor.fetchall()

print(f"{'ID':<4} | {'Tên Sản Phẩm':<20} | {'Giá':<10} | {'Số Lượng':<10}")
for p in after_delete:
    print(f"{p[0]:<4} | {p[1]:<20} | {p[2]:<10} | {p[3]:<10}")

# Dong ket noi
conn.close()
