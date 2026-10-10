
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# 1. Membaca data pemain yang sudah dibersihkan
data_pemain = pd.read_csv("data/pemain_bersih.csv")

print("=== ANALISIS PEMAIN SEPAK BOLA ===")
print("Jumlah pemain yang dianalisis:", len(data_pemain))

# 2. Menentukan statistik yang digunakan untuk analisis
fitur_pemain = [
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

# 3. Menyamakan skala nilai statistik pemain
penyama_skala = StandardScaler()
data_skala = penyama_skala.fit_transform(
    data_pemain[fitur_pemain]
)

# 4. Membuat model pengelompokan pemain
model_pengelompokan = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

# 5. Menentukan kelompok setiap pemain
data_pemain["Kelompok"] = model_pengelompokan.fit_predict(
    data_skala
)

# 6. Mengukur kualitas pengelompokan
nilai_siluet = silhouette_score(
    data_skala,
    data_pemain["Kelompok"],
    sample_size=2000,
    random_state=42
)

print("\n=== HASIL PENGELOMPOKAN PEMAIN ===")
print("Jumlah pemain:", len(data_pemain))
print("Jumlah kelompok:", data_pemain["Kelompok"].nunique())
print("Nilai kualitas pengelompokan:", round(nilai_siluet, 3))

# 7. Menghitung jumlah pemain dalam setiap kelompok
print("\n=== JUMLAH PEMAIN DALAM SETIAP KELOMPOK ===")

jumlah_per_kelompok = (
    data_pemain["Kelompok"]
    .value_counts()
    .sort_index()
)

for nomor_kelompok, jumlah_pemain in jumlah_per_kelompok.items():
    print(f"Kelompok {nomor_kelompok}: {jumlah_pemain} pemain")

# 8. Menghitung rata-rata statistik setiap kelompok
nama_statistik = {
    "Age": "Usia",
    "Overall": "Nilai Keseluruhan",
    "Potential": "Potensi",
    "Acceleration": "Akselerasi",
    "Sprint speed": "Kecepatan Lari",
    "Finishing": "Penyelesaian Akhir",
    "Short passing": "Umpan Pendek",
    "Dribbling": "Menggiring Bola",
    "Ball control": "Penguasaan Bola",
    "Stamina": "Daya Tahan",
    "Strength": "Kekuatan",
    "Standing tackle": "Kemampuan Merebut Bola"
}

print("\n=== RATA-RATA STATISTIK SETIAP KELOMPOK ===")

rata_rata_kelompok = (
    data_pemain.groupby("Kelompok")[fitur_pemain]
    .mean()
    .round(2)
    .rename(columns=nama_statistik)
)

print(rata_rata_kelompok.to_string())

# 9. Menampilkan lima pemain dengan nilai tertinggi
print("\n=== LIMA PEMAIN DENGAN NILAI TERTINGGI ===")

for nomor_kelompok in sorted(data_pemain["Kelompok"].unique()):
    print(f"\nKelompok {nomor_kelompok}:")

    pemain_teratas = (
        data_pemain[
            data_pemain["Kelompok"] == nomor_kelompok
        ]
        .sort_values("Overall", ascending=False)
        [[
            "Name",
            "Preferred Positions",
            "Overall",
            "Potential"
        ]]
        .head(5)
        .rename(columns={
            "Name": "Nama Pemain",
            "Preferred Positions": "Posisi Bermain",
            "Overall": "Nilai Keseluruhan",
            "Potential": "Potensi"
        })
    )

    print(pemain_teratas.to_string(index=False))

# 10. Menyimpan hasil analisis
data_pemain.to_csv(
    "data/pemain_cluster.csv",
    index=False
)

rata_rata_kelompok.to_csv(
    "data/rata_rata_kelompok.csv"
)

print("\n=== PENYIMPANAN SELESAI ===")
print("Hasil pengelompokan: data/pemain_cluster.csv")
print("Rata-rata statistik: data/rata_rata_kelompok.csv")
