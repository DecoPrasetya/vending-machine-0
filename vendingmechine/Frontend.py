import os
import shutil
import tkinter as tk
from collections import Counter
from tkinter import Frame, Label, Button, messagebox, Scrollbar, Text, simpledialog, Entry, filedialog
from tkinter import ttk

from PIL import Image, ImageTk

from controller import update_stock, load_products, get_admin_password, add_product, update_product, \
    delete_product, get_product_image_extensions, get_products  # TAMBAHKAN get_products


# ===================== HELPER FUNCTIONS =====================
def get_product_by_id(product_id):
    """Mendapatkan produk berdasarkan ID"""
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def get_product_name_by_id(product_id):
    """Mendapatkan nama produk berdasarkan ID"""
    product = get_product_by_id(product_id)
    return product["name"] if product else None


def get_product_price_by_id(product_id):
    """Mendapatkan harga produk berdasarkan ID"""
    product = get_product_by_id(product_id)
    return product["price"] if product else 0


def upload_image(product_name):
    """Fungsi untuk upload gambar produk"""
    filetypes = [
        ('Image files', '*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG'),
        ('All files', '*.*')
    ]

    filepath = filedialog.askopenfilename(
        title="Pilih Gambar Produk",
        filetypes=filetypes
    )

    if filepath:
        # Cek apakah folder images ada
        if not os.path.exists("images"):
            os.makedirs("images")

        # Dapatkan ekstensi file
        _, ext = os.path.splitext(filepath)

        # Nama file baru (gunakan nama produk)
        new_filename = product_name + ext.lower()
        destination = os.path.join("images", new_filename)

        try:
            # Copy file ke folder images
            shutil.copy2(filepath, destination)
            messagebox.showinfo("Berhasil", f"Gambar berhasil diupload ke:\n{destination}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengupload gambar: {str(e)}")
            return False

    return False


# ===================== INITIAL SETUP =====================
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
product_cards = []
product_stock_labels = []

# MUAT PRODUK DARI CONTROLLER
load_products()  # Pertama, muat produk ke database
products = get_products()  # Kemudian dapatkan list produk dari controller

print(f"DEBUG: Total products loaded: {len(products)}")  # Debug print
if products:
    print(f"DEBUG: First product: {products[0]}")  # Debug print

 
# ===================== FUNGSI LOAD GAMBAR =====================
def load_image_auto(name):
    """Load gambar produk dari folder images"""
    folder = "images"
    possible_ext = [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]

    for ext in possible_ext:
        path = os.path.join(folder, name + ext)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize((50, 50))
                return ImageTk.PhotoImage(img)
            except:
                print(f"[ERROR] Gagal load gambar: {path}")
                return None

    # Jika gambar tidak ditemukan
    print(f"[WARNING] Gambar tidak ditemukan: {name}")
    return None


# ===================== FUNGSI RESIZE DINAMIS =====================
def resize(event=None):
    w = root.winfo_width()
    h = root.winfo_height()
    left_width = int(w * 0.6)  # Kurangi dari 0.63
    right_width = int(w * 0.35)  # Naikkan dari 0.32

    left_panel.place(x=15, y=15, width=left_width, height=h - 30)
    right_panel.place(x=left_width + 25, y=15, width=right_width - 15, height=h - 30)

    # Update ukuran canvas dan items_frame
    if 'canvas' in globals():
        canvas.config(width=left_width - 30)  # Sesuaikan lebar canvas

    # Update ukuran product cards
    card_width = int((left_width - 100) / 3)  # 3 kolom dengan padding
    for card in product_cards:
        card.config(width=card_width, height=150)  # Fixed height atau sesuaikan

    # Update button sizes
    button_size = int(right_width / 8)
    for btn in keypad_buttons:
        btn.config(width=int(button_size / 15), height=int(button_size / 40))


root.bind("<Configure>", resize)


# ===================== FUNGSI PRODUK =====================
def select_product(product_id, stock_label, index):
    """Fungsi utama untuk memilih produk"""
    product = get_product_by_id(product_id)
    if not product:
        messagebox.showerror("Error", "Produk tidak ditemukan!")
        return

    current_stock = product["stock"]

    if current_stock <= 0:
        messagebox.showwarning("Stok Habis", f"{product['name']} sudah habis!")
        return

    # Kurangi stok
    new_stock = current_stock - 1

    # Update di dictionary
    product["stock"] = new_stock
    product["stock_display"] = f"Stok {new_stock}"

    # Update label di GUI
    stock_label.config(text=f"Stok {new_stock}")

    # Tambahkan ke keranjang
    selected_products.append({
        "id": product_id,
        "name": product["name"],
        "price": product["price"],
        "index": index
    })

    update_order_display()
    messagebox.showinfo("Ditambahkan", f"{product['name']} telah ditambahkan ke keranjang!")


def update_order_display():
    if not selected_products:
        order_text.delete(1.0, tk.END)
        order_text.insert(1.0, "Belum ada pesanan")
        total_price_var.set("TOTAL: Rp 0")
        return

    counter = Counter([p["name"] for p in selected_products])
    order_list = []

    for name, count in counter.items():
        # Cari harga satuan dari products
        unit_price = 0
        for product in products:
            if product["name"] == name:
                unit_price = product["price"]  # integer
                break

        order_list.append((name, count, unit_price * count))

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
    # Reload dari database untuk mendapatkan stok asli
    load_products()  # Fungsi dari controller
    global products
    products = get_products()  # Refresh products list

    # Reset semua label stok
    for i, product in enumerate(products):
        if i < len(product_stock_labels):
            product_stock_labels[i].config(text=f"Stok {product['stock']}")

    selected_products = []
    update_order_display()
    messagebox.showinfo("Dihapus", "Semua pesanan telah dihapus!")


def process_payment():
    if not selected_products:
        messagebox.showwarning("Keranjang Kosong", "Tambahkan produk terlebih dahulu!")
        return

    total = 0
    for prod in selected_products:
        total += prod["price"]

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
        # Cari harga produk
        unit_price = 0
        for prod in products:
            if prod["name"] == name:
                unit_price = prod["price"]
                break

        struk_text += f"{name} x{count}: Rp {unit_price * count:,}\n"

    struk_text += f"\nTotal: Rp {total:,}\n"
    struk_text += f"Uang: Rp {money_entered:,}\n"
    struk_text += f"Kembali: Rp {kembalian:,}\n"
    struk_text += "=" * 25

    messagebox.showinfo("Pembayaran Berhasil", struk_text)
    clear_order()
    clear()


# ===================== FUNGSI ADMIN =====================
def admin_login():
    """Fungsi untuk login admin"""
    password = simpledialog.askstring("Admin Login", "Masukkan password admin:", show='*')

    if password == get_admin_password():
        show_admin_panel()
    elif password is not None:
        messagebox.showerror("Login Gagal", "Password salah!")


def show_admin_panel():
    """Panel admin """
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Panel - Kelola Produk")
    admin_window.geometry("700x600")
    admin_window.configure(bg="#f0f0f0")

    # Notebook
    notebook = ttk.Notebook(admin_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # ===================== TAB KELOLA PRODUK  =====================
    manage_frame = Frame(notebook, bg="#f0f0f0")
    notebook.add(manage_frame, text="Kelola Produk")

    Label(manage_frame, text="KELOLA PRODUK", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

    product_list_frame = Frame(manage_frame, bg="white", relief="solid", bd=1)
    product_list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Header
    header = Frame(product_list_frame, bg="#e0e0e0")
    header.pack(fill="x")
    Label(header, text="Nama", width=20, font=("Arial", 10, "bold"), bg="#e0e0e0").pack(side="left", padx=5)
    Label(header, text="Harga", width=10, font=("Arial", 10, "bold"), bg="#e0e0e0").pack(side="left", padx=5)
    Label(header, text="Stok", width=7, font=("Arial", 10, "bold"), bg="#e0e0e0").pack(side="left", padx=5)
    Label(header, text="Aksi", width=25, font=("Arial", 10, "bold"), bg="#e0e0e0").pack(side="left", padx=5)

    for i, prod_data in enumerate(products):
        product_frame = Frame(product_list_frame, bg="white")
        product_frame.pack(fill="x", pady=3)

        Label(product_frame, text=prod_data["name"], width=20, anchor="w", bg="white").pack(side="left", padx=5)
        Label(product_frame, text=f"Rp {prod_data['price']:,}", width=10, bg="white").pack(side="left", padx=5)

        stock_label = Label(product_frame, text=str(prod_data["stock"]), width=7, bg="white")
        stock_label.pack(side="left", padx=5)

        # Fungsi tombol stok
        def add_stock(idx=i, lbl=stock_label):
            new = int(lbl.cget("text")) + 1
            lbl.config(text=str(new))
            products[idx]["stock"] = new
            products[idx]["stock_display"] = f"Stok {new}"

        def remove_stock(idx=i, lbl=stock_label):
            current = int(lbl.cget("text"))
            if current > 0:
                new = current - 1
                lbl.config(text=str(new))
                products[idx]["stock"] = new
                products[idx]["stock_display"] = f"Stok {new}"

        Button(product_frame, text="+", width=3, bg="green", fg="white",
               command=add_stock).pack(side="left", padx=3)
        Button(product_frame, text="-", width=3, bg="red", fg="white",
               command=remove_stock).pack(side="left", padx=3)

        # Tombol Edit
        def edit_selected(pid=prod_data["id"]):
            edit_product_window(pid)

        Button(product_frame, text="Edit", width=5, bg="#3498db", fg="white",
               command=edit_selected).pack(side="left", padx=3)

        # Tombol Hapus
        def delete_selected(pid=prod_data["id"], name=prod_data["name"]):
            confirm = messagebox.askyesno("Konfirmasi", f"Hapus produk '{name}'?")
            if confirm:
                if delete_product(pid):
                    messagebox.showinfo("Berhasil", "Produk dihapus.")
                    admin_window.destroy()
                    refresh_product_display()

        Button(product_frame, text="Hapus", width=6, bg="#e74c3c", fg="white",
               command=delete_selected).pack(side="left", padx=3)

    # ===== TAB TAMBAH PRODUK =====
    add_frame = Frame(notebook, bg="#f0f0f0")
    notebook.add(add_frame, text="Tambah Produk")

    Label(add_frame, text="TAMBAH PRODUK BARU", font=("Arial", 16, "bold"),
          bg="#f0f0f0").pack(pady=10)

    form_frame = Frame(add_frame, bg="white", relief="solid", bd=1)
    form_frame.pack(fill="x", padx=20, pady=10)

    # Nama Produk
    Label(form_frame, text="Nama Produk:", font=("Arial", 10), bg="white").grid(row=0, column=0, sticky="w", padx=10,
                                                                                pady=10)
    name_var = tk.StringVar()
    name_entry = Entry(form_frame, textvariable=name_var, font=("Arial", 10), width=30)
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    # Harga
    Label(form_frame, text="Harga (Rp):", font=("Arial", 10), bg="white").grid(row=1, column=0, sticky="w", padx=10,
                                                                               pady=10)
    price_var = tk.StringVar()
    price_entry = Entry(form_frame, textvariable=price_var, font=("Arial", 10), width=30)
    price_entry.grid(row=1, column=1, padx=10, pady=10)

    # Stok Awal
    Label(form_frame, text="Stok Awal:", font=("Arial", 10), bg="white").grid(row=2, column=0, sticky="w", padx=10,
                                                                              pady=10)
    stock_var = tk.StringVar(value="0")
    stock_entry = Entry(form_frame, textvariable=stock_var, font=("Arial", 10), width=30)
    stock_entry.grid(row=2, column=1, padx=10, pady=10)

    # Info Gambar
    Label(form_frame, text="Info Gambar:", font=("Arial", 10),
          bg="white").grid(row=3, column=0, sticky="w", padx=10, pady=10)
    image_info = Label(form_frame, text="Simpan gambar dengan nama yang sama\nFormat: PNG, JPG, JPEG",
                       font=("Arial", 8), bg="white", justify="left", fg="gray")
    image_info.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    # Tombol Upload (opsional sebelum simpan)
    def upload_new_product_image():
        name = name_var.get().strip()
        if not name:
            messagebox.showwarning("Peringatan", "Masukkan nama produk terlebih dahulu!")
            return

        upload_image(name)
        # Update info setelah upload
        existing_images = get_product_image_extensions(name)
        if existing_images:
            image_info.config(text=f"Gambar tersedia: {', '.join(existing_images)}", fg="green")

    btn_upload_new = Button(form_frame, text="Upload Gambar", font=("Arial", 9), bg="#3498db", fg="white",
                            command=upload_new_product_image)
    btn_upload_new.grid(row=3, column=2, padx=10, pady=10)

    def add_new_product():
        name = name_var.get().strip()
        price = price_var.get().strip()
        stock = stock_var.get().strip()

        if not name or not price or not stock:
            messagebox.showwarning("Input Error", "Semua field harus diisi!")
            return

        try:
            price_int = int(price)
            stock_int = int(stock)

            if price_int <= 0:
                messagebox.showwarning("Input Error", "Harga harus lebih dari 0!")
                return

            if stock_int < 0:
                messagebox.showwarning("Input Error", "Stok tidak boleh negatif!")
                return

            # Tambah produk ke database
            product_id = add_product(name, price_int, stock_int)

            if product_id:
                # Tanya upload gambar setelah produk berhasil ditambahkan
                if messagebox.askyesno("Upload Gambar",
                                       f"Produk '{name}' berhasil ditambahkan!\n\n""Apakah Anda ingin mengupload gambar sekarang?"):
                    upload_image(name)

                messagebox.showinfo("Berhasil", f"Produk '{name}' berhasil ditambahkan!")
                name_var.set("")
                price_var.set("")
                stock_var.set("0")
                admin_window.destroy()
                refresh_product_display()
            else:
                messagebox.showerror("Error", "Gagal menambahkan produk!")

        except ValueError:
            messagebox.showerror("Input Error", "Harga dan Stok harus angka!")

    def save_changes():
        try:
            for prod_data in products:
                product_id = prod_data["id"]
                current_stock = prod_data["stock"]
                success = update_stock(product_id, current_stock)
                if success:
                    print(f"Saved stock for {prod_data['name']}: {current_stock}")

            messagebox.showinfo("Berhasil", "Perubahan stok berhasil disimpan!")
            admin_window.destroy()
            refresh_product_display()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")

    Button(admin_window, text="Simpan Semua Perubahan", font=("Arial", 12),
           bg="#4CAF50", fg="white", command=save_changes).pack(pady=10)


def edit_product_window(product_id):
    """Window untuk edit detail produk"""
    edit_window = tk.Toplevel(root)
    edit_window.title(f"Edit Produk - ID: {product_id}")
    edit_window.geometry("450x450")  # Perbesar sedikit
    edit_window.configure(bg="#f0f0f0")

    # Cari produk berdasarkan ID
    product = None
    for prod in products:
        if prod["id"] == product_id:
            product = prod
            break

    if not product:
        messagebox.showerror("Error", "Produk tidak ditemukan!")
        edit_window.destroy()
        return

    Label(edit_window, text=f"EDIT PRODUK: {product['name']}",
          font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

    form_frame = Frame(edit_window, bg="white", relief="solid", bd=1)
    form_frame.pack(fill="both", padx=20, pady=10)

    # Nama Produk
    Label(form_frame, text="Nama Produk:", font=("Arial", 10),
          bg="white").grid(row=0, column=0, sticky="w", padx=10, pady=10)
    name_var = tk.StringVar(value=product["name"])
    name_entry = Entry(form_frame, textvariable=name_var, font=("Arial", 10), width=30)
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    # Harga
    Label(form_frame, text="Harga (Rp):", font=("Arial", 10),
          bg="white").grid(row=1, column=0, sticky="w", padx=10, pady=10)
    price_var = tk.StringVar(value=str(product["price"]))
    price_entry = Entry(form_frame, textvariable=price_var, font=("Arial", 10), width=30)
    price_entry.grid(row=1, column=1, padx=10, pady=10)

    # Stok
    Label(form_frame, text="Stok:", font=("Arial", 10),
          bg="white").grid(row=2, column=0, sticky="w", padx=10, pady=10)
    stock_var = tk.StringVar(value=str(product["stock"]))
    stock_entry = Entry(form_frame, textvariable=stock_var, font=("Arial", 10), width=30)
    stock_entry.grid(row=2, column=1, padx=10, pady=10)

    # Info Gambar - ROW 3
    Label(form_frame, text="Gambar Saat Ini:", font=("Arial", 10),
          bg="white").grid(row=3, column=0, sticky="w", padx=10, pady=10)

    # Frame untuk info gambar dan tombol
    image_frame = Frame(form_frame, bg="white")
    image_frame.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    existing_images = get_product_image_extensions(product["name"])
    if existing_images:
        image_info = Label(image_frame, text=f"Format tersedia: {', '.join(existing_images)}",
                           font=("Arial", 8), bg="white", justify="left", fg="green")
    else:
        image_info = Label(image_frame, text="Belum ada gambar",
                           font=("Arial", 8), bg="white", justify="left", fg="red")
    image_info.pack(anchor="w")

    # TOMBOL UPLOAD GAMBAR - ROW 4
    Label(form_frame, text="Upload Gambar:", font=("Arial", 10),
          bg="white").grid(row=4, column=0, sticky="w", padx=10, pady=10)

    upload_frame = Frame(form_frame, bg="white")
    upload_frame.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    def upload_for_edit():
        """Fungsi upload khusus untuk edit"""
        if upload_image(product["name"]):
            # Refresh info gambar
            existing_images_new = get_product_image_extensions(product["name"])
            if existing_images_new:
                image_info.config(text=f"Format tersedia: {', '.join(existing_images_new)}", fg="green")
            else:
                image_info.config(text="Belum ada gambar", fg="red")

    btn_upload = Button(upload_frame, text="Pilih Gambar", font=("Arial", 9),
                        bg="#3498db", fg="white", command=upload_for_edit)
    btn_upload.pack(side="left", padx=(0, 5))

    # Label info format
    Label(upload_frame, text="Format: PNG, JPG, JPEG",
          font=("Arial", 8), bg="white", fg="gray").pack(side="left")

    # Fungsi save edit
    def save_edit():
        new_name = name_var.get().strip()
        new_price = price_var.get().strip()
        new_stock = stock_var.get().strip()

        if not new_name or not new_price or not new_stock:
            messagebox.showwarning("Input Error", "Semua field harus diisi!")
            return

        try:
            price_int = int(new_price)
            stock_int = int(new_stock)

            if price_int <= 0:
                messagebox.showwarning("Input Error", "Harga harus lebih dari 0!")
                return

            if stock_int < 0:
                messagebox.showwarning("Input Error", "Stok tidak boleh negatif!")
                return

            # Update produk
            success = update_product(product_id, new_name, price_int, stock_int)

            if success:
                messagebox.showinfo("Berhasil", "Produk berhasil diupdate!")
                edit_window.destroy()
                refresh_product_display()
            else:
                messagebox.showerror("Error", "Gagal mengupdate produk!")

        except ValueError:
            messagebox.showerror("Input Error", "Harga dan Stok harus angka!")

    # Frame untuk tombol
    button_frame = Frame(edit_window, bg="#f0f0f0")
    button_frame.pack(pady=10)

    Button(button_frame, text="Simpan Perubahan", font=("Arial", 12),
           bg="#4CAF50", fg="white", command=save_edit).pack(side="left", padx=5)

    Button(button_frame, text="Batal", font=("Arial", 12),
           bg="#f44336", fg="white", command=edit_window.destroy).pack(side="left", padx=5)


def refresh_product_display():
    """Refresh tampilan produk di main window"""
    global products, product_cards, product_stock_labels

    # Reload produk dari database
    load_products()
    products = get_products()  # Refresh products list

    # Tampilkan ulang produk
    display_products()

    # Update layout
    resize()


# ===================== PANEL KIRI DENGAN SCROLLBAR PRODUK =====================
left_panel = Frame(root, bg="#00B4D8")
left_panel.place(x=15, y=15)

title = Label(
    left_panel,
    text="Vending Machine",
    font=("Itim", 20, "bold"),
    fg="#F5F5F5",
    bg="#00B4D8"
)
title.pack(pady=15)

# ===== CANVAS DENGAN SCROLLBAR UNTUK PRODUK =====
# Frame untuk canvas dan scrollbar
canvas_frame = Frame(left_panel, bg="#90E0EF")
canvas_frame.pack(fill="both", expand=True, pady=8)

# Canvas untuk menampung produk dengan scrollbar
canvas = tk.Canvas(canvas_frame, bg="#90E0EF", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

# Scrollbar vertikal
scrollbar = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

# Konfigurasi canvas
canvas.configure(yscrollcommand=scrollbar.set)

# Frame di dalam canvas untuk menampung produk
items_frame = Frame(canvas, bg="#90E0EF")
canvas.create_window((0, 0), window=items_frame, anchor="nw")


# Fungsi untuk update scrollregion
def update_scrollregion(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))
    # Update lebar canvas window
    canvas.itemconfig(canvas_window, width=canvas.winfo_width())


canvas_window = canvas.create_window((0, 0), window=items_frame, anchor="nw")
items_frame.bind("<Configure>", update_scrollregion)


# Fungsi untuk mouse wheel scrolling
def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


canvas.bind_all("<MouseWheel>", on_mousewheel)


# ===================== FUNGSI ITEM DENGAN GAMBAR DAN DICTIONARY =====================
def create_item(parent, product_dict, index):
    product_id = product_dict["id"]
    name = product_dict["name"]
    price = product_dict["price_display"]
    stock = product_dict["stock_display"]

    frame = Frame(parent, bg="white", highlightthickness=1, highlightbackground="#0077b6")
    frame.pack_propagate(False)

    # LOAD GAMBAR DARI FOLDER
    img = load_image_auto(name)

    def on_click(event):
        select_product(product_id, stock_label, index)

    frame.bind("<Button-1>", on_click)

    def on_enter(event):
        frame.config(bg="#e8f4fd", highlightbackground="#0096c7")

    def on_leave(event):
        frame.config(bg="white", highlightbackground="#0077b6")

    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)

    # Frame untuk gambar
    img_frame = Frame(frame, bg="white", height=60)
    img_frame.pack(fill="x", pady=(5, 0))
    img_frame.pack_propagate(False)

    if img:
        img_label = Label(img_frame, image=img, bg="white")
        img_label.image = img  # Keep reference
        img_label.pack()
        img_label.bind("<Button-1>", on_click)
    else:
        # Placeholder jika gambar tidak ditemukan
        placeholder = Label(img_frame, text="🛒", font=("Arial", 24), bg="white")
        placeholder.pack()
        placeholder.bind("<Button-1>", on_click)

    # Frame untuk informasi teks
    info_frame = Frame(frame, bg="white")
    info_frame.pack(fill="both", expand=True, padx=5, pady=5)

    name_label = Label(info_frame, text=name, font=("Itim", 11, "bold"), bg="white", wraplength=140)
    name_label.pack()

    price_label = Label(info_frame, text=price, font=("Itim", 10), fg="blue", bg="white")
    price_label.pack()

    stock_label = Label(info_frame, text=stock, font=("Itim", 9), bg="white")
    stock_label.pack(pady=(0, 5))

    for widget in [name_label, price_label, stock_label]:
        widget.bind("<Button-1>", on_click)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.config(cursor="hand2")

    click_label = Label(info_frame, text="[Klik untuk memesan]", font=("Itim", 7),
                        fg="gray", bg="white")
    click_label.pack(pady=(0, 5))
    click_label.bind("<Button-1>", on_click)

    return frame, stock_label


# CREATE PRODUK DARI DICTIONARY DENGAN GAMBAR
product_cards = []
product_stock_labels = []

# Grid configuration untuk items_frame
for i in range(3):  # 3 kolom
    items_frame.columnconfigure(i, weight=1)


# ===================== FUNGSI UNTUK MEMBUAT ULANG TAMPILAN PRODUK =====================
def display_products():
    """Menampilkan produk dalam grid layout"""
    global product_cards, product_stock_labels

    try:
        # Pastikan products ada dan tidak kosong
        if not products or len(products) == 0:
            print("DEBUG: products is empty")
            print(f"DEBUG: products variable type: {type(products)}")
            print(f"DEBUG: products value: {products}")

            # Tampilkan pesan di canvas
            no_products_label = Label(items_frame, text="Tidak ada produk tersedia",
                                      font=("Arial", 12), bg="#90E0EF", fg="red")
            no_products_label.pack(pady=50)
            return

        print(f"DEBUG: Displaying {len(products)} products")  # Debug print

        # Hapus widget lama jika ada
        for widget in items_frame.winfo_children():
            widget.destroy()

        product_cards = []
        product_stock_labels = []

        # Tampilkan produk dalam grid
        row = 0
        col = 0

        for i, product in enumerate(products):
            try:
                print(f"DEBUG: Creating product {i}: {product['name']}")  # Debug print
                item, stock_label = create_item(items_frame, product, i)
                item.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                product_cards.append(item)
                product_stock_labels.append(stock_label)

                col += 1
                if col == 3:
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Error creating product {i}: {e}")
                continue

        # Update ukuran frame produk
        for i in range(3):
            items_frame.columnconfigure(i, weight=1)

        # Update scrollregion setelah semua produk ditambahkan
        items_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    except Exception as e:
        print(f"Error in display_products: {e}")
        import traceback
        traceback.print_exc()  # Print traceback untuk debugging
        # Tampilkan pesan error
        error_label = Label(items_frame, text=f"Error loading products: {e}",
                            font=("Arial", 10), bg="#90E0EF", fg="red")
        error_label.pack(pady=50)


# ===================== Pesanan Box dengan SCROLLBAR =====================
order_box = Frame(left_panel, bg="#2c3e50")
order_box.pack(fill="both", expand=True, pady=15, padx=15)

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
order_scrollbar = Scrollbar(text_frame)
order_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Text widget untuk menampilkan pesanan
order_text = Text(text_frame, font=("Courier New", 9, "bold"),
                  fg="white", bg="#34495e",
                  width=40, height=10,
                  wrap=tk.WORD,
                  yscrollcommand=order_scrollbar.set,
                  state="normal")
order_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Konfigurasi scrollbar
order_scrollbar.config(command=order_text.yview)

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
welcome_box.pack(fill="x", pady=15, padx=15)

Label(welcome_box, text="SELAMAT DATANG", font=("Itim", 14, "bold"),
      fg="white", bg="#00B4D8").pack(pady=3)
Label(welcome_box, text="PILIH MENU:", font=("Itim", 12, "bold"),
      fg="white", bg="#00B4D8").pack()
Label(welcome_box, text="1. BELANJA", font=("Itim", 10), fg="white", bg="#00B4D8").pack()
Label(welcome_box, text="2. ADMIN", font=("Itim", 10), fg="white", bg="#00B4D8").pack()

money_box = Frame(right_panel, bg="#1a1f33")
money_box.pack(fill="x", pady=15, padx=15)

money_var = tk.StringVar(value="Rp 0")

Label(money_box, text="Uang Masuk:", font=("Arial", 11), fg="white", bg="#1a1f33").pack(anchor="w", pady=3)
Label(money_box, textvariable=money_var, font=("Arial", 16, "bold"), fg="white",
      bg="#1a1f33").pack(anchor="w", pady=3)

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
            keypad_frame, text=num, font=("Itim", 14),
            command=lambda n=num: keypad_press(n),
            relief="raised",
            borderwidth=1,
            width=4,
            height=1
        )
        btn.grid(row=r, column=c, padx=5, pady=5, ipadx=3, ipady=3)
        keypad_buttons.append(btn)
        index += 1

btn_clear = Button(keypad_frame, text="C", font=("Itim", 14),
                   bg="#c0392b", fg="white", command=clear,
                   width=4, height=1)

btn_zero = Button(keypad_frame, text="0", font=("Itim", 14),
                  command=lambda: keypad_press("0"),
                  width=4, height=1)

btn_ok = Button(keypad_frame, text="OK", font=("Itim", 14),
                bg="#27ae60", fg="white",
                command=process_payment,
                width=4, height=1)

btn_clear.grid(row=3, column=0, padx=5, pady=5, ipadx=3, ipady=3)
btn_zero.grid(row=3, column=1, padx=5, pady=5, ipadx=3, ipady=3)
btn_ok.grid(row=3, column=2, padx=5, pady=5, ipadx=3, ipady=3)

keypad_buttons.extend([btn_clear, btn_zero, btn_ok])

Button(right_panel, text="ADMIN", font=("Itim", 12, "bold"),
       bg="#f39c12", fg="white", command=admin_login,
       padx=5, pady=3).pack(pady=10, fill="x", padx=15)

# ===================== INISIALISASI AKHIR =====================
# Panggil display_products() setelah semua setup GUI selesai
try:
    display_products()
    print(f"DEBUG: After display_products, products count: {len(products)}")
except Exception as e:
    print(f"Error displaying products: {e}")
    import traceback

    traceback.print_exc()
    messagebox.showerror("Error", f"Gagal memuat produk: {e}")

root.mainloop()