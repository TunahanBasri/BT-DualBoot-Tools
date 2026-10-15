# 🚀 BT-DualBoot Tools - Türkçe Kullanım Kılavuzu

Bu kılavuz, hem **Windows** hem **Linux** (Ubuntu, Arch, Fedora, Debian, Mint vb.) kullanan çift önyüklemeli (dual-boot) bilgisayarlarda, Bluetooth klavye ve farelerin **her işletim sistemi değişiminde yeniden eşleştirilme zorunluluğunu** kalıcı olarak ortadan kaldırmak için hazırlanmıştır.

---

## 📌 Mantık: Neden 3 Adım Yapıyoruz?

Bluetooth cihazınız (klavye/fare), hafızasında **yalnızca 1 adet en son üretilen şifreyi** tutabilir.
1. Cihazınızı **önce Linux'ta** eşleştiririz -> Linux, cihaza ait donanım kimlik dosyasını oluşturur.
2. Cihazınızı **sonra Windows'ta** eşleştiririz -> Cihaz hafızasındaki şifreyi Windows'unkine günceller.
3. Windows'taki bu en güncel şifreyi **`Export-Keys.bat`** ile alıp Linux'un içine yazarız -> Artık iki işletim sistemi de **birebir aynı şifreyi** kullanır ve cihaz hiç kopmadan anında bağlanır!

---

## 🧰 Hazırlık & Gereksinimler

* Bir adet **USB Flash Bellek** (veya Windows ile Linux arasında dosya taşıyabileceğiniz ortak bir disk/klasör).
* Bluetooth klavye veya fareniz.
* Bilgisayarınızda hem Windows hem Linux kurulu olması.

---

## 🛠️ Adım Adım Kolay Kurulum (Toplam Süre: ~3 Dakika)

```
[ ADIM 1: Linux ]             [ ADIM 2: Windows ]               [ ADIM 3: Linux ]
Ayarlardan Cihazı     ──►   Ayarlardan Cihazı       ──►    sudo python sync.py
1 Kez Eşleştirin            1 Kez Eşleştirin               (btkeys.json dosyasını
(Donanım Kimliği            Export-Keys.bat (Çift Tık)     bu ekrana sürükleyin)
Oluşsun)                    Oluşan btkeys.json'ı           🎉 BİTTİ! Artık her iki
                            USB belleğe atın               sistemde de hep bağlı!
```

---

### ADIM 1: Linux'ta İlk Eşleştirme (Sıfır Noktası)
1. Bilgisayarınızı **Linux** ile başlatın.
2. Linux Sistem Ayarları -> **Bluetooth** bölümünü açın.
3. Klavyenizi / farenizi eşleştirme (pairing) moduna alıp Linux'a normal şekilde bağlayın.
4. Cihazınızın çalıştığını teyit edin.
5. *(Not: Linux donanım kimliği böylece oluşmuş oldu.)*

---

### ADIM 2: Windows'ta Eşleştirme ve Anahtar Çıkarma
1. Bilgisayarınızı yeniden başlatıp **Windows**'a geçin.
2. Windows Ayarlar -> **Bluetooth ve Cihazlar** bölümünü açın.
3. Cihazınızı tekrar eşleştirme moduna alıp Windows'a da bağlayın.
4. Bu proje klasörünün içindeki **`Export-Keys.bat`** (veya `windows\Export-Keys.bat`) dosyasına **sağ tıklayıp "Yönetici Olarak Çalıştır"** deyin (veya çift tıklayın).
5. Ekrana yeşil renkli **"TEBRİKLER! BLUETOOTH ANAHTAR PAKETİNİZ HAZIR"** yazısı gelecektir.
6. Klasörün içinde otomatik olarak **`btkeys.json`** adında bir dosya oluşacaktır.
7. Bu **`btkeys.json`** dosyasını **USB belleğinize kopyalayın**.

---

### ADIM 3: Linux'a Geri Dönüş ve Tek Tıkla Senkronizasyon
1. Bilgisayarı yeniden başlatıp tekrar **Linux**'a geçin.
2. USB belleğinizi takın.
3. Terminali açın ve proje klasöründe şu komutu çalıştırın:
   ```bash
   sudo python sync.py
   ```
4. Karşınıza akıllı arayüz çıkacaktır.
5. USB belleğinizdeki `btkeys.json` dosyasını farenizle tutup **doğrudan bu siyah terminal ekranının içine sürükleyip bırakın** ve **Enter**'a basın!
   *(İsterseniz dosyayı doğrudan proje klasörünün içine kopyalayıp menüden [1] tuşuna da basabilirsiniz.)*
6. Sistem otomatik olarak:
   * Mevcut ayarlarınızın tarihli yedeğini alır (`/var/lib/bluetooth/backups/`).
   * Windows anahtarlarını Linux BlueZ formatına dönüştürür.
   * Bluetooth servisini yeniden başlatır ve canlı bağlantıyı test eder:
     ```text
     Canlı Bağlantı Durumu:
      ✔ Logitech MX Master 3 -> ANINDA BAĞLANDI! 🎉
     ```

**Tebrikler! İşlem bu kadar.** Artık bilgisayarınızı ister Windows'ta açın, ister Linux'ta; cihazınız hiçbir şifre sormadan doğrudan bağlanacaktır.

---

## ❓ Sıkça Sorulan Sorular & Sorun Giderme

### Soru 1: Dosyayı terminale sürükledim ama çalışmadı?
* **Cevap:** Terminal penceresine odaklandığınızdan emin olun. Terminal ekranına bıraktığınızda dosya yolu otomatik yazılır (Örn: `'/media/usb/btkeys.json'`). `Enter` tuşuna basmanız yeterlidir.

### Soru 2: "Device directory not found. Please pair device once in Linux first" hatası aldım?
* **Cevap:** Cihazınızı ADIM 1'de Linux Bluetooth ayarlarından eşleştirmeyi unuttunuz demektir. Önce Linux ayarlarından cihazı normalce ekleyin, ardından scripti tekrar çalıştırın.

### Soru 3: Bir şeyler ters giderse ayarlarımı eski haline nasıl alırım?
* **Cevap:** Sistem her işlemden önce tam snapshot yedeği alır. Terminalde şunu yazarak tek saniyede geri dönebilirsiniz:
  ```bash
  sudo python sync.py
  ```
  ve menüden **[4] (Geri Al / Rollback)** seçeneğini seçin.

### Soru 4: Keychron / Logitech gibi yeni nesil BLE klavyem var, çalışır mı?
* **Cevap:** Evet! Bu araç Classic Bluetooth (LinkKey) ve Bluetooth Low Energy (BLE LTK, ERand, EDiv) kriptografik standartlarının tamamını destekler.
