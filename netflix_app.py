import sqlite3import reimport tkinter as tkfrom tkinter import ttk, messagebox, simpledialogfrom datetime import datetime, date

DB_NAME = "netflix_final_full.db"EMAIL_RE = re.compile(r"^[\w.-]+@[\w.-]+.\w+$")

COUNTRIES = ["Türkiye", "Suriye", "Filistin", "Ürdün", "Lübnan", "Irak", "Mısır", "Almanya", "Fransa", "ABD", "Kanada", "Diğer"]

PROGRAMS = [("Interstellar", "Film", "Aksiyon ve Macera, Drama, Bilim Kurgu", 2014, 1, 169),("Başlangıç", "Film", "Aksiyon ve Macera, Bilim Kurgu", 2010, 1, 148),("Kara Şövalye", "Film", "Aksiyon ve Macera", 2008, 1, 152),("Yüzüklerin Efendisi İki Kule", "Film", "Aksiyon ve Macera, Fantastik", 2002, 1, 179),("Shrek", "Film", "Çocuk ve Aile, Komedi", 2001, 1, 90),("Kung Fu Panda", "Film", "Çocuk ve Aile, Aksiyon ve Macera", 2008, 1, 92),("Dangal", "Film", "Drama", 2016, 1, 161),("Jaws", "Film", "Gerilim", 1975, 1, 124),("Stranger Things", "Dizi", "Aksiyon ve Macera, Korku, Bilim Kurgu", 2016, 10, 50),("The Blacklist", "Dizi", "Aksiyon ve Macera, Gerilim", 2013, 10, 43),("How I Met Your Mother", "Dizi", "Komedi, Romantik", 2005, 10, 22),("Diriliş Ertuğrul", "Dizi", "Aksiyon ve Macera, Drama", 2014, 10, 45),("Atiye", "Dizi", "Aksiyon ve Macera, Romantik", 2019, 8, 45),("Car Masters", "Tv Show", "Reality Program", 2018, 8, 40),]

def parse_birth_date(text):text = text.strip()for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"):try:return datetime.strptime(text, fmt).date().isoformat()except ValueError:passraise ValueError("Doğum tarihi yanlış. Örnek: 2004-04-03 veya 03/04/2004")

def calculate_age(birth_iso):b = date.fromisoformat(birth_iso)today = date.today()return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

class Database:def init(self):self.con = sqlite3.connect(DB_NAME)self.con.row_factory = sqlite3.Rowself.con.execute("PRAGMA foreign_keys = ON")self.create_tables()self.seed()

def q(self, sql, params=(), one=False):
    cur = self.con.execute(sql, params)
    rows = cur.fetchall()
    if one:
        return rows[0] if rows else None
    return rows

def x(self, sql, params=()):
    cur = self.con.execute(sql, params)
    self.con.commit()
    return cur.lastrowid

def create_tables(self):
    self.con.executescript("""
    CREATE TABLE IF NOT EXISTS Rol(
        rol_id INTEGER PRIMARY KEY,
        rol_adi TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Kullanici(
        kullanici_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rol_id INTEGER NOT NULL,
        ad TEXT NOT NULL,
        soyad TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        sifre TEXT NOT NULL,
        dogum_tarihi TEXT NOT NULL,
        cinsiyet TEXT NOT NULL,
        ulke TEXT NOT NULL,
        aktif INTEGER DEFAULT 1,
        FOREIGN KEY(rol_id) REFERENCES Rol(rol_id)
    );

    CREATE TABLE IF NOT EXISTS Program(
        program_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT UNIQUE NOT NULL,
        aciklama TEXT,
        program_tipi TEXT NOT NULL,
        yayin_yili INTEGER NOT NULL,
        bolum_sayisi INTEGER NOT NULL,
        bolum_uzunlugu INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Tur(
        tur_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tur_adi TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ProgramTur(
        program_id INTEGER,
        tur_id INTEGER,
        PRIMARY KEY(program_id, tur_id),
        FOREIGN KEY(program_id) REFERENCES Program(program_id) ON DELETE CASCADE,
        FOREIGN KEY(tur_id) REFERENCES Tur(tur_id)
    );

    CREATE TABLE IF NOT EXISTS KullaniciTur(
        kullanici_id INTEGER,
        tur_id INTEGER,
        PRIMARY KEY(kullanici_id, tur_id),
        FOREIGN KEY(kullanici_id) REFERENCES Kullanici(kullanici_id),
        FOREIGN KEY(tur_id) REFERENCES Tur(tur_id)
    );

    CREATE TABLE IF NOT EXISTS Favori(
        favori_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_id INTEGER,
        program_id INTEGER,
        UNIQUE(kullanici_id, program_id),
        FOREIGN KEY(kullanici_id) REFERENCES Kullanici(kullanici_id),
        FOREIGN KEY(program_id) REFERENCES Program(program_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS KullaniciProgram(
        kullanici_id INTEGER,
        program_id INTEGER,
        son_bolum INTEGER DEFAULT 1,
        kalinan_dakika INTEGER DEFAULT 0,
        tamamlandi INTEGER DEFAULT 0,
        puan INTEGER,
        son_tarih TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(kullanici_id, program_id),
        FOREIGN KEY(kullanici_id) REFERENCES Kullanici(kullanici_id),
        FOREIGN KEY(program_id) REFERENCES Program(program_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS IzlemeLog(
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_id INTEGER,
        program_id INTEGER,
        bolum_no INTEGER,
        izleme_suresi INTEGER,
        tamamlandi INTEGER,
        puan INTEGER,
        tarih TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(kullanici_id) REFERENCES Kullanici(kullanici_id),
        FOREIGN KEY(program_id) REFERENCES Program(program_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS OturumLog(
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_id INTEGER,
        islem TEXT,
        tarih TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

def seed(self):
    self.x("INSERT OR IGNORE INTO Rol VALUES(1,'normal')")
    self.x("INSERT OR IGNORE INTO Rol VALUES(2,'admin')")

    self.x("""
    INSERT OR IGNORE INTO Kullanici
    (kullanici_id, rol_id, ad, soyad, email, sifre, dogum_tarihi, cinsiyet, ulke)
    VALUES(1,2,'Admin','User','admin@netflix.local','admin123','1990-01-01','Erkek','Türkiye')
    """)

    if self.q("SELECT COUNT(*) c FROM Program", one=True)["c"] > 0:
        return

    for ad, tip, turler, yil, bolum, sure in PROGRAMS:
        pid = self.x("""
        INSERT INTO Program(ad, aciklama, program_tipi, yayin_yili, bolum_sayisi, bolum_uzunlugu)
        VALUES(?,?,?,?,?,?)
        """, (ad, ad + " açıklaması.", tip, yil, bolum, sure))

        for tur in [t.strip() for t in turler.split(",")]:
            self.x("INSERT OR IGNORE INTO Tur(tur_adi) VALUES(?)", (tur,))
            tid = self.q("SELECT tur_id FROM Tur WHERE tur_adi=?", (tur,), True)["tur_id"]
            self.x("INSERT OR IGNORE INTO ProgramTur VALUES(?,?)", (pid, tid))

class App(tk.Tk):def init(self):super().init()self.db = Database()self.user = Noneself.title("Netflix Benzeri Platform")self.geometry("1250x760")self.configure(bg="#070707")self.make_style()self.login_page()

def make_style(self):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", padding=8, font=("Segoe UI", 10, "bold"))
    style.configure("TNotebook", background="#141414", borderwidth=0)
    style.configure("TNotebook.Tab", background="#2b2b2b", foreground="white", padding=[14, 7], font=("Segoe UI", 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", "#e50914")], foreground=[("selected", "white")])
    style.configure("Treeview", background="#ffffff", foreground="#111111", rowheight=32, fieldbackground="#ffffff", font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background="#dcdcdc", foreground="#111111", font=("Segoe UI", 10, "bold"))

def clear(self):
    for w in self.winfo_children():
        w.destroy()

def outside_background(self):
    c = tk.Canvas(self, bg="#070707", highlightthickness=0)
    c.pack(fill="both", expand=True)
    c.create_rectangle(0, 0, 1250, 760, fill="#080808", outline="")
    c.create_oval(-200, -120, 420, 450, fill="#5a0008", outline="")
    c.create_oval(850, 300, 1500, 900, fill="#240060", outline="")
    c.create_text(625, 75, text="NETFLIX PROJECT", fill="white", font=("Segoe UI", 36, "bold"))
    c.create_text(625, 120, text="Python Desktop App + SQLite Database", fill="#dddddd", font=("Segoe UI", 13))
    return c

def panel(self, canvas, width, height):
    f = tk.Frame(canvas, bg="#111111", highlightbackground="#333333", highlightthickness=1)
    canvas.create_window(625, 420, window=f, width=width, height=height)
    return f

def form_label(self, parent, text, row):
    tk.Label(parent, text=text, bg="#111111", fg="white", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="e", padx=10)

def login_page(self):
    self.clear()
    c = self.outside_background()
    p = self.panel(c, 470, 420)

    tk.Label(p, text="Giriş Yap", bg="#111111", fg="white", font=("Segoe UI", 24, "bold")).grid(row=0, column=0, columnspan=2, pady=25)

    email = ttk.Entry(p, width=35)
    password = ttk.Entry(p, width=35, show="*")

    self.form_label(p, "E-mail", 1)
    email.grid(row=1, column=1, pady=7)
    self.form_label(p, "Şifre", 2)
    password.grid(row=2, column=1, pady=7)

    def login():
        try:
            if not EMAIL_RE.match(email.get().strip()):
                raise ValueError("E-mail formatı hatalı.")

            u = self.db.q("""
            SELECT k.*, r.rol_adi
            FROM Kullanici k
            JOIN Rol r ON r.rol_id = k.rol_id
            WHERE email=? AND aktif=1
            """, (email.get().strip(),), True)

            if not u:
                raise ValueError("Kullanıcı bulunamadı.")
            if u["sifre"] != password.get():
                raise ValueError("Şifre yanlış.")

            self.user = u
            self.db.x("INSERT INTO OturumLog(kullanici_id, islem) VALUES(?,?)", (u["kullanici_id"], "Giriş"))

            if u["rol_adi"] == "admin":
                self.admin_page()
            else:
                self.user_page()
        except Exception as e:
            messagebox.showerror("Giriş Hatası", str(e))

    ttk.Button(p, text="Giriş Yap", command=login).grid(row=3, column=0, columnspan=2, sticky="ew", padx=35, pady=18)
    ttk.Button(p, text="Kayıt Ol", command=self.register_page).grid(row=4, column=0, columnspan=2, sticky="ew", padx=35)
    tk.Label(p, text="Admin: admin@netflix.local / admin123", bg="#111111", fg="#bbbbbb").grid(row=5, column=0, columnspan=2, pady=18)

def register_page(self):
    self.clear()
    c = self.outside_background()
    p = self.panel(c, 850, 600)

    tk.Label(p, text="Kullanıcı Kayıt", bg="#111111", fg="white", font=("Segoe UI", 23, "bold")).grid(row=0, column=0, columnspan=4, pady=18)

    entries = {}
    fields = [
        ("ad", "Ad"),
        ("soyad", "Soyad"),
        ("email", "E-mail"),
        ("sifre", "Şifre"),
        ("sifre2", "Şifre Tekrar"),
        ("dogum", "Doğum Tarihi")
    ]

    for i, (key, label) in enumerate(fields, 1):
        self.form_label(p, label, i)
        e = ttk.Entry(p, width=32, show="*" if "sifre" in key else "")
        e.grid(row=i, column=1, pady=5)
        entries[key] = e

    entries["dogum"].insert(0, "2004-04-03")

    self.form_label(p, "Cinsiyet", 7)
    gender = ttk.Combobox(p, values=["Erkek", "Kadın"], width=30, state="readonly")
    gender.current(0)
    gender.grid(row=7, column=1, pady=5)

    self.form_label(p, "Ülke", 8)
    country = ttk.Combobox(p, values=COUNTRIES, width=30, state="readonly")
    country.current(0)
    country.grid(row=8, column=1, pady=5)

    tk.Label(p, text="3 farklı favori tür seç", bg="#111111", fg="white", font=("Segoe UI", 11, "bold")).grid(row=1, column=2, columnspan=2)

    genres = self.db.q("SELECT * FROM Tur ORDER BY tur_adi")
    genre_box = tk.Listbox(p, selectmode="multiple", width=38, height=13, bg="#222222", fg="white", selectbackground="#e50914")
    genre_box.grid(row=2, column=2, rowspan=8, columnspan=2, padx=25)

    for g in genres:
        genre_box.insert("end", g["tur_adi"])

    tk.Label(p, text="Tarih: 2004-04-03 veya 03/04/2004", bg="#111111", fg="#bbbbbb").grid(row=10, column=0, columnspan=4, pady=5)

    def register():
        try:
            data = {k: v.get().strip() for k, v in entries.items()}

            if any(not v for v in data.values()):
                raise ValueError("Boş alan bırakılamaz.")
            if not EMAIL_RE.match(data["email"]):
                raise ValueError("E-mail formatı hatalı.")
            if self.db.q("SELECT 1 FROM Kullanici WHERE email=?", (data["email"],), True):
                raise ValueError("Bu e-mail zaten kayıtlı.")
            if data["sifre"] != data["sifre2"]:
                raise ValueError("Şifreler aynı değil.")
            if len(data["sifre"]) < 6:
                raise ValueError("Şifre en az 6 karakter olmalı.")

            birth = parse_birth_date(data["dogum"])

            if date.fromisoformat(birth) > date.today():
                raise ValueError("Doğum tarihi bugünden büyük olamaz.")

            selected = [genres[i]["tur_id"] for i in genre_box.curselection()]
            if len(set(selected)) != 3:
                raise ValueError("Tam 3 farklı favori tür seçmelisin.")

            uid = self.db.x("""
            INSERT INTO Kullanici(rol_id, ad, soyad, email, sifre, dogum_tarihi, cinsiyet, ulke)
            VALUES(1,?,?,?,?,?,?,?)
            """, (data["ad"], data["soyad"], data["email"], data["sifre"], birth, gender.get(), country.get()))

            for tid in selected:
                self.db.x("INSERT INTO KullaniciTur VALUES(?,?)", (uid, tid))

            messagebox.showinfo("Başarılı", "Kayıt tamamlandı.")
            self.login_page()
        except Exception as e:
            messagebox.showerror("Kayıt Hatası", str(e))

    ttk.Button(p, text="Geri", command=self.login_page).grid(row=11, column=0, columnspan=2, sticky="ew", padx=30, pady=18)
    ttk.Button(p, text="Kaydı Tamamla", command=register).grid(row=11, column=2, columnspan=2, sticky="ew", padx=30, pady=18)

def topbar(self, root, title):
    header = tk.Frame(root, bg="#050505", height=60)
    header.pack(fill="x")
    tk.Label(header, text=title, bg="#050505", fg="white", font=("Segoe UI", 18, "bold")).pack(side="left", padx=18)
    ttk.Button(header, text="Çıkış", command=self.login_page).pack(side="right", padx=15, pady=9)

def user_page(self):
    self.clear()
    root = tk.Frame(self, bg="#151515")
    root.pack(fill="both", expand=True)
    self.topbar(root, f"Kullanıcı Paneli - {self.user['ad']} {self.user['soyad']}")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True, padx=10, pady=10)

    self.contents_tab(nb)
    self.recommend_tab(nb)
    self.favorites_tab(nb)
    self.history_tab(nb)
    self.profile_tab(nb)

def program_rows(self, name="", genre="", tip="", year="", min_puan="", fav=False):
    sql = """
    SELECT p.*,
           GROUP_CONCAT(DISTINCT t.tur_adi) turler,
           COALESCE(ROUND(AVG(kp.puan),1),0) ort_puan,
           COUNT(DISTINCT il.log_id) izlenme
    FROM Program p
    LEFT JOIN ProgramTur pt ON pt.program_id = p.program_id
    LEFT JOIN Tur t ON t.tur_id = pt.tur_id
    LEFT JOIN KullaniciProgram kp ON kp.program_id = p.program_id AND kp.puan IS NOT NULL
    LEFT JOIN IzlemeLog il ON il.program_id = p.program_id
    """
    params = []
    where = []

    if fav:
        sql += " JOIN Favori f ON f.program_id = p.program_id AND f.kullanici_id=? "
        params.append(self.user["kullanici_id"])

    if name:
        where.append("p.ad LIKE ?")
        params.append(f"%{name}%")
    if tip:
        where.append("p.program_tipi=?")
        params.append(tip)
    if year:
        where.append("p.yayin_yili=?")
        params.append(year)

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " GROUP BY p.program_id "

    having = []
    if genre:
        having.append("turler LIKE ?")
        params.append(f"%{genre}%")
    if min_puan:
        having.append("ort_puan >= ?")
        params.append(float(min_puan))

    if having:
        sql += " HAVING " + " AND ".join(having)

    sql += " ORDER BY p.yayin_yili DESC"
    return self.db.q(sql, params)

def user_state(self, pid):
    return self.db.q("""
    SELECT * FROM KullaniciProgram
    WHERE kullanici_id=? AND program_id=?
    """, (self.user["kullanici_id"], pid), True)

def make_tree(self, parent, columns):
    frame = tk.Frame(parent, bg="#151515")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    scroll = ttk.Scrollbar(frame, command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return tree

def fill_program_tree(self, tree, rows):
    tree.delete(*tree.get_children())
    for r in rows:
        st = self.user_state(r["program_id"]) if self.user and self.user["rol_adi"] == "normal" else None
        durum = "İzlenmedi"
        if st:
            durum = "Tamamlandı" if st["tamamlandi"] else f"Devam: {st['son_bolum']}. bölüm {st['kalinan_dakika']}. dk"

        tree.insert("", "end", values=(
            r["program_id"], r["ad"], r["program_tipi"], r["turler"],
            r["bolum_sayisi"], f"{r['bolum_uzunlugu']} dk",
            r["yayin_yili"], r["ort_puan"], r["izlenme"], durum
        ))

def contents_tab(self, nb):
    tab = tk.Frame(nb, bg="#141414")
    nb.add(tab, text="İçerikler")

    search_bar = tk.Frame(tab, bg="#141414")
    search_bar.pack(fill="x", padx=18, pady=15)

    tk.Label(search_bar, text="Netflix", bg="#141414", fg="#e50914", font=("Segoe UI", 24, "bold")).pack(side="left", padx=(0, 25))

    search_entry = ttk.Entry(search_bar, width=28)
    genre_entry = ttk.Entry(search_bar, width=18)
    type_box = ttk.Combobox(search_bar, values=["", "Film", "Dizi", "Tv Show"], width=10, state="readonly")
    year_entry = ttk.Entry(search_bar, width=8)
    min_rating = ttk.Entry(search_bar, width=8)

    for text, widget in [
        ("Arama", search_entry),
        ("Tür", genre_entry),
        ("Tip", type_box),
        ("Yıl", year_entry),
        ("Min Puan", min_rating)
    ]:
        tk.Label(search_bar, text=text, bg="#141414", fg="white", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        widget.pack(side="left", padx=5)

    columns = ("ID", "Ad", "Tip", "Türler", "Bölüm", "Süre", "Yıl", "Puan", "İzlenme", "Durum")
    tree = self.make_tree(tab, columns)

    def load():
        rows = self.program_rows(
            name=search_entry.get(),
            genre=genre_entry.get(),
            tip=type_box.get(),
            year=year_entry.get(),
            min_puan=min_rating.get()
        )
        self.fill_program_tree(tree, rows)

    def selected_id():
        if not tree.selection():
            messagebox.showwarning("Seçim", "Önce bir film veya dizi seç.")
            return None
        return int(tree.item(tree.selection()[0])["values"][0])

    buttons = tk.Frame(tab, bg="#141414")
    buttons.pack(fill="x", padx=18, pady=10)

    tk.Button(buttons, text="🔍 ARA / SEARCH", bg="#e50914", fg="white",
              font=("Segoe UI", 12, "bold"), relief="flat",
              padx=20, pady=8, command=load).pack(side="left", padx=6)

    tk.Button(buttons, text="▶ İZLE / DEVAM ET", bg="white", fg="#111111",
              font=("Segoe UI", 12, "bold"), relief="flat",
              padx=20, pady=8,
              command=lambda: self.watch_window(selected_id(), load)).pack(side="left", padx=6)

    tk.Button(buttons, text="ℹ DETAY", bg="#333333", fg="white",
              font=("Segoe UI", 12, "bold"), relief="flat",
              padx=20, pady=8,
              command=lambda: self.detail_window(selected_id())).pack(side="left", padx=6)

    tk.Button(buttons, text="❤ FAVORİ", bg="#333333", fg="white",
              font=("Segoe UI", 12, "bold"), relief="flat",
              padx=20, pady=8,
              command=lambda: self.toggle_favorite(selected_id())).pack(side="left", padx=6)

    search_entry.bind("<Return>", lambda e: load())
    genre_entry.bind("<Return>", lambda e: load())

    load()

def recommend_tab(self, nb):
    tab = tk.Frame(nb, bg="#151515")
    nb.add(tab, text="Öneriler")

    tree = self.make_tree(tab, ("ID", "Ad", "Tip", "Türler", "Bölüm", "Süre", "Yıl", "Puan", "İzlenme", "Durum"))

    rows = self.db.q("""
    SELECT p.*,
           GROUP_CONCAT(DISTINCT t.tur_adi) turler,
           COALESCE(ROUND(AVG(kp.puan),1),0) ort_puan,
           COUNT(DISTINCT il.log_id) izlenme
    FROM Program p
    JOIN ProgramTur pt ON pt.program_id = p.program_id
    JOIN Tur t ON t.tur_id = pt.tur_id
    LEFT JOIN KullaniciProgram kp ON kp.program_id = p.program_id AND kp.puan IS NOT NULL
    LEFT JOIN IzlemeLog il ON il.program_id = p.program_id
    WHERE pt.tur_id IN (
        SELECT tur_id FROM KullaniciTur WHERE kullanici_id=?
    )
    GROUP BY p.program_id
    ORDER BY ort_puan DESC, izlenme DESC, p.yayin_yili DESC
    LIMIT 6
    """, (self.user["kullanici_id"],))

    self.fill_program_tree(tree, rows)

def program_detail(self, pid):
    return self.db.q("""
    SELECT p.*,
           GROUP_CONCAT(DISTINCT t.tur_adi) turler,
           COALESCE(ROUND(AVG(kp.puan),1),0) ort_puan,
           COUNT(DISTINCT il.log_id) izlenme
    FROM Program p
    LEFT JOIN ProgramTur pt ON pt.program_id = p.program_id
    LEFT JOIN Tur t ON t.tur_id = pt.tur_id
    LEFT JOIN KullaniciProgram kp ON kp.program_id = p.program_id AND kp.puan IS NOT NULL
    LEFT JOIN IzlemeLog il ON il.program_id = p.program_id
    WHERE p.program_id=?
    GROUP BY p.program_id
    """, (pid,), True)

def detail_window(self, pid):
    if not pid:
        return

    p = self.program_detail(pid)
    st = self.user_state(pid)

    msg = f"""İçerik adı: {p['ad']}

Açıklama: {p['aciklama']}Program tipi: {p['program_tipi']}Türleri: {p['turler']}Yayın yılı: {p['yayin_yili']}Bölüm sayısı: {p['bolum_sayisi']}Film / Bölüm süresi: {p['bolum_uzunlugu']} dakikaOrtalama puan: {p['ort_puan']}Toplam izlenme: {p['izlenme']}"""

    if st:
        msg += f"""

Kaldığı bölüm: {st['son_bolum']}Kaldığı dakika: {st['kalinan_dakika']}Verdiği puan: {st['puan']}Tamamlandı mı: {'Evet' if st['tamamlandi'] else 'Hayır'}"""else:msg += "\nDurum: Henüz izlemedi"

    messagebox.showinfo("İçerik Detay", msg)

def toggle_favorite(self, pid):
    if not pid:
        return

    old = self.db.q("""
    SELECT 1 FROM Favori WHERE kullanici_id=? AND program_id=?
    """, (self.user["kullanici_id"], pid), True)

    if old:
        self.db.x("DELETE FROM Favori WHERE kullanici_id=? AND program_id=?", (self.user["kullanici_id"], pid))
        messagebox.showinfo("Favori", "Favorilerden çıkarıldı.")
    else:
        self.db.x("INSERT OR IGNORE INTO Favori(kullanici_id, program_id) VALUES(?,?)", (self.user["kullanici_id"], pid))
        messagebox.showinfo("Favori", "Favorilere eklendi.")

def watch_window(self, pid, refresh=None):
    if not pid:
        return

    p = self.db.q("SELECT * FROM Program WHERE program_id=?", (pid,), True)
    st = self.user_state(pid)

    w = tk.Toplevel(self)
    w.title("İzleme Ekranı")
    w.geometry("520x500")
    w.configure(bg="#141414")

    tk.Label(w, text=p["ad"], bg="#141414", fg="white", font=("Segoe UI", 20, "bold")).pack(pady=(20, 5))
    tk.Label(w, text=f"{p['program_tipi']} • {p['yayin_yili']} • {p['bolum_uzunlugu']} dk",
             bg="#141414", fg="#bbbbbb", font=("Segoe UI", 11)).pack()

    if st and not st["tamamlandi"]:
        tk.Label(w, text=f"▶ Kaldığın yer: {st['son_bolum']}. bölüm {st['kalinan_dakika']}. dakika",
                 bg="#4a2f12", fg="white", font=("Segoe UI", 12, "bold"),
                 padx=10, pady=8).pack(fill="x", padx=30, pady=15)

    if st and st["tamamlandi"]:
        tk.Label(w, text="✓ Bu içerik tamamlandı. İstersen tekrar izleyebilirsin.",
                 bg="#1f3b2d", fg="white", font=("Segoe UI", 12, "bold"),
                 padx=10, pady=8).pack(fill="x", padx=30, pady=15)

    box = tk.Frame(w, bg="#1f1f1f")
    box.pack(fill="x", padx=35, pady=20)

    bolum = tk.IntVar(value=st["son_bolum"] if st else 1)
    dakika = tk.IntVar(value=st["kalinan_dakika"] if st else 0)
    puan = tk.StringVar(value=str(st["puan"]) if st and st["puan"] else "")
    tamamlandi = tk.BooleanVar(value=False)

    def field(label, var):
        tk.Label(box, text=label, bg="#1f1f1f", fg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18, pady=(12, 2))
        ttk.Entry(box, textvariable=var).pack(fill="x", padx=18, pady=(0, 5))

    field(f"Bölüm No 1-{p['bolum_sayisi']}", bolum)
    field(f"Dakika 0-{p['bolum_uzunlugu']}", dakika)
    field("Puan 1-10", puan)

    ttk.Checkbutton(box, text="İzlemeyi tamamla", variable=tamamlandi).pack(anchor="w", padx=18, pady=12)

    def save_watch():
        try:
            rating = int(puan.get()) if puan.get().strip() else None

            if bolum.get() < 1 or bolum.get() > p["bolum_sayisi"]:
                raise ValueError("Bölüm numarası geçersiz.")
            if dakika.get() < 0 or dakika.get() > p["bolum_uzunlugu"]:
                raise ValueError(f"Dakika 0 ile {p['bolum_uzunlugu']} arasında olmalı.")
            if rating is not None and not 1 <= rating <= 10:
                raise ValueError("Puan 1 ile 10 arasında olmalı.")

            self.db.x("""
            INSERT INTO KullaniciProgram
            (kullanici_id, program_id, son_bolum, kalinan_dakika, tamamlandi, puan, son_tarih)
            VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP)
            ON CONFLICT(kullanici_id, program_id)
            DO UPDATE SET
                son_bolum=excluded.son_bolum,
                kalinan_dakika=excluded.kalinan_dakika,
                tamamlandi=excluded.tamamlandi,
                puan=excluded.puan,
                son_tarih=CURRENT_TIMESTAMP
            """, (
                self.user["kullanici_id"], pid, bolum.get(), dakika.get(),
                1 if tamamlandi.get() else 0, rating
            ))

            self.db.x("""
            INSERT INTO IzlemeLog
            (kullanici_id, program_id, bolum_no, izleme_suresi, tamamlandi, puan)
            VALUES(?,?,?,?,?,?)
            """, (
                self.user["kullanici_id"], pid, bolum.get(), dakika.get(),
                1 if tamamlandi.get() else 0, rating
            ))

            messagebox.showinfo("Kaydedildi",
                                f"Kaldığın yer kaydedildi:\n{bolum.get()}. bölüm {dakika.get()}. dakika")

            w.destroy()
            if refresh:
                refresh()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    tk.Button(w, text="Kaydet ve Devam Et", bg="#e50914", fg="white",
              font=("Segoe UI", 12, "bold"), relief="flat",
              padx=15, pady=8, command=save_watch).pack(fill="x", padx=35, pady=10)

def favorites_tab(self, nb):
    tab = tk.Frame(nb, bg="#151515")
    nb.add(tab, text="Favoriler")

    tree = self.make_tree(tab, ("ID", "Ad", "Tip", "Türler", "Yıl", "Süre", "Puan", "Durum"))

    def load():
        tree.delete(*tree.get_children())
        rows = self.program_rows(fav=True)

        for r in rows:
            st = self.user_state(r["program_id"])
            durum = "İzlenmedi"
            if st:
                durum = "Tamamlandı" if st["tamamlandi"] else f"{st['son_bolum']}. bölüm {st['kalinan_dakika']}. dk"

            tree.insert("", "end", values=(
                r["program_id"], r["ad"], r["program_tipi"], r["turler"],
                r["yayin_yili"], f"{r['bolum_uzunlugu']} dk", r["ort_puan"], durum
            ))

    ttk.Button(tab, text="Yenile", command=load).pack(anchor="w", padx=10, pady=8)
    load()

def history_tab(self, nb):
    tab = tk.Frame(nb, bg="#151515")
    nb.add(tab, text="İzleme Geçmişi")

    tree = self.make_tree(tab, ("İçerik", "Tarih", "Bölüm", "Dakika", "Puan", "Tamamlandı"))

    rows = self.db.q("""
    SELECT p.ad, il.*
    FROM IzlemeLog il
    JOIN Program p ON p.program_id = il.program_id
    WHERE il.kullanici_id=?
    ORDER BY il.tarih DESC
    """, (self.user["kullanici_id"],))

    for r in rows:
        tree.insert("", "end", values=(
            r["ad"], r["tarih"], r["bolum_no"], r["izleme_suresi"],
            r["puan"], "Evet" if r["tamamlandi"] else "Hayır"
        ))

def profile_tab(self, nb):
    tab = tk.Frame(nb, bg="#151515")
    nb.add(tab, text="Profil")

    age = calculate_age(self.user["dogum_tarihi"])

    stats = self.db.q("""
    SELECT COALESCE(SUM(kalinan_dakika),0) toplam_sure,
           COUNT(*) izlenen_sayi,
           COALESCE(ROUND(AVG(puan),1),0) ort_puan
    FROM KullaniciProgram
    WHERE kullanici_id=?
    """, (self.user["kullanici_id"],), True)

    fav_genres = self.db.q("""
    SELECT t.tur_adi
    FROM KullaniciTur kt
    JOIN Tur t ON t.tur_id = kt.tur_id
    WHERE kt.kullanici_id=?
    """, (self.user["kullanici_id"],))

    fav_text = ", ".join([g["tur_adi"] for g in fav_genres])

    text = f"""

Ad: {self.user['ad']}Soyad: {self.user['soyad']}E-mail: {self.user['email']}Doğum tarihi: {self.user['dogum_tarihi']}Yaş: {age}Cinsiyet: {self.user['cinsiyet']}Ülke: {self.user['ulke']}Favori türler: {fav_text}

Toplam izleme süresi: {stats['toplam_sure']} dakikaİzlenen içerik sayısı: {stats['izlenen_sayi']}Verilen ortalama puan: {stats['ort_puan']}"""

    tk.Label(tab, text=text, bg="#151515", fg="white", font=("Segoe UI", 14), justify="left").pack(anchor="w", padx=50, pady=40)

def admin_page(self):
    self.clear()
    root = tk.Frame(self, bg="#151515")
    root.pack(fill="both", expand=True)
    self.topbar(root, "Yönetici Paneli")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True, padx=10, pady=10)

    self.admin_programs_tab(nb)
    self.admin_genres_tab(nb)
    self.admin_users_tab(nb)
    self.admin_reports_tab(nb)

def admin_programs_tab(self, nb):
    tab = tk.Frame(nb, bg="#151515")
    nb.add(tab, text="İçerik Yönetimi")

    tree = self.make_tree(tab, ("ID", "Ad", "Tip", "Türler", "Bölüm", "Süre", "Yıl", "Puan", "İzlenme"))

    def load():
        tree.delete(*tree.get_children())
        for r in self.program_rows():
            tree.insert("", "end", values=(
                r["program_id"], r["ad"], r["program_tipi"], r["turler"],
                r["bolum_sayisi"], f"{r['bolum_uzunlugu']} dk",
                r["yayin_yili"], r["ort_puan"], r["izlenme"]
            ))

    def selected():
        if not tree.selection():
            messagebox.showwarning("Seçim", "Önce içerik seç.")
            return None
        return int(tree.item(tree.selection()[0])["values"][0])

    def program_form(edit=False):
        pid = selected() if edit else None
        old = self.db.q("SELECT * FROM Program WHERE program_id=?", (pid,), True) if edit and pid else None
        if edit and not old:
            return

        w = tk.Toplevel(self)
        w.title("Program Form")
        w.geometry("520x470")
        w.configure(bg="#111111")

        tk.Label(w, text="İçerik Bilgileri", bg="#111111", fg="white", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        fields = {}
        labels = [
            ("ad", "Ad"),
            ("aciklama", "Açıklama"),
            ("yil", "Yayın yılı"),
            ("bolum", "Bölüm sayısı"),
            ("sure", "Süre dakika"),
            ("turler", "Türler virgülle")
        ]

        for i, (key, label) in enumerate(labels, 1):
            tk.Label(w, text=label, bg="#111111", fg="white").grid(row=i, column=0, sticky="e", padx=8, pady=5)
            e = ttk.Entry(w, width=38)
            e.grid(row=i, column=1, pady=5)
            fields[key] = e

        tk.Label(w, text="Tip", bg="#111111", fg="white").grid(row=7, column=0, sticky="e", padx=8, pady=5)
        tip = ttk.Combobox(w, values=["Film", "Dizi", "Tv Show"], state="readonly", width=35)
        tip.grid(row=7, column=1, pady=5)

        if old:
            fields["ad"].insert(0, old["ad"])
            fields["aciklama"].insert(0, old["aciklama"])
            fields["yil"].insert(0, old["yayin_yili"])
            fields["bolum"].insert(0, old["bolum_sayisi"])
            fields["sure"].insert(0, old["bolum_uzunlugu"])
            tip.set(old["program_tipi"])

            gs = self.db.q("""
            SELECT t.tur_adi
            FROM ProgramTur pt
            JOIN Tur t ON t.tur_id=pt.tur_id
            WHERE pt.program_id=?
            """, (pid,))
            fields["turler"].insert(0, ", ".join([g["tur_adi"] for g in gs]))
        else:
            tip.current(0)

        def save():
            try:
                ad = fields["ad"].get().strip()
                aciklama = fields["aciklama"].get().strip()
                yil = int(fields["yil"].get())
                bolum = int(fields["bolum"].get())
                sure = int(fields["sure"].get())
                turler = fields["turler"].get().strip()

                if not ad or not aciklama or not turler:
                    raise ValueError("Boş alan bırakma.")

                if edit:
                    self.db.x("""
                    UPDATE Program
                    SET ad=?, aciklama=?, program_tipi=?, yayin_yili=?, bolum_sayisi=?, bolum_uzunlugu=?
                    WHERE program_id=?
                    """, (ad, aciklama, tip.get(), yil, bolum, sure, pid))
                    self.db.x("DELETE FROM ProgramTur WHERE program_id=?", (pid,))
                    use_pid = pid
                else:
                    use_pid = self.db.x("""
                    INSERT INTO Program(ad, aciklama, program_tipi, yayin_yili, bolum_sayisi, bolum_uzunlugu)
                    VALUES(?,?,?,?,?,?)
                    """, (ad, aciklama, tip.get(), yil, bolum, sure))

                for t in [x.strip() for x in turler.split(",") if x.strip()]:
                    self.db.x("INSERT OR IGNORE INTO Tur(tur_adi) VALUES(?)", (t,))
                    tid = self.db.q("SELECT tur_id FROM Tur WHERE tur_adi=?", (t,), True)["tur_id"]
                    self.db.x("INSERT OR IGNORE INTO ProgramTur VALUES(?,?)", (use_pid, tid))

                w.destroy()
                load()
            except Exception as e:
                messagebox.showerror("Hata", str(e))

        ttk.Button(w, text="Kaydet", command=save).grid(row=8, column=0, columnspan=2, sticky="ew", padx=30, pady=20)

    buttons = tk.Frame(tab, bg="#151515")
    buttons.pack(fill="x", pady=8)

    ttk.Button(buttons, text="Yeni İçerik", command=lambda: program_form(False)).pack(side="left", padx=5)
    ttk.Button(buttons, text="Güncelle", command=lambda: program_form(True)).pack(side="left", padx=5)
    ttk.Button(buttons, text="Sil", command=lambda: (self.db.x("DELETE FROM Program WHERE program_id=?", (selected(),)), load()) if selected() else None).pack(side="left", padx=5)
    ttk.Button(buttons, text="Yenile", command=load).pack(side="left", padx=5)

    load()

def admin_genres_tab(self, nb):
    tab = tk.Frame(nb, bg="#151515")
    nb.add(tab, text="Tür Yönetimi")

    tree = self.make_tree(tab, ("ID", "Tür", "Bağlı İçerik Sayısı"))

    def load():
        tree.delete(*tree.get_children())
        rows = self.db.q("""
        SELECT t.tur_id, t.tur_adi, COUNT(pt.program_id) sayi
        FROM Tur t
        LEFT JOIN ProgramTur pt ON pt.tur_id=t.tur_id
        GROUP BY t.tur_id
        ORDER BY t.tur_adi
        """)
        for r in rows:
            tree.insert("", "end", values=(r["tur_id"], r["tur_adi"], r["sayi"]))

    def selected():
        if not tree.selection():
            messagebox.showwarning("Seçim", "Önce tür seç.")
            return None
        return tree.item(tree.selection()[0])["values"]

    def add_genre():
        name = simpledialog.askstring("Yeni Tür", "Tür adı:")
        if name:
            self.db.x("INSERT OR IGNORE INTO Tur(tur_adi) VALUES(?)", (name.strip(),))
            load()

    def update_genre():
        vals = selected()
        if not vals:
            return
        new_name = simpledialog.askstring("Tür Güncelle", "Yeni tür adı:", initialvalue=vals[1])
        if new_name:
            self.db.x("UPDATE Tur SET tur_adi=? WHERE tur_id=?", (new_name.strip(), vals[0]))
            load()

    def delete_genre():
        vals = selected()
        if not vals:
            return
        if int(vals[2]) > 0:
            messagebox.showerror("Silinemez", "Bu türe bağlı içerik var. Önce içerikten kaldır.")
            return
        self.db.x("DELETE FROM Tur WHERE tur_id=?", (vals[0],))
        load()

    buttons = tk.Frame(tab, bg="#151515")
    buttons.pack(fill="x", pady=8)

    ttk.Button(buttons, text="Yeni Tür", command=add_genre).pack(side="left", padx=5)
    ttk.Button(buttons, text="Tür Güncelle", command=update_genre).pack(side="left", padx=5)
    ttk.Button(buttons, text="Tür Sil", command=delete_genre).pack(side="left", padx=5)
    ttk.Button(buttons, text="Yenile", command=load).pack(side="left", padx=5)

    load()

def admin_users_tab(self, nb):
    tab = tk.Frame(nb, bg="#151515")
    nb.add(tab, text="Kullanıcı Yönetimi")

    tree = self.make_tree(tab, ("ID", "Ad", "Soyad", "Email", "Rol", "Aktif", "Toplam Süre"))

    def load():
        tree.delete(*tree.get_children())
        rows = self.db.q("""
        SELECT k.*, r.rol_adi, COALESCE(SUM(kp.kalinan_dakika),0) toplam_sure
        FROM Kullanici k
        JOIN Rol r ON r.rol_id=k.rol_id
        LEFT JOIN KullaniciProgram kp ON kp.kullanici_id=k.kullanici_id
        GROUP BY k.kullanici_id
        """)
        for r in rows:
            tree.insert("", "end", values=(
                r["kullanici_id"], r["ad"], r["soyad"], r["email"],
                r["rol_adi"], "Evet" if r["aktif"] else "Hayır", r["toplam_sure"]
            ))

    def selected_user():
        if not tree.selection():
            messagebox.showwarning("Seçim", "Önce kullanıcı seç.")
            return None
        return tree.item(tree.selection()[0])["values"]

    def deactivate():
        vals = selected_user()
        if not vals:
            return
        uid = vals[0]
        if uid == 1:
            messagebox.showerror("Hata", "Admin pasif yapılamaz.")
            return
        self.db.x("UPDATE Kullanici SET aktif=0 WHERE kullanici_id=?", (uid,))
        load()

    def show_user_history():
        vals = selected_user()
        if not vals:
            return
        uid = vals[0]
        rows = self.db.q("""
        SELECT p.ad, il.tarih, il.bolum_no, il.izleme_suresi, il.puan, il.tamamlandi
        FROM IzlemeLog il
        JOIN Program p ON p.program_id=il.program_id
        WHERE il.kullanici_id=?
        ORDER BY il.tarih DESC
        """, (uid,))

        msg = ""
        for r in rows:
            msg += f"{r['ad']} | {r['tarih']} | Bölüm {r['bolum_no']} | {r['izleme_suresi']} dk | Puan {r['puan']} | {'Tamamlandı' if r['tamamlandi'] else 'Devam'}\n"

        if not msg:
            msg = "Bu kullanıcı henüz içerik izlememiş."

        messagebox.showinfo("Kullanıcı İzleme Geçmişi", msg)

    buttons = tk.Frame(tab, bg="#151515")
    buttons.pack(fill="x", pady=8)

    ttk.Button(buttons, text="Kullanıcıyı Pasif Yap", command=deactivate).pack(side="left", padx=5)
    ttk.Button(buttons, text="İzleme Geçmişi", command=show_user_history).pack(side="left", padx=5)
    ttk.Button(buttons, text="Yenile", command=load).pack(side="left", padx=5)

    load()

def admin_reports_tab(self, nb):
    tab = tk.Frame(nb, bg="#151515")
    nb.add(tab, text="Raporlar")

    text = tk.Text(tab, bg="#111111", fg="white", font=("Consolas", 11))
    text.pack(fill="both", expand=True, padx=10, pady=10)

    def section(title, rows):
        text.insert("end", f"\n--- {title} ---\n")
        if not rows:
            text.insert("end", "Kayıt yok.\n")
        for r in rows:
            text.insert("end", " | ".join(str(x) for x in tuple(r)) + "\n")

    section("En çok izlenen 10 içerik", self.db.q("""
    SELECT p.ad, COUNT(il.log_id) izlenme
    FROM Program p
    LEFT JOIN IzlemeLog il ON il.program_id = p.program_id
    GROUP BY p.program_id
    ORDER BY izlenme DESC
    LIMIT 10
    """))

    section("En yüksek puanlı 10 içerik", self.db.q("""
    SELECT p.ad, ROUND(AVG(kp.puan),1) puan
    FROM Program p
    JOIN KullaniciProgram kp ON kp.program_id = p.program_id
    WHERE kp.puan IS NOT NULL
    GROUP BY p.program_id
    ORDER BY puan DESC
    LIMIT 10
    """))

    section("En çok izlenen türler", self.db.q("""
    SELECT t.tur_adi, COUNT(il.log_id) izlenme
    FROM Tur t
    JOIN ProgramTur pt ON pt.tur_id=t.tur_id
    JOIN IzlemeLog il ON il.program_id=pt.program_id
    GROUP BY t.tur_id
    ORDER BY izlenme DESC
    """))

    section("En aktif kullanıcılar", self.db.q("""
    SELECT k.email, COALESCE(SUM(kp.kalinan_dakika),0) toplam_sure
    FROM Kullanici k
    LEFT JOIN KullaniciProgram kp ON kp.kullanici_id = k.kullanici_id
    GROUP BY k.kullanici_id
    ORDER BY toplam_sure DESC
    LIMIT 10
    """))

    section("Son 7 günde izlenen içerikler", self.db.q("""
    SELECT p.ad, il.tarih
    FROM IzlemeLog il
    JOIN Program p ON p.program_id=il.program_id
    WHERE date(il.tarih) >= date('now','-7 day')
    ORDER BY il.tarih DESC
    """))

    section("Genel Sayılar", self.db.q("""
    SELECT
    (SELECT COUNT(*) FROM Kullanici) kullanici_sayisi,
    (SELECT COUNT(*) FROM IzlemeLog) toplam_izlenme,
    (SELECT COUNT(puan) FROM KullaniciProgram WHERE puan IS NOT NULL) toplam_puan
    """))

if name == "main":App().mainloop()
