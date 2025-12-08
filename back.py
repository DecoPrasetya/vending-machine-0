import os
import tkinter as tk
from collections import Counter
from tkinter import Frame, Label, Button, messagebox, Scrollbar, Text, simpledialog
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error


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
                product_id, name, harga, qty = row
                # Format harga ke string dengan pemisah ribuan
                harga_formatted = f"Rp {harga:,}".replace(",", ".")
                stok_text = f"Stok {qty}"
                # Simpan sebagai tuple dengan 4 elemen
                products.append((product_id, name, harga_formatted, stok_text))
            
            cursor.close()
            connection.close()
            print(f"Loaded {len(products)} products from database")
            return True
        except Error as e:
            print(f"Gagal memuat produk: {e}")
            return False
    else:
        print("Koneksi database gagal!")
        return False

def update_stock(product_id, new_stock):
    """Update stok produk di database"""
    connection = getConnection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE product SET qty = %s WHERE id = %s", 
                         (new_stock, product_id))
            connection.commit()
            cursor.close()
            connection.close()
            print(f"Updated stock for product {product_id} to {new_stock}")
            return True
        except Error as e:
            print(f"Gagal update stok: {e}")
            return False
    return False

# ===================== INISIALISASI APLIKASI =====================
root = tk.Tk()
root.title("Vending Machine")
root.configure(bg="#CAF0F8")

# Set ukuran window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.9)
window_height = int(screen_height * 0.85)
root.geometry(
    f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")

# ===================== VARIABEL GLOBAL =====================
selected_products = []
entered_number = ""
products = []  # Akan diisi dari database
product_cards = []
product_stock_labels = []
total_price_var = tk.StringVar(value="TOTAL: Rp 0")


# ===================== FUNGSI RESIZE DINAMIS =====================
def resize(event=None):
    w = root.winfo_width()
    h = root.winfo_height()
    left_width = int(w * 0.6)
    right_width = int(w * 0.35)

    left_panel.place(x=15, y=15, width=left_width, height=h - 30)
    right_panel.place(x=left_width + 25, y=15, width=right_width - 15, height=h - 30)

    for card in product_cards:
        card.config(width=int(left_width / 4.5), height=int((h - 150) / 5))

    button_size = int(right_width / 8)
    for btn in keypad_buttons:
        btn.config(width=int(button_size / 15), height=int(button_size / 40))


root.bind("<Configure>", resize)


# ===================== FUNGSI PRODUK =====================
def select_product(product_id, name, price, stock_label, index):
    stock_text = stock_label.cget("text")
    if "Stok" in stock_text:
        try:
            current_stock = int(stock_text.split(" ")[1])
            if current_stock <= 0:
                messagebox.showwarning("Stok Habis", f"{name} sudah habis!")
                return

            new_stock = current_stock - 1
            stock_label.config(text=f"Stok {new_stock}")
            selected_products.append({
                "id": product_id,  
                "name": name,
                "price": price,
                "index": index
            })
            update_order_display()
            messagebox.showinfo("Ditambahkan", f"{name} telah ditambahkan ke keranjang!")
        except (ValueError, IndexError):
            messagebox.showerror("Error", f"Format stok tidak valid: {stock_text}")
    else:
        messagebox.showwarning("Error", "Format stok tidak valid")


def update_order_display():
    if not selected_products:
        order_text.delete(1.0, tk.END)
        order_text.insert(1.0, "Belum ada pesanan")
        total_price_var.set("TOTAL: Rp 0")
        return

    counter = Counter([p["name"] for p in selected_products])
    order_list = []

    for name, count in counter.items():
        for prod in products:
            if prod[1] == name:  # prod[1] adalah nama produk
                try:
                    price = int(prod[2].replace("Rp ", "").replace(".", ""))
                    total_item = price * count
                    order_list.append((name, count, total_item))
                except ValueError:
                    print(f"Error parsing price for {name}: {prod[2]}")
                break

    mid = (len(order_list) + 1) // 2
    left_column = order_list[:mid]
    right_column = order_list[mid:]

    # Clear text widget
    order_text.delete(1.0, tk.END)

    # Tambahkan header
    order_text.insert(tk.END, "PESANAN SEMENTARA:\n\n")

    max_items = max(len(left_column), len(right_column))

    for i in range(max_items):
        left_text = ""
        right_text = ""

        if i < len(left_column):
            name, count, total = left_column[i]
            left_text = f"{name} x{count}: Rp {total:,}"

        if i < len(right_column):
            name, count, total = right_column[i]
            right_text = f"{name} x{count}: Rp {total:,}"

        col_width = 30
        line_text = f"{left_text:<{col_width}}  {right_text:<{col_width}}\n"
        order_text.insert(tk.END, line_text)

    total = sum(item[2] for item in order_list)
    total_price_var.set(f"TOTAL: Rp {total:,}")

    # Tambahkan garis dan total di bawah
    order_text.insert(tk.END, f"\n{'=' * 60}\n")


def clear_order():
    global selected_products
    for prod in selected_products:
        index = prod["index"]
        if 0 <= index < len(product_stock_labels) and 0 <= index < len(products):
            stock_label = product_stock_labels[index]
            stock_label.config(text=products[index][3])  # prod[3] adalah stok

    selected_products = []
    update_order_display()
    messagebox.showinfo("Dihapus", "Semua pesanan telah dihapus!")


def process_payment():
    if not selected_products:
        messagebox.showwarning("Keranjang Kosong", "Tambahkan produk terlebih dahulu!")
        return

    total = 0
    for prod in selected_products:
        try:
            price = int(prod["price"].replace("Rp ", "").replace(".", ""))
            total += price
        except ValueError:
            messagebox.showerror("Error", f"Harga tidak valid: {prod['price']}")
            return

    money_text = money_var.get().replace("Rp ", "")
    try:
        money_entered = int(money_text) if money_text else 0
    except:
        money_entered = 0

    if money_entered < total:
        messagebox.showwarning(
            "Uang Kurang",
            f"Uang Anda kurang Rp {total - money_entered:,}"
        )
        return

    kembalian = money_entered - total

    struk_text = "=== STRUK PEMBELIAN ===\n"
    struk_text += "Vending Machine\n\n"

    counter = Counter([p["name"] for p in selected_products])
    for name, count in counter.items():
        for prod in products:
            if prod[1] == name:  # prod[1] adalah nama
                try:
                    price = int(prod[2].replace("Rp ", "").replace(".", ""))
                    struk_text += f"{name} x{count}: Rp {price * count:,}\n"
                except ValueError:
                    struk_text += f"{name} x{count}: ERROR (harga tidak valid)\n"
                break

    struk_text += f"\nTotal: Rp {total:,}\n"
    struk_text += f"Uang: Rp {money_entered:,}\n"
    struk_text += f"Kembali: Rp {kembalian:,}\n"
    struk_text += "=" * 25

    messagebox.showinfo("Pembayaran Berhasil", struk_text)
    
    # Update stok di database setelah pembayaran
    for prod in selected_products:
        product_id = prod["id"]
        index = prod["index"]
        if 0 <= index < len(product_stock_labels):
            stock_label = product_stock_labels[index]
            try:
                current_stock = int(stock_label.cget("text").split(" ")[1])
                update_stock(product_id, current_stock)
            except (ValueError, IndexError):
                print(f"Error getting stock for product {product_id}")
    
    clear_order()
    clear()


# ===================== FUNGSI ADMIN =====================
def admin_login():
    """Fungsi untuk login admin"""
    password = simpledialog.askstring("Admin Login", "Masukkan password admin:", show='*')
    
    if password == "admin123":
        show_admin_panel()
    elif password is not None:
        messagebox.showerror("Login Gagal", "Password salah!")


def show_admin_panel():
    """Panel admin untuk mengelola stok"""
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Panel - Kelola Stok")
    admin_window.geometry("400x500")
    admin_window.configure(bg="#f0f0f0")
    
    Label(admin_window, text="ADMIN PANEL", font=("Arial", 16, "bold"), 
          bg="#f0f0f0").pack(pady=10)
    
    products_frame = Frame(admin_window, bg="white", relief="solid", bd=1)
    products_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    header_frame = Frame(products_frame, bg="#e0e0e0")
    header_frame.pack(fill="x", pady=(5, 0))
    Label(header_frame, text="Produk", width=20, font=("Arial", 10, "bold"), 
          bg="#e0e0e0").pack(side="left", padx=5)
    Label(header_frame, text="Stok", width=15, font=("Arial", 10, "bold"), 
          bg="#e0e0e0").pack(side="left", padx=5)
    Label(header_frame, text="Aksi", width=10, font=("Arial", 10, "bold"), 
          bg="#e0e0e0").pack(side="left", padx=5)
    
    for i, prod_data in enumerate(products):
        product_id, name, price, stock_text = prod_data
        try:
            current_stock = int(stock_text.split(" ")[1])
        except (ValueError, IndexError):
            current_stock = 0
        
        product_frame = Frame(products_frame, bg="white")
        product_frame.pack(fill="x", pady=2)
        
        Label(product_frame, text=name, width=20, anchor="w", 
              bg="white").pack(side="left", padx=5)
        
        stock_label = Label(product_frame, text=str(current_stock), width=15, 
                           bg="white")
        stock_label.pack(side="left", padx=5)
        
        def add_stock(idx=i, lbl=stock_label, prod_id=product_id, prod_name=name):
            current = int(lbl.cget("text"))
            new_stock = current + 1
            lbl.config(text=str(new_stock))
            if 0 <= idx < len(products):
                products[idx] = (prod_id, prod_name, price, f"Stok {new_stock}")
            if 0 <= idx < len(product_stock_labels):
                product_stock_labels[idx].config(text=f"Stok {new_stock}")
        
        def remove_stock(idx=i, lbl=stock_label, prod_id=product_id, prod_name=name):
            current = int(lbl.cget("text"))
            if current > 0:
                new_stock = current - 1
                lbl.config(text=str(new_stock))
                if 0 <= idx < len(products):
                    products[idx] = (prod_id, prod_name, price, f"Stok {new_stock}")
                if 0 <= idx < len(product_stock_labels):
                    product_stock_labels[idx].config(text=f"Stok {new_stock}")
        
        Button(product_frame, text="+", width=3, bg="green", fg="white",
               command=add_stock).pack(side="left", padx=2)
        Button(product_frame, text="-", width=3, bg="red", fg="white",
               command=remove_stock).pack(side="left", padx=2)
    
    def save_changes():
        try:
            for prod_data in products:
                product_id, name, price, stock_text = prod_data
                try:
                    current_stock = int(stock_text.split(" ")[1])
                    success = update_stock(product_id, current_stock)
                    if success:
                        print(f"Saved stock for {name}: {current_stock}")
                except (ValueError, IndexError):
                    print(f"Invalid stock format for {name}: {stock_text}")
            
            messagebox.showinfo("Berhasil", "Perubahan stok berhasil disimpan!")
            admin_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")
    
    Button(admin_window, text="Simpan Perubahan", font=("Arial", 12),
           bg="#4CAF50", fg="white", command=save_changes).pack(pady=10)
    
    Button(admin_window, text="Tutup", font=("Arial", 12),
           bg="#f44336", fg="white", command=admin_window.destroy).pack(pady=5)


# ===================== PANEL KIRI =====================
left_panel = Frame(root, bg="#00B4D8")
left_panel.place(x=15, y=15)

title = Label(
    left_panel,
    text="Vending Machine",
    font=("Arial", 20, "bold"),  # Ganti ke font yang lebih umum
    fg="#F5F5F5",
    bg="#00B4D8"
)
title.pack(pady=15)

items_frame = Frame(left_panel, bg="#90E0EF")
items_frame.pack(pady=8)

products = []

product_cards = []
product_stock_labels = []

# ===================== FUNGSI ITEM DENGAN GAMBAR =====================
def create_item(parent, product_id, name, price, stock, index):
    frame = Frame(parent, bg="white", highlightthickness=1, highlightbackground="#0077b6")
    frame.pack_propagate(False)

    # LOAD GAMBAR OTOMATIS
    img = load_image_auto(name)

    def on_click(event):
        select_product(product_id, name, price, stock_label, index)

    frame.bind("<Button-1>", on_click)

    def on_enter(event):
        frame.config(bg="#e8f4fd", highlightbackground="#0096c7")

    def on_leave(event):
        frame.config(bg="white", highlightbackground="#0077b6")

    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)
    
    if img:
        img_label = Label(frame, image=img, bg="white")
        img_label.image = img  # Simpan referensi
        img_label.pack(expand=True)
        img_label.bind("<Button-1>", on_click)
    else:
        no_img_label = Label(frame, text="[Gambar]", bg="white", 
                           font=("Arial", 8), fg="gray")
        no_img_label.pack(expand=True)
        no_img_label.bind("<Button-1>", on_click)

    name_label = Label(frame, text=name, font=("Arial", 10, "bold"), bg="white")
    name_label.pack()

    price_label = Label(frame, text=price, font=("Arial", 9), fg="blue", bg="white")
    price_label.pack()

    stock_label = Label(frame, text=stock, font=("Arial", 8), bg="white")
    stock_label.pack(pady=(0, 5))

    for widget in [name_label, price_label, stock_label]:
        widget.bind("<Button-1>", on_click)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.config(cursor="hand2")

    click_label = Label(frame, text="[Klik untuk memesan]", font=("Arial", 7),
                        fg="gray", bg="white")
    click_label.pack(pady=2)
    click_label.bind("<Button-1>", on_click)

    return frame, stock_label


def load_image_auto(name):
    folder = "images"
    possible_ext = [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]

    for ext in possible_ext:
        path = os.path.join(folder, name + ext)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize((50, 50))  # Gambar lebih kecil
                return ImageTk.PhotoImage(img)
            except:
                return None

    print(f"[WARNING] Gambar tidak ditemukan: {name}")
    return None


# ===================== LOAD DATA PRODUK =====================
# Load produk dari database
if not load_products():
    print("Menggunakan data produk default...")
    # Data default jika database kosong
    products = [
        (1, "Coca Cola", "Rp 8.000", "Stok 10"),
        (2, "Aqua", "Rp 5.000", "Stok 15"),
        (3, "Bintang", "Rp 20.000", "Stok 20"),
        (4, "Teh Pucuk", "Rp 5.000", "Stok 8"),
        (5, "Whisky", "Rp 300.000", "Stok 25"),
        (6, "Pocari Sweat", "Rp 10.000", "Stok 12"),
        (7, "Iceland", "Rp 120.000", "Stok 10"),
        (8, "Nescaffe", "Rp 10.000", "Stok 15"),
        (9, "Vodka", "Rp 130.000", "Stok 10")
    ]

# ===================== BUAT ITEM PRODUK =====================
row = 0
col = 0

for i, prod_data in enumerate(products):
    try:
        product_id, name, price, stock = prod_data
        item, stock_label = create_item(items_frame, product_id, name, price, stock, i)
        item.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        product_cards.append(item)
        product_stock_labels.append(stock_label)

        col += 1
        if col == 3:
            col = 0
            row += 1
    except Exception as e:
        print(f"Error creating product item {i}: {e}")

# Konfigurasi grid weight agar responsive
for i in range(3):
    items_frame.grid_columnconfigure(i, weight=1, uniform="col")
for i in range((len(products) + 2) // 3):
    items_frame.grid_rowconfigure(i, weight=1, uniform="row")

# ===================== Pesanan Box dengan SCROLLBAR =====================
order_box = Frame(left_panel, bg="#2c3e50")
order_box.pack(fill="both", expand=True, pady=15, padx=15)

# Header untuk PESANAN, TOTAL, dan Hapus Pesanan
order_header = Frame(order_box, bg="#2c3e50")
order_header.pack(fill="x", padx=10, pady=(5, 0))

# Label PESANAN di kiri
Label(order_header, text="PESANAN", font=("Arial", 12, "bold"),
      fg="white", bg="#2c3e50").pack(side="left", pady=3)

# Total Pesanan di tengah
total_price_label = Label(order_header, textvariable=total_price_var,
                          font=("Arial", 11, "bold"),
                          fg="#f1c40f", bg="#2c3e50")
total_price_label.pack(side="left", expand=True, pady=3)

# Tombol Hapus Pesanan di kanan
btn_clear_order = Button(order_header, text="Hapus Pesanan", font=("Arial", 9),
                         bg="#e74c3c", fg="white", command=clear_order,
                         padx=10, pady=4)
btn_clear_order.pack(side="right", pady=3)

# Frame untuk daftar pesanan DENGAN SCROLLBAR
order_content = Frame(order_box, bg="#34495e")
order_content.pack(fill="both", expand=True, padx=10, pady=10)

# Buat Text widget dengan Scrollbar
text_frame = Frame(order_content, bg="#34495e")
text_frame.pack(fill="both", expand=True)

# Scrollbar vertikal
scrollbar = Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Text widget untuk menampilkan pesanan
order_text = Text(text_frame, font=("Courier New", 9, "bold"),
                  fg="white", bg="#34495e",
                  wrap=tk.WORD,
                  yscrollcommand=scrollbar.set,
                  state="normal")
order_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Konfigurasi scrollbar
scrollbar.config(command=order_text.yview)

# Set text awal
order_text.insert(1.0, "Belum ada pesanan")

# Nonaktifkan editing oleh user
def disable_text_input(event=None):
    return "break"

order_text.bind("<Key>", disable_text_input)

# ===================== PANEL KANAN =====================
right_panel = Frame(root, bg="#90E0EF")
right_panel.place(x=600, y=15)  # Posisi sementara

welcome_box = Frame(right_panel, bg="#00B4D8")
welcome_box.pack(fill="x", pady=15, padx=15)

Label(welcome_box, text="SELAMAT DATANG", font=("Arial", 14, "bold"),
      fg="white", bg="#00B4D8").pack(pady=3)
Label(welcome_box, text="PILIH MENU:", font=("Arial", 12, "bold"),
      fg="white", bg="#00B4D8").pack()
Label(welcome_box, text="1. BELANJA", font=("Arial", 10), fg="white", bg="#00B4D8").pack()
Label(welcome_box, text="2. ADMIN", font=("Arial", 10), fg="white", bg="#00B4D8").pack()

money_box = Frame(right_panel, bg="#1a1f33")
money_box.pack(fill="x", pady=15, padx=15)

money_var = tk.StringVar(value="Rp 0")

Label(money_box, text="Uang Masuk:", font=("Arial", 11), fg="white", bg="#1a1f33").pack(anchor="w", pady=3)
Label(money_box, textvariable=money_var, font=("Arial", 16, "bold"), fg="white", bg="#1a1f33").pack(anchor="w", pady=3)

keypad_frame = Frame(right_panel, bg="#0f1323")
keypad_frame.pack(pady=15)

keypad_buttons = []


def keypad_press(num):
    global entered_number
    entered_number += num
    money_var.set("Rp " + entered_number)


def clear():
    global entered_number
    entered_number = ""
    money_var.set("Rp 0")


keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

index = 0
for r in range(3):
    for c in range(3):
        num = keys[index]
        btn = Button(
            keypad_frame, text=num, font=("Arial", 14),
            command=lambda n=num: keypad_press(n),
            relief="raised",
            borderwidth=2,
            width=4,
            height=1,
            bg="white",
            activebackground="#e0e0e0"
        )
        btn.grid(row=r, column=c, padx=5, pady=5, ipadx=5, ipady=5)
        keypad_buttons.append(btn)
        index += 1

btn_clear = Button(keypad_frame, text="C", font=("Arial", 14), 
                   bg="#c0392b", fg="white", command=clear, 
                   width=4, height=1, activebackground="#a93226")
btn_zero = Button(keypad_frame, text="0", font=("Arial", 14), 
                  command=lambda: keypad_press("0"),
                  width=4, height=1, bg="white", activebackground="#e0e0e0")
btn_ok = Button(keypad_frame, text="OK", font=("Arial", 14), 
                bg="#27ae60", fg="white", command=process_payment,
                width=4, height=1, activebackground="#229954")

btn_clear.grid(row=3, column=0, padx=5, pady=5, ipadx=5, ipady=5)
btn_zero.grid(row=3, column=1, padx=5, pady=5, ipadx=5, ipady=5)
btn_ok.grid(row=3, column=2, padx=5, pady=5, ipadx=5, ipady=5)

keypad_buttons.extend([btn_clear, btn_zero, btn_ok])

Button(right_panel, text="ADMIN", font=("Arial", 12, "bold"),
       bg="#f39c12", fg="white", command=admin_login,
       padx=10, pady=5).pack(pady=10, fill="x", padx=15)

# ===================== INISIALISASI LAYOUT =====================
# Panggil resize untuk inisialisasi awal
root.after(100, resize)

# Start aplikasi
try:
    root.mainloop()
except Exception as e:
    print(f"Error running application: {e}")