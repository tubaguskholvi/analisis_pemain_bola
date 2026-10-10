import streamlit as st

# set_page_config harus menjadi perintah Streamlit pertama
st.set_page_config(
    page_title="PlayerAnalyzer - AI Scout Suite",
    page_icon="⚽",
    layout="wide"
)

from umum import KOLOM_WAJIB, pasang_css, baca_data, format_angka
from tampilan import (
    dashboard, eksplorasi, analisis, clustering,
    evaluasi, perbandingan, tentang,
)

pasang_css()

# ---------- Membaca data + pemeriksaan kolom ----------
try:
    data_pemain, rata_rata = baca_data()
except FileNotFoundError as galat:
    st.error(f"File data tidak ditemukan: {galat}")
    st.info("Pastikan perintah dijalankan dari folder proyek dan folder `data` berisi file CSV.")
    st.stop()

kolom_hilang = [k for k in KOLOM_WAJIB if k not in data_pemain.columns]
if kolom_hilang:
    st.error("Kolom berikut tidak ditemukan di `data/pemain_cluster.csv`:")
    st.code(", ".join(kolom_hilang))
    st.write("Kolom yang tersedia di file:")
    st.code(", ".join(data_pemain.columns))
    st.stop()

# ---------- Sidebar navigasi ----------
MENU = [
    " Dashboard",
    "Eksplorasi Dataset",
    " Analisis Pemain",
    " AI Clustering",
    " Evaluasi Model",
    " Perbandingan Pemain",
    " Tentang Aplikasi",
]

with st.sidebar:
    st.markdown(
        '<div class="brand">'
        '<span class="brand-nama">⚽ PlayerAnalyzer</span>'
        '<span class="brand-sub">AI SCOUT SUITE</span>'
        '</div>'
        '<span class="lencana-kecil">FIFA 18 Academic</span>',
        unsafe_allow_html=True
    )

    pilihan = st.radio("Menu", MENU, label_visibility="collapsed")

    st.markdown(
        f'<div class="kotak-dataset">'
        f'<span class="titik"></span><b>Dataset FIFA 18</b><br>'
        f'{format_angka(len(data_pemain))} profil pemain'
        f'</div>',
        unsafe_allow_html=True
    )

halaman = pilihan.split(" ", 1)[1]

# ---------- Menampilkan halaman yang dipilih ----------
if halaman == "Dashboard":
    dashboard.tampilkan()
elif halaman == "Eksplorasi Dataset":
    eksplorasi.tampilkan()
elif halaman == "Analisis Pemain":
    analisis.tampilkan()
elif halaman == "AI Clustering":
    clustering.tampilkan()
elif halaman == "Evaluasi Model":
    evaluasi.tampilkan()
elif halaman == "Perbandingan Pemain":
    perbandingan.tampilkan()
else:
    tentang.tampilkan()