
# 🧠 CraftWorld Auto Bot — Token Version

Bot otomatis untuk game [Craft World](https://preview.craft-world.gg) yang memanfaatkan **JWT token** dari `token.txt` dan konfigurasi per akun dari `config.json`.

> ✅ Tidak menggunakan private key  
> 🔐 Aman dan efisien untuk multi-akun  
> ⚙️ Mendukung upgrade otomatis, start pabrik, dan klaim area  

---

## ✨ Fitur

- ✅ Multi-akun: jalan otomatis berdasarkan `token.txt`
- 🔁 Loop otomatis: aksi setiap 30 detik
- 🧱 Auto `START_MINE`, `CLAIM_MINE`, `UPGRADE`, `START_FACTORY`, dan `CLAIM_AREA`
- 📄 Konfigurasi fleksibel via `config.json`
- 📊 Tampilan info akun dengan format tabel

---

## 📁 Struktur File

```
craftworld/
├── bot.py              # Bot utama
├── token.txt           # Daftar JWT token
├── config.json         # Konfigurasi per akun
├── requirements.txt    # Dependensi Python
└── README.md           # Dokumentasi ini
```

---

## 🧰 Persiapan

### 1. Install Python

Pastikan kamu sudah install **Python 3.10+**

---

### 2. Install Virtual Environment (Opsional)

```bash
python -m venv .venv
```

Aktifkan:

- **Windows**:
  ```bash
  .venv\Scripts\activate
  ```
- **Mac/Linux**:
  ```bash
  source .venv/bin/activate
  ```

---

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

Contoh isi `requirements.txt`:

```
requests
rich
```

---

### 4. Isi File `token.txt`

Masukkan JWT token (tanpa awalan `jwt_`) **satu baris per akun**, contoh:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 5. Isi File `config.json`

Contoh `config.json` untuk 2 akun:

```json
{
  "mineId_1": "MINE_ID_AKUN1",
  "factoryMud_1": ["FACTORY_ID_1"],
  "factoryClay_1": ["FACTORY_ID_2"],
  "factorySand_1": ["FACTORY_ID_3"],
  "areaId_1": "AREA_MUD_ID",
  "areaClay_1": "AREA_CLAY_ID",
  "areaSand_1": "AREA_SAND_ID",
  "upgradeMine_1": true,
  "upgradeFactoryMud_1": true,
  "upgradeFactoryClay_1": true,
  "upgradeFactorySand_1": true,

  "mineId_2": "MINE_ID_AKUN2",
  "factoryMud_2": ["FACTORY_ID_4"],
  "factoryClay_2": ["FACTORY_ID_5"],
  "factorySand_2": ["FACTORY_ID_6"],
  "areaId_2": "AREA_MUD_ID_2",
  "areaClay_2": "AREA_CLAY_ID_2",
  "areaSand_2": "AREA_SAND_ID_2",
  "upgradeMine_2": false,
  "upgradeFactoryMud_2": false,
  "upgradeFactoryClay_2": false,
  "upgradeFactorySand_2": false
}
```

---

## 📌 Cara Mendapatkan `mineId`, `factoryId`, dan `areaId`

### 1. Buka [Craft World](https://preview.craft-world.gg) di browser  
### 2. Tekan `F12` untuk membuka DevTools → Buka tab `Network`  
### 3. Klik request `ingest` dan lihat di tab `Payload`

---

### 🪓 mineId

Gunakan untuk `START_MINE`

```json
{
  "actionType": "START_MINE",
  "payload": {
    "mineId": "0684d501-b8fd-7f3b-8000-5eb5a929a01f"
  }
}
```

📸 Contoh:  
![mineId](https://i.imgur.com/Pa2TgCA.png)

---

### 🏭 factoryId

Gunakan untuk `START_FACTORY`

```json
{
  "actionType": "START_FACTORY",
  "payload": {
    "factoryId": "0684fe2c-d2a7-7ef9-8000-4b4b00926cf8"
  }
}
```

📸 Contoh:  
![factoryId](https://i.imgur.com/f4ZnEQc.png)


---

### 🌍 areaId

Gunakan untuk `CLAIM_AREA`

```json
{
  "actionType": "CLAIM_AREA",
  "payload": {
    "areaId": "0684d501-1c8b-7439-8000-b0d609cc70db",
    "amountToClaim": 1258
  }
}
```

📸 Contoh:  
![areaId](https://i.imgur.com/Lk5bx4T.png)

---

## ▶️ Menjalankan Bot

```bash
python craftworld.py
```

- Bot akan memulai dari `START_MINE`, lalu lanjut ke `START_FACTORY`, `CLAIM_AREA`, dan `UPGRADE` jika diaktifkan.
- Siklus akan berjalan **setiap 30 detik**.
- Informasi akun akan ditampilkan setelah setiap aksi.

---

## ⚠️ Catatan

- Token kadaluarsa dapat menyebabkan error 401. Perbarui token jika ini terjadi.
- Jangan bagikan file `token.txt` ke siapa pun.
- Gunakan `factoryMud`, `factoryClay`, dan `factorySand` sebagai list meskipun hanya 1 ID.

---

> Dibuat dengan 💜 oleh Robi x Willyam | `LYAMRIZZ INSIDER`
