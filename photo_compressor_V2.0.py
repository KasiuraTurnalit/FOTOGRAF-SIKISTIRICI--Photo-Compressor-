#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fotoğraf Sıkıştırıcı - İlerleme Çubuğu ve Anlık Bilgi
"""

import os
import sys
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import shutil
import threading
import time

class PhotoCompressor:
    def __init__(self):
        self.os_type = platform.system()
        self.source_folder = ""
        self.target_folder = ""
        self.total_files = 0
        self.processed_files = 0
        self.root = tk.Tk()
        self.setup_gui()
        
    def setup_gui(self):
        """GUI'yi kur"""
        self.root.title("FOTOĞRAF SIKIŞTIRICI")
        self.root.geometry("750x650")
        
        # Ana konteyner
        main_container = tk.Frame(self.root, padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # BAŞLIK
        title_frame = tk.Frame(main_container, bg="#2c3e50", height=80)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        title_frame.pack_propagate(False)
        
        title = tk.Label(title_frame, text="📸 FOTOĞRAF SIKIŞTIRICI", 
                        font=("Arial", 22, "bold"), bg="#2c3e50", fg="white")
        title.pack(expand=True)
        
        subtitle = tk.Label(title_frame, text="Kasiura Turnalit Tarafından Hazırlanmıştır", 
                          font=("Arial", 11), bg="#2c3e50", fg="#ecf0f1")
        subtitle.pack()
        
        # ANA İÇERİK
        content_frame = tk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # SOL PANEL - KLASÖR SEÇİMİ
        left_panel = tk.Frame(content_frame, width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 20))
        
        # 1. KAYNAK KLASÖR BÖLÜMÜ
        source_frame = tk.LabelFrame(left_panel, text="1. KAYNAK KLASÖR", 
                                    font=("Arial", 12, "bold"), padx=15, pady=15)
        source_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.source_btn = tk.Button(source_frame, text="📁 KAYNAK KLASÖRÜ SEÇ", 
                                   command=self.select_source,
                                   bg="#3498db", fg="white", 
                                   font=("Arial", 11, "bold"),
                                   height=2, width=25)
        self.source_btn.pack(pady=5)
        
        self.source_label = tk.Label(source_frame, text="Henüz seçilmedi", 
                                    font=("Arial", 9), fg="#7f8c8d",
                                    wraplength=280, justify=tk.LEFT, height=2)
        self.source_label.pack(fill=tk.X, pady=(5, 0))
        
        # 2. HEDEF KLASÖR BÖLÜMÜ
        target_frame = tk.LabelFrame(left_panel, text="2. HEDEF KLASÖR", 
                                    font=("Arial", 12, "bold"), padx=15, pady=15)
        target_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.target_btn = tk.Button(target_frame, text="💾 HEDEF KLASÖRÜ SEÇ", 
                                   command=self.select_target,
                                   bg="#9b59b6", fg="white", 
                                   font=("Arial", 11, "bold"),
                                   height=2, width=25)
        self.target_btn.pack(pady=5)
        
        self.target_label = tk.Label(target_frame, text="Henüz seçilmedi", 
                                    font=("Arial", 9), fg="#7f8c8d",
                                    wraplength=280, justify=tk.LEFT, height=2)
        self.target_label.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(target_frame, text="🔄 OTOMATİK HEDEF", 
                 command=self.auto_target,
                 bg="#2ecc71", fg="white", font=("Arial", 9)).pack(pady=(10, 0))
        
        # SAĞ PANEL - AYARLAR ve İŞLEM
        right_panel = tk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # AYARLAR BÖLÜMÜ
        settings_frame = tk.LabelFrame(right_panel, text="⚙️  AYARLAR", 
                                      font=("Arial", 12, "bold"), padx=15, pady=15)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Kalite Seçimi
        tk.Label(settings_frame, text="Kalite:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.quality_var = tk.IntVar(value=85)
        
        quality_frame = tk.Frame(settings_frame)
        quality_frame.pack(fill=tk.X, pady=(5, 10))
        
        qualities = [("Yüksek (85%)", 85), ("Orta (70%)", 70), ("Düşük (50%)", 50)]
        for text, value in qualities:
            tk.Radiobutton(quality_frame, text=text, variable=self.quality_var, 
                         value=value, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Boyut Seçimi
        tk.Label(settings_frame, text="Maks. Boyut:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.max_size_var = tk.StringVar(value="1920x1080")
        
        size_frame = tk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, pady=(5, 0))
        
        sizes = [("Orijinal", "Orijinal"), ("Full HD (Önerilen)", "1920x1080"), ("HD", "1280x720"), ("Küçük", "800x600")]
        for text, value in sizes:
            tk.Radiobutton(size_frame, text=text, variable=self.max_size_var, 
                         value=value, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # İLERLEME BÖLÜMÜ
        progress_frame = tk.LabelFrame(right_panel, text="📊 İLERLEME", 
                                      font=("Arial", 12, "bold"), padx=15, pady=15)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=300, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Yüzde gösterge
        self.percent_var = tk.StringVar(value="%0")
        percent_label = tk.Label(progress_frame, textvariable=self.percent_var, 
                               font=("Arial", 14, "bold"), fg="#2c3e50")
        percent_label.pack()
        
        # Anlık bilgi
        info_frame = tk.Frame(progress_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Sol: Toplam ve işlenen
        left_info = tk.Frame(info_frame)
        left_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.total_var = tk.StringVar(value="Toplam: 0")
        tk.Label(left_info, textvariable=self.total_var, font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.processed_var = tk.StringVar(value="İşlenen: 0")
        tk.Label(left_info, textvariable=self.processed_var, font=("Arial", 10)).pack(anchor=tk.W)
        
        # Sağ: Kalan süre/kalan
        right_info = tk.Frame(info_frame)
        right_info.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.remaining_var = tk.StringVar(value="Kalan: 0")
        tk.Label(right_info, textvariable=self.remaining_var, font=("Arial", 10)).pack(anchor=tk.E)
        
        self.current_file_var = tk.StringVar(value="Dosya: -")
        tk.Label(right_info, textvariable=self.current_file_var, font=("Arial", 9), fg="#7f8c8d").pack(anchor=tk.E)
        
        # Durum metni
        self.status_var = tk.StringVar(value="Kaynak ve hedef klasörlerini seçin")
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var, 
                                    font=("Arial", 10), fg="#2c3e50",
                                    wraplength=350, justify=tk.LEFT, height=2)
        self.status_label.pack(fill=tk.X, pady=(15, 0))
        
        # SIKIŞTIR BUTONU
        self.compress_btn = tk.Button(progress_frame, text="⏳ SIKIŞTIRMAYA HAZIR", 
                                     command=self.start_compression,
                                     bg="#27ae60", fg="white", 
                                     font=("Arial", 12, "bold"),
                                     height=2, state=tk.DISABLED)
        self.compress_btn.pack(fill=tk.X, pady=(15, 0))
        
        # ALT BİLGİ
        bottom_frame = tk.Frame(main_container, bg="#f8f9fa", height=40)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        bottom_frame.pack_propagate(False)
        
        tk.Label(bottom_frame, text=f"Sistem: {self.os_type}", 
                font=("Arial", 9), bg="#f8f9fa", fg="#7f8c8d").pack(side=tk.LEFT, padx=10)
        
        tk.Button(bottom_frame, text="🗑️  Temizle", command=self.clear_all,
                 bg="#e74c3c", fg="white", font=("Arial", 9)).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(bottom_frame, text="❌ Çıkış", command=self.root.quit,
                 bg="#95a5a6", fg="white", font=("Arial", 9)).pack(side=tk.RIGHT, padx=10)
        
        # Pencereyi ortala
        self.center_window()
    
    def center_window(self):
        """Pencereyi ortala"""
        self.root.update_idletasks()
        width = 750
        height = 650
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def select_source(self):
        """Kaynak klasörü seç"""
        folder = filedialog.askdirectory(title="KAYNAK KLASÖRÜ SEÇİN")
        if folder:
            self.source_folder = folder
            short_path = self.shorten_path(folder)
            self.source_label.config(text=f"✓ {short_path}", fg="#27ae60")
            self.update_compress_button()
    
    def select_target(self):
        """Hedef klasörü seç"""
        initial_dir = os.path.dirname(self.source_folder) if self.source_folder else None
        folder = filedialog.askdirectory(title="HEDEF KLASÖRÜ SEÇİN", initialdir=initial_dir)
        if folder:
            self.target_folder = folder
            short_path = self.shorten_path(folder)
            self.target_label.config(text=f"✓ {short_path}", fg="#27ae60")
            self.update_compress_button()
    
    def auto_target(self):
        """Otomatik hedef oluştur"""
        if not self.source_folder:
            messagebox.showwarning("Uyarı", "Önce kaynak klasörü seçmelisiniz!")
            return
        
        base_name = os.path.basename(self.source_folder)
        parent_dir = os.path.dirname(self.source_folder)
        
        counter = 0
        while True:
            if counter == 0:
                target_path = os.path.join(parent_dir, f"{base_name}_KÜÇÜLTÜLMÜŞ")
            else:
                target_path = os.path.join(parent_dir, f"{base_name}_KÜÇÜLTÜLMÜŞ_{counter}")
            
            if not os.path.exists(target_path):
                self.target_folder = target_path
                short_path = self.shorten_path(target_path)
                self.target_label.config(text=f"✓ {short_path} (Otomatik)", fg="#27ae60")
                self.update_compress_button()
                messagebox.showinfo("Otomatik Hedef", f"Hedef klasörü oluşturuldu:\n{target_path}")
                break
            counter += 1
    
    def shorten_path(self, path, max_length=40):
        """Uzun yolu kısalt"""
        if len(path) <= max_length:
            return path
        parts = os.path.normpath(path).split(os.sep)
        if len(parts) <= 2:
            return path
        shortened = ".../" + "/".join(parts[-2:])
        return shortened
    
    def update_compress_button(self):
        """Sıkıştır butonunu güncelle"""
        if self.source_folder and self.target_folder:
            self.compress_btn.config(text="🚀 SIKIŞTIRMAYI BAŞLAT", state=tk.NORMAL, bg="#27ae60")
            self.status_var.set("✓ Her iki klasör de seçildi\n▶ 'Sıkıştırmayı Başlat' butonuna tıklayın")
        else:
            self.compress_btn.config(text="⏳ SIKIŞTIRMAYA HAZIR", state=tk.DISABLED, bg="#95a5a6")
            if not self.source_folder and not self.target_folder:
                self.status_var.set("Kaynak ve hedef klasörlerini seçin")
            elif not self.source_folder:
                self.status_var.set("Kaynak klasörünü seçin")
            else:
                self.status_var.set("Hedef klasörünü seçin")
    
    def clear_all(self):
        """Tüm seçimleri temizle"""
        self.source_folder = ""
        self.target_folder = ""
        self.source_label.config(text="Henüz seçilmedi", fg="#7f8c8d")
        self.target_label.config(text="Henüz seçilmedi", fg="#7f8c8d")
        self.update_compress_button()
        self.reset_progress()
        messagebox.showinfo("Temizlendi", "Tüm seçimler temizlendi.")
    
    def reset_progress(self):
        """İlerlemeyi sıfırla"""
        self.progress_var.set(0)
        self.percent_var.set("%0")
        self.total_var.set("Toplam: 0")
        self.processed_var.set("İşlenen: 0")
        self.remaining_var.set("Kalan: 0")
        self.current_file_var.set("Dosya: -")
        self.status_var.set("Kaynak ve hedef klasörlerini seçin")
    
    def get_max_size(self):
        """Maksimum boyutu al"""
        size_text = self.max_size_var.get()
        if size_text == "Orijinal":
            return (0, 0)
        elif "1920" in size_text:
            return (1920, 1080)
        elif "1280" in size_text:
            return (1280, 720)
        elif "800" in size_text:
            return (800, 600)
        else:
            return (1920, 1080)
    
    def is_hidden_file(self, filename):
        """Gizli dosya kontrolü"""
        if filename.startswith('.'):
            return True
        if filename.lower() in ['thumbs.db', 'desktop.ini', '.ds_store']:
            return True
        return False
    
    def compress_image(self, input_path, output_path, quality, max_size):
        """Tek bir fotoğrafı sıkıştır"""
        try:
            if self.is_hidden_file(os.path.basename(input_path)):
                return "hidden"
            
            with Image.open(input_path) as img:
                exif_data = img.info.get('exif')
                
                if max_size[0] > 0 and max_size[1] > 0:
                    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                ext = os.path.splitext(input_path)[1].lower()
                
                if ext in ['.jpg', '.jpeg']:
                    save_args = {'quality': quality, 'optimize': True}
                    if exif_data:
                        save_args['exif'] = exif_data
                    img.save(output_path, 'JPEG', **save_args)
                elif ext == '.png':
                    img.save(output_path, 'PNG', optimize=True)
                elif ext == '.gif':
                    img.save(output_path, 'GIF', optimize=True)
                elif ext == '.bmp':
                    img.save(output_path, 'BMP')
                elif ext == '.webp':
                    img.save(output_path, 'WEBP', quality=quality)
                else:
                    shutil.copy2(input_path, output_path)
                    return "copied"
                
                return "compressed"
                
        except Exception as e:
            print(f"Hata: {e}")
            return "error"
    
    def update_progress(self, current, total, current_file=""):
        """İlerlemeyi güncelle"""
        if total > 0:
            percent = (current / total) * 100
            self.progress_var.set(percent)
            self.percent_var.set(f"%{int(percent)}")
            self.total_var.set(f"Toplam: {total}")
            self.processed_var.set(f"İşlenen: {current}")
            self.remaining_var.set(f"Kalan: {total - current}")
            
            if current_file:
                short_name = current_file[:30] + "..." if len(current_file) > 30 else current_file
                self.current_file_var.set(f"Dosya: {short_name}")
            
            self.root.update()
    
    def count_total_files(self):
        """Toplam fotoğraf sayısını hesapla"""
        count = 0
        for root, dirs, files in os.walk(self.source_folder):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')):
                    if not self.is_hidden_file(file):
                        count += 1
        return count
    
    def start_compression(self):
        """Sıkıştırmayı başlat"""
        if not self.source_folder:
            messagebox.showerror("Hata", "Kaynak klasörü seçilmedi!")
            return
        
        if not self.target_folder:
            messagebox.showerror("Hata", "Hedef klasörü seçilmedi!")
            return
        
        if self.source_folder == self.target_folder:
            messagebox.showerror("Hata", "Kaynak ve hedef klasörleri aynı olamaz!")
            return
        
        # Hedef klasör kontrolü
        if os.path.exists(self.target_folder) and os.listdir(self.target_folder):
            response = messagebox.askyesno("Uyarı", "Hedef klasörü dolu! İçindekiler silinecek. Devam?")
            if not response:
                return
            try:
                shutil.rmtree(self.target_folder)
                os.makedirs(self.target_folder)
            except Exception as e:
                messagebox.showerror("Hata", f"Klasör temizlenemedi: {e}")
                return
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.compression_thread)
        thread.daemon = True
        thread.start()
    
    def compression_thread(self):
        """Sıkıştırma işlemini thread'de çalıştır"""
        try:
            # Butonları devre dışı bırak
            self.compress_btn.config(state=tk.DISABLED, text="⏳ İŞLEM SÜRÜYOR...", bg="#f39c12")
            self.source_btn.config(state=tk.DISABLED)
            self.target_btn.config(state=tk.DISABLED)
            
            # Toplam dosya sayısını hesapla
            self.status_var.set("📊 Fotoğraflar sayılıyor...")
            self.total_files = self.count_total_files()
            
            if self.total_files == 0:
                messagebox.showwarning("Uyarı", "Kaynak klasöründe fotoğraf bulunamadı!")
                self.reset_buttons()
                return
            
            # Ayarları al
            quality = self.quality_var.get()
            max_size = self.get_max_size()
            
            # İstatistikler
            stats = {'total': 0, 'compressed': 0, 'copied': 0, 'hidden': 0, 'errors': 0}
            self.processed_files = 0
            
            # İlerlemeyi başlat
            self.status_var.set(f"📁 Klasör yapısı oluşturuluyor...\n📊 Toplam {self.total_files} fotoğraf bulundu")
            self.update_progress(0, self.total_files)
            
            # 1. Klasör yapısını oluştur
            folder_count = 0
            for root, dirs, files in os.walk(self.source_folder):
                rel_path = os.path.relpath(root, self.source_folder)
                target_path = self.target_folder if rel_path == "." else os.path.join(self.target_folder, rel_path)
                os.makedirs(target_path, exist_ok=True)
                folder_count += 1
            
            # 2. Dosyaları işle
            current_count = 0
            for root, dirs, files in os.walk(self.source_folder):
                rel_path = os.path.relpath(root, self.source_folder)
                target_path = self.target_folder if rel_path == "." else os.path.join(self.target_folder, rel_path)
                
                current_folder = rel_path if rel_path != "." else "Ana Klasör"
                self.status_var.set(f"📁 {current_folder}\n📊 {current_count}/{self.total_files} işlendi")
                
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')):
                        stats['total'] += 1
                        current_count += 1
                        
                        # Her dosyada ilerlemeyi güncelle
                        self.update_progress(current_count, self.total_files, file)
                        
                        source_file = os.path.join(root, file)
                        target_file = os.path.join(target_path, file)
                        
                        result = self.compress_image(source_file, target_file, quality, max_size)
                        
                        if result == "hidden":
                            stats['hidden'] += 1
                            stats['total'] -= 1
                            current_count -= 1  # Gizli dosyaları sayma
                        elif result == "compressed":
                            stats['compressed'] += 1
                        elif result == "copied":
                            stats['copied'] += 1
                        elif result == "error":
                            stats['errors'] += 1
                            try:
                                shutil.copy2(source_file, target_file)
                                stats['copied'] += 1
                            except:
                                pass
            
            # İşlem tamamlandı
            self.update_progress(self.total_files, self.total_files, "Tamamlandı!")
            self.status_var.set(f"✅ İşlem tamamlandı!\n📊 {self.total_files} fotoğraf işlendi")
            
            # Sonuç mesajı
            result_message = f"""
✅ İŞLEM TAMAMLANDI!

📊 DETAYLI RAPOR:
• Toplam Fotoğraf: {self.total_files}
• Başarıyla Sıkıştırılan: {stats['compressed']}
• Orijinal Kopyalanan: {stats['copied']}
• Gizli Dosya Atlanılan: {stats['hidden']}
• Hata Alınan: {stats['errors']}

📂 Hedef Klasör:
{self.target_folder}
"""
            
            messagebox.showinfo("🎉 Başarılı", result_message)
            
            # Butonları tekrar aktif et
            self.reset_buttons()
            
            # Klasörü aç
            if messagebox.askyesno("Klasörü Aç", "Hedef klasörü açmak ister misiniz?"):
                try:
                    if self.os_type == "Windows":
                        os.startfile(self.target_folder)
                    elif self.os_type == "Linux":
                        os.system(f'xdg-open "{self.target_folder}"')
                except:
                    pass
            
        except Exception as e:
            self.reset_buttons()
            messagebox.showerror("Hata", f"İşlem sırasında hata:\n\n{str(e)}")
            self.status_var.set(f"❌ Hata: {str(e)[:50]}")
    
    def reset_buttons(self):
        """Butonları eski haline getir"""
        self.compress_btn.config(state=tk.NORMAL, text="🚀 YENİDEN SIKIŞTIR", bg="#27ae60")
        self.source_btn.config(state=tk.NORMAL)
        self.target_btn.config(state=tk.NORMAL)
    
    def run(self):
        """Programı çalıştır"""
        self.root.mainloop()

def main():
    """Ana fonksiyon"""
    try:
        from PIL import Image
    except ImportError:
        os_type = platform.system()
        if os_type == "Windows":
            error_msg = "Pillow yüklü değil!\n\nKomut İstemi'nde:\npip install pillow"
        else:
            error_msg = "Pillow yüklü değil!\n\nTerminal'de:\npip3 install pillow"
        
        messagebox.showerror("Kurulum Gerekli", error_msg)
        return
    
    app = PhotoCompressor()
    app.run()

if __name__ == "__main__":
    main()