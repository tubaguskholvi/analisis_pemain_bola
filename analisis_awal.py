
import pandas as pd

file_path = "data/CompleteDataset.csv"

df = pd.read_csv(file_path, low_memory=False)

print("=== INFORMASI DATASET ===")
print("Jumlah baris:", len(df))
print("Jumlah kolom:", len(df.columns))

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

print("\n=== TIPE DATA FITUR ===")
print(df[fitur].dtypes)

print("\n=== JUMLAH DATA KOSONG ===")
print(df[fitur].isnull().sum())

print("\n=== CONTOH DATA ===")
print(df[fitur].head())

print("\n=== JUMLAH PEMAIN UNIK ===")
print(df["Name"].nunique())
