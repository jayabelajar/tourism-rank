# TourismRank

TourismRank adalah aplikasi Sistem Pendukung Keputusan (SPK) untuk merangking destinasi wisata Indonesia menggunakan metode Simple Additive Weighting (SAW). Aplikasi dibuat dengan Streamlit dan menampilkan proses perhitungan secara transparan, mulai dari dataset, kriteria, normalisasi, pembobotan, hingga hasil ranking.

## Fitur Utama

- Dashboard ringkasan dataset destinasi wisata.
- Tabel dataset dengan pencarian, filter provinsi, filter jenis wisata, dan pagination.
- Preferensi pengguna berdasarkan jenis wisata, bulan perjalanan, provinsi, dan bobot kriteria.
- Perhitungan SAW dengan kriteria harga tiket, popularitas, kecocokan jenis wisata, dan kecocokan waktu.
- Tampilan detail alternatif, matriks keputusan, normalisasi, kontribusi bobot, dan ranking akhir.
- Fallback data sampel jika dataset Hugging Face belum bisa diunduh.

## Prasyarat

Pastikan sudah menginstal:

- Python 3.10 atau lebih baru.
- pip.
- Koneksi internet jika ingin mengunduh ulang dataset dari Hugging Face.

Cek versi Python:

```bash
python --version
```

Di Windows, jika perintah `python` tidak tersedia, gunakan:

```bash
py --version
```

## Instalasi

Clone atau buka folder project ini, lalu jalankan perintah berikut dari root project:

```bash
cd tourism-rank
```

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

macOS atau Linux:

```bash
source .venv/bin/activate
```

Upgrade pip dan install dependency:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Menyiapkan atau Update Dataset

Aplikasi menggunakan dataset `LorthGyu/indonesian-tourism` dari Hugging Face.

Untuk mengunduh atau memperbarui dataset secara manual:

```bash
python download_dataset.py
```

Dataset mentah akan disimpan ke:

```text
data/raw/indonesian_tourism.csv
```

Hasil preprocessing akan dibuat otomatis saat aplikasi dijalankan dan disimpan ke:

```text
data/processed/tourism_saw.csv
```

Jika dataset Hugging Face gagal diunduh, aplikasi tetap bisa berjalan menggunakan data sampel bawaan.

## Menjalankan Aplikasi

Jalankan Streamlit dari root project:

```bash
streamlit run app.py
```

Setelah berhasil, buka URL yang muncul di terminal, biasanya:

```text
http://localhost:8501
```

Di halaman utama tersedia tombol:

- `Siapkan Dataset` untuk membaca dataset lokal dan membuat file preprocessing.
- `Refresh dari Hugging Face` untuk mengambil ulang dataset dari Hugging Face.

## Menjalankan Test

Unit test dapat dijalankan dengan:

```bash
python -m unittest discover -s tests
```

## Struktur Project

```text
tourism-rank/
├── app.py
├── download_dataset.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── pages/
├── src/
│   ├── dataset.py
│   ├── preprocessing.py
│   ├── saw.py
│   └── utils.py
└── tests/
```

## Metode SAW

Kriteria yang digunakan:

| Kode | Kriteria | Jenis | Bobot Default |
|---|---|---|---:|
| C1 | Harga Tiket | Cost | 30% |
| C2 | Popularitas | Benefit | 30% |
| C3 | Kecocokan Jenis Wisata | Benefit | 25% |
| C4 | Kecocokan Waktu | Benefit | 15% |

Normalisasi benefit:

```text
rij = xij / max(xij)
```

Normalisasi cost harga:

```text
rij = 1 - (xij / max(x))
```

Nilai preferensi:

```text
Vi = sum(wj * rij)
```

Ranking diurutkan berdasarkan nilai `Vi` terbesar.

## Troubleshooting

Jika `streamlit` tidak dikenali, pastikan virtual environment sudah aktif dan dependency sudah terinstall:

```bash
pip install -r requirements.txt
```

Jika aktivasi virtual environment di PowerShell diblokir, jalankan PowerShell sebagai user biasa lalu gunakan:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Jika update dataset gagal, cek koneksi internet. Aplikasi masih dapat berjalan karena memiliki fallback data sampel.
