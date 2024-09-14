import tkinter as tk
import PyPDF2
import os
import sqlite3
from gtts import gTTS
from tkinter import filedialog
from tkinter import ttk
from tkcalendar import DateEntry
from googletrans import Translator

class KitapKayıtSistemi:
    def __init__(self, pencere):
        # ANA PENCEREYİ OLUŞTUR
        self.pencere = pencere
        self.pencere.title("Kitap Kayıt Sistemi")

        # VERİ TABANINI OLUŞTUR
        self.conn = sqlite3.connect("KitapKayıt.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Kitaplar (
                id TEXT PRIMARY KEY,
                Kitap_Adı TEXT,
                Kitap_Türü TEXT,
                Yazarı TEXT,
                Başlangıç_Tarihi DATE,
                Bitiş_Tarihi DATE
            )
        """)
        self.conn.commit()

        # ID
        self.id_label = tk.Label(pencere, text="ID:")
        self.id_label.grid(row=0, column=0)
        self.id_entry = tk.Entry(pencere)
        self.id_entry.grid(row=0, column=1)

        # Kitap Adı
        self.Kitap_Adı_label = tk.Label(pencere, text="Kitap Adı:")
        self.Kitap_Adı_label.grid(row=1, column=0)
        self.Kitap_Adı_entry = tk.Entry(pencere)
        self.Kitap_Adı_entry.grid(row=1, column=1)

        # Kitap Türü
        self.KitapTürü_label = tk.Label(pencere, text="Kitap Türü:")
        self.KitapTürü_label.grid(row=2, column=0)
        self.KitapTürü_entry = tk.Entry(pencere)
        self.KitapTürü_entry.grid(row=2, column=1)

        # Yazarı
        self.Yazarı_label = tk.Label(pencere, text="Yazarı:")
        self.Yazarı_label.grid(row=3, column=0)
        self.Yazarı_entry = tk.Entry(pencere)
        self.Yazarı_entry.grid(row=3, column=1)

        # Başlangıç Tarihi
        self.BaşlangıçTarihi_label = tk.Label(pencere, text="Başlangıç Tarihi:")
        self.BaşlangıçTarihi_label.grid(row=4, column=0)
        self.BaşlangıçTarihi_dateEntry = DateEntry(pencere, format='yyyy-mm-dd')
        self.BaşlangıçTarihi_dateEntry.grid(row=4, column=1)

        # Bitiş Tarihi
        self.BitişTarihi_label = tk.Label(pencere, text="Bitiş Tarihi:")
        self.BitişTarihi_label.grid(row=5, column=0)
        self.BitişTarihi_dateEntry = DateEntry(pencere, format='yyyy-mm-dd')
        self.BitişTarihi_dateEntry.grid(row=5, column=1)

        # İşlem Butonları
        self.ekle_button = tk.Button(pencere, text="Ekle", command=self.ekle)
        self.ekle_button.grid(row=6, column=0)

        self.düzenle_button = tk.Button(pencere, text="Düzenle", command=self.düzenle)
        self.düzenle_button.grid(row=6, column=1)

        self.sil_button = tk.Button(pencere, text="Sil", command=self.sil)
        self.sil_button.grid(row=6, column=2)

        self.temizle_button = tk.Button(pencere, text="Temizle", command=self.temizle)
        self.temizle_button.grid(row=6, column=3)
        
        self.seç_button = tk.Button(pencere, text="PDF Seç", command=self.dosya_seç)
        self.seç_button.grid(row=6, column=4)

        self.TürkçeyeÇevir_button = tk.Button(pencere, text="PDF'yi Türkçeye Çevir", command=self.TürkçeyeÇevir)
        self.TürkçeyeÇevir_button.grid(row=6, column=5)  # Butonu uygun bir konumda yerleştiriyoruz

        # Arama Çubuğu
        self.arama_label = tk.Label(pencere, text="Ara")
        self.arama_label.grid(row=7, column=0)
        self.arama_entry = tk.Entry(pencere)
        self.arama_entry.grid(row=7, column=1)

        # Arama Tetikleyicisi
        self.arama_entry.bind("<KeyRelease>", self.arama)

        # Tablo Oluştur
        self.tablo = ttk.Treeview(pencere, columns=("ID", "KitapAdı", "KitapTürü", "Yazarı", "BaşlangıçTarihi", "BitişTarihi"), show="headings")
        self.tablo.heading("ID", text="ID")
        self.tablo.heading("KitapAdı", text="Kitap Adı")
        self.tablo.heading("KitapTürü", text="Kitap Türü")
        self.tablo.heading("Yazarı", text="Yazarı")
        self.tablo.heading("BaşlangıçTarihi", text="Başlangıç Tarihi")
        self.tablo.heading("BitişTarihi", text="Bitiş Tarihi")
        self.tablo.grid(row=8, column=0, columnspan=6, sticky="nsew")

        # Pencereyi yeniden boyutlandırmak için
        pencere.grid_rowconfigure(8, weight=1)
        pencere.grid_columnconfigure(0, weight=1)
        pencere.grid_columnconfigure(1, weight=1)
        pencere.grid_columnconfigure(2, weight=1)
        pencere.grid_columnconfigure(3, weight=1)
        pencere.grid_columnconfigure(4, weight=1)
        pencere.grid_columnconfigure(5, weight=1)

        # Verileri Yükle
        self.verileri_yukle()

    def verileri_yukle(self):
        for row in self.tablo.get_children():
            self.tablo.delete(row)
        self.cursor.execute("SELECT * FROM Kitaplar")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tablo.insert("", tk.END, values=row)

    def ekle(self):
        id_ = self.id_entry.get()
        kitap_adı = self.Kitap_Adı_entry.get()
        kitap_türü = self.KitapTürü_entry.get()
        yazarı = self.Yazarı_entry.get()
        başlangıç_tarihi = self.BaşlangıçTarihi_dateEntry.get_date()
        bitiş_tarihi = self.BitişTarihi_dateEntry.get_date()

        self.cursor.execute("INSERT INTO Kitaplar (id, Kitap_Adı, Kitap_Türü, Yazarı, Başlangıç_Tarihi, Bitiş_Tarihi) VALUES (?, ?, ?, ?, ?, ?)", 
                            (id_, kitap_adı, kitap_türü, yazarı, başlangıç_tarihi, bitiş_tarihi))
        self.conn.commit()
        self.verileri_yukle()

    def düzenle(self):
        id_ = self.id_entry.get()
        kitap_adı = self.Kitap_Adı_entry.get()
        kitap_türü = self.KitapTürü_entry.get()
        yazarı = self.Yazarı_entry.get()
        başlangıç_tarihi = self.BaşlangıçTarihi_dateEntry.get_date()
        bitiş_tarihi = self.BitişTarihi_dateEntry.get_date()

        self.cursor.execute("""
            UPDATE Kitaplar 
            SET Kitap_Adı = ?, Kitap_Türü = ?, Yazarı = ?, Başlangıç_Tarihi = ?, Bitiş_Tarihi = ?
            WHERE id = ?
        """, (kitap_adı, kitap_türü, yazarı, başlangıç_tarihi, bitiş_tarihi, id_))
        self.conn.commit()
        self.verileri_yukle()

    def sil(self):
        selected_item = self.tablo.selection()
        if selected_item:
            id_ = self.tablo.item(selected_item)['values'][0]
            self.cursor.execute("DELETE FROM Kitaplar WHERE id = ?", (id_,))
            self.conn.commit()
            self.verileri_yukle()

    def temizle(self):
        self.id_entry.delete(0, tk.END)
        self.Kitap_Adı_entry.delete(0, tk.END)
        self.KitapTürü_entry.delete(0, tk.END)
        self.Yazarı_entry.delete(0, tk.END)
        self.BaşlangıçTarihi_dateEntry.set_date(self.BaşlangıçTarihi_dateEntry.min_date())  
        self.BitişTarihi_dateEntry.set_date(self.BitişTarihi_dateEntry.min_date()) 
        self.arama_entry.delete(0, tk.END)


    def arama(self, event):
        arama_terimi = self.arama_entry.get().lower()
        for row in self.tablo.get_children():
            self.tablo.delete(row)
        self.cursor.execute("""
            SELECT * FROM Kitaplar
            WHERE LOWER(Kitap_Adı) LIKE ? OR LOWER(Kitap_Türü) LIKE ? OR LOWER(Yazarı) LIKE ?
        """, (f"%{arama_terimi}%", f"%{arama_terimi}%", f"%{arama_terimi}%"))
        rows = self.cursor.fetchall()
        for row in rows:
            self.tablo.insert("", tk.END, values=row)

    def dosya_seç(self):
        dosya_yolu = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf")])
        if dosya_yolu:
            self.pdf_dosyası = dosya_yolu
            tk.messagebox.showinfo("Bilgi", f"Seçilen dosya: {dosya_yolu}")

    def TürkçeyeÇevir(self):
        if hasattr(self, 'pdf_dosyası'):
            translator = Translator()
            with open(self.pdf_dosyası, 'rb') as dosya:
                pdf = PyPDF2.PdfReader(dosya)
                metin = ""
                for sayfa in pdf.pages:
                    metin += sayfa.extract_text()

            # Metni Türkçeye Çevir
            çeviri = translator.translate(metin, dest='tr')
            türkçe_metin = çeviri.text

            # Çevrilen metni seslendirme
            tts = gTTS(text=türkçe_metin, lang='tr')
            ses_dosyası = "çeviri.mp3"
            tts.save(ses_dosyası)
            tk.messagebox.showinfo("Bilgi", f"PDF Türkçeye çevrildi ve ses dosyası oluşturuldu: {ses_dosyası}")
        else:
            tk.messagebox.showerror("Hata", "Bir PDF dosyası seçilmedi.")

if __name__ == "__main__":
    pencere = tk.Tk()
    uygulama = KitapKayıtSistemi(pencere)
    pencere.mainloop()
