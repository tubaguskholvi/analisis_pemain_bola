
import pandas as pd

# 1. Membaca dataset
file_path = "data/CompleteDataset.csv"
df = pd.read_csv(file_path, low_memory=False)

print("Jumlah data sebelum dibersihkan:", len(df))

# 2. Memilih fitur yang digunakan untuk analisis pemain
fitur = [
    "Age",
    "Overall",
    "Potential",
    "Acceleration",
    "Sprint speed",
    "Finishing",
    "Short passing",
    "Dribbling",
    "Ball control",
    "Stamina",
    "Strength",
    "Standing tackle"
]

# 3. Mengambil kolom yang dibutuhkan
data = df[["Name", "Nationality", "Club", "Preferred Positions"] + fitur].copy()

# 4. Mengubah fitur menjadi angka
for kolom in fitur:
    data[kolom] = pd.to_numeric(data[kolom], errors="coerce")

# 5. Menghapus baris yang memiliki nilai kosong pada fitur
data = data.dropna(subset=fitur).copy()

# 6. Menghapus data pemain yang memiliki fitur duplikat
# tidak dilakukan agar pemain dengan statistik sama tetap dapat dianalisis

# 7. Menyimpan hasil preprocessing
data.to_csv("data/pemain_bersih.csv", index=False)

print("Jumlah data setelah dibersihkan:", len(data))
print("Jumlah fitur numerik:", len(fitur))
print("\nTipe data setelah dibersihkan:")
print(data[fitur].dtypes)

print("\nContoh data bersih:")
print(data.head())

print("\nFile berhasil disimpan: data/pemain_bersih.csv")
