import streamlit as st

from umum import (
    LEBAR_PENUH, baca_data, format_angka, header_halaman,
)


def tampilkan():
    data_pemain, _ = baca_data()

    header_halaman(
        "Katalog Data & Atribut",
        "Eksplorasi Dataset Pemain FIFA 18",
        "Telusuri, cari, dan filter data pemain dari dataset FIFA 18 "
        "(data historis, bukan kondisi pemain terkini)."
    )

    usia_min, usia_maks = int(data_pemain["Age"].min()), int(data_pemain["Age"].max())
    ovr_min, ovr_maks = int(data_pemain["Overall"].min()), int(data_pemain["Overall"].max())

    daftar_negara = ["Semua Negara"] + sorted(data_pemain["Nationality"].dropna().astype(str).unique().tolist())
    daftar_klub = ["Semua Klub"] + sorted(data_pemain["Club"].dropna().astype(str).unique().tolist())
    daftar_posisi = ["Semua Posisi"] + sorted(data_pemain["Kategori Posisi"].unique().tolist())

    KUNCI_FILTER = ["f_cari", "f_negara", "f_klub", "f_posisi", "f_usia",
                    "f_ovr", "f_urut", "f_naik", "f_ukuran", "f_halaman"]

    def reset_filter():
        for kunci in KUNCI_FILTER:
            st.session_state.pop(kunci, None)

    # ---------- Panel filter ----------
    with st.container(border=True):
        cari = st.text_input("Cari nama pemain", key="f_cari",
                             placeholder="Contoh: Messi, Neymar, Hazard ...")
        c1, c2, c3 = st.columns(3)
        negara = c1.selectbox("Kebangsaan / Negara", daftar_negara, key="f_negara")
        klub = c2.selectbox("Klub Sepak Bola", daftar_klub, key="f_klub")
        posisi = c3.selectbox("Kategori Posisi", daftar_posisi, key="f_posisi")

        c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1])
        rentang_usia = c4.slider("Rentang Usia", usia_min, usia_maks,
                                 (usia_min, usia_maks), key="f_usia")
        ovr_minimum = c5.slider("Overall minimum", ovr_min, ovr_maks, ovr_min, key="f_ovr")
        urut_label = c6.selectbox("Urutkan berdasarkan",
                                  ["Overall", "Potential", "Usia", "Nama"], key="f_urut")
        naik = c7.checkbox("Naik (A-Z / kecil-besar)", value=False, key="f_naik")
        st.button("Reset Filter", on_click=reset_filter)

    st.caption(
        "Kategori Posisi ditentukan dari posisi pertama pada kolom 'Preferred Positions' "
        "(Bertahan: CB/LB/RB/LWB/RWB, Tengah: CDM/CM/CAM/LM/RM, Depan: ST/CF/LW/RW/LF/RF)."
    )

    # ---------- Terapkan filter ----------
    hasil = data_pemain
    cari = cari.strip()
    if cari:
        hasil = hasil[hasil["Name"].str.contains(cari, case=False, na=False, regex=False)]
    if negara != "Semua Negara":
        hasil = hasil[hasil["Nationality"] == negara]
    if klub != "Semua Klub":
        hasil = hasil[hasil["Club"] == klub]
    if posisi != "Semua Posisi":
        hasil = hasil[hasil["Kategori Posisi"] == posisi]
    hasil = hasil[hasil["Age"].between(rentang_usia[0], rentang_usia[1])]
    hasil = hasil[hasil["Overall"] >= ovr_minimum]

    # ---------- Urutkan ----------
    kolom_urut = {"Overall": "Overall", "Potential": "Potential",
                  "Usia": "Age", "Nama": "Name"}[urut_label]
    if kolom_urut == "Name":
        hasil = hasil.sort_values("Name", ascending=naik)
    else:
        hasil = hasil.sort_values([kolom_urut, "Name"], ascending=[naik, True])

    st.markdown(
        f"**{format_angka(len(hasil))}** dari {format_angka(len(data_pemain))} pemain ditemukan"
    )

    if hasil.empty:
        st.info("Tidak ada pemain yang cocok. Coba kurangi filter atau perluas rentang usia/Overall.")
        return

    # ---------- Pagination ----------
    p1, p2, p3 = st.columns([1, 1, 2])
    ukuran = p1.selectbox("Baris per halaman", [10, 25, 50, 100], key="f_ukuran")
    total_halaman = max(1, -(-len(hasil) // ukuran))   # pembulatan ke atas

    if st.session_state.get("f_halaman", 1) > total_halaman:
        st.session_state.pop("f_halaman", None)        # kembali ke halaman 1

    nomor_halaman = p2.number_input("Halaman", min_value=1, max_value=total_halaman,
                                    value=1, step=1, key="f_halaman")
    p3.markdown(
        f'<div style="padding-top:30px;color:#9fb0cf">Halaman <b>{nomor_halaman}</b> '
        f'dari <b>{format_angka(total_halaman)}</b></div>',
        unsafe_allow_html=True
    )

    awal = (nomor_halaman - 1) * ukuran
    bagian = hasil.iloc[awal: awal + ukuran].copy()
    bagian["Kelompok"] = "Kelompok " + bagian["Kelompok"].astype(str)

    kolom_tabel = ["Name", "Nationality", "Club", "Preferred Positions",
                   "Age", "Overall", "Potential", "Kelompok"]
    tabel = bagian[kolom_tabel].rename(columns={
        "Name": "Nama Pemain", "Nationality": "Kebangsaan", "Club": "Klub",
        "Preferred Positions": "Posisi", "Age": "Usia",
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

    # ---------- Ekspor CSV (seluruh hasil filter) ----------
    csv = hasil.drop(columns=["Kategori Posisi"]).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Ekspor CSV (semua hasil filter)",
        data=csv, file_name="pemain_hasil_filter.csv", mime="text/csv"
    )