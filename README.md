# BT DualBoot Tools 🚀

**BT DualBoot Tools**, Windows ve Linux (BlueZ) işletim sistemlerini çift önyükleme (dual-boot) olarak kullanan kişilerin, her işletim sistemi geçişinde Bluetooth cihazlarını (klavye, fare, kulaklık vb.) tekrar tekrar eşleştirmek zorunda kalmasını önleyen, eşleştirme anahtarlarını yedekleyip senkronize etmeyi kolaylaştıran açık kaynaklı bir araçtır.

---

## 🛠️ Temel İş Akışı (Quickstart)

Eşleştirme anahtarlarını senkronize etmek için aşağıdaki adımları sırasıyla uygulayabilirsiniz:

```
[ Windows ]                                 [ Linux ]
  Windows PowerShell / Python                  Sudo Python Import
 ┌─────────────────────────┐                 ┌────────────────────────┐
 │   .\Export-Keys.ps1     │ ──btkeys.json─> │ sudo python import.py  │
 └─────────────────────────┘                 └────────────────────────┘
                                                         │
                                                         ▼
                                                 Bluetooth Hazır! 🎉
```

1.  **Windows**: PowerShell veya Python scriptini Yönetici olarak çalıştırın:
    ```powershell
    # Windows/ klasörünün içinde:
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
│   ├── Export-BluetoothKeys.py
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
│   └── Bluetooth.md        # Cryptography, Endianness ve ERand dönüştürme mantığı
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

## 📖 Detaylı Teknik Dökümanlar

Sistemlerin Bluetooth anahtarlarını saklama biçimi ve arka planda çalışan dönüşüm algoritmaları hakkında daha fazla bilgi edinebilirsiniz:
*   [Windows Bluetooth Registry Dökümantasyonu](docs/Windows.md)
*   [Linux BlueZ Config Dökümantasyonu](docs/Linux.md)
*   [Bluetooth Kriptografi ve Endianness Dönüşüm Detayları](docs/Bluetooth.md)

---

## 📄 Lisans
Bu proje **MIT Lisansı** altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına göz atabilirsiniz.
