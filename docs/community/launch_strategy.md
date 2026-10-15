# 📢 BT-DualBoot Tools: Global Lansman ve Topluluk Dağıtım Rehberi

Bu rehber; **BT-DualBoot Tools** projesini global Linux ve Dual-Boot topluluklarında duyurarak **GitHub'da 500+ yıldız (star) toplamak**, LinkedIn'de Sistem Mühendisliği pozisyonları için kıdemli seviye algısı yaratmak ve Hacker News üzerinde öne çıkmak için hazırlanmış kopyala-yapıştır hazır dağıtım paketidir.

---

## 🎬 1. 10 Saniyelik Vitrin GIF'i / Videosu Hazırlama

Geliştiriciler ve sistem yöneticileri uzun metinler yerine çalışan çıktıyı görmek ister. `README.md`'nin tepesine koyulacak 10 saniyelik GIF çekim senaryosu:

1. **Windows (3 Saniye):**
   - Yönetici PowerShell açılır: `.\Export-BluetoothKeys.ps1` (veya `Export-Keys.bat`) çalıştırılır.
   - Ekranda hızlıca `[SUCCESS] Export written to: btkeys.json` ve cihazların (Logitech Mouse vb.) yeşil renkli listesi görünür.
2. **Linux (7 Saniye - Büyük Çözüm Anı):**
   - Terminal açılır: `sudo python sync.py` yazılır.
   - Dosya sürüklenir, `--dry-run` tablosunun aktığı ve `[OK] Updated` çıktısı sonrası farenin imlecinin **hiçbir eşleştirme düğmesine basmadan ekranda anında hareket ettiği** gösterilir.
3. **Araç:** Windows'ta *ScreenToGif* veya Linux'ta *Peek / Kooha* kullanarak GIF üretilip doğrudan repoya veya GitHub Issue asset alanına yüklenir.

---

## 👾 2. Topluluk Paylaşım Şablonları (Kopyala & Yapıştır)

### A. Reddit (`r/linux`, `r/dualboot`, `r/archlinux`)

* **Önerilen Gönderi Zamanı:** Salı veya Çarşamba günü TSİ 16:00 - 18:00 (ABD Doğu Saati 09:00 - 11:00)
* **Başlık:** *Tired of re-pairing your Bluetooth mouse and keyboard every time you switch between Windows and Linux? I built an open-source sync tool.*
* **Metin (Markdown):**
```markdown
Hey everyone,

Like pretty much everyone who dual-boots Windows 11 and Linux, I was endlessly frustrated having to delete and re-pair my Bluetooth mouse and keyboard every single reboot.

Because each OS generates a completely different Link Key during pairing, the peripheral's secret gets overwritten every time you switch OS.

To permanently solve this without using sketchy third-party closed-source binaries or manually hex-editing raw hives, I built **BT-DualBoot Tools**:

- **Windows Extraction**: Uses native, ephemeral Windows Scheduled Tasks running as `NT AUTHORITY/SYSTEM` to read `BTHPORT\Parameters\Keys` and self-destructs immediately with zero residual files.
- **Friendly Name Resolution**: Maps hex MACs back to real device names (e.g., Logitech MX Master 3).
- **Non-Destructive BlueZ Parser**: Updates only the `[LinkKey]` and `[LongTermKey]` section under `/var/lib/bluetooth` while preserving all comments and custom device flags.
- **BLE Support**: Automatic Little-Endian to Big-Endian Rand/EDiv conversion for modern mechanical keyboards (Keychron, Logitech, etc.).
- **Safety**: Automatically creates timestamped snapshot backups with a built-in `--rollback` command, plus `--dry-run` preview.
- **Pure Python + PowerShell**: Zero external dependencies required (30 automated unit tests).

It's 100% open-source under the MIT license:
👉 https://github.com/TunahanBasri/bt-dualboot-tools

Feedback and thoughts are warmly welcome!
```

---

### B. Hacker News ("Show HN")

* **Başlık:** `Show HN: BT-DualBoot – Sync Bluetooth pairing keys across Windows and Linux`
* **Metin:**
```text
I built an open-source tool to solve a chronic dual-boot friction point: Bluetooth peripherals needing to be re-paired on every boot between Windows and Linux.

Key implementation details:
1. Windows kernel stores Link Keys in HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys, accessible only by NT AUTHORITY\SYSTEM. The script provisions an ephemeral scheduled task that cleans up automatically in a finally block.
2. Linux BlueZ stores info files as INI. Standard configparser strips comments and reorders entries, which can confuse bluetoothd; so I wrote a lightweight non-destructive INI updater.
3. Bluetooth Low Energy (BLE) peripheral support with Little-Endian to Big-Endian 64-bit Rand integer arithmetic.
4. Built with zero external dependencies and 30 unit tests for safe rollback and format validation.

GitHub: https://github.com/TunahanBasri/bt-dualboot-tools
Feedback and bug reports are warmly welcome!
```

---

### C. LinkedIn (Sistem Mühendisliği & Düşük Seviye Vitrini)

```text
Windows ve Linux'u aynı bilgisayarda (dual-boot) kullanan herkesin yaşadığı kronik bir donanım problemi vardır: İşletim sistemi değiştirdiğinizde Bluetooth fareniz ve klavyeniz çalışmaz, yeniden eşleştirmeniz gerekir.

Çünkü her iki işletim sistemi de aynı Bluetooth adaptörü için cihazla farklı kriptografik anahtarlar (Link Key) üretir ve birindeki eşleşme diğerini geçersiz kılar.

Bu problemi kalıcı olarak çözmek için geliştirdiğim açık kaynaklı sistem aracım: **BT-DualBoot Tools** 🚀

Bu projede üzerinde durduğum mühendislik zorlukları:
🔒 Windows Kernel & SYSTEM İzolasyonu: `BTHPORT` anahtarları varsayılan olarak Administrator'a dahi kilitlidir. Üçüncü parti şüpheli binary'ler yerine yerel PowerShell ile geçici bir SYSTEM scheduled task oluşturup anahtarları bellekten okudum ve geçici dosyaları anında imha eden bir güvenlik yaşam döngüsü kurdum.
🐧 Linux BlueZ Entegrasyonu: Linux'taki `/var/lib/bluetooth` yapılandırma dosyalarını bozmadan, sadece ilgili cihazın link key'ini güncelleyen ve öncesinde anlık geri alma (snapshot rollback) yedeği alan bir motor geliştirdim.
⚡ BLE ve Little-Endian Dönüşümü: Keychron ve yeni nesil klavyeler için ERand/EDiv bayt dönüşümlerini Linux BlueZ ondalık standardına eşledim.
🛡️ Sıfır Bağımlılık & Test Odaklılık: Dış kütüphane bağımlılığı olmadan saf Python ve PowerShell ile çalıştığı gibi, 30 farklı birim testiyle donatıldı.

Projeyi MIT lisansıyla tamamen açık kaynak olarak paylaştım.
GitHub Linki: https://github.com/TunahanBasri/bt-dualboot-tools

#Linux #Windows #Bluetooth #SystemsEngineering #Python #OpenSource #DevOps
```

---

### D. X / Twitter (Teknik Bilgi Akışı / Thread)

```text
1/4 Fixed the most annoying dual-boot friction: having to re-pair your Bluetooth mouse and keyboard every time you switch between Windows and Linux.

Built an open-source sync tool: BT-DualBoot Tools 🐧🪟

2/4 How it works:
- Windows exports BTHPORT registry keys via an ephemeral SYSTEM task (native & self-cleaning)
- Resolves friendly names (Logitech, Keychron, etc.)
- Python CLI safely updates Linux BlueZ /var/lib/bluetooth configs with automatic snapshot rollback
- Full BLE Little-to-Big Endian conversion support

3/4 Zero external dependencies, pure Python 3.8+ & PowerShell, with full --dry-run simulation mode & 30 passing unit tests.

4/4 Check it out on GitHub (MIT): https://github.com/TunahanBasri/bt-dualboot-tools
Retweets appreciated! 🚀
```
