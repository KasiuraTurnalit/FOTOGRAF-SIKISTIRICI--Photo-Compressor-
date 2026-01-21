#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows için Fotoğraf Sıkıştırma Programı - ORİJİNAL YÖN KORUMALI
Fotoğrafların orijinal yönlerini değiştirmez, sadece boyut ve kalite ayarlarını uygular
"""

import os
import sys
from PIL import Image
from pathlib import Path
import shutil

def is_hidden_file(filename):
    """Gizli dosya kontrolü - sessizce atlanacak"""
    # . ile başlayan dosyalar (Mac/Linux gizli dosyaları)
    if filename.startswith('.'):
        return True
    # Windows gizli/sistem dosyaları
    if filename.lower() in ['thumbs.db', 'desktop.ini', '.ds_store', 'icon\r']:
        return True
    # ~ ile başlayan veya biten geçici dosyalar
    if filename.startswith('~') or filename.endswith('~'):
        return True
    return False

def compress_image_preserve_orientation(input_path, output_path, quality=85, max_size=(1920, 1080)):
    """
    Tek bir fotoğrafı sıkıştırır - Orijinal yönü korur
    """
    try:
        # Gizli dosya kontrolü - sessizce atla
        if is_hidden_file(os.path.basename(input_path)):
            return None  # None döndür, böylece sessizce atlanacak
        
        with Image.open(input_path) as img:
            # EXIF verilerini koru
            exif_data = img.info.get('exif')
            
            # Orijinal boyutları al
            original_width, original_height = img.size
            
            # Boyut oranını koruyarak yeniden boyutlandır (sadece gerekirse)
            if max_size[0] > 0 and max_size[1] > 0:
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Dosya formatına göre kaydet
            ext = os.path.splitext(input_path)[1].lower()
            
            # Kaydetme parametreleri
            save_params = {}
            
            if ext in ['.jpg', '.jpeg']:
                format = 'JPEG'
                save_params = {
                    'quality': quality,
                    'optimize': True,
                    'progressive': False  # Progressive JPEG'i kapat
                }
                
                # EXIF verilerini koru
                if exif_data:
                    save_params['exif'] = exif_data
                    
            elif ext == '.png':
                format = 'PNG'
                save_params = {'optimize': True}
            elif ext == '.webp':
                format = 'WEBP'
                save_params = {'quality': quality, 'method': 6}
            elif ext == '.bmp':
                format = 'BMP'
            elif ext == '.gif':
                format = 'GIF'
                save_params = {'optimize': True}
            elif ext == '.tiff' or ext == '.tif':
                format = 'TIFF'
                save_params = {'compression': 'jpeg'}
            else:
                # Diğer formatlar için orijinalini kopyala
                shutil.copy2(input_path, output_path)
                return False
            
            # Orijinal yönü koruyarak kaydet
            img.save(output_path, format, **save_params)
            
            # Boyut karşılaştırması
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            
            if original_size > 0:
                compression_ratio = (1 - compressed_size / original_size) * 100
            else:
                compression_ratio = 0
            
            new_width, new_height = img.size
            return {
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'original_dimensions': (original_width, original_height),
                'new_dimensions': (new_width, new_height)
            }
            
    except Exception as e:
        print(f"  Hata: {str(e)}")
        return None

def get_unique_target_dir(base_target_dir):
    """
    Benzersiz bir hedef klasör adı oluşturur
    """
    if not os.path.exists(base_target_dir):
        return base_target_dir
    
    counter = 1
    while True:
        new_target = f"{base_target_dir}_{counter}"
        if not os.path.exists(new_target):
            return new_target
        counter += 1

def process_directory_structure(source_dir, target_dir, quality=85, max_size=(1920, 1080)):
    """
    Kaynak klasör yapısını hedefte oluşturur ve tüm fotoğrafları işler
    """
    
    # Desteklenen formatlar
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif')
    
    # İstatistikler
    stats = {
        'total_files': 0,
        'processed_files': 0,
        'skipped_files': 0,
        'total_original_size': 0,
        'total_compressed_size': 0,
        'failed_files': []
    }
    
    print(f"📁 Kaynak: {source_dir}")
    print(f"📁 Hedef: {target_dir}")
    print("=" * 60)
    print("⚠ DİKKAT: Fotoğrafların orijinal yönü korunacaktır!")
    print("=" * 60)
    
    # Önce tüm klasör yapısını oluştur
    print("\n📂 Klasör yapısı oluşturuluyor...")
    for root, dirs, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)
        
        if relative_path == ".":
            target_subdir = target_dir
        else:
            target_subdir = os.path.join(target_dir, relative_path)
        
        os.makedirs(target_subdir, exist_ok=True)
    
    # Şimdi dosyaları işle
    for root, dirs, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)
        
        if relative_path == ".":
            target_subdir = target_dir
        else:
            target_subdir = os.path.join(target_dir, relative_path)
        
        print(f"\n📂 İşleniyor: {relative_path if relative_path != '.' else 'Ana Klasör'}")
        print("-" * 40)
        
        # Dosyaları işle
        for file in files:
            if file.lower().endswith(supported_formats):
                stats['total_files'] += 1
                
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_subdir, file)
                
                print(f"  📸 {file}...")
                
                # Fotoğrafı sıkıştır (orijinal yön korunarak)
                result = compress_image_preserve_orientation(source_file, target_file, quality, max_size)
                
                if result:
                    stats['processed_files'] += 1
                    stats['total_original_size'] += result['original_size']
                    stats['total_compressed_size'] += result['compressed_size']
                    
                    print(f"    ✓ {result['original_dimensions'][0]}x{result['original_dimensions'][1]} → "
                          f"{result['new_dimensions'][0]}x{result['new_dimensions'][1]}")
                    
                    if result['original_size'] > 0 and result['compressed_size'] > 0:
                        print(f"    📊 {result['original_size']/1024/1024:.2f}MB → "
                              f"{result['compressed_size']/1024/1024:.2f}MB "
                              f"(%{result['compression_ratio']:.1f} tasarruf)")
                        
                elif result is False:
                    # Kopyalanan dosya (desteklenmeyen format)
                    stats['skipped_files'] += 1
                    original_size = os.path.getsize(source_file)
                    stats['total_original_size'] += original_size
                    stats['total_compressed_size'] += original_size
                    print(f"    ⚠ Kopyalandı (desteklenmeyen format)")
                elif result is None:
                    # Gizli dosya - sessizce atla, istatistikleri güncelleme
                    stats['total_files'] -= 1  # Toplamdan çıkar
                    continue  # Hiçbir mesaj gösterme, bir sonraki dosyaya geç
                else:
                    # Hata durumu
                    stats['skipped_files'] += 1
                    stats['failed_files'].append(source_file)
                    print(f"    ✗ İşlenemedi")
    
    return stats

def get_settings_from_user():
    """
    Kullanıcıdan ayarları alır
    """
    print("\n" + "="*60)
    print("FOTOĞRAF SIKIŞTIRMA PROGRAMI")
    print("✓ Orijinal yön korunur")
    print("✓ Alt klasör yapısı korunur")
    print("="*60)
    
    # Klasör yolları
    while True:
        source_dir = input("📁 Kaynak klasör yolunu girin: ").strip('"')
        
        if not source_dir:
            print("❌ Lütfen bir klasör yolu girin!")
            continue
            
        if os.path.exists(source_dir):
            break
        else:
            print("❌ Kaynak klasör bulunamadı! Tekrar deneyin.")
    
    # Hedef klasör (kaynakla aynı yerde '_compressed' klasörü)
    source_name = os.path.basename(source_dir)
    default_target = os.path.join(os.path.dirname(source_dir), f"{source_name}_compressed")
    
    print(f"\n📁 Hedef klasör için seçenekler:")
    print(f"1. Varsayılan: {default_target}")
    print(f"2. Özel yol")
    
    choice = input("\nSeçiminiz (1-2, varsayılan: 1): ").strip()
    
    if choice == "2":
        target_dir = input("📁 Hedef klasör yolunu girin: ").strip('"')
        if not target_dir:
            target_dir = default_target
    else:
        target_dir = default_target
    
    # Hedef klasör zaten varsa otomatik benzersiz isim oluştur
    if os.path.exists(target_dir):
        print(f"\n⚠ '{target_dir}' zaten var!")
        print("Otomatik olarak benzersiz isim oluşturuluyor...")
        target_dir = get_unique_target_dir(target_dir)
        print(f"✅ Yeni hedef klasör: {target_dir}")
    
    # Kalite ayarı
    print("\n⚙️  Sıkıştırma Ayarları:")
    print("1. Çok Yüksek Kalite (95% - Neredeyse kayıpsız)")
    print("2. Yüksek Kalite (85% - Önerilen)")
    print("3. Orta Kalite (75%)")
    print("4. Sadece boyutu küçült, kaliteyi değiştirme")
    print("5. Özel Ayarlar")
    
    choice = input("Seçiminiz (1-5, varsayılan: 2): ").strip()
    
    if choice == '1':
        quality = 95
        max_size = (1920, 1080)
    elif choice == '3':
        quality = 75
        max_size = (1920, 1080)
    elif choice == '4':
        quality = 100  # Kalite değişmez
        max_size = (1920, 1080)
    elif choice == '5':
        quality_input = input("JPEG kalitesi (1-100, varsayılan: 85): ").strip()
        quality = int(quality_input) if quality_input else 85
        
        resize_choice = input("Boyutu değiştirmek istiyor musunuz? (e/h, varsayılan: e): ").lower().strip()
        if resize_choice == 'h':
            max_size = (0, 0)  # Boyut değiştirme
        else:
            max_width = input("Maksimum genişlik (pixel, varsayılan: 1920): ").strip()
            max_height = input("Maksimum yükseklik (pixel, varsayılan: 1080): ").strip()
            max_size = (int(max_width) if max_width else 1920, 
                       int(max_height) if max_height else 1080)
    else:
        # Varsayılan
        quality = 85
        max_size = (1920, 1080)
    
    return source_dir, target_dir, quality, max_size

def print_summary(stats, target_dir):
    """
    İşlem özetini gösterir
    """
    print("\n" + "="*60)
    print("İŞLEM ÖZETİ")
    print("="*60)
    
    print(f"📊 Toplam Dosya: {stats['total_files']}")
    print(f"✅ İşlenen: {stats['processed_files']}")
    print(f"⏭️  Atlanan: {stats['skipped_files']}")
    
    if stats['failed_files']:
        print(f"❌ Başarısız: {len(stats['failed_files'])}")
        for failed in stats['failed_files'][:3]:
            print(f"   - {os.path.basename(failed)}")
    
    if stats['total_original_size'] > 0:
        total_saved = stats['total_original_size'] - stats['total_compressed_size']
        total_saved_percent = (total_saved / stats['total_original_size']) * 100 if stats['total_original_size'] > 0 else 0
        
        print(f"\n💾 Boyut Özeti:")
        print(f"   Orijinal: {stats['total_original_size']/1024/1024:.2f} MB")
        print(f"   Sıkıştırılmış: {stats['total_compressed_size']/1024/1024:.2f} MB")
        
        if total_saved > 0:
            print(f"   Tasarruf: {total_saved/1024/1024:.2f} MB (%{total_saved_percent:.1f})")
        else:
            print(f"   Tasarruf: 0 MB")
    
    print(f"\n📂 Sıkıştırılmış dosyalar: {target_dir}")
    print("="*60)

def main():
    """
    Ana program
    """
    try:
        # Gerekli kütüphaneleri kontrol et
        try:
            from PIL import Image
        except ImportError:
            print("❌ PIL/Pillow kütüphanesi yüklü değil!")
            print("📦 Yüklemek için: pip install pillow")
            input("\nÇıkmak için Enter tuşuna basın...")
            sys.exit(1)
        #Yapımcı
        print("Kasiura Turnalit Tarafından Hazırlanmıştır...")
        # Başlık
        print("\n" + "="*60)
        print("FOTOĞRAF SIKIŞTIRICI")
        print("✓ Fotoğrafların yönü değişmez")
        print("✓ Tüm EXIF verileri korunur")
        print("✓ Gizli dosyalar sessizce atlanır")
        print("="*60)
        
        # Ayarları al
        source_dir, target_dir, quality, max_size = get_settings_from_user()
        
        # İşlemi başlat
        print(f"\n⏳ İşlem başlatılıyor...")
        print(f"   Kaynak: {source_dir}")
        print(f"   Hedef: {target_dir}")
        print(f"   Kalite: %{quality}")
        
        if max_size[0] > 0 and max_size[1] > 0:
            print(f"   Maksimum boyut: {max_size[0]}x{max_size[1]}")
        else:
            print(f"   Boyut değiştirme: Kapalı")
        
        print(f"\n⚠ UYARI: Fotoğrafların orijinal yönü ve EXIF verileri korunacaktır!")
        print("ℹ️  NOT: Gizli dosyalar (. ile başlayanlar) sessizce atlanacaktır.")
        
        # Onay
        devam = input("\nDevam etmek istiyor musunuz? (e/h, varsayılan: e): ").lower().strip()
        if devam == 'h':
            print("❌ İşlem iptal edildi.")
            input("\nÇıkmak için Enter tuşuna basın...")
            return
        
        # Klasör yapısını işle
        stats = process_directory_structure(source_dir, target_dir, quality, max_size)
        
        # Özeti göster
        print_summary(stats, target_dir)
        
        # Tamamlama
        print("\n🎉 İşlem başarıyla tamamlandı!")
        print(f"📌 Tüm fotoğraflar orijinal yönleriyle korundu.")
        print(f"📌 Gizli dosyalar atlandı ve listelenmedi.")
        
        # Klasörü açma seçeneği
        open_folder = input("\n📂 Hedef klasörü açmak ister misiniz? (e/h, varsayılan: e): ").lower().strip()
        if open_folder != 'h':
            os.startfile(target_dir)
        
    except KeyboardInterrupt:
        print("\n\n⚠ İşlem kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {str(e)}")
    finally:
        input("\nÇıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    main()