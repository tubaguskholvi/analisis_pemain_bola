import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from umum import (
    LEBAR_PENUH, NAMA_FITUR,
    baca_data, tentukan_fitur, format_angka, format_desimal,
    kartu_statistik, header_halaman, atur_grafik,
)

UKURAN_SAMPEL = 5000

CSS_HALAMAN = """
<style>
.rentang {
    background:#131c31; border:1px solid #1f2b45; border-radius:14px;
    padding:14px 16px; height:100%;
}
.rentang.aktif {border:1px solid #a3e635; background:#17233a;}
.rentang-angka {font-size:.8rem; color:#8a97b3;}
.rentang-judul {font-weight:700; color:#f1f5fb; margin:4px 0;}
.rentang-isi {font-size:.82rem; color:#9fb0cf;}
.rentang-tag {display:inline-block; margin-top:8px; padding:2px 10px; border-radius:6px;
              background:#a3e635; color:#04111f; font-size:.72rem; font-weight:700;}
</style>
"""

RENTANG = [
    ("0,71 - 1,00", "Struktur Sangat Kuat",
     "Kelompok terpisah sangat jelas dan jarang terjadi pada data nyata.", 0.71),
    ("0,51 - 0,70", "Struktur Wajar & Kuat",
     "Kelompok cukup terpisah dengan sedikit tumpang tindih.", 0.51),
    ("0,26 - 0,50", "Struktur Lemah",
     "Banyak pemain berada di perbatasan antar kelompok.", 0.26),
    ("0,25 ke bawah", "Struktur Tidak Nyata",
     "Kelompok hampir tidak berbeda satu sama lain.", -1.0),
]


def indeks_rentang(skor):
    for i, (_, _, _, batas) in enumerate(RENTANG):
        if skor >= batas:
            return i
    return len(RENTANG) - 1


@st.cache_data(show_spinner=False)
def hitung_sapuan_k(nilai, k_awal=2, k_akhir=6):
    """Menjalankan K-Means untuk beberapa nilai K lalu menghitung metrik evaluasi."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score, davies_bouldin_score
    from sklearn.preprocessing import StandardScaler

    X = StandardScaler().fit_transform(nilai)
    hasil = []
    for k in range(k_awal, k_akhir + 1):
        model = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
        sil = silhouette_score(X, model.labels_,
                               sample_size=min(UKURAN_SAMPEL, len(X)), random_state=42)
        dbi = davies_bouldin_score(X, model.labels_)
        hasil.append({"K": k, "Silhouette": sil, "Inersia": model.inertia_,
                      "Davies-Bouldin": dbi})
    return pd.DataFrame(hasil)


@st.cache_data(show_spinner=False)
def hitung_label_tersimpan(nilai, label):
    """Menghitung metrik untuk pengelompokan yang tersimpan di pemain_cluster.csv."""
    import numpy as np
    from sklearn.metrics import silhouette_score, davies_bouldin_score
    from sklearn.preprocessing import StandardScaler

    X = StandardScaler().fit_transform(nilai)
    label = np.asarray(label)
    sil = silhouette_score(X, label, sample_size=min(UKURAN_SAMPEL, len(X)), random_state=42)
    dbi = davies_bouldin_score(X, label)
    inersia = 0.0
    for k in np.unique(label):
        titik = X[label == k]
        inersia += ((titik - titik.mean(axis=0)) ** 2).sum()
    return sil, dbi, inersia


def tampilkan():
    data_pemain, rata_rata = baca_data()
    st.markdown(CSS_HALAMAN, unsafe_allow_html=True)

    header_halaman(
        "Validasi Algoritma",
        "Evaluasi Model K-Means",
        "Kualitas pengelompokan diukur dengan Silhouette Score, Davies-Bouldin Index, "
        "dan inersia (metode Elbow). Semua angka dihitung dari datamu, bukan angka contoh."
    )

    fitur, sumber = tentukan_fitur(data_pemain, rata_rata)
    nilai = data_pemain[fitur].fillna(data_pemain[fitur].median())
    k_dipakai = int(data_pemain["Kelompok"].nunique())

    with st.spinner("Menghitung metrik evaluasi (hanya sekali, hasilnya disimpan)..."):
        tabel = hitung_sapuan_k(nilai)
        sil, dbi, inersia = hitung_label_tersimpan(nilai, data_pemain["Kelompok"].values)

    # ---------- Ringkasan model yang dipakai ----------
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kartu_statistik(
            "Silhouette Score", format_desimal(sil, 3),
            f"Sampel {format_angka(min(UKURAN_SAMPEL, len(nilai)))} pemain", "lime"),
            unsafe_allow_html=True)
    with k2:
        st.markdown(kartu_statistik(
            "Davies-Bouldin Index", format_desimal(dbi, 3),
            "Makin kecil makin baik", "cyan"), unsafe_allow_html=True)
    with k3:
        st.markdown(kartu_statistik(
            "Inersia (WCSS)", format_angka(inersia),
            "Pada data yang distandarkan", "putih"), unsafe_allow_html=True)
    with k4:
        st.markdown(kartu_statistik(
            "Jumlah Kelompok (K)", str(k_dipakai),
            "Dibaca dari pemain_cluster.csv", "putih"), unsafe_allow_html=True)

    st.markdown(
        '<div class="catatan"><b>Cara perhitungan:</b> fitur = '
        f'{", ".join(NAMA_FITUR.get(k, k) for k in fitur)} (dari {sumber}), '
        'distandarkan dengan StandardScaler, lalu metrik dihitung dari kelompok yang tersimpan '
        'di pemain_cluster.csv. Angka ini bisa berbeda dari catatan awalmu (sekitar 0,211) '
        'jika fitur, skala, atau sampel di model_ai.py tidak sama persis. '
        'Silhouette dihitung pada sampel acak agar cepat.</div>',
        unsafe_allow_html=True
    )

    # ---------- Posisi dalam panduan rentang ----------
    st.subheader("Panduan Membaca Silhouette Score")
    st.caption("Silhouette berkisar -1 sampai +1. Makin mendekati +1, makin jelas pemisahan antar kelompok. "
               "Rentang di bawah adalah pedoman umum, bukan aturan mutlak.")
    aktif = indeks_rentang(sil)
    kolom = st.columns(4)
    for i, (angka, judul, isi, _) in enumerate(RENTANG):
        tag = '<span class="rentang-tag">Model proyek ini</span>' if i == aktif else ""
        kelas = "rentang aktif" if i == aktif else "rentang"
        with kolom[i]:
            st.markdown(
                f'<div class="{kelas}"><div class="rentang-angka">{angka}</div>'
                f'<div class="rentang-judul">{judul}</div>'
                f'<div class="rentang-isi">{isi}</div>{tag}</div>',
                unsafe_allow_html=True
            )

    st.write("")

    # ---------- Grafik Silhouette dan Elbow ----------
    kiri, kanan = st.columns(2)
    sorot = tabel[tabel["K"] == k_dipakai]

    with kiri:
        g1 = go.Figure()
        g1.add_trace(go.Scatter(
            x=tabel["K"], y=tabel["Silhouette"], mode="lines+markers+text",
            text=[format_desimal(v, 3) for v in tabel["Silhouette"]],
            textposition="top center", line=dict(color="#38bdf8", width=3),
            name="Silhouette"))
        if not sorot.empty:
            g1.add_trace(go.Scatter(
                x=sorot["K"], y=sorot["Silhouette"], mode="markers",
                marker=dict(size=16, color="#a3e635", symbol="star"),
                name=f"K dipakai ({k_dipakai})"))
        g1.update_layout(title="Silhouette Score per K (makin tinggi makin baik)",
                         xaxis_title="Jumlah kelompok (K)", yaxis_title="Silhouette",
                         xaxis=dict(dtick=1))
        st.plotly_chart(atur_grafik(g1, 380), **LEBAR_PENUH)

    with kanan:
        g2 = go.Figure()
        g2.add_trace(go.Scatter(
            x=tabel["K"], y=tabel["Inersia"], mode="lines+markers",
            line=dict(color="#38bdf8", width=3), name="Inersia"))
        if not sorot.empty:
            g2.add_trace(go.Scatter(
                x=sorot["K"], y=sorot["Inersia"], mode="markers",
                marker=dict(size=16, color="#a3e635", symbol="star"),
                name=f"K dipakai ({k_dipakai})"))
        g2.update_layout(title="Metode Elbow: inersia per K",
                         xaxis_title="Jumlah kelompok (K)", yaxis_title="Inersia (WCSS)",
                         xaxis=dict(dtick=1))
        st.plotly_chart(atur_grafik(g2, 380), **LEBAR_PENUH)

    st.caption("Inersia selalu turun saat K bertambah. Pada metode Elbow, K dipilih di titik siku, "
               "yaitu saat penurunannya mulai melandai. Titik siku dinilai dengan mata, "
               "tidak ditentukan otomatis di sini.")

    # ---------- Tabel perbandingan ----------
    st.subheader("Tabel Perbandingan K = 2 sampai 6")
    k_sil_terbaik = int(tabel.loc[tabel["Silhouette"].idxmax(), "K"])
    k_dbi_terbaik = int(tabel.loc[tabel["Davies-Bouldin"].idxmin(), "K"])

    baris = []
    for _, r in tabel.iterrows():
        k = int(r["K"])
        catatan = []
        if k == k_sil_terbaik:
            catatan.append("Silhouette tertinggi")
        if k == k_dbi_terbaik:
            catatan.append("Davies-Bouldin terendah")
        if k == k_dipakai:
            catatan.append("K yang dipakai")
        baris.append({
            "K": k,
            "Silhouette": format_desimal(r["Silhouette"], 3),
            "Inersia (WCSS)": format_angka(r["Inersia"]),
            "Davies-Bouldin": format_desimal(r["Davies-Bouldin"], 3),
            "Keterangan": " · ".join(catatan) if catatan else "-",
        })
    st.dataframe(pd.DataFrame(baris), hide_index=True, **LEBAR_PENUH)

    # ---------- Kesimpulan otomatis ----------
    kalimat = (
        f"Dari K = 2 sampai 6, Silhouette tertinggi ada pada K = {k_sil_terbaik} "
        f"({format_desimal(tabel['Silhouette'].max(), 3)}) dan Davies-Bouldin terendah pada "
        f"K = {k_dbi_terbaik} ({format_desimal(tabel['Davies-Bouldin'].min(), 3)}). "
        f"Proyek ini memakai K = {k_dipakai}."
    )
    if k_dipakai != k_sil_terbaik:
        kalimat += (" K yang dipakai berbeda dari K dengan Silhouette tertinggi. "
                    "Itu boleh saja jika kamu punya alasan lain (misalnya mudah ditafsirkan), "
                    "dan alasannya sebaiknya kamu siapkan untuk presentasi.")
    kalimat += (f" Silhouette model proyek ({format_desimal(sil, 3)}) termasuk kategori "
                f"\"{RENTANG[aktif][1]}\". Metrik ini tidak membuktikan kelompok sesuai posisi "
                "sebenarnya, hanya mengukur seberapa terpisah kelompok pada angka atribut.")
    st.markdown(f'<div class="panel"><h3>Kesimpulan (otomatis dari angka)</h3><p>{kalimat}</p></div>',
                unsafe_allow_html=True)

    with st.expander("Penjelasan singkat tiap metrik"):
        st.markdown(
            "- **Silhouette Score**: untuk tiap pemain, bandingkan jarak rata-rata ke pemain "
            "sekelompok dengan jarak ke kelompok terdekat lain. Rata-ratanya adalah skor akhir.\n"
            "- **Davies-Bouldin Index**: rata-rata kemiripan tiap kelompok dengan kelompok yang "
            "paling mirip dengannya. Makin kecil makin baik.\n"
            "- **Inersia (WCSS)**: jumlah kuadrat jarak pemain ke pusat kelompoknya. "
            "Dipakai pada metode Elbow."
        )