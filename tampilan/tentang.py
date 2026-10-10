import sys
import importlib.metadata as meta
import pandas as pd
import streamlit as st

from umum import (
    LEBAR_PENUH, NAMA_FITUR,
    baca_data, tentukan_fitur, format_angka, kartu_statistik,
    header_halaman, ringkasan_kelompok,
)


def versi(paket):
    try:
        return meta.version(paket)
    except Exception:
        return "tidak terdeteksi"


def tampilkan():
    data_pemain, rata_rata = baca_data()
    fitur, sumber = tentukan_fitur(data_pemain, rata_rata)

    header_halaman(
        "Dokumentasi Proyek",
        "Tentang Aplikasi & Dokumentasi Proyek",
        "Football Player Analyzer AI adalah proyek kuliah untuk menganalisis dan "
        "mengelompokkan pemain sepak bola dari dataset FIFA 18."
    )

    # ---------- Latar belakang & tujuan ----------
    kiri, kanan = st.columns(2)
    with kiri:
        st.markdown(
            '<div class="panel"><span class="label-kecil">Latar belakang</span>'
            '<h3 style="margin-top:8px">Apa yang dilakukan aplikasi ini?</h3>'
            '<p>Aplikasi membaca data pemain FIFA 18, membersihkannya, lalu mengelompokkan pemain '
            'yang punya pola atribut mirip dengan algoritma K-Means. Hasilnya ditampilkan dalam '
            'dashboard interaktif.</p>'
            '<p style="margin-top:10px"><b>Penting:</b> dataset bersifat historis (FIFA 18, '
            'musim 2017/2018), bukan kondisi pemain terkini.</p></div>',
            unsafe_allow_html=True
        )
    with kanan:
        st.markdown(
            '<div class="panel"><span class="label-kecil">Tujuan</span>'
            '<h3 style="margin-top:8px">Fitur utama</h3><ul>'
            '<li>Eksplorasi, pencarian, dan filter data pemain (dengan ekspor CSV).</li>'
            '<li>Analisis atribut satu pemain dengan grafik radar.</li>'
            '<li>Pengelompokan pemain dengan K-Means dan visualisasi PCA.</li>'
            '<li>Evaluasi model dengan Silhouette, Davies-Bouldin, dan Elbow.</li>'
            '<li>Perbandingan dua pemain.</li></ul></div>',
            unsafe_allow_html=True
        )

    st.write("")

    # ---------- Alur kerja ----------
    st.subheader("Alur Kerja Sains Data")
    langkah = [
        ("Tahap 1", "Pengumpulan Data",
         "File data/CompleteDataset.csv dari Kaggle (FIFA 18 Complete Player Dataset), "
         "sekitar 17.981 baris dan 75 kolom menurut catatan proyek."),
        ("Tahap 2", "Preprocessing",
         "preprocessing.py membersihkan data dan menyimpan data/pemain_bersih.csv. "
         f"Pada aplikasi ini terbaca {format_angka(len(data_pemain))} pemain."),
        ("Tahap 3", "Pemodelan K-Means",
         "model_ai.py menjalankan K-Means dan menyimpan data/pemain_cluster.csv "
         "serta data/rata_rata_kelompok.csv."),
        ("Tahap 4", "Visualisasi (Streamlit)",
         "aplikasi.py dan folder tampilan/ membaca hasil di atas lalu menampilkan "
         "dashboard dengan Plotly."),
    ]
    kolom = st.columns(4)
    for i, (tahap, judul, isi) in enumerate(langkah):
        with kolom[i]:
            st.markdown(
                f'<div class="kartu"><div class="kartu-judul">{tahap}</div>'
                f'<div style="font-size:1.1rem;font-weight:700;color:#f1f5fb;margin:6px 0">{judul}</div>'
                f'<div class="kartu-ket">{isi}</div></div>',
                unsafe_allow_html=True
            )

    st.write("")

    # ---------- Informasi dataset (dihitung) ----------
    st.subheader("Informasi Dataset yang Dipakai Aplikasi")
    jumlah_kolom = len([k for k in data_pemain.columns if k != "Kategori Posisi"])
    a, b, c, d = st.columns(4)
    a.markdown(kartu_statistik("Pemain", format_angka(len(data_pemain)),
                               "Setelah preprocessing", "lime"), unsafe_allow_html=True)
    b.markdown(kartu_statistik("Kolom", str(jumlah_kolom),
                               "Pada pemain_cluster.csv", "cyan"), unsafe_allow_html=True)
    c.markdown(kartu_statistik("Fitur Model", str(len(fitur)),
                               f"Diambil dari {sumber}", "putih"), unsafe_allow_html=True)
    d.markdown(kartu_statistik("Kelompok", str(data_pemain["Kelompok"].nunique()),
                               "Hasil K-Means", "lime"), unsafe_allow_html=True)
    st.caption("Fitur: " + ", ".join(NAMA_FITUR.get(k, k) for k in fitur))

    # ---------- Hasil pengelompokan (dihitung) ----------
    st.subheader("Hasil Pengelompokan")
    ringkas = ringkasan_kelompok(data_pemain)
    tabel = pd.DataFrame([{
        "Kelompok": f"Kelompok {r['nomor']}",
        "Jumlah Pemain": format_angka(r["jumlah"]),
        "Rata-rata Overall": f"{r['rata_overall']:.1f}",
        "Atribut Menonjol": ", ".join(r["menonjol"]) or "-",
    } for r in ringkas])
    st.dataframe(tabel, hide_index=True, **LEBAR_PENUH)
    st.caption("Kelompok tidak diberi nama karangan. Maknanya dibaca dari atribut yang menonjol.")

    # ---------- Teknologi (versi asli di komputermu) ----------
    st.subheader("Teknologi yang Digunakan")
    tek = pd.DataFrame([
        {"Teknologi": "Python", "Versi": sys.version.split()[0], "Fungsi": "Bahasa pemrograman"},
        {"Teknologi": "Pandas", "Versi": versi("pandas"), "Fungsi": "Mengolah data tabel"},
        {"Teknologi": "NumPy", "Versi": versi("numpy"), "Fungsi": "Perhitungan numerik"},
        {"Teknologi": "Scikit-learn", "Versi": versi("scikit-learn"),
         "Fungsi": "K-Means, StandardScaler, PCA, metrik evaluasi"},
        {"Teknologi": "Streamlit", "Versi": versi("streamlit"), "Fungsi": "Antarmuka web"},
        {"Teknologi": "Plotly", "Versi": versi("plotly"), "Fungsi": "Grafik interaktif"},
    ])
    st.dataframe(tek, hide_index=True, **LEBAR_PENUH)

    # ---------- Batasan ----------
    st.markdown(
        '<div class="panel"><h3>Batasan yang perlu disampaikan saat presentasi</h3><ul>'
        '<li>Data historis FIFA 18, bukan statistik pemain terkini.</li>'
        '<li>Kelompok K-Means dibentuk dari kemiripan angka atribut, bukan posisi resmi.</li>'
        '<li>Atribut yang dipakai adalah atribut pemain lapangan, sehingga penjaga gawang '
        'kurang terwakili.</li>'
        '<li>PCA hanya untuk visualisasi 2D dan tidak mengubah hasil K-Means.</li>'
        '<li>Kategori Posisi di filter ditentukan dari posisi pertama pada Preferred Positions.</li>'
        '<li>Metrik evaluasi mengukur keterpisahan kelompok, bukan akurasi prediksi.</li>'
        '</ul></div>',
        unsafe_allow_html=True
    )