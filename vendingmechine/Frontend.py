import os
import tkinter as tk
from collections import Counter
from tkinter import Frame, Label, Button, messagebox, Scrollbar, Text

from PIL import Image, ImageTk

root = tk.Tk()
root.title("Vending Machine")
root.configure(bg="#CAF0F8")

# Set ukuran window yang lebih kecil dan pas
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.9)  # 90% dari lebar layar
window_height = int(screen_height * 0.85)  # 85% dari tinggi layar
root.geometry(
    f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")

# ===================== VARIABEL GLOBAL =====================
selected_products = []
entered_number = ""
total_price_var = tk.StringVar(value="TOTAL: Rp 0")


# ===================== FUNGSI RESIZE DINAMIS =====================
def resize(event=None):
    w = root.winfo_width()
    h = root.winfo_height()
    left_width = int(w * 0.6)  # Kurangi dari 0.63
    right_width = int(w * 0.35)  # Naikkan dari 0.32

    left_panel.place(x=15, y=15, width=left_width, height=h - 30)  # Kurangi margin
    right_panel.place(x=left_width + 25, y=15, width=right_width - 15, height=h - 30)

    for card in product_cards:
        card.config(width=int(left_width / 4.5), height=int((h - 150) / 5))  # Kurangi height

    button_size = int(right_width / 8)
    for btn in keypad_buttons:
        btn.config(width=int(button_size / 15), height=int(button_size / 40))  # Tombol lebih kecil


root.bind("<Configure>", resize)


# ===================== FUNGSI PRODUK =====================
def select_product(name, price, stock_label, index):
    stock_text = stock_label.cget("text")
    if "Stok" in stock_text:
        current_stock = int(stock_text.split(" ")[1])
        if current_stock <= 0:
            messagebox.showwarning("Stok Habis", f"{name} sudah habis!")
            return

        new_stock = current_stock - 1
        stock_label.config(text=f"Stok {new_stock}")
        selected_products.append({
            "name": name,
            "price": price,
            "index": index
        })
        update_order_display()
        messagebox.showinfo("Ditambahkan", f"{name} telah ditambahkan ke keranjang!")
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
            if prod[0] == name:
                price = int(prod[1].replace("Rp ", "").replace(".", ""))
                total_item = price * count
                order_list.append((name, count, total_item))
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

        col_width = 30  # Kurangi col width
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
        stock_label = product_stock_labels[index]
        stock_label.config(text=products[index][2])

    selected_products = []
    update_order_display()
    messagebox.showinfo("Dihapus", "Semua pesanan telah dihapus!")


def process_payment():
    if not selected_products:
        messagebox.showwarning("Keranjang Kosong", "Tambahkan produk terlebih dahulu!")
        return

    total = 0
    for prod in selected_products:
        price = int(prod["price"].replace("Rp ", "").replace(".", ""))
        total += price

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
            if prod[0] == name:
                price = int(prod[1].replace("Rp ", "").replace(".", ""))
                struk_text += f"{name} x{count}: Rp {price * count:,}\n"
                break

    struk_text += f"\nTotal: Rp {total:,}\n"
    struk_text += f"Uang: Rp {money_entered:,}\n"
    struk_text += f"Kembali: Rp {kembalian:,}\n"
    struk_text += "=" * 25

    messagebox.showinfo("Pembayaran Berhasil", struk_text)
    clear_order()
    clear()


# ===================== PANEL KIRI =====================
left_panel = Frame(root, bg="#00B4D8")
left_panel.place(x=15, y=15)

title = Label(
    left_panel,
    text="Vending Machine",
    font=("Itim", 20, "bold"),  # Kurangi font size
    fg="#F5F5F5",
    bg="#00B4D8"
)
title.pack(pady=15)  # Kurangi padding

items_frame = Frame(left_panel, bg="#90E0EF")
items_frame.pack(pady=8)  # Kurangi padding

products = [
    ("Coca Cola", "Rp 8.000", "Stok 10"),
    ("Aqua", "Rp 5.000", "Stok 15"),
    ("Bintang", "Rp 20.000", "Stok 20"),
    ("Teh Pucuk", "Rp 5.000", "Stok 8"),
    ("Whisky", "Rp 300.000", "Stok 25"),
    ("Pocari Sweat", "Rp 10.000", "Stok 12"),
    ("Iceland", "Rp 120.000", "Stok 10"),
    ("Nescaffe", "Rp 10.000", "Stok 15"),
    ("Vodka", "Rp 130.000", "Stok 10")
]

product_cards = []
product_stock_labels = []


# ===================== FUNGSI ITEM DENGAN GAMBAR =====================
def create_item(parent, name, price, stock, index):
    frame = Frame(parent, bg="white", highlightthickness=1, highlightbackground="#0077b6")  # Kurangi border
    frame.pack_propagate(False)

    # LOAD GAMBAR OTOMATIS - ukuran lebih kecil
    img = load_image_auto(name)

    def on_click(event):
        select_product(name, price, stock_label, index)

    frame.bind("<Button-1>", on_click)

    def on_enter(event):
        frame.config(bg="#e8f4fd", highlightbackground="#0096c7")

    def on_leave(event):
        frame.config(bg="white", highlightbackground="#0077b6")

    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)

    if img:
        img_label = Label(frame, image=img, bg="white")
        img_label.image = img
        img_label.pack(pady=3)  # Kurangi padding
        img_label.bind("<Button-1>", on_click)

    name_label = Label(frame, text=name, font=("Itim", 11, "bold"), bg="white")  # Font lebih kecil
    name_label.pack()

    price_label = Label(frame, text=price, font=("Itim", 10), fg="blue", bg="white")  # Font lebih kecil
    price_label.pack()

    stock_label = Label(frame, text=stock, font=("Itim", 9), bg="white")  # Font lebih kecil
    stock_label.pack(pady=(0, 5))  # Kurangi padding

    for widget in [name_label, price_label, stock_label]:
        widget.bind("<Button-1>", on_click)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.config(cursor="hand2")

    click_label = Label(frame, text="[Klik untuk memesan]", font=("Itim", 7),  # Font lebih kecil
                        fg="gray", bg="white")
    click_label.pack(pady=2)  # Kurangi padding
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


row = 0
col = 0

for i, (name, price, stock) in enumerate(products):
    item, stock_label = create_item(items_frame, name, price, stock, i)
    item.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")  # Kurangi padding
    product_cards.append(item)
    product_stock_labels.append(stock_label)

    col += 1
    if col == 3:
        col = 0
        row += 1

# ===================== Pesanan Box dengan SCROLLBAR =====================
order_box = Frame(left_panel, bg="#2c3e50")
order_box.pack(fill="both", expand=True, pady=15, padx=15)  # expand=True agar bisa memenuhi ruang

# Header untuk PESANAN, TOTAL, dan Hapus Pesanan
order_header = Frame(order_box, bg="#2c3e50")
order_header.pack(fill="x", padx=10, pady=(5, 0))

# Label PESANAN di kiri
Label(order_header, text="PESANAN", font=("Itim", 12, "bold"),
      fg="white", bg="#2c3e50").pack(side="left", pady=3)

# Total Pesanan di tengah (pakai StringVar)
total_price_label = Label(order_header, textvariable=total_price_var,
                          font=("Itim", 11, "bold"),
                          fg="#f1c40f", bg="#2c3e50")
total_price_label.pack(side="left", expand=True, pady=3)

# Tombol Hapus Pesanan di kanan
btn_clear_order = Button(order_header, text="Hapus Pesanan", font=("Itim", 9),
                         bg="#e74c3c", fg="white", command=clear_order,
                         padx=8, pady=2)
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
                  width=40, height=10,  # Ukuran minimum
                  wrap=tk.WORD,  # Wrap text
                  yscrollcommand=scrollbar.set,
                  state="normal")  # Bisa diedit untuk insert text
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
right_panel.place(x=600, y=15)

welcome_box = Frame(right_panel, bg="#00B4D8")
welcome_box.pack(fill="x", pady=15, padx=15)  # Kurangi padding

Label(welcome_box, text="SELAMAT DATANG", font=("Itim", 14, "bold"),  # Font lebih kecil
      fg="white", bg="#00B4D8").pack(pady=3)  # Kurangi padding
Label(welcome_box, text="PILIH MENU:", font=("Itim", 12, "bold"),  # Font lebih kecil
      fg="white", bg="#00B4D8").pack()
Label(welcome_box, text="1. BELANJA", font=("Itim", 10), fg="white", bg="#00B4D8").pack()  # Font lebih kecil
Label(welcome_box, text="2. ADMIN", font=("Itim", 10), fg="white", bg="#00B4D8").pack()  # Font lebih kecil

money_box = Frame(right_panel, bg="#1a1f33")
money_box.pack(fill="x", pady=15, padx=15)  # Kurangi padding

money_var = tk.StringVar(value="Rp 0")

Label(money_box, text="Uang Masuk:", font=("Arial", 11), fg="white", bg="#1a1f33").pack(anchor="w",
                                                                                        pady=3)  # Font lebih kecil
Label(money_box, textvariable=money_var, font=("Arial", 16, "bold"), fg="white",  # Font lebih kecil
      bg="#1a1f33").pack(anchor="w", pady=3)  # Kurangi padding

keypad_frame = Frame(right_panel, bg="#0f1323")
keypad_frame.pack(pady=15)  # Kurangi padding

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
            keypad_frame, text=num, font=("Itim", 14),  # Font lebih kecil
            command=lambda n=num: keypad_press(n),
            relief="raised",
            borderwidth=1,  # Border lebih tipis
            width=4,  # Tombol lebih kecil
            height=1
        )
        btn.grid(row=r, column=c, padx=5, pady=5, ipadx=3, ipady=3)  # Padding lebih kecil
        keypad_buttons.append(btn)
        index += 1

btn_clear = Button(keypad_frame, text="C", font=("Itim", 14),  # Font lebih kecil
                   bg="#c0392b", fg="white", command=clear,
                   width=4, height=1)

btn_zero = Button(keypad_frame, text="0", font=("Itim", 14),  # Font lebih kecil
                  command=lambda: keypad_press("0"),
                  width=4, height=1)

btn_ok = Button(keypad_frame, text="OK", font=("Itim", 14),  # Font lebih kecil
                bg="#27ae60", fg="white",
                command=process_payment,
                width=4, height=1)

btn_clear.grid(row=3, column=0, padx=5, pady=5, ipadx=3, ipady=3)  # Padding lebih kecil
btn_zero.grid(row=3, column=1, padx=5, pady=5, ipadx=3, ipady=3)  # Padding lebih kecil
btn_ok.grid(row=3, column=2, padx=5, pady=5, ipadx=3, ipady=3)  # Padding lebih kecil

keypad_buttons.extend([btn_clear, btn_zero, btn_ok])

Button(right_panel, text="ADMIN", font=("Itim", 12, "bold"),  # Font lebih kecil
       bg="#f39c12", fg="white",
       padx=5, pady=3).pack(pady=10, fill="x", padx=15)  # Kurangi padding

root.mainloop()