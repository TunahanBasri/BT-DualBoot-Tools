# BT DualBoot Tools 🚀 (v1.0 - Classic Bluetooth)

**BT DualBoot Tools**, Windows ve Linux (BlueZ) işletim sistemlerini çift önyükleme (dual-boot) olarak kullanan kişilerin, her işletim sistemi geçişinde Bluetooth cihazlarını (klavye, fare vb.) tekrar tekrar eşleştirmek zorunda kalmasını önleyen, eşleştirme anahtarlarını yedekleyip senkronize etmeyi kolaylaştıran açık kaynaklı bir araçtır.

**Sürüm 1.0 (v1.0) Hedefi**: Yalnızca Classic Bluetooth HID (Klavye, Fare vb.) cihazlarını destekler. Bu sayede ilk sürüm kararlı, sade ve kullanımı kolay tutulmuştur.

---

## 🛠️ Temel İş Akışı (Quickstart)

Eşleştirme anahtarlarını senkronize etmek için aşağıdaki adımları sırasıyla uygulayabilirsiniz:

```
[ Windows ]                                 [ Linux ]
  Windows PowerShell                           Sudo Python Import
 ┌─────────────────────────┐                 ┌────────────────────────┐
 │   .\Export-Keys.ps1     │ ──btkeys.json─> │ sudo python import.py  │
 └─────────────────────────┘                 └────────────────────────┘
                                                         │
                                                         ▼
                                                 Bluetooth Hazır! 🎉
```

1.  **Windows**: PowerShell scriptini Yönetici yetkileriyle çalıştırın:
    ```powershell
    # Windows/ klasörünün içinde:
    Set-ExecutionPolicy Bypass -Scope Process -Force
    .\Export-BluetoothKeys.ps1
    ```
    Bu işlem geçerli dizinde bir `btkeys.json` dosyası oluşturur.
2.  **Dosya Aktarımı**: Oluşan `btkeys.json` dosyasını Linux ortamına aktarın.
3.  **Linux**: Import scriptini çalıştırın:
    ```bash
    # Linux/ klasörünün içinde:
    sudo python import_key.py /yol/btkeys.json
    ```
4.  **Hazır!**: Bluetooth servisiniz otomatik olarak yeniden başlatılacak ve cihazlarınız çalışacaktır.

---

## 📁 Proje Yapısı

```
bt-dualboot-tools/
│
├── windows/                # Windows veri aktarma araçları
│   ├── Export-BluetoothKeys.ps1
│   └── README.md
│
├── linux/                  # Linux içe aktarma ve yedekleme araçları
│   ├── import_key.py
│   ├── backup.py
│   └── README.md
│
├── docs/                   # Detaylı teknik dökümantasyonlar
│   ├── Windows.md          # Registry detayları ve SYSTEM yetkisi
│   ├── Linux.md            # BlueZ dosya mimarisi
│   └── Bluetooth.md        # Cryptography ve anahtar dönüştürme mantığı
│
├── LICENSE                 # MIT Lisansı
└── README.md               # Bu dosya
```

---

## 🛡️ Güvenlik Açıklamaları (Security & Privacy)

Bu aracı kullanırken güvenlik ve gizlilik hakkında bilmeniz gereken temel hususlar:

*   **Yerel Çalışma**: Bu araç **yalnızca yerel Bluetooth eşleştirme anahtarlarını yedekler ve senkronize eder**. İnternet şifreleri, kişisel veriler veya tarayıcı geçmişleriyle hiçbir ilgisi yoktur.
*   **Geçici SYSTEM Görevi**: Windows üzerinde `BTHPORT` anahtarları varsayılan olarak sadece `SYSTEM` hesabı tarafından okunabilir. Bu nedenle script, yalnızca export süresince çalışacak geçici bir Windows Scheduled Task (Zamanlanmış Görev) oluşturur. İşlem biter bitmez bu görev sistemden tamamen silinir.
*   **Otomatik Temizlik**: Export işlemi sırasında oluşturulan geçici `.reg` dosyası, in-memory parse işlemi tamamlanır tamamlanmaz diskten kalıcı olarak silinir.
*   **Linux Yedekleme**: Linux tarafında import işlemi başlatıldığında, mevcut `/var/lib/bluetooth` dizininiz otomatik olarak `/var/lib/bluetooth_backup_<timestamp>` formatında yedeklenir. Olası bir hata durumunda eski yapılandırmanıza kolayca dönebilirsiniz.

---

## 🛣️ Yol Haritası (Roadmap)

*   **v1.0 (Mevcut)**: Klasik Bluetooth HID Cihaz desteği (Klavye, Fare vb.), Cihaz Adı Eşleştirme (Friendly Name Lookup).
*   **v1.1**: Bluetooth Low Energy (BLE) desteği (LTK, EDIV, Rand parametreleri ve endianness dönüşümleri).
*   **v1.2**: Kulaklık / Ses cihazı eşleştirme desteği.
*   **v1.3**: Gamepad (Oyun kolları) eşleştirme desteği.

---

## 📖 Detaylı Teknik Dökümanlar

*   [Windows Bluetooth Registry Dökümantasyonu](docs/Windows.md)
*   [Linux BlueZ Config Dökümantasyonu](docs/Linux.md)
*   [Bluetooth Kriptografi Detayları](docs/Bluetooth.md)

---

## 📄 Lisans
Bu proje **MIT Lisansı** altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına göz atabilirsiniz.
