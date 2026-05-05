import streamlit as st
import pandas as pd
import os
import base64
import plotly.express as px

# 1. KONFIGURASI HALAMAN & THEME
st.set_page_config(page_title="HABOCK - DLH KAB. TTS", layout="wide", page_icon="🍃")

# 2. DATA SOURCE (GOOGLE SHEETS)
# Ganti URL ini dengan link publik CSV dari Google Sheet Anda
URL_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_ZOXOlq8tAN3z3zMMMbh1JFS-Sl9LecCVE7gNAoDm_IF0oFDuredZXbtO_rAPF54hlzyervBGwvuq/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(URL_DATA)

# 3. CSS CUSTOM: PREMIUM GOVERNMENT UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Montserrat:wght@800;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8f9fa; }

    /* Header & Title Section */
    .header-container { display: flex; align-items: center; gap: 20px; margin-bottom: 25px; }
    .vertical-line { width: 5px; height: 85px; background: #1b5e20; border-radius: 10px; }
    .header-text h1 { 
        font-family: 'Montserrat', sans-serif; font-size: 2.2em; color: #1b5e20; 
        margin: 0; line-height: 1.1; font-weight: 900;
    }
    .header-text p { margin: 0; color: #636e72; font-size: 0.9em; letter-spacing: 1px; }
    .bidang-tag { 
        background: #1b5e20; color: white; padding: 4px 12px; 
        border-radius: 5px; font-size: 0.75em; font-weight: 700; display: inline-block; margin-top: 8px;
    }

    /* Hero Banner */
    .hero-box {
        height: 380px; border-radius: 35px; overflow: hidden; margin-bottom: 40px;
        background-size: cover; background-position: center 85%;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    .hero-overlay {
        background: rgba(0, 0, 0, 0.6); width: 100%; height: 100%;
        display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
    }
    .banner-title { font-family: 'Montserrat', sans-serif; font-size: 3.5em; color: white; margin: 0; text-shadow: 2px 2px 10px rgba(0,0,0,0.5); }

    /* Buttons */
    .btn-group { display: flex; gap: 15px; margin-top: 25px; }
    .btn-public { 
        background: #ff4757; color: white !important; padding: 14px 35px; 
        border-radius: 50px; text-decoration: none; font-weight: 800; transition: 0.3s;
        border: 2px solid white; box-shadow: 0 10px 20px rgba(255, 71, 87, 0.4);
    }
    .btn-officer { 
        background: #1b5e20; color: white !important; padding: 14px 35px; 
        border-radius: 50px; text-decoration: none; font-weight: 800; transition: 0.3s;
        border: 2px solid white; box-shadow: 0 10px 20px rgba(27, 94, 32, 0.4);
    }
    .btn-public:hover, .btn-officer:hover { transform: translateY(-5px); }

    /* Project Title Card */
    .project-card { 
        background: white; padding: 25px; border-radius: 20px; 
        border-left: 10px solid #1b5e20; margin-bottom: 35px; box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNGSI GAMBAR
def get_image_base64(target):
    files = os.listdir(".")
    img = next((f for f in files if target.lower() in f.lower()), None)
    if img:
        with open(img, 'rb') as f: return base64.b64encode(f.read()).decode()
    return ""

# --- RENDER HEADER ---
logo_pemda = get_image_base64("pemda")
st.markdown(f"""
    <div class="header-container">
        <img src="data:image/png;base64,{logo_pemda}" width="95">
        <div class="vertical-line"></div>
        <div class="header-text">
            <p>PEMERINTAH KABUPATEN TIMOR TENGAH SELATAN</p>
            <h1>DINAS LINGKUNGAN HIDUP</h1>
            <div class="bidang-tag">Bidang Pengelolaan Sampah, Limbah B3 dan Peningkatan Kapasitas</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- RENDER JUDUL PROYEK (LATSAR) ---
st.markdown("""
    <div class="project-card">
        <small style="color: #1b5e20; font-weight: 800; text-transform: uppercase;">Judul Proyek Perubahan (LATSAR CPNS):</small>
        <p style="font-size: 1.1em; color: #2d3436; margin-top: 10px; font-weight: 700; line-height: 1.4;">
            "DIGITALISASI SISTEM PENGAWASAN DAN PELAYANAN INFORMASI PERSAMPAHAN TERINTEGRASI MELALUI IMPLEMENTASI PLATFORM HABOCK PADA BIDANG PENGELOLAAN SAMPAH, LIMBAH B3 DAN PENINGKATAN KAPASITAS DINAS LINGKUNGAN HIDUP KABUPATEN TIMOR TENGAH SELATAN"
        </p>
    </div>
""", unsafe_allow_html=True)

# --- RENDER HERO BANNER ---
bg_kantor = get_image_base64("kantor")
logo_hb = get_image_base64("logo")
st.markdown(f"""
    <div class="hero-box" style='background-image: url("data:image/jpg;base64,{bg_kantor}");'>
        <div class="hero-overlay">
            <div style="display: flex; align-items: center; gap: 20px;">
                <img src="data:image/png;base64,{logo_hb}" width="80">
                <h1 class="banner-title">HABOCK DIGITAL</h1>
            </div>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.3em; font-weight: 300; margin-top: 10px;">
                Sistem Terpadu Pengawasan TPS & Pelayanan Informasi Publik
            </p>
            <div class="btn-group">
                <a href="https://forms.gle/ISI_LINK_GFORM_ANDA" target="_blank" class="btn-public">📩 LAPOR SAMPAH (PUBLIK)</a>
                <a href="https://www.appsheet.com/start/YOUR_APPSHEET_ID" target="_blank" class="btn-officer">👮 PORTAL PETUGAS (UPTD)</a>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- DASHBOARD INTEGRASI ---
tab_stats, tab_map, tab_logs = st.tabs(["📊 Statistik Kinerja", "📍 GIS Pengawasan", "📜 Rekapitulasi Data"])

try:
    df = load_data()
    
    with tab_stats:
        st.subheader("Ringkasan Pengawasan Terpadu")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Laporan", f"{len(df)} Data")
        m2.metric("TPS Terpantau", "24 Titik") # Bisa dihitung dari kolom TPS
        m3.metric("Status Selesai", len(df[df['Status'] == 'Selesai']))
        m4.metric("Dalam Proses", len(df[df['Status'] == 'Belum Proses']))
        
        st.write("---")
        # Grafik Plotly (Sudah bisa jalan karena library sudah oke)
        fig = px.bar(df, x='Status', color='Status', 
                     title="Progres Penanganan Aduan & Pengawasan",
                     color_discrete_map={'Selesai':'#1b5e20', 'Belum Proses':'#ff4757'})
        st.plotly_chart(fig, use_container_width=True)

    with tab_map:
        st.subheader("Peta Persebaran Lokasi (GIS Soe City)")
        # Menampilkan peta jika kolom Latitude & Longitude tersedia di Sheet
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            st.map(df[['Latitude', 'Longitude']])
        else:
            st.info("Peta GIS sedang sinkronisasi dengan data koordinat dari AppSheet Petugas.")

    with tab_logs:
        st.subheader("Data Log Pengawasan & Pelaporan")
        st.dataframe(df, use_container_width=True)

except Exception:
    st.warning("Menghubungkan ke basis data Google Sheets. Pastikan koneksi internet stabil.")

st.markdown("<br><hr><p style='text-align: center; color: #aaa; font-size: 0.8em;'>Sistem Informasi HABOCK Digital v2.0 | © 2026 Bidang Pengelolaan Sampah DLH TTS</p>", unsafe_allow_html=True)