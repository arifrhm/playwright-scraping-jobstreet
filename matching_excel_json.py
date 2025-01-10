import pandas as pd
from openpyxl import load_workbook
from difflib import get_close_matches

# Membaca file JSON
json_file_path = "proposal-riset-all.json"
df_json = pd.read_json(json_file_path)
data_proposals = df_json['data']  # Mengambil bagian 'data' dari JSON

# Membaca file Excel yang sudah ada
excel_file_path = "Usulan RKAP (Anggaran dan Target).xlsx"
workbook = load_workbook(excel_file_path)

# Memilih worksheet yang akan diisi
sheet = workbook.active  # Mengambil sheet aktif, atau Anda bisa memilih berdasarkan nama sheet yang diinginkan

# Mengambil header dari baris pertama sebagai dictionary
headers = {}
for cell in sheet[1]:
    if cell.value is not None:  # Pastikan cell bukan kosong
        headers[cell.value] = cell.column  # Menggunakan atribut 'column' yang lebih aman daripada 'column_letter'

# Mengambil semua key dari JSON untuk dicocokkan dengan header Excel
keys_json = list(data_proposals[0].keys())  # Mengambil semua key dari JSON

# Mencocokkan header Excel dengan properti JSON secara otomatis
mapping = {}
for header_name in headers.keys():
    match = get_close_matches(header_name.lower(), keys_json, n=1, cutoff=0.5)
    if match:
        json_key = match[0]
        excel_column = headers[header_name]
        mapping[json_key] = {
            'header_excel': header_name,
            'excel_column': excel_column
        }

# Menampilkan hasil mapping
for json_key, mapping_info in mapping.items():
    print(f"JSON Property: '{json_key}' -> Header Excel: '{mapping_info['header_excel']}', Column: '{mapping_info['excel_column']}'")

# Menutup workbook
workbook.close()
