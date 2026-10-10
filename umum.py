import html
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# KONSTANTA
# =========================================================
# Streamlit versi baru memakai width="stretch", versi lama use_container_width
_versi = tuple(int(x) for x in st.__version__.split(".")[:2])
LEBAR_PENUH = {"width": "stretch"} if _versi >= (1, 50) else {"use_container_width": True}

KOLOM_KEMAMPUAN = {
    "Acceleration": "Akselerasi",
    "Sprint speed": "Kecepatan Lari",
    "Finishing": "Penyelesaian Akhir",
    "Short passing": "Umpan Pendek",
    "Dribbling": "Menggiring Bola",
    "Ball control": "Penguasaan Bola",
    "Stamina": "Daya Tahan",
    "Strength": "Kekuatan",
    "Standing tackle": "Kemampuan Merebut Bola",
}

NAMA_FITUR = {**KOLOM_KEMAMPUAN, "Age": "Usia", "Overall": "Overall", "Potential": "Potential"}

KOLOM_WAJIB = [
    "Name", "Age", "Nationality", "Overall", "Potential",
    "Club", "Preferred Positions", "Kelompok",
] + list(KOLOM_KEMAMPUAN.keys())

WARNA_KELOMPOK = ["#a3e635", "#38bdf8", "#c4b5fd", "#fb923c", "#f472b6", "#facc15"]

# Pengelompokan posisi (berdasarkan POSISI PERTAMA di 'Preferred Positions')
POSISI_BERTAHAN = {"CB", "LB", "RB", "LWB", "RWB"}
POSISI_TENGAH = {"CDM", "CM", "CAM", "LM", "RM"}
POSISI_DEPAN = {"ST", "CF", "LW", "RW", "LF", "RF"}

# =========================================================
# GAYA TAMPILAN (CSS)
# =========================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif;
}

#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

.block-container {padding-top: 2rem; max-width: 1300px;}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: #0e1628;
    border-right: 1px solid #1f2b45;
}
.brand {display:flex; flex-direction:column; margin: 4px 0 6px 4px;}
.brand-nama {font-size: 1.35rem; font-weight: 700; color: #e6edf7;}
.brand-sub {font-size: .72rem; letter-spacing: .12em; font-weight: 600; color: #38bdf8;}
.lencana-kecil {
    display:inline-block; margin: 8px 0 18px 4px; padding: 3px 10px;
    border-radius: 6px; background:#1a2540; color:#9fb0cf; font-size:.75rem;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {gap: 4px;}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 10px 14px; border-radius: 12px; cursor: pointer;
    width: 100%; transition: background .15s;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {background:#16213a;}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {display:none;}
section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: .98rem; font-weight: 500; color: #b8c4dd;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: #00a8e8;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #04111f; font-weight: 700;
}

.kotak-dataset {
    margin-top: 30px; padding: 12px 14px; border-radius: 12px;
    background:#131c31; border:1px solid #1f2b45; font-size:.82rem; color:#9fb0cf;
}
.kotak-dataset b {color:#e6edf7;}
.titik {display:inline-block; width:8px; height:8px; border-radius:50%;
        background:#a3e635; margin-right:6px;}

/* ---------- Header halaman ---------- */
.label-kecil {
    display:inline-block; padding: 3px 12px; border-radius: 999px;
    background:#13203a; color:#38bdf8; font-size:.75rem; font-weight:600;
    letter-spacing:.06em; text-transform:uppercase;
}
.judul-halaman {font-size: 2.1rem; font-weight: 700; color:#f1f5fb; margin: 8px 0 4px 0;}
.deskripsi-halaman {color:#9fb0cf; font-size: 1rem; margin-bottom: 18px;}

.lencana-atas {
    display:inline-block; margin-right: 8px; padding: 5px 14px; border-radius: 999px;
    background:#131c31; border:1px solid #1f2b45; color:#c9d4ea; font-size:.8rem;
}

/* ---------- Kartu statistik ---------- */
.kartu {
    background: #131c31; border: 1px solid #1f2b45; border-radius: 18px;
    padding: 18px 20px; height: 100%;
}
.kartu-judul {font-size:.75rem; letter-spacing:.08em; font-weight:600;
              color:#8a97b3; text-transform:uppercase;}
.kartu-nilai {font-size: 2.3rem; font-weight: 700; margin: 6px 0 2px 0;}
.kartu-nilai.lime {color:#a3e635;}
.kartu-nilai.cyan {color:#38bdf8;}
.kartu-nilai.putih {color:#f1f5fb;}
.kartu-ket {font-size:.85rem; color:#9fb0cf;}

/* ---------- Panel ---------- */
.panel {
    background:#131c31; border:1px solid #1f2b45; border-radius:18px;
    padding: 22px 24px; margin-top: 8px;
}
.panel h3 {margin:0 0 6px 0; color:#f1f5fb;}
.panel p {color:#9fb0cf; margin:0;}
.panel ul {color:#c9d4ea; margin: 8px 0 0 0; padding-left: 20px;}
.panel li {margin: 5px 0; font-size:.92rem;}
.panel b {color:#f1f5fb;}

.catatan {
    background:#10243a; border:1px solid #1f3b5c; border-radius:12px;
    padding: 10px 14px; color:#b8d4f0; font-size:.88rem; margin: 10px 0;
}

/* ---------- Batang distribusi usia ---------- */
.bar-baris {margin: 14px 0;}
.bar-atas {display:flex; justify-content:space-between; font-size:.9rem;
           color:#c9d4ea; margin-bottom:6px;}
.bar-atas span.angka {color:#8a97b3;}
.bar-atas span.angka b {color:#38bdf8; font-weight:600;}
.bar-jalur {height:10px; border-radius:999px; background:#0e1628; overflow:hidden;}
.bar-isi {height:100%; border-radius:999px;
          background: linear-gradient(90deg, #38bdf8, #a3e635);}

/* ---------- Kartu kelompok ---------- */
.kartu-kelompok {
    background:#131c31; border:1px solid #1f2b45; border-radius:18px;
    padding:16px 18px; height:100%;
}
.kk-judul {font-weight:700; color:#f1f5fb; font-size:1.05rem;}
.kk-titik {display:inline-block; width:10px; height:10px; border-radius:50%;
           margin-right:8px;}
.kk-nilai {font-size:1.9rem; font-weight:700; color:#f1f5fb; margin:6px 0 0 0;}
.kk-ket {font-size:.8rem; color:#8a97b3; margin-bottom:10px;}
.kk-baris {font-size:.85rem; color:#c9d4ea; margin:3px 0;}
.kk-baris b {color:#a3e635;}
.kk-menonjol {font-size:.82rem; color:#9fb0cf; margin-top:10px;
              border-top:1px solid #1f2b45; padding-top:8px;}

/* ---------- Profil pemain ---------- */
.profil {
    display:flex; align-items:center; gap:20px; flex-wrap:wrap;
    background:#131c31; border:1px solid #1f2b45; border-radius:18px;
    padding: 20px 24px;
}
.avatar {
    width:76px; height:76px; border-radius:20px; background:#0e1628;
    border:2px solid #a3e635; color:#a3e635; font-size:1.5rem; font-weight:700;
    display:flex; align-items:center; justify-content:center;
}
.profil-info {flex:1; min-width:240px;}
.profil-nama {font-size:1.7rem; font-weight:700; color:#f1f5fb;}
.profil-meta {color:#9fb0cf; font-size:.92rem; margin:4px 0 8px 0;}
.badge-pos {
    display:inline-block; margin-right:6px; padding:2px 10px; border-radius:6px;
    background:#3b1d24; color:#fca5a5; font-size:.78rem; font-weight:600;
}
.badge-kel {
    display:inline-block; margin-right:6px; padding:2px 10px; border-radius:6px;
    background:#13203a; color:#38bdf8; font-size:.78rem; font-weight:600;
}
.rating {text-align:center; background:#0e1628; border-radius:16px; padding:10px 22px;}
.rating-label {font-size:.7rem; letter-spacing:.1em; color:#8a97b3; text-transform:uppercase;}
.rating-angka {font-size:2.6rem; font-weight:700; color:#a3e635; line-height:1.1;}
.rating-pot {font-size:.8rem; color:#38bdf8;}

/* ---------- Kartu atribut ---------- */
.atribut {
    background:#131c31; border:1px solid #1f2b45; border-radius:14px;
    padding:14px 16px; margin-bottom:12px;
}
.atribut-atas {display:flex; justify-content:space-between; align-items:baseline;}
.atribut-nama {color:#c9d4ea; font-size:.9rem; font-weight:500;}
.atribut-nilai {font-size:1.5rem; font-weight:700;}
.atribut-nilai small {font-size:.75rem; color:#8a97b3; font-weight:400;}
.atribut-jalur {height:8px; border-radius:999px; background:#0e1628; margin:8px 0 6px 0; overflow:hidden;}
.atribut-isi {height:100%; border-radius:999px;}
.atribut-ket {font-size:.78rem; color:#8a97b3;}

div[data-testid="stMetric"] {
    background:#131c31; border:1px solid #1f2b45; border-radius:14px; padding:14px 16px;
}
</style>
"""


def pasang_css():
    """Memasang tema gelap ke seluruh aplikasi."""
    st.markdown(CSS, unsafe_allow_html=True)


# =========================================================
# FUNGSI BANTU TAMPILAN
# =========================================================
def format_angka(nilai):
    """Mengubah 17509 menjadi '17.509' (format Indonesia)."""
    return f"{int(nilai):,}".replace(",", ".")


def format_desimal(nilai, digit=1):
    """Mengubah 66.24 menjadi '66,2' (format Indonesia)."""
    return f"{nilai:.{digit}f}".replace(".", ",")


def aman(teks):
    """Membuat teks aman dimasukkan ke HTML. Nilai kosong menjadi '-'."""
    if pd.isna(teks):
        return "-"
    return html.escape(str(teks))


def kategori_posisi(teks):
    """Menentukan kategori posisi dari posisi PERTAMA pada 'Preferred Positions'."""
    if pd.isna(teks) or not str(teks).strip():
        return "Tidak diketahui"
    pertama = str(teks).split()[0].upper()
    if pertama == "GK":
        return "Penjaga Gawang"
    if pertama in POSISI_BERTAHAN:
        return "Bertahan"
    if pertama in POSISI_TENGAH:
        return "Tengah"
    if pertama in POSISI_DEPAN:
        return "Depan"
    return "Lainnya"


def kartu_statistik(judul, nilai, keterangan, warna="lime"):
    return (
        f'<div class="kartu">'
        f'<div class="kartu-judul">{judul}</div>'
        f'<div class="kartu-nilai {warna}">{nilai}</div>'
        f'<div class="kartu-ket">{keterangan}</div>'
        f'</div>'
    )


def header_halaman(label, judul, deskripsi):
    st.markdown(
        f'<span class="label-kecil">{label}</span>'
        f'<div class="judul-halaman">{judul}</div>'
        f'<div class="deskripsi-halaman">{deskripsi}</div>',
        unsafe_allow_html=True
    )


def atur_grafik(gambar, tinggi=380):
    """Membuat grafik Plotly menyatu dengan tema gelap."""
    gambar.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=tinggi,
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Space Grotesk, sans-serif", color="#c9d4ea"),
    )
    gambar.update_xaxes(gridcolor="#1f2b45")
    gambar.update_yaxes(gridcolor="#1f2b45")
    return gambar


def hitung_distribusi_usia(usia):
    """Mengelompokkan usia ke 5 rentang dan menghitung jumlah serta persentasenya."""
    batas = [0, 20, 25, 30, 35, 200]
    label = ["16 - 20 tahun", "21 - 25 tahun", "26 - 30 tahun",
             "31 - 35 tahun", "36+ tahun"]
    kelompok_usia = pd.cut(usia, bins=batas, labels=label, right=True)
    jumlah = kelompok_usia.value_counts().reindex(label).fillna(0).astype(int)
    persen = jumlah / jumlah.sum() * 100
    return jumlah, persen


def html_batang_usia(jumlah, persen):
    terbesar = jumlah.max() if jumlah.max() > 0 else 1
    isi = ""
    for nama in jumlah.index:
        lebar = jumlah[nama] / terbesar * 100
        isi += (
            '<div class="bar-baris">'
            '<div class="bar-atas">'
            f'<span>{nama}</span>'
            f'<span class="angka">{format_angka(jumlah[nama])} '
            f'(<b>{format_desimal(persen[nama])}%</b>)</span>'
            '</div>'
            '<div class="bar-jalur">'
            f'<div class="bar-isi" style="width:{lebar:.1f}%"></div>'
            '</div></div>'
        )
    return isi


def ringkasan_kelompok(data):
    """Menghitung ringkasan tiap kelompok dari data aktual."""
    atribut = list(KOLOM_KEMAMPUAN.keys())
    rata_global = data[atribut].mean()
    rata_kelompok = data.groupby("Kelompok")[atribut].mean()
    hasil = []
    for nomor in sorted(data["Kelompok"].unique()):
        bagian = data[data["Kelompok"] == nomor]
        selisih = (rata_kelompok.loc[nomor] - rata_global).sort_values(ascending=False)
        menonjol = [
            f"{KOLOM_KEMAMPUAN[k]} (+{format_desimal(v)})"
            for k, v in selisih.head(3).items() if v > 0
        ]
        hasil.append({
            "nomor": int(nomor),
            "jumlah": len(bagian),
            "persen": len(bagian) / len(data) * 100,
            "rata_overall": bagian["Overall"].mean(),
            "rata_usia": bagian["Age"].mean(),
            "menonjol": menonjol,
        })
    return hasil


def html_kartu_kelompok(info, warna):
    menonjol = ", ".join(info["menonjol"]) if info["menonjol"] else "Tidak ada yang di atas rata-rata"
    return (
        '<div class="kartu-kelompok">'
        f'<div class="kk-judul"><span class="kk-titik" style="background:{warna}"></span>'
        f'Kelompok {info["nomor"]}</div>'
        f'<div class="kk-nilai">{format_angka(info["jumlah"])}</div>'
        f'<div class="kk-ket">pemain ({format_desimal(info["persen"])}%)</div>'
        f'<div class="kk-baris">Rata-rata Overall: <b>{format_desimal(info["rata_overall"])}</b></div>'
        f'<div class="kk-baris">Rata-rata usia: <b>{format_desimal(info["rata_usia"])} th</b></div>'
        f'<div class="kk-menonjol">Atribut paling menonjol dibanding rata-rata semua pemain: '
        f'{menonjol}</div>'
        '</div>'
    )


def inisial(nama):
    bagian = [b for b in str(nama).replace(".", " ").split() if b]
    return "".join(b[0] for b in bagian[:2]).upper() or "?"


def html_kartu_atribut(nama, nilai, persentil):
    warna = "#a3e635" if nilai >= 75 else "#38bdf8"
    return (
        '<div class="atribut">'
        '<div class="atribut-atas">'
        f'<span class="atribut-nama">{nama}</span>'
        f'<span class="atribut-nilai" style="color:{warna}">{int(nilai)}<small>/100</small></span>'
        '</div>'
        '<div class="atribut-jalur">'
        f'<div class="atribut-isi" style="width:{min(nilai, 100):.0f}%;background:{warna}"></div>'
        '</div>'
        f'<div class="atribut-ket">Lebih tinggi dari {format_desimal(persentil, 0)}% pemain</div>'
        '</div>'
    )


def halaman_belum_siap(judul, tahap, deskripsi):
    header_halaman("Segera Hadir", judul, deskripsi)
    st.markdown(
        f'<div class="panel"><h3>Halaman ini dikerjakan di {tahap}</h3>'
        f'<p>Menu sudah terpasang dan berfungsi. Isinya akan dibuat setelah '
        f'tahap sebelumnya selesai diuji.</p></div>',
        unsafe_allow_html=True
    )


# =========================================================
# MEMBACA DATA
# =========================================================
@st.cache_data
def baca_data():
    data = pd.read_csv("data/pemain_cluster.csv")
    rata_rata = pd.read_csv("data/rata_rata_kelompok.csv")

    if "Kelompok" not in data.columns and "Cluster" in data.columns:
        data = data.rename(columns={"Cluster": "Kelompok"})
    if "Kelompok" not in rata_rata.columns and "Cluster" in rata_rata.columns:
        rata_rata = rata_rata.rename(columns={"Cluster": "Kelompok"})

    # Kolom tambahan untuk filter posisi (tidak mengubah file CSV)
    if "Preferred Positions" in data.columns:
        data["Kategori Posisi"] = data["Preferred Positions"].apply(kategori_posisi)

    return data, rata_rata


@st.cache_data
def buat_label_pemain(nama, klub, overall):
    """Label pilihan pemain: 'Nama - Klub · Overall'. Dibuat sekali agar cepat."""
    teks = (nama.astype(str) + " - " + klub.fillna("-").astype(str)
            + " · Overall " + overall.astype(int).astype(str))
    return dict(zip(teks.index, teks))


@st.cache_data
def hitung_pca(nilai):
    """PCA 2 dimensi untuk VISUALISASI saja (tidak mengubah hasil K-Means)."""
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    skala = StandardScaler().fit_transform(nilai)
    pca = PCA(n_components=2, random_state=42)
    koordinat = pca.fit_transform(skala)
    return koordinat, pca.explained_variance_ratio_


def tentukan_fitur(data, rata_rata):
    """Fitur diambil dari kolom file rata_rata_kelompok.csv (jika bisa)."""
    kandidat = [
        k for k in rata_rata.columns
        if k in data.columns and k != "Kelompok"
        and pd.api.types.is_numeric_dtype(data[k])
    ]
    if len(kandidat) >= 3:
        return kandidat, "kolom pada rata_rata_kelompok.csv"
    return list(KOLOM_KEMAMPUAN.keys()), "9 atribut kemampuan (cadangan)"