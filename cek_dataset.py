
import pandas as pd

file_path = "data/CompleteDataset.csv"

try:
    df = pd.read_csv(file_path, low_memory=False)

    print("Dataset berhasil dibaca!")
    print("Jumlah baris:", len(df))
    print("Jumlah kolom:", len(df.columns))

    print("\nNama-nama kolom:")
    print(df.columns.tolist())

    print("\nContoh 5 baris pertama:")
    print(df.head())

except FileNotFoundError:
    print("File dataset tidak ditemukan.")
    print("Periksa folder data dan nama file CSV.")
