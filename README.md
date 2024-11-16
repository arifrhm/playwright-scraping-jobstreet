# JobStreet Scraper

Proyek ini adalah scraper untuk mengambil data pekerjaan dari JobStreet dan menyimpannya dalam format JSON.

## Prasyarat

Sebelum menjalankan scraper, pastikan Anda telah menginstal Docker dan memiliki Python di sistem Anda.

## Instalasi

1. Jalankan Selenium Chrome standalone menggunakan Docker:

```bash
docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-chrome:latest
```

Ini akan menjalankan browser Chrome yang dapat diakses melalui port 4444.

2. Buat dan aktifkan virtual environment:

```bash
uv venv venv
source venv/bin/activate
```

3. Instal dependensi yang diperlukan:

```bash
uv pip install -r req.txt
```

## Penggunaan

1. Jalankan scraper utama untuk mengambil daftar pekerjaan:

```bash
python main.py
```

2. Setelah selesai, jalankan scraper detail untuk mengambil informasi lebih lanjut tentang setiap pekerjaan:

```bash
python detail.py
```

## Output

Hasil scraping akan disimpan dalam file JSON yang dapat digunakan untuk analisis lebih lanjut atau integrasi dengan aplikasi lain.

## Catatan

- Pastikan untuk mematuhi Terms of Service dari JobStreet saat menggunakan scraper ini.
- Tambahkan delay yang sesuai antara requests untuk menghindari pembatasan akses.
- Gunakan data yang dihasilkan secara bertanggung jawab dan sesuai dengan hukum yang berlaku.

