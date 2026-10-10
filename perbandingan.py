import html
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from umum import (
    LEBAR_PENUH, KOLOM_KEMAMPUAN,
    baca_data, buat_label_pemain, format_desimal, aman, inisial,
    header_halaman, atur_grafik,
)

WARNA_A = "#a3e635"
WARNA_B = "#38bdf8"


def html_kartu(pemain, warna, peran):
    badge = "".join(
        f'<span class="badge-pos">{html.escape(p)}</span>'
        for p in str(pemain["Preferred Positions"]).split()
    )
    return (
        f'<div class="profil" style="border-left:4px solid {warna}">'
        f'<div class="avatar" style="border-color:{warna};color:{warna}">'
        f'{html.escape(inisial(pemain["Name"]))}</div>'
        '<div class="profil-info">'
        f'<div class="rating-label" style="color:{warna}">{peran}</div>'
        f'<div class="profil-nama">{aman(pemain["Name"])}</div>'
        f'<div class="profil-meta">🏟️ {aman(pemain["Club"])} · 🌍 {aman(pemain["Nationality"])} '
        f'· 🎂 {int(pemain["Age"])} tahun</div>'
        f'<div>{badge}<span class="badge-kel">Kelompok {int(pemain["Kelompok"])}</span></div>'
        '</div>'
        '<div class="rating">'
        '<div class="rating-label">Overall</div>'
        f'<div class="rating-angka" style="color:{warna}">{int(pemain["Overall"])}</div>'
        f'<div class="rating-pot">Potential {int(pemain["Potential"])}</div>'
        '</div></div>'
    )


def tampilkan():
    data_pemain, _ = baca_data()

    header_halaman(
        "Duel Atribut",
        "Perbandingan Dua Pemain",
        "Pilih dua pemain untuk membandingkan atribut yang tersedia di dataset FIFA 18 "
        "(data historis, bukan kondisi pemain terkini)."
    )

    urutan = (data_pemain
              .sort_values(["Overall", "Potential", "Name"], ascending=[False, False, True])
              .index.tolist())
    label = buat_label_pemain(data_pemain["Name"], data_pemain["Club"], data_pemain["Overall"])

    c1, c2 = st.columns(2)
    ia = c1.selectbox("Pemain A (hijau)", urutan, index=0,
                      format_func=lambda i: label[i], key="banding_a")
    ib = c2.selectbox("Pemain B (biru)", urutan, index=1,
                      format_func=lambda i: label[i], key="banding_b")

    if ia == ib:
        st.warning("Pilih dua pemain yang berbeda.")
        return

    a, b = data_pemain.loc[ia], data_pemain.loc[ib]
    nama_a, nama_b = str(a["Name"]), str(b["Name"])

    k1, k2 = st.columns(2)
    k1.markdown(html_kartu(a, WARNA_A, "Pemain A"), unsafe_allow_html=True)
    k2.markdown(html_kartu(b, WARNA_B, "Pemain B"), unsafe_allow_html=True)
    st.write("")

    atribut = list(KOLOM_KEMAMPUAN.keys())
    nama_id = list(KOLOM_KEMAMPUAN.values())
    nilai_a = [float(a[k]) for k in atribut]
    nilai_b = [float(b[k]) for k in atribut]

    kiri, kanan = st.columns(2)

    # ---------- Radar ----------
    with kiri:
        radar = go.Figure()
        for nilai, nama, warna, isi in [
            (nilai_a, f"{nama_a} (A)", WARNA_A, "rgba(163,230,53,0.20)"),
            (nilai_b, f"{nama_b} (B)", WARNA_B, "rgba(56,189,248,0.20)"),
        ]:
            radar.add_trace(go.Scatterpolar(
                r=nilai + [nilai[0]], theta=nama_id + [nama_id[0]],
                fill="toself", name=nama, line=dict(color=warna, width=3), fillcolor=isi))
        radar.update_layout(
            title="Radar 9 atribut (skala 0 - 100)",
            polar=dict(bgcolor="rgba(0,0,0,0)",
                       radialaxis=dict(range=[0, 100], gridcolor="#1f2b45", linecolor="#1f2b45"),
                       angularaxis=dict(gridcolor="#1f2b45", linecolor="#1f2b45")),
            legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(atur_grafik(radar, 480), **LEBAR_PENUH)

    # ---------- Batang berdampingan ----------
    with kanan:
        batang = go.Figure()
        batang.add_trace(go.Bar(y=nama_id, x=nilai_a, orientation="h", name=f"{nama_a} (A)",
                                marker_color=WARNA_A, text=[int(v) for v in nilai_a]))
        batang.add_trace(go.Bar(y=nama_id, x=nilai_b, orientation="h", name=f"{nama_b} (B)",
                                marker_color=WARNA_B, text=[int(v) for v in nilai_b]))
        batang.update_layout(title="Nilai per atribut", barmode="group",
                             xaxis=dict(range=[0, 100]),
                             yaxis=dict(autorange="reversed"),
                             legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(atur_grafik(batang, 480), **LEBAR_PENUH)

    # ---------- Tabel selisih ----------
    selisih = {k: float(a[k]) - float(b[k]) for k in atribut}
    baris = []
    for k in atribut:
        s = selisih[k]
        unggul = nama_a if s > 0 else (nama_b if s < 0 else "Seimbang")
        baris.append({
            "Atribut": KOLOM_KEMAMPUAN[k],
            nama_a + " (A)": int(a[k]),
            nama_b + " (B)": int(b[k]),
            "Selisih (A - B)": int(s),
            "Unggul": unggul,
        })
    tabel = pd.DataFrame(baris)
    st.subheader("Tabel Perbandingan Atribut")
    st.dataframe(tabel, hide_index=True, **LEBAR_PENUH)

    # ---------- Kesimpulan otomatis ----------
    rata_a, rata_b = sum(nilai_a) / len(nilai_a), sum(nilai_b) / len(nilai_b)
    menang_a = sum(1 for s in selisih.values() if s > 0)
    menang_b = sum(1 for s in selisih.values() if s < 0)
    unggul_a = sorted([k for k in atribut if selisih[k] > 0], key=selisih.get, reverse=True)[:3]
    unggul_b = sorted([k for k in atribut if selisih[k] < 0], key=selisih.get)[:3]

    def teks(daftar, tanda):
        return ", ".join(f"{KOLOM_KEMAMPUAN[k]} ({tanda}{int(abs(selisih[k]))})" for k in daftar)

    kalimat = (
        f"<b>{aman(nama_a)}</b> unggul pada {menang_a} dari 9 atribut"
        + (f", terutama {teks(unggul_a, '+')}" if unggul_a else "")
        + f". <b>{aman(nama_b)}</b> unggul pada {menang_b} atribut"
        + (f", terutama {teks(unggul_b, '+')}" if unggul_b else "")
        + f". Rata-rata 9 atribut: {format_desimal(rata_a)} (A) dan {format_desimal(rata_b)} (B). "
        f"Overall {int(a['Overall'])} (A) dan {int(b['Overall'])} (B); "
        f"Potential {int(a['Potential'])} (A) dan {int(b['Potential'])} (B). "
    )
    if int(a["Kelompok"]) == int(b["Kelompok"]):
        kalimat += f"Keduanya berada di Kelompok {int(a['Kelompok'])} hasil K-Means. "
    else:
        kalimat += (f"A berada di Kelompok {int(a['Kelompok'])} dan B di Kelompok "
                    f"{int(b['Kelompok'])} hasil K-Means. ")
    st.markdown(
        '<div class="panel"><span class="label-kecil">Kesimpulan otomatis</span>'
        f'<p style="margin-top:8px">{kalimat}</p></div>'
        '<div class="catatan">Perbandingan hanya memakai 9 atribut lapangan yang ada di dataset. '
        'Atribut itu kurang menggambarkan penjaga gawang, dan perbedaan angka tidak otomatis '
        'berarti satu pemain lebih baik dalam pertandingan nyata.</div>',
        unsafe_allow_html=True
    )

    st.download_button(
        "⬇️ Ekspor perbandingan (CSV)",
        data=tabel.to_csv(index=False).encode("utf-8-sig"),
        file_name="perbandingan_pemain.csv", mime="text/csv"
    )