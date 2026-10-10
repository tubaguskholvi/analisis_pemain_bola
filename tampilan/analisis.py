import html
import streamlit as st
import plotly.graph_objects as go

from umum import (
    LEBAR_PENUH, KOLOM_KEMAMPUAN,
    baca_data, buat_label_pemain, format_desimal, aman, inisial,
    header_halaman, atur_grafik, html_kartu_atribut,
)


def grafik_radar(pemain, rata_kelompok, nomor):
    label = list(KOLOM_KEMAMPUAN.values())
    nilai = [float(pemain[k]) for k in KOLOM_KEMAMPUAN]
    pembanding = [float(rata_kelompok[k]) for k in KOLOM_KEMAMPUAN]

    gambar = go.Figure()
    gambar.add_trace(go.Scatterpolar(
        r=pembanding + [pembanding[0]], theta=label + [label[0]],
        fill="toself", name=f"Rata-rata Kelompok {nomor}",
        line=dict(color="#38bdf8", width=2),
        fillcolor="rgba(56,189,248,0.15)",
    ))
    gambar.add_trace(go.Scatterpolar(
        r=nilai + [nilai[0]], theta=label + [label[0]],
        fill="toself", name=str(pemain["Name"]),
        line=dict(color="#a3e635", width=3),
        fillcolor="rgba(163,230,53,0.25)",
    ))
    gambar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], gridcolor="#1f2b45", linecolor="#1f2b45"),
            angularaxis=dict(gridcolor="#1f2b45", linecolor="#1f2b45"),
        ),
        legend=dict(orientation="h", y=-0.12),
    )
    return atur_grafik(gambar, 460)


def tampilkan():
    data_pemain, _ = baca_data()

    header_halaman(
        "Modul Analisis Individual",
        "Analisis Mendalam Profil & Atribut Pemain",
        "Pilih pemain (boleh ketik untuk mencari) untuk melihat profil dan "
        "radar atribut berdasarkan data FIFA 18."
    )

    urutan = (data_pemain
              .sort_values(["Overall", "Potential", "Name"], ascending=[False, False, True])
              .index.tolist())
    label_pemain = buat_label_pemain(
        data_pemain["Name"], data_pemain["Club"], data_pemain["Overall"])

    indeks = st.selectbox("Pilih pemain", urutan, format_func=lambda i: label_pemain[i])
    pemain = data_pemain.loc[indeks]
    nomor = int(pemain["Kelompok"])
    atribut = list(KOLOM_KEMAMPUAN.keys())

    # ---------- Kartu profil ----------
    badge_posisi = "".join(
        f'<span class="badge-pos">{html.escape(p)}</span>'
        for p in str(pemain["Preferred Positions"]).split()
    )
    st.markdown(
        '<div class="profil">'
        f'<div class="avatar">{html.escape(inisial(pemain["Name"]))}</div>'
        '<div class="profil-info">'
        f'<div class="profil-nama">{aman(pemain["Name"])}</div>'
        f'<div class="profil-meta">🏟️ {aman(pemain["Club"])} · '
        f'🌍 {aman(pemain["Nationality"])} · 🎂 {int(pemain["Age"])} tahun</div>'
        f'<div>{badge_posisi}<span class="badge-kel">Kelompok {nomor}</span></div>'
        '</div>'
        '<div class="rating">'
        '<div class="rating-label">Overall</div>'
        f'<div class="rating-angka">{int(pemain["Overall"])}</div>'
        f'<div class="rating-pot">Potential {int(pemain["Potential"])}</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.write("")

    # ---------- Perhitungan untuk radar & ringkasan ----------
    rata_kel = data_pemain[data_pemain["Kelompok"] == nomor][atribut].mean()
    persentil = {k: (data_pemain[k] < float(pemain[k])).mean() * 100 for k in atribut}
    nilai_atribut = {k: float(pemain[k]) for k in atribut}
    urut_nilai = sorted(nilai_atribut, key=nilai_atribut.get, reverse=True)
    kuat = urut_nilai[:3]
    lemah = urut_nilai[-3:][::-1]
    selisih_kel = {k: nilai_atribut[k] - float(rata_kel[k]) for k in atribut}
    di_atas = [k for k in sorted(selisih_kel, key=selisih_kel.get, reverse=True)[:3] if selisih_kel[k] > 0]
    di_bawah = [k for k in sorted(selisih_kel, key=selisih_kel.get)[:3] if selisih_kel[k] < 0]
    jarak_potensi = int(pemain["Potential"]) - int(pemain["Overall"])

    def teks_atribut(daftar):
        return ", ".join(
            f"{KOLOM_KEMAMPUAN[k]} ({int(nilai_atribut[k])})" for k in daftar)

    def teks_selisih(daftar):
        return ", ".join(
            f"{KOLOM_KEMAMPUAN[k]} ({'+' if selisih_kel[k] > 0 else ''}{format_desimal(selisih_kel[k])})"
            for k in daftar) or "tidak ada"

    kiri, kanan = st.columns([3, 2])

    with kiri:
        st.markdown(
            '<div class="panel"><span class="label-kecil">Radar atribut</span>'
            '<h3 style="margin-top:8px">Radar Karakteristik Atribut</h3>'
            f'<p>Hijau = pemain ini, biru = rata-rata Kelompok {nomor}. '
            'Skala 0 - 100.</p></div>',
            unsafe_allow_html=True
        )
        st.plotly_chart(grafik_radar(pemain, rata_kel, nomor), **LEBAR_PENUH)

    with kanan:
        if jarak_potensi > 0:
            ket_potensi = (f"Potential {int(pemain['Potential'])} berada {jarak_potensi} poin di atas "
                           "Overall, artinya data FIFA 18 memperkirakan masih ada ruang berkembang.")
        else:
            ket_potensi = "Overall sudah sama dengan Potential pada data FIFA 18."
        st.markdown(
            '<div class="panel"><span class="label-kecil">Ringkasan otomatis</span>'
            '<h3 style="margin-top:8px">Ringkasan Berdasarkan Data</h3>'
            '<ul>'
            f'<li><b>Atribut tertinggi:</b> {teks_atribut(kuat)}</li>'
            f'<li><b>Atribut terendah:</b> {teks_atribut(lemah)}</li>'
            f'<li><b>Dibanding rata-rata Kelompok {nomor}:</b> lebih tinggi pada '
            f'{teks_selisih(di_atas)}; lebih rendah pada {teks_selisih(di_bawah)}.</li>'
            f'<li><b>Potensi:</b> {ket_potensi}</li>'
            '</ul></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="catatan">Kelompok {nomor} adalah hasil K-Means berdasarkan '
            'kemiripan angka atribut, bukan posisi resmi pemain.</div>',
            unsafe_allow_html=True
        )
        if pemain["Kategori Posisi"] == "Penjaga Gawang":
            st.markdown(
                '<div class="catatan">Atribut yang tersedia adalah atribut pemain lapangan, '
                'sehingga kurang menggambarkan kemampuan penjaga gawang.</div>',
                unsafe_allow_html=True
            )

    # ---------- Kartu 9 atribut ----------
    st.subheader("Dekomposisi Atribut FIFA 18")
    st.caption("Persentil dihitung terhadap seluruh pemain pada dataset yang dipakai aplikasi ini.")
    kolom_atribut = st.columns(3)
    for i, k in enumerate(atribut):
        with kolom_atribut[i % 3]:
            st.markdown(
                html_kartu_atribut(KOLOM_KEMAMPUAN[k], nilai_atribut[k], persentil[k]),
                unsafe_allow_html=True
            )