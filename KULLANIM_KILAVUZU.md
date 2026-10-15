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

* Bluetooth klavye veya fareniz.
* Bilgisayarınızda hem Windows hem Linux kurulu olması.
* `btkeys.json` dosyasını iki sistem arasında taşımak için: WhatsApp Web, Telegram, Bulut (Google Drive vb.), ortak Windows C:\ diski VEYA klasik bir USB bellek.

---

## 🛠️ Adım Adım Kolay Kurulum (Toplam Süre: ~3 Dakika)

```
[ ADIM 1: Linux ]             [ ADIM 2: Windows ]               [ ADIM 3: Linux ]
Ayarlardan Cihazı     ──►   Ayarlardan Cihazı       ──►    sudo python sync.py
1 Kez Eşleştirin            1 Kez Eşleştirin               (btkeys.json dosyasını
(Donanım Kimliği            Export-Keys.bat (Çift Tık)     bu ekrana sürükleyin)
Oluşsun)                    Oluşan btkeys.json'ı           🎉 BİTTİ! Artık her iki
                            WhatsApp/Bulut/USB ile atın    sistemde de hep bağlı!
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
7. **Bu `btkeys.json` dosyasını Linux'a aktarın (Size en kolay gelen yolu seçin):**
   * 💬 **1. Yol (En Pratiği - Flash Belleksiz):** Dosyayı WhatsApp Web'den kendinize (veya Telegram Kayıtlı Mesajlar / Google Drive / Email) atın. Linux'a geçince tarayıcıdan indirin!
   * 📂 **2. Yol (Doğrudan Windows Diski):** Linux dosya yöneticisinde sol menüdeki Windows (C:) diskinize tıklayıp doğrudan bu klasörün içinden alın.
   * 💾 **3. Yol (Geleneksel USB):** Dosyayı bir USB flash belleğe kopyalayın.

> [!NOTE]
> 🔒 **Güvenlik Tavsiyesi:** Bluetooth eşleşme anahtarları donanım şifreleme anahtarlarıdır. Dosyayı WhatsApp, Telegram veya E-posta ile aktardıysanız, senkronizasyon tamamlandıktan sonra dosyayı sohbetinizden ve İndirilenler klasöründen silmeniz önerilir.

---

### ADIM 3: Linux'a Geri Dönüş ve Tek Tıkla Senkronizasyon
1. Bilgisayarı yeniden başlatıp tekrar **Linux**'a geçin.
2. WhatsApp, Bulut, C: diski veya USB üzerinden dosyanız hazır olsun.
3. Terminali açın ve proje klasöründe şu komutu çalıştırın:
   ```bash
   sudo python sync.py
   ```
4. Karşınıza akıllı arayüz çıkacaktır.
5. `btkeys.json` dosyasını (örneğin İndirilenler klasöründen veya USB'den) farenizle tutup **doğrudan bu siyah terminal ekranının içine sürükleyip bırakın** ve **Enter**'a basın!
   *(İsterseniz dosyayı doğrudan proje klasörünün içine kopyalayıp menüden [1] tuşuna da basabilirsiniz.)*
6. Sistem otomatik olarak:
   * Mevcut ayarlarınızın tarihli yedeğini alır (`/var/lib/bluetooth/backups/`).
   * Eşleşme anahtarlarını Linux BlueZ yapılandırmasına aktarır.
   * Bluetooth servisini yeniden başlatır ve canlı bağlantıyı test eder:
     ```text
     Canlı Bağlantı Durumu:
      ✔ Sony WH-1000XM4 -> ANINDA BAĞLANDI! 🎉
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

### Soru 4: Keychron / Logitech gibi yeni nesil klavye veya fareler çalışır mı?
* **Cevap:** Evet! Bu araç Classic Bluetooth (LinkKey) ve Bluetooth Low Energy (BLE LTK, ERand, EDiv) standartlarını destekler. (Not: Bazı modern Bluetooth Smart/BLE fare modelleri her yeni eşleştirmede donanım MAC adresini kaydırdığı için bu tür farelerin Classic Bluetooth moduyla veya varsa USB alıcısıyla eşleştirilmesi önerilir.)
