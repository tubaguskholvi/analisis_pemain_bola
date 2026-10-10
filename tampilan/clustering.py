import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from umum import (
    LEBAR_PENUH, WARNA_KELOMPOK, NAMA_FITUR,
    baca_data, hitung_pca, tentukan_fitur, format_angka, format_desimal,
    header_halaman, atur_grafik, ringkasan_kelompok, html_kartu_kelompok,
)


def tampilkan():
    data_pemain, rata_rata = baca_data()

    header_halaman(
        "Unsupervised Learning",
        "AI Clustering dengan K-Means",
        "K-Means mengelompokkan pemain berdasarkan kemiripan angka atribut, "
        "tanpa label posisi. Hasilnya dibaca dari data, bukan dari nama karangan."
    )

    fitur, sumber = tentukan_fitur(data_pemain, rata_rata)
    jumlah_k = data_pemain["Kelompok"].nunique()
    nomor_kelompok = sorted(data_pemain["Kelompok"].unique())
    warna = {int(n): WARNA_KELOMPOK[i % len(WARNA_KELOMPOK)] for i, n in enumerate(nomor_kelompok)}

    st.markdown(
        '<div class="panel"><h3>Cara kerja K-Means (bahasa sederhana)</h3>'
        '<ul>'
        f'<li>Pilih jumlah kelompok K. Pada proyek ini <b>K = {jumlah_k}</b>.</li>'
        '<li>Setiap pemain dimasukkan ke kelompok yang pusatnya (centroid) paling dekat '
        'dengan angka atributnya.</li>'
        '<li>Pusat tiap kelompok dihitung ulang dari rata-rata anggotanya.</li>'
        '<li>Langkah 2-3 diulang sampai pusat kelompok tidak banyak berubah.</li>'
        '</ul></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="catatan">Nomor kelompok hanya penanda. Kelompok 0 tidak berarti '
        '"terbaik" atau posisi tertentu. Maknanya dibaca dari rata-rata atribut di bawah.</div>',
        unsafe_allow_html=True
    )

    # ---------- Kartu kelompok ----------
    ringkasan = ringkasan_kelompok(data_pemain)
    kolom = st.columns(len(ringkasan))
    for i, info in enumerate(ringkasan):
        with kolom[i]:
            st.markdown(html_kartu_kelompok(info, warna[info["nomor"]]), unsafe_allow_html=True)

    st.write("")

    # ---------- Proyeksi PCA ----------
    nilai_fitur = data_pemain[fitur].fillna(data_pemain[fitur].median())
    koordinat, varians = hitung_pca(nilai_fitur)

    plot = pd.DataFrame({
        "PC1": koordinat[:, 0], "PC2": koordinat[:, 1],
        "Pemain": data_pemain["Name"].values,
        "Overall": data_pemain["Overall"].values,
        "Kelompok": data_pemain["Kelompok"].astype(int).values,
    })
    plot["Label"] = "Kelompok " + plot["Kelompok"].astype(str)
    urutan_label = [f"Kelompok {int(n)}" for n in nomor_kelompok]
    peta_warna = {f"Kelompok {n}": w for n, w in warna.items()}

    sampel = plot.sample(min(4000, len(plot)), random_state=42)
    gambar = px.scatter(
        sampel, x="PC1", y="PC2", color="Label",
        color_discrete_map=peta_warna, category_orders={"Label": urutan_label},
        hover_data={"Pemain": True, "Overall": True, "PC1": False, "PC2": False, "Label": False},
        opacity=0.6,
        title="Proyeksi 2D (PCA) hasil pengelompokan"
    )
    gambar.update_traces(marker=dict(size=5))   # titik pemain diperkecil

    pusat = plot.groupby("Kelompok")[["PC1", "PC2"]].mean()
    gambar.add_trace(go.Scatter(
        x=pusat["PC1"], y=pusat["PC2"], mode="markers+text",
        text=[f"K{int(n)}" for n in pusat.index], textposition="top center",
        marker=dict(symbol="star", size=18, color=[warna[int(n)] for n in pusat.index],
                    line=dict(color="white", width=1.5)),
        name="Pusat kelompok"
    ))
    gambar.update_layout(
        xaxis_title=f"PC1 ({format_desimal(varians[0] * 100)}% varians)",
        yaxis_title=f"PC2 ({format_desimal(varians[1] * 100)}% varians)",
    )
    st.plotly_chart(atur_grafik(gambar, 520), **LEBAR_PENUH)
    st.caption(
        f"PCA meringkas {len(fitur)} fitur menjadi 2 sumbu hanya untuk visualisasi. "
        f"Dua sumbu ini menjelaskan {format_desimal(sum(varians) * 100)}% variasi data, "
        f"jadi sebagian informasi tidak terlihat. Titik yang ditampilkan: sampel "
        f"{format_angka(len(sampel))} dari {format_angka(len(plot))} pemain. "
        "Kelompok sendiri ditentukan oleh model K-Means, bukan oleh PCA."
    )

    # ---------- Profil kelompok ----------
    rata_global = data_pemain[fitur].mean()
    rata_kel = data_pemain.groupby("Kelompok")[fitur].mean()

    st.subheader("Tabel Profil Kelompok")
    st.caption("Rata-rata nilai asli (skala data) per kelompok, dihitung dari pemain_cluster.csv.")
    tabel_profil = rata_kel.round(1).rename(columns=NAMA_FITUR)
    tabel_profil.insert(0, "Jumlah Pemain", data_pemain["Kelompok"].value_counts().sort_index())
    tabel_profil.index = [f"Kelompok {int(n)}" for n in tabel_profil.index]
    tabel_profil.index.name = "Kelompok"
    st.dataframe(tabel_profil.reset_index(), hide_index=True, **LEBAR_PENUH)

    selisih = (rata_kel - rata_global)
    selisih.index = [f"Kelompok {int(n)}" for n in selisih.index]
    selisih = selisih.rename(columns=NAMA_FITUR)
    heat = px.imshow(
        selisih.round(1), text_auto=".1f", aspect="auto",
        color_continuous_scale=[[0, "#fb923c"], [0.5, "#131c31"], [1, "#a3e635"]],
        color_continuous_midpoint=0,
        title="Selisih rata-rata kelompok terhadap rata-rata semua pemain "
              "(hijau = di atas, oranye = di bawah)"
    )
    st.plotly_chart(atur_grafik(heat, 360), **LEBAR_PENUH)

    # ---------- Komposisi posisi ----------
    st.subheader("Komposisi Kategori Posisi per Kelompok")
    st.caption("Bukti tambahan: seberapa banyak tiap kategori posisi muncul di dalam kelompok (persen per baris).")
    komposisi = pd.crosstab(data_pemain["Kelompok"], data_pemain["Kategori Posisi"],
                            normalize="index") * 100
    komposisi.index = [f"Kelompok {int(n)}" for n in komposisi.index]
    komposisi.index.name = "Kelompok"
    tampil = komposisi.round(1).astype(str) + "%"
    st.dataframe(tampil.reset_index(), hide_index=True, **LEBAR_PENUH)

    # ---------- Interpretasi hati-hati ----------
    st.subheader("Interpretasi Singkat (otomatis dari data)")
    baris = ""
    for n in nomor_kelompok:
        n = int(n)
        sel = (rata_kel.loc[n] - rata_global).sort_values(ascending=False)
        tinggi = [NAMA_FITUR.get(k, k) for k, v in sel.head(3).items() if v > 0]
        rendah = [NAMA_FITUR.get(k, k) for k, v in sel.tail(3).items() if v < 0]
        dominan = komposisi.loc[f"Kelompok {n}"].idxmax()
        persen_dominan = komposisi.loc[f"Kelompok {n}", dominan]
        baris += (
            f'<li><b>Kelompok {n}</b> ({format_angka((data_pemain["Kelompok"] == n).sum())} pemain): '
            f'relatif tinggi pada {", ".join(tinggi) or "-"}; '
            f'relatif rendah pada {", ".join(rendah) or "-"}. '
            f'Kategori posisi terbanyak: {dominan} ({format_desimal(persen_dominan)}%).</li>'
        )
    st.markdown(
        f'<div class="panel"><ul>{baris}</ul></div>'
        '<div class="catatan">Interpretasi ini hanya ringkasan statistik. Kelompok bukan posisi '
        'resmi dan tidak menilai kualitas pemain secara mutlak.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="catatan"><b>Fitur yang dipakai untuk tabel & PCA:</b> '
        f'{", ".join(NAMA_FITUR.get(k, k) for k in fitur)} (diambil dari {sumber}). '
        'Pastikan daftar ini sama dengan fitur di model_ai.py. '
        'Metrik evaluasi model (Silhouette dll.) ditampilkan di Tahap 7 setelah benar-benar dihitung.</div>',
        unsafe_allow_html=True
    )