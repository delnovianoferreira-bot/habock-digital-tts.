import streamlit as st
import pandas as pd
import os
import base64
import plotly.express as px
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# 1. KONFIGURASI HALAMAN
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="HABOCK Digital — DLH Kab. TTS",
    layout="wide",
    page_icon="🍃",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# 2. DATA SOURCE (GOOGLE SHEETS)
# ═══════════════════════════════════════════════════════════════
URL_DATA             = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_ZOXOlq8tAN3z3zMMMbh1JFS-Sl9LecCVE7gNAoDm_IF0oFDuredZXbtO_rAPF54hlzyervBGwvuq/pub?output=csv"
URL_BOKASHI_PRODUKSI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_ZOXOlq8tAN3z3zMMMbh1JFS-Sl9LecCVE7gNAoDm_IF0oFDuredZXbtO_rAPF54hlzyervBGwvuq/pub?gid=538980514&single=true&output=csv"
URL_BOKASHI_KATALOG  = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_ZOXOlq8tAN3z3zMMMbh1JFS-Sl9LecCVE7gNAoDm_IF0oFDuredZXbtO_rAPF54hlzyervBGwvuq/pub?gid=1511411011&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        return pd.read_csv(URL_DATA)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_bokashi_produksi():
    try:
        df = pd.read_csv(URL_BOKASHI_PRODUKSI, skiprows=2)
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=["Tanggal"])
        df = df[df["Tanggal"].astype(str).str.match(r'\d{2}/\d{2}/\d{4}')]
        df["Tanggal"] = pd.to_datetime(df["Tanggal"], format="%d/%m/%Y", errors="coerce")
        for col in ["Bahan Baku Masuk (kg)", "Pupuk Diproduksi (kg)", "Pupuk Terjual (kg)",
                    "Harga/kg", "Total Pendapatan", "Stok Tersisa"]:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "").str.replace(".", ""),
                    errors="coerce"
                ).fillna(0)
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_bokashi_katalog():
    try:
        df = pd.read_csv(URL_BOKASHI_KATALOG, skiprows=2)
        df.columns = df.columns.str.strip()
        df = df[df.iloc[:, 0].astype(str).str.startswith("BOK-")]
        return df
    except:
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════════
# 3. FUNGSI GAMBAR
# ═══════════════════════════════════════════════════════════════
def get_image_base64(target):
    files = os.listdir(".")
    img = next((f for f in files if target.lower() in f.lower()), None)
    if img:
        with open(img, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_pemda = get_image_base64("pemda")
logo_hb    = get_image_base64("logo")
bg_kantor  = get_image_base64("kantor")

# ═══════════════════════════════════════════════════════════════
# 4. CSS PREMIUM
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: #eef2ee; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; }

/* TOPBAR */
.topbar {
    background: linear-gradient(90deg, #0a3d1f 0%, #1b5e20 60%, #2e7d32 100%);
    padding: 12px 28px; border-radius: 18px; margin-bottom: 10px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 6px 24px rgba(10,61,31,0.3);
}
.topbar-left { display: flex; align-items: center; gap: 16px; }
.topbar-divider { width: 2px; height: 52px; background: rgba(255,255,255,0.2); border-radius: 4px; }
.topbar-inst p  { margin: 0; font-size: 0.68em; color: rgba(255,255,255,0.65); letter-spacing: 0.5px; }
.topbar-inst h3 { margin: 0; font-size: 0.92em; font-weight: 800; color: white; }
.topbar-brand h1 {
    font-family: 'Outfit', sans-serif; font-size: 1.65em;
    margin: 0; font-weight: 900; color: white; letter-spacing: 1px;
}
.topbar-brand p { margin: 0; font-size: 0.65em; color: rgba(255,255,255,0.65); letter-spacing: 2px; }
.topbar-time {
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.25);
    color: rgba(255,255,255,0.9); padding: 7px 16px; border-radius: 30px;
    font-size: 0.72em; font-weight: 600; white-space: nowrap;
}

/* PROJECT BANNER */
.proj-banner {
    background: white; border-radius: 16px; padding: 16px 24px;
    border-left: 7px solid #1b5e20; margin-bottom: 16px;
    box-shadow: 0 3px 16px rgba(0,0,0,0.05);
    display: flex; align-items: center; gap: 16px;
}
.proj-banner-icon { font-size: 2em; }
.proj-banner small { color: #1b5e20; font-weight: 700; font-size: 0.7em; text-transform: uppercase; letter-spacing: 1px; }
.proj-banner p { margin: 4px 0 0 0; font-size: 0.88em; color: #2d3436; font-weight: 600; line-height: 1.45; }

/* HERO */
.hero-wrap {
    border-radius: 26px; overflow: hidden; margin-bottom: 22px;
    box-shadow: 0 20px 55px rgba(0,0,0,0.2); position: relative; height: 390px;
    background-size: cover; background-position: center;
}
.hero-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(150deg, rgba(0,0,0,0.5) 0%, rgba(10,61,31,0.82) 100%);
    display: flex; flex-direction: column; justify-content: center;
    align-items: center; text-align: center; padding: 40px;
}
.hero-chip {
    background: rgba(255,255,255,0.13); border: 1px solid rgba(255,255,255,0.35);
    color: rgba(255,255,255,0.92); padding: 5px 18px; border-radius: 30px;
    font-size: 0.73em; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 14px;
}
.hero-title {
    font-family: 'Outfit', sans-serif; font-size: 4em; color: white;
    margin: 0 0 10px 0; font-weight: 900; line-height: 1;
    text-shadow: 0 4px 24px rgba(0,0,0,0.45);
}
.hero-sub {
    color: rgba(255,255,255,0.85); font-size: 1.05em; font-weight: 400;
    margin: 0 0 30px 0; max-width: 560px; line-height: 1.55;
}
.hero-btns { display: flex; gap: 14px; flex-wrap: wrap; justify-content: center; }
.btn-lapor {
    background: #e74c3c; color: white !important; padding: 13px 28px;
    border-radius: 50px; text-decoration: none !important; font-weight: 800; font-size: 0.88em;
    box-shadow: 0 8px 22px rgba(231,76,60,0.45); border: 2px solid rgba(255,255,255,0.25);
}
.btn-petugas {
    background: rgba(255,255,255,0.13); color: white !important; padding: 13px 28px;
    border-radius: 50px; text-decoration: none !important; font-weight: 800; font-size: 0.88em;
    border: 2px solid rgba(255,255,255,0.55);
}

/* METRIC CARDS */
.metric-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 20px; }
.mc {
    background: white; border-radius: 18px; padding: 20px 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06); border-top: 4px solid #1b5e20; text-align: center;
}
.mc.gold { border-top-color: #c9992a; }
.mc.red  { border-top-color: #e74c3c; }
.mc.blue { border-top-color: #2980b9; }
.mc .ico { font-size: 1.9em; margin-bottom: 8px; }
.mc .val { font-family:'Outfit',sans-serif; font-size:1.75em; font-weight:900; color:#1a1a2e; line-height:1; }
.mc .lbl { font-size:0.7em; color:#999; font-weight:700; margin-top:5px; text-transform:uppercase; letter-spacing:0.5px; }

/* CARD */
.card {
    background: white; border-radius: 18px; padding: 20px 22px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06); margin-bottom: 16px;
}

/* SECTION HEADER */
.sh { display:flex; align-items:center; gap:10px; margin: 18px 0 12px 0; }
.sh .dot { width:9px; height:9px; background:#1b5e20; border-radius:50%; flex-shrink:0; }
.sh h3 { margin:0; font-size:1.02em; font-weight:800; color:#1a1a2e; }
.sh span { font-size:0.75em; color:#bbb; }

/* PRODUCT CARD */
.pc {
    background:white; border-radius:14px; padding:14px 18px;
    border:1.5px solid #e8f5e9; box-shadow:0 2px 10px rgba(0,0,0,0.04);
    display:flex; justify-content:space-between; align-items:center;
    margin-bottom:10px; transition:all 0.18s;
}
.pc:hover { border-color:#1b5e20; transform:translateX(3px); box-shadow:0 5px 18px rgba(27,94,32,0.1); }
.pc .pn { font-weight:800; color:#1a1a2e; font-size:0.92em; }
.pc .pk { font-size:0.73em; color:#aaa; margin-top:2px; }
.pc .ph { font-family:'Outfit',sans-serif; font-size:1.1em; font-weight:900; color:#1b5e20; }
.ok  { background:#e8f5e9; color:#1b5e20; padding:2px 9px; border-radius:20px; font-size:0.68em; font-weight:700; }
.no  { background:#fdecea; color:#c0392b; padding:2px 9px; border-radius:20px; font-size:0.68em; font-weight:700; }

/* INFO BOX */
.ib {
    background: linear-gradient(135deg, #0a3d1f, #1b5e20);
    border-radius:16px; padding:20px 22px; color:white; margin-top:14px;
}
.ib h4 { margin:0 0 13px 0; font-size:0.95em; font-weight:800; }
.ib .st { display:flex; align-items:flex-start; gap:10px; margin-bottom:9px; font-size:0.82em; line-height:1.4; }
.ib .sn {
    background:rgba(255,255,255,0.18); border-radius:50%;
    width:22px; height:22px; display:flex; align-items:center; justify-content:center;
    font-weight:800; font-size:0.78em; flex-shrink:0;
}
.ib .lok { background:rgba(255,255,255,0.1); border-radius:10px; padding:9px 13px; margin-top:12px; font-size:0.8em; }

/* MANFAAT */
.mg { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:12px; }
.mi {
    background:#f0f9f0; border-radius:11px; padding:10px 12px;
    display:flex; align-items:flex-start; gap:9px;
    font-size:0.78em; border:1px solid #d4edda; color:#2d3436; line-height:1.4;
}

/* ALUR */
.alur {
    display:flex; align-items:center; justify-content:center;
    gap:0; flex-wrap:wrap; text-align:center; padding:16px 0;
}
.alur-step {
    padding:14px 18px; border-radius:14px; min-width:105px;
}
.alur-arrow { padding:0 6px; color:#ccc; font-size:1.4em; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background:white; border-radius:14px; padding:5px;
    box-shadow:0 2px 12px rgba(0,0,0,0.06); gap:4px; margin-bottom:8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius:10px; font-weight:700; font-size:0.85em; padding:9px 18px; color:#666;
}
.stTabs [aria-selected="true"] { background:#1b5e20 !important; color:white !important; }

/* FOOTER */
.footer {
    text-align:center; padding:22px 0 6px 0;
    border-top:1px solid #dde; margin-top:20px;
    color:#ccc; font-size:0.76em; line-height:1.7;
}
.footer strong { color:#1b5e20; }
.footer .star { color:#daa520; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 5. TOPBAR
# ═══════════════════════════════════════════════════════════════
now = datetime.now().strftime("📅 %d %B %Y  ·  🕐 %H:%M WITA")
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <img src="data:image/png;base64,{logo_pemda}" width="54" style="border-radius:8px;">
        <div class="topbar-divider"></div>
        <div class="topbar-inst">
            <p>PEMERINTAH KABUPATEN TIMOR TENGAH SELATAN</p>
            <h3>DINAS LINGKUNGAN HIDUP</h3>
        </div>
        <div class="topbar-divider"></div>
        <img src="data:image/png;base64,{logo_hb}" width="44" style="border-radius:8px;">
        <div class="topbar-brand">
            <h1>HABOCK</h1>
            <p>SISTEM INFORMASI DIGITAL</p>
        </div>
    </div>
    <div class="topbar-time">{now}</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 6. PROJECT BANNER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="proj-banner">
    <div class="proj-banner-icon">🏛️</div>
    <div>
        <small>Proyek Aktualisasi LATSAR CPNS Angkatan 274 · DLH Kab. Timor Tengah Selatan</small>
        <p>Optimalisasi Potensi Ekonomi Sirkular & Efisiensi Kinerja Pelayanan Persampahan melalui Platform HABOCK — Bidang Pengelolaan Sampah, Limbah B3 dan Peningkatan Kapasitas</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 7. HERO BANNER
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-wrap" style="background-image:url('data:image/jpeg;base64,{bg_kantor}');">
    <div class="hero-overlay">
        <div class="hero-chip">🍃 Platform Persampahan Terintegrasi · Kota Soe, TTS</div>
        <h1 class="hero-title">HABOCK DIGITAL</h1>
        <p class="hero-sub">Sistem terpadu pengawasan TPS, absensi petugas, informasi publik &amp; ekonomi sirkular pupuk bokashi Kabupaten Timor Tengah Selatan</p>
        <div class="hero-btns">
            <a href="https://docs.google.com/forms/d/e/1FAIpQLSejAQXpYJh_v9QZeAaoyqy66puWQutFnV7V6Ux9od-uMWr0UQ/viewform?usp=dialog" target="_blank" class="btn-lapor">📩 Lapor Sampah</a>
            <a href="https://www.appsheet.com/start/YOUR_APPSHEET_ID" target="_blank" class="btn-petugas">👮 Portal Petugas</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 8. TABS
# ═══════════════════════════════════════════════════════════════
tab_home, tab_stats, tab_map, tab_logs, tab_bokashi = st.tabs([
    "🏠  Beranda",
    "📊  Statistik Kinerja",
    "📍  Peta TPS",
    "📜  Log Pengawasan",
    "🌿  Pupuk Bokashi",
])

# ── BERANDA ─────────────────────────────────────────────────────
with tab_home:
    c1, c2, c3 = st.columns(3, gap="large")
    cards = [
        ("🗑️","Pengawasan TPS",
         "Pemantauan 32 titik TPS di Kota Soe secara real-time melalui AppSheet oleh 6 operator lapangan mulai pukul 03.00 WITA setiap hari.",
         "#f0f9f0","#1b5e20","📍 32 Titik TPS  ·  👷 6 Operator  ·  ⏰ 03.00 WITA"),
        ("📢","Pengaduan Publik",
         "Masyarakat dapat melaporkan tumpukan sampah liar, TPS penuh, atau jadwal angkut terlambat melalui formulir digital yang mudah diakses.",
         "#fff3f3","#e74c3c","🔴 Klik tombol 'Lapor Sampah' di atas"),
        ("🌿","Pupuk Bokashi",
         "Sampah organik dari TPS diolah menjadi pupuk bokashi berkualitas. Tersedia untuk petani dan masyarakat umum mulai Rp 5.000/kg.",
         "#f0f9f0","#1b5e20","🛒 Lihat katalog di tab Pupuk Bokashi"),
    ]
    for col, (ico, title, desc, bg, fc, note) in zip([c1,c2,c3], cards):
        with col:
            st.markdown(f"""
            <div class="card" style="height:100%;">
                <div style="font-size:2.4em;margin-bottom:10px;">{ico}</div>
                <h4 style="color:#1b5e20;margin:0 0 9px 0;font-size:1.02em;">{title}</h4>
                <p style="color:#555;font-size:0.85em;line-height:1.6;margin:0 0 12px 0;">{desc}</p>
                <div style="padding:9px 13px;background:{bg};border-radius:10px;font-size:0.77em;color:{fc};font-weight:700;">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="sh" style="margin-top:24px;"><div class="dot"></div><h3>Alur Sistem HABOCK</h3></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
      <div class="alur">
        <div class="alur-step" style="background:#f0f9f0;"><div style="font-size:1.7em;">🗑️</div><div style="font-weight:800;color:#1b5e20;font-size:0.82em;margin-top:5px;">Sampah Masuk</div><div style="font-size:0.68em;color:#999;">TPS Kota Soe</div></div>
        <div class="alur-arrow">→</div>
        <div class="alur-step" style="background:#e8f4fd;"><div style="font-size:1.7em;">📱</div><div style="font-weight:800;color:#2980b9;font-size:0.82em;margin-top:5px;">AppSheet</div><div style="font-size:0.68em;color:#999;">Input Petugas</div></div>
        <div class="alur-arrow">→</div>
        <div class="alur-step" style="background:#fef9e7;"><div style="font-size:1.7em;">📊</div><div style="font-weight:800;color:#b8860b;font-size:0.82em;margin-top:5px;">Google Sheets</div><div style="font-size:0.68em;color:#999;">Database</div></div>
        <div class="alur-arrow">→</div>
        <div class="alur-step" style="background:#f5eef8;"><div style="font-size:1.7em;">🌿</div><div style="font-weight:800;color:#7d3c98;font-size:0.82em;margin-top:5px;">Bokashi</div><div style="font-size:0.68em;color:#999;">Ekonomi Sirkular</div></div>
        <div class="alur-arrow">→</div>
        <div class="alur-step" style="background:#fdecea;"><div style="font-size:1.7em;">💰</div><div style="font-weight:800;color:#c0392b;font-size:0.82em;margin-top:5px;">PAD Daerah</div><div style="font-size:0.68em;color:#999;">Pendapatan Asli</div></div>
        <div class="alur-arrow">→</div>
        <div class="alur-step" style="background:#e8f8f5;"><div style="font-size:1.7em;">🌐</div><div style="font-weight:800;color:#1abc9c;font-size:0.82em;margin-top:5px;">Web HABOCK</div><div style="font-size:0.68em;color:#999;">Info Publik</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── STATISTIK ───────────────────────────────────────────────────
with tab_stats:
    df = load_data()
    if not df.empty:
        total   = len(df)
        selesai = len(df[df['Status'] == 'Selesai'])   if 'Status' in df.columns else 0
        proses  = len(df[df['Status'] == 'Belum Proses']) if 'Status' in df.columns else 0
        st.markdown(f"""
        <div class="metric-row">
            <div class="mc"><div class="ico">📋</div><div class="val">{total}</div><div class="lbl">Total Laporan</div></div>
            <div class="mc"><div class="ico">📍</div><div class="val">32</div><div class="lbl">TPS Dipantau</div></div>
            <div class="mc gold"><div class="ico">✅</div><div class="val">{selesai}</div><div class="lbl">Selesai Ditangani</div></div>
            <div class="mc red"><div class="ico">⏳</div><div class="val">{proses}</div><div class="lbl">Dalam Proses</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if 'Status' in df.columns:
            fig = px.bar(df, x='Status', color='Status',
                         title="Progres Penanganan Aduan & Pengawasan",
                         color_discrete_map={'Selesai':'#1b5e20','Belum Proses':'#e74c3c'},
                         height=340)
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                              showlegend=False, margin=dict(t=40,b=10,l=0,r=0),
                              title_font=dict(size=13))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⏳ Menghubungkan ke database...")

# ── PETA ────────────────────────────────────────────────────────
with tab_map:
    st.markdown('<div class="sh"><div class="dot"></div><h3>Peta Persebaran TPS</h3><span>32 titik · Kota Soe, Kab. TTS</span></div>', unsafe_allow_html=True)
    df = load_data()
    if not df.empty and 'Latitude' in df.columns and 'Longitude' in df.columns:
        st.map(df[['Latitude','Longitude']].dropna(), zoom=13)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:60px 20px;">
            <div style="font-size:3em;margin-bottom:14px;">🗺️</div>
            <h3 style="color:#1b5e20;margin:0 0 8px;">Peta GIS Sedang Sinkronisasi</h3>
            <p style="color:#999;font-size:0.88em;">Data koordinat 32 titik TPS sedang disiapkan dari AppSheet petugas lapangan.</p>
        </div>
        """, unsafe_allow_html=True)

# ── LOG ─────────────────────────────────────────────────────────
with tab_logs:
    st.markdown('<div class="sh"><div class="dot"></div><h3>Log Pengawasan & Pelaporan</h3><span>Data real-time dari Google Sheets</span></div>', unsafe_allow_html=True)
    df = load_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("⏳ Memuat data...")

# ── BOKASHI ─────────────────────────────────────────────────────
with tab_bokashi:
    df_prod    = load_bokashi_produksi()
    df_katalog = load_bokashi_katalog()

    total_prod    = int(df_prod["Pupuk Diproduksi (kg)"].sum()) if not df_prod.empty and "Pupuk Diproduksi (kg)" in df_prod.columns else 0
    total_terjual = int(df_prod["Pupuk Terjual (kg)"].sum())    if not df_prod.empty and "Pupuk Terjual (kg)"     in df_prod.columns else 0
    total_pad     = int(df_prod["Total Pendapatan"].sum())       if not df_prod.empty and "Total Pendapatan"       in df_prod.columns else 0
    stok_sisa     = int(df_prod["Stok Tersisa"].iloc[-1])        if not df_prod.empty and "Stok Tersisa"           in df_prod.columns and len(df_prod) > 0 else 0

    st.markdown(f"""
    <div class="metric-row">
        <div class="mc"><div class="ico">🌾</div><div class="val">{total_prod:,} kg</div><div class="lbl">Total Diproduksi</div></div>
        <div class="mc red"><div class="ico">🛒</div><div class="val">{total_terjual:,} kg</div><div class="lbl">Total Terjual</div></div>
        <div class="mc blue"><div class="ico">📦</div><div class="val">{stok_sisa:,} kg</div><div class="lbl">Stok Tersisa</div></div>
        <div class="mc gold"><div class="ico">💰</div><div class="val">Rp {total_pad:,.0f}</div><div class="lbl">Total PAD</div></div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sh" style="margin-top:0;"><div class="dot"></div><h3>Grafik Produksi & Penjualan Harian</h3></div>', unsafe_allow_html=True)
        if not df_prod.empty and "Tanggal" in df_prod.columns:
            df_c = df_prod[["Tanggal","Pupuk Diproduksi (kg)","Pupuk Terjual (kg)"]].dropna()
            df_m = df_c.melt(id_vars="Tanggal", var_name="Keterangan", value_name="kg")
            fig  = px.bar(df_m, x="Tanggal", y="kg", color="Keterangan", barmode="group",
                          color_discrete_map={"Pupuk Diproduksi (kg)":"#1b5e20","Pupuk Terjual (kg)":"#c9992a"},
                          height=270)
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                              margin=dict(t=10,b=10,l=0,r=0),
                              legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,font=dict(size=10)),
                              xaxis=dict(title=""), yaxis=dict(title="kg", gridcolor="#f0f0f0"))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⏳ Data produksi belum tersedia.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sh" style="margin-top:0;"><div class="dot"></div><h3>Log Produksi Terbaru</h3><span>10 entri terakhir</span></div>', unsafe_allow_html=True)
        if not df_prod.empty:
            cols_show = ["Tanggal","Pupuk Diproduksi (kg)","Pupuk Terjual (kg)","Total Pendapatan","Pembeli","Stok Tersisa"]
            cols_show = [c for c in cols_show if c in df_prod.columns]
            st.dataframe(df_prod[cols_show].sort_values("Tanggal",ascending=False).head(10),
                         use_container_width=True, hide_index=True)
        else:
            st.info("⏳ Belum ada data.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="sh"><div class="dot"></div><h3>Katalog Produk</h3><span>Rumah Bokashi DLH TTS</span></div>', unsafe_allow_html=True)

        katalog_data = []
        if not df_katalog.empty:
            for _, row in df_katalog.iterrows():
                try:
                    kode    = str(row.iloc[0])
                    nama    = str(row.iloc[1])
                    kemasan = str(row.iloc[2])
                    harga   = int(float(str(row.iloc[3]).replace(",","").replace(".","")))
                    try:    stok_v = int(float(str(row.iloc[4]).replace(",","")))
                    except: stok_v = 1
                    katalog_data.append((kode, nama, kemasan, harga, stok_v))
                except:
                    pass

        if not katalog_data:
            katalog_data = [
                ("BOK-001","Pupuk Bokashi Curah",    "Per kg",         5000,  100),
                ("BOK-002","Bokashi Kemasan 5 kg",   "5 kg / sak",     25000, 50),
                ("BOK-003","Bokashi Kemasan 10 kg",  "10 kg / sak",    48000, 30),
                ("BOK-004","Bokashi Kemasan 25 kg",  "25 kg / karung", 115000, 15),
            ]

        for kode, nama, kemasan, harga, stok_v in katalog_data:
            badge = '<span class="ok">✅ Tersedia</span>' if stok_v > 0 else '<span class="no">⚠️ Habis</span>'
            st.markdown(f"""
            <div class="pc">
                <div>
                    <div class="pn">{nama}</div>
                    <div class="pk">📦 {kemasan} · {kode}</div>
                    <div style="margin-top:5px;">{badge}</div>
                </div>
                <div class="ph">Rp {harga:,}</div>
            </div>
            """, unsafe_allow_html=True)

        import urllib.parse
        wa_number = "6282196444851"
        wa_pesan  = "Halo, saya ingin memesan pupuk bokashi DLH Kab. TTS. Mohon informasi stok dan cara pembayarannya. Terima kasih 🙏"
        wa_link   = f"https://wa.me/{wa_number}?text={urllib.parse.quote(wa_pesan)}"
        st.markdown(f"""
        <div class="ib">
            <h4>📞 Cara Pemesanan</h4>
            <div class="st"><div class="sn">1</div><div>Klik tombol WhatsApp di bawah</div></div>
            <div class="st"><div class="sn">2</div><div>Sebutkan nama, alamat &amp; jumlah pesanan</div></div>
            <div class="st"><div class="sn">3</div><div>Bayar tunai / transfer rekening DLH</div></div>
            <div class="st"><div class="sn">4</div><div>Ambil di Rumah Bokashi, Kota Soe</div></div>
            <div class="st"><div class="sn">5</div><div>Pengiriman tersedia untuk pembelian ≥ 50 kg</div></div>
            <div class="lok">📍 Rumah Bokashi DLH Kab. TTS · Kota Soe · Timor Tengah Selatan</div>
            <a href="{wa_link}" target="_blank" style="display:block;margin-top:14px;text-align:center;background:#25D366;color:white;text-decoration:none;padding:12px 20px;border-radius:50px;font-weight:800;font-size:0.95em;box-shadow:0 4px 14px rgba(37,211,102,0.4);">
                💬 Pesan via WhatsApp — 0821-9644-4851
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sh" style="margin-top:16px;"><div class="dot"></div><h3>Manfaat Pupuk Bokashi</h3></div>
        <div class="mg">
            <div class="mi"><span style="font-size:1.2em;">🌱</span>Memperbaiki struktur &amp; kesuburan tanah</div>
            <div class="mi"><span style="font-size:1.2em;">⚡</span>Mempercepat pertumbuhan tanaman</div>
            <div class="mi"><span style="font-size:1.2em;">♻️</span>Ramah lingkungan dari sampah organik</div>
            <div class="mi"><span style="font-size:1.2em;">💸</span>Lebih murah dari pupuk kimia</div>
            <div class="mi"><span style="font-size:1.2em;">🏘️</span>Mendukung kebersihan Kota Soe</div>
            <div class="mi"><span style="font-size:1.2em;">📈</span>Mendukung PAD &amp; ekonomi sirkular TTS</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 9. FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    <strong>HABOCK Digital</strong> — Sistem Informasi Persampahan &amp; Ekonomi Sirkular Kab. Timor Tengah Selatan<br>
    © 2026 · Bidang Pengelolaan Sampah, Limbah B3 dan Peningkatan Kapasitas · DLH Kab. TTS<br>
    <span class="star">★</span> Proyek Aktualisasi LATSAR CPNS Gelombang 8 Angkatan 274
</div>
""", unsafe_allow_html=True)
