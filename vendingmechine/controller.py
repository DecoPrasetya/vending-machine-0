import mysql .connector
from mysql.connector import Error
import tkinter as tk
from tkinter import Frame, Label, Button, messagebox, Entry, StringVar, IntVar

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
            cursor.execute("SELECT id, name, harga, qty FROM product ORDER BY id")
            rows = cursor.fetchall()
            
            for row in rows:
                id, name, harga, qty = row
                # Format harga ke string dengan pemisah ribuan
                harga = f"Rp {harga:,}".replace(",", ".")
                stok = f"Stok {qty}"
                products.append((id, name, harga, stok))
            
            cursor.close()
            connection.close()
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Gagal memuat produk: {e}")
            connection.close()
            return False
    return False

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
            connection.close()
            return None
    return None