import streamlit as st
import plotly.express as px

from umum import (
    LEBAR_PENUH, WARNA_KELOMPOK,
    baca_data, format_angka, format_desimal, kartu_statistik, header_halaman,
    atur_grafik, hitung_distribusi_usia, html_batang_usia,
    ringkasan_kelompok, html_kartu_kelompok,
)


def tampilkan():
    data_pemain, _ = baca_data()


    header_halaman(
        "Ringkasan Dataset",
        "Football Player Analyzer AI",
        "Analisis profil pemain FIFA 18 dan pengelompokan pemain "
        "menggunakan algoritma K-Means. Data bersifat historis (FIFA 18), "
        "bukan kondisi pemain terkini."
    )

    usia = data_pemain["Age"]
    overall = data_pemain["Overall"]
    potensi = data_pemain["Potential"]
    selisih_potensi = (potensi - overall).mean()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kartu_statistik(
            "Total Pemain", format_angka(len(data_pemain)),
            f"{format_angka(data_pemain['Nationality'].nunique())} negara · "
            f"{format_angka(data_pemain['Club'].nunique())} klub",
            "putih"), unsafe_allow_html=True)
    with k2:
        st.markdown(kartu_statistik(
            "Rata-rata Usia", f"{format_desimal(usia.mean())} th",
            f"Rentang {int(usia.min())} - {int(usia.max())} tahun",
            "cyan"), unsafe_allow_html=True)
    with k3:
        st.markdown(kartu_statistik(
            "Rata-rata Overall", format_desimal(overall.mean()),
            f"Tertinggi {int(overall.max())} · Terendah {int(overall.min())}",
            "lime"), unsafe_allow_html=True)
    with k4:
        st.markdown(kartu_statistik(
            "Rata-rata Potensi", format_desimal(potensi.mean()),
            f"Rata-rata +{format_desimal(selisih_potensi)} poin di atas Overall",
            "cyan"), unsafe_allow_html=True)

    st.write("")

    kiri, kanan = st.columns(2)

    with kiri:
        jumlah_usia, persen_usia = hitung_distribusi_usia(usia)
        puncak = jumlah_usia.idxmax()
        st.markdown(
            '<div class="panel">'
            '<span class="label-kecil">Histogram data</span>'
            '<h3 style="margin-top:8px">Distribusi Usia Pemain</h3>'
            f'<p>Rentang usia terbanyak: <b>{puncak}</b> '
            f'({format_desimal(persen_usia[puncak])}% dari seluruh pemain).</p>'
            + html_batang_usia(jumlah_usia, persen_usia) +
            '</div>',
            unsafe_allow_html=True
        )

    with kanan:
        rata = overall.mean()
        simpangan = overall.std()
        kemiringan = overall.skew()
        if abs(kemiringan) < 0.5:
            ket_miring = "mendekati simetris"
        elif kemiringan > 0:
            ket_miring = "condong ke nilai rendah (ekor kanan panjang)"
        else:
            ket_miring = "condong ke nilai tinggi (ekor kiri panjang)"

        st.markdown(
            '<div class="panel">'
            '<span class="label-kecil">Distribusi nilai</span>'
            '<h3 style="margin-top:8px">Distribusi Rating Overall</h3>'
            f'<p>Rata-rata {format_desimal(rata)} · '
            f'Simpangan baku {format_desimal(simpangan)} · '
            f'Skewness {format_desimal(kemiringan, 2)} ({ket_miring}).</p>'
            '</div>',
            unsafe_allow_html=True
        )
        hist = px.histogram(
            data_pemain, x="Overall", nbins=40,
            color_discrete_sequence=["#a3e635"],
            labels={"Overall": "Overall", "count": "Jumlah Pemain"}
        )
        hist.add_vline(
            x=rata, line_dash="dash", line_color="#38bdf8",
            annotation_text=f"Rata-rata {format_desimal(rata)}",
            annotation_font_color="#38bdf8"
        )
        hist.update_layout(yaxis_title="Jumlah Pemain", bargap=0.05)
        st.plotly_chart(atur_grafik(hist, 300), **LEBAR_PENUH)

    st.write("")

    st.subheader("Ringkasan Kelompok (Hasil K-Means)")
    st.caption(
        "Kelompok dibentuk otomatis dari kemiripan atribut, bukan posisi resmi pemain. "
        "Atribut menonjol = atribut dengan rata-rata kelompok paling jauh di atas "
        "rata-rata seluruh pemain."
    )

    ringkasan = ringkasan_kelompok(data_pemain)
    kolom_kelompok = st.columns(len(ringkasan))
    for i, info in enumerate(ringkasan):
        warna = WARNA_KELOMPOK[i % len(WARNA_KELOMPOK)]
        with kolom_kelompok[i]:
            st.markdown(html_kartu_kelompok(info, warna), unsafe_allow_html=True)

    jumlah_kel = (
        data_pemain["Kelompok"].value_counts().sort_index()
        .rename_axis("Kelompok").reset_index(name="Jumlah Pemain")
    )
    jumlah_kel["Kelompok"] = "Kelompok " + jumlah_kel["Kelompok"].astype(str)
    grafik = px.bar(
        jumlah_kel, x="Kelompok", y="Jumlah Pemain", text="Jumlah Pemain",
        color="Kelompok", color_discrete_sequence=WARNA_KELOMPOK,
        title="Distribusi Pemain Berdasarkan Kelompok"
    )
    grafik.update_layout(showlegend=False)
    st.plotly_chart(atur_grafik(grafik, 340), **LEBAR_PENUH)

    st.subheader("Pemain Berperingkat Tertinggi")
    jumlah_tampil = st.slider("Jumlah pemain yang ditampilkan", 5, 20, 10)
    st.caption(
        "Kriteria: diurutkan dari Overall tertinggi. Jika Overall sama, "
        "diurutkan dari Potential tertinggi, lalu nama (A-Z)."
    )

    unggulan = (
        data_pemain
        .sort_values(["Overall", "Potential", "Name"], ascending=[False, False, True])
        .head(jumlah_tampil)
        .copy()
    )
    unggulan["Kelompok"] = "Kelompok " + unggulan["Kelompok"].astype(str)
    tabel = unggulan[["Name", "Preferred Positions", "Club", "Nationality",
                      "Age", "Kelompok", "Overall", "Potential"]].rename(columns={
        "Name": "Pemain", "Preferred Positions": "Posisi", "Club": "Klub",
        "Nationality": "Kebangsaan", "Age": "Usia",
    })
    st.dataframe(
        tabel, hide_index=True, **LEBAR_PENUH,
        column_config={
            "Overall": st.column_config.ProgressColumn(
                "Overall", min_value=0, max_value=100, format="%d"),
            "Potential": st.column_config.ProgressColumn(
                "Potential", min_value=0, max_value=100, format="%d"),
        }
    )

    with st.expander("Lihat Tabel Data Pemain"):
        st.dataframe(data_pemain, hide_index=True, **LEBAR_PENUH)