import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox
import os

# ===================== VARIABEL GLOBAL =====================
products = []  # Akan diisi dari database

# ===================== FUNGSI DATABASE =====================
def getConnection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="vending_machine",
            port=3306
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Connection Error: {err}")
        return None

def load_products():
    """Memuat produk dari database"""
    global products
    products = []
    
    connection = getConnection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM product ORDER BY id")
            rows = cursor.fetchall()
            
            for row in rows:
                id, name, qty, harga = row
                product_data = {
                    "id": id,
                    "name": name,
                    "price": harga,  # Simpan sebagai integer untuk perhitungan
                    "price_display": f"Rp {harga:,}".replace(",", "."),  # Untuk display
                    "stock": qty,  # Simpan sebagai integer
                    "stock_display": f"Stok {qty}"  # Untuk display
                }
                products.append(product_data)
            
            cursor.close()
            connection.close()
            
            # DEBUG PRINT
            print("=" * 50)
            print("PRODUCTS LOADED (DICTIONARY FORMAT)")
            print(f"Total products: {len(products)}")
            for p in products:
                print(f"  id: {p['id']}, name: {p['name']}, price: {p['price']}, stock: {p['stock']}")
            print("=" * 50)
            
            return True
            
        except Error as e:
            messagebox.showerror("Database Error", f"Gagal memuat produk: {e}")
            if connection:
                connection.close()
            return False
    return False

load_products()

def update_stock(product_id, new_stock):
    """Update stok produk di database"""
    connection = getConnection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE product SET qty = %s WHERE id = %s", (new_stock, product_id))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Gagal update stok: {e}")
            if connection:
                connection.close()
            return False
    return False

def get_product_by_id(product_id):
    """Mendapatkan informasi produk berdasarkan ID"""
    connection = getConnection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT name, harga, qty FROM product WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            cursor.close()
            connection.close()
            return product
        except Error as e:
            messagebox.showerror("Database Error", f"Gagal mengambil data produk: {e}")
            if connection:
                connection.close()
            return None
    return None

def get_admin_password():
    """Ambil password admin dari database"""
    connection = getConnection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT password FROM admin")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result[0] if result else None
        except Error as e:
            print(f"Error getting admin password: {e}")
            if connection:
                connection.close()
            return None
    return None

# ===================== FUNGSI CRUD PRODUK =====================
def add_product(name, price, stock):
    """Menambahkan produk baru ke database"""
    connection = getConnection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO product (name, harga, qty) VALUES (%s, %s, %s)",
                (name, price, stock)
            )
            connection.commit()
            product_id = cursor.lastrowid
            cursor.close()
            connection.close()
            
            # Reload products
            load_products()
            return product_id
        except Error as e:
            messagebox.showerror("Database Error", f"Gagal menambahkan produk: {e}")
            if connection:
                connection.close()
            return None
    return None

def update_product(product_id, name=None, price=None, stock=None):
    """Update data produk di database"""
    connection = getConnection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Build dynamic update query
            update_fields = []
            values = []
            
            if name is not None:
                update_fields.append("name = %s")
                values.append(name)
            if price is not None:
                update_fields.append("harga = %s")
                values.append(price)
            if stock is not None:
                update_fields.append("qty = %s")
                values.append(stock)
            
            if update_fields:
                values.append(product_id)
                query = f"UPDATE product SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(query, values)
                connection.commit()
            
            cursor.close()
            connection.close()
            
            # Reload products
            load_products()
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Gagal update produk: {e}")
            if connection:
                connection.close()
            return False
    return False

def delete_product(product_id):
    """Menghapus produk dari database"""
    connection = getConnection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
            connection.commit()
            cursor.close()
            connection.close()
            
            # Reload products
            load_products()
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Gagal menghapus produk: {e}")
            if connection:
                connection.close()
            return False
    return False

def get_product_image_extensions(name):
    """Mendapatkan ekstensi file gambar yang tersedia untuk produk"""
    folder = "images"
    possible_ext = [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]
    existing_images = []
    
    for ext in possible_ext:
        path = os.path.join(folder, name + ext)
        if os.path.exists(path):
            existing_images.append(ext)
    
    return existing_images