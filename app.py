import streamlit as st
import pandas as pd
import os
import base64
import plotly.express as px
from datetime import datetime
import urllib.parse
import folium
from folium.plugins import MiniMap, Fullscreen
from streamlit_folium import st_folium

st.set_page_config(
    page_title="HABOCK Digital — DLH Kab. TTS",
    layout="wide",
    page_icon="🍃",
    initial_sidebar_state="collapsed"
)

# ── URL DATA ──────────────────────────────────────────────────
SHEET_ID = "1zyZ7cDh_5M5K-VCNt_sQllmrsoPVGtbC6aJ9DSfL1NE"
URL_DATA             = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0" # Ganti gid=0 jika data utama bukan di tab pertama
URL_BOKASHI_PRODUKSI = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=538980514"
URL_BOKASHI_KATALOG  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1511411011"
URL_MASTER           = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=YOUR_MASTER_GID" # Ganti YOUR_MASTER_GID dengan angka GID tab master kamu
# ── KOORDINAT FALLBACK 32 TPS ─────────────────────────────────
TPS_FALLBACK = [
    {"id":"01","nama":"Pasar Inpres",      "kel":"Kota Soe",     "lat":-9.8618,"lng":124.2834},
    {"id":"02","nama":"Km 3",              "kel":"Karang Siri",  "lat":-9.8701,"lng":124.2762},
    {"id":"03","nama":"Perumahan",         "kel":"Kota Soe",     "lat":-9.8575,"lng":124.2781},
    {"id":"04","nama":"Puskesmas Soe",     "kel":"Kota Soe",     "lat":-9.8545,"lng":124.2853},
    {"id":"05","nama":"Km 7",              "kel":"Molo Selatan", "lat":-9.8783,"lng":124.2698},
    {"id":"06","nama":"SD Negeri 1 Soe",   "kel":"Kota Soe",     "lat":-9.8612,"lng":124.2901},
    {"id":"07","nama":"Terminal Soe",      "kel":"Kota Soe",     "lat":-9.8498,"lng":124.2745},
    {"id":"08","nama":"Stadion Olahraga",  "kel":"Kota Soe",     "lat":-9.8671,"lng":124.2952},
    {"id":"09","nama":"Lapangan Bola",     "kel":"Karang Siri",  "lat":-9.8748,"lng":124.2883},
    {"id":"10","nama":"Pasar Malam",       "kel":"Kota Soe",     "lat":-9.8561,"lng":124.2692},
    {"id":"11","nama":"Jl. Diponegoro",    "kel":"Kota Soe",     "lat":-9.8692,"lng":124.2801},
    {"id":"12","nama":"Kantor Bupati TTS", "kel":"Kota Soe",     "lat":-9.8594,"lng":124.2841},
    {"id":"13","nama":"RSUD Soe",          "kel":"Kota Soe",     "lat":-9.8532,"lng":124.2921},
    {"id":"14","nama":"Km 4",              "kel":"Karang Siri",  "lat":-9.8722,"lng":124.2731},
    {"id":"15","nama":"Jl. Sudirman",      "kel":"Kota Soe",     "lat":-9.8641,"lng":124.2872},
    {"id":"16","nama":"Gereja Katedral",   "kel":"Kota Soe",     "lat":-9.8572,"lng":124.2812},
    {"id":"17","nama":"Komplek DLH",       "kel":"Kota Soe",     "lat":-9.8658,"lng":124.2771},
    {"id":"18","nama":"Pasar Besi",        "kel":"Karang Siri",  "lat":-9.8731,"lng":124.2831},
    {"id":"19","nama":"Km 10",             "kel":"Molo Selatan", "lat":-9.8821,"lng":124.2651},
    {"id":"20","nama":"Jl. Kartini",       "kel":"Kota Soe",     "lat":-9.8601,"lng":124.2931},
    {"id":"21","nama":"Masjid Raya Soe",   "kel":"Kota Soe",     "lat":-9.8551,"lng":124.2791},
    {"id":"22","nama":"Terminal Lama",     "kel":"Kota Soe",     "lat":-9.8471,"lng":124.2721},
    {"id":"23","nama":"Jl. Ahmad Yani",    "kel":"Kota Soe",     "lat":-9.8681,"lng":124.2901},
    {"id":"24","nama":"Pusat Kota",        "kel":"Kota Soe",     "lat":-9.8611,"lng":124.2831},
    {"id":"25","nama":"Km 2",              "kel":"Karang Siri",  "lat":-9.8691,"lng":124.2851},
    {"id":"26","nama":"Kec. Molo",         "kel":"Molo Selatan", "lat":-9.8451,"lng":124.2681},
    {"id":"27","nama":"Jl. Veteran",       "kel":"Karang Siri",  "lat":-9.8741,"lng":124.2911},
    {"id":"28","nama":"Pasar Rabu",        "kel":"Kota Soe",     "lat":-9.8651,"lng":124.2711},
    {"id":"29","nama":"Kec. Kie",          "kel":"Kie",          "lat":-9.8791,"lng":124.2991},
    {"id":"30","nama":"Jl. Patimura",      "kel":"Kota Soe",     "lat":-9.8581,"lng":124.2751},
    {"id":"31","nama":"Kel. Karang Siri",  "kel":"Karang Siri",  "lat":-9.8761,"lng":124.2941},
    {"id":"32","nama":"Rumah Bokashi DLH", "kel":"Kota Soe",     "lat":-9.8631,"lng":124.2691},
]

@st.cache_data(ttl=60)
def load_data():
    try: return pd.read_csv(URL_DATA)
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def load_master():
    try:
        df = pd.read_csv(URL_MASTER)
        df.columns = df.columns.str.strip()
        if "Latitude" in df.columns and "Longitude" in df.columns:
            df["Latitude"]  = pd.to_numeric(df["Latitude"],  errors="coerce")
            df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
            df = df.dropna(subset=["Latitude","Longitude"])
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def load_bokashi_produksi():
    try:
        df = pd.read_csv(URL_BOKASHI_PRODUKSI, skiprows=2)
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=["Tanggal"])
        df = df[df["Tanggal"].astype(str).str.match(r'\d{2}/\d{2}/\d{4}')]
        df["Tanggal"] = pd.to_datetime(df["Tanggal"], format="%d/%m/%Y", errors="coerce")
        for col in ["Bahan Baku Masuk (kg)","Pupuk Diproduksi (kg)","Pupuk Terjual (kg)",
                    "Harga/kg","Total Pendapatan","Stok Tersisa"]:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",","").str.replace(".",""),
                    errors="coerce").fillna(0)
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def load_bokashi_katalog():
    try:
        df = pd.read_csv(URL_BOKASHI_KATALOG, skiprows=2)
        df.columns = df.columns.str.strip()
        return df[df.iloc[:,0].astype(str).str.startswith("BOK-")]
    except: return pd.DataFrame()

def get_img(target):
    files = os.listdir(".")
    img = next((f for f in files if target.lower() in f.lower()), None)
    if img:
        with open(img,'rb') as f: return base64.b64encode(f.read()).decode()
    return ""

logo_pemda = get_img("pemda")
logo_hb    = get_img("logo")
bg_kantor  = get_img("kantor")

_map_counter = {"n": 0}

def render_peta_gis(height=420, show_stats=True):
    _map_counter["n"] += 1
    map_key = f"habock_map_{_map_counter['n']}"

    WARNA = {
        "Selesai":       "#22c55e",
        "Sedang Proses": "#f59e0b",
        "Belum Proses":  "#ef4444",
        "Menunggu":      "#60a5fa",
    }
    BG_PILL = {
        "Selesai":       ("#d4f7dc","#1a5c24"),
        "Sedang Proses": ("#fef3c7","#92400e"),
        "Belum Proses":  ("#fee2e2","#991b1b"),
        "Menunggu":      ("#e0f2fe","#075985"),
    }

    df_main   = load_data()
    df_master = load_master()

    status_dict = {}
    if not df_main.empty:
        for col_k in ["Kode TPS","ID TPS","TPS","Lokasi"]:
            if col_k in df_main.columns and "Status" in df_main.columns:
                for _, row in df_main.iterrows():
                    k = str(row.get(col_k,"")).strip().lstrip("TPS-").lstrip("0")
                    status_dict[k] = str(row.get("Status","Selesai")).strip()
                break

    use_sheets = (not df_master.empty
                  and "Latitude" in df_master.columns
                  and "Longitude" in df_master.columns)

    titik = []
    if use_sheets:
        for _, row in df_master.iterrows():
            kode = str(row.get("Kode TPS", row.get("ID TPS",""))).strip().lstrip("TPS-").lstrip("0")
            titik.append({
                "id":     kode,
                "nama":   str(row.get("Nama TPS","TPS")),
                "kel":    str(row.get("Kelurahan","—")),
                "lat":    float(row["Latitude"]),
                "lng":    float(row["Longitude"]),
                "status": status_dict.get(kode, str(row.get("Status","Selesai"))),
            })
    else:
        for t in TPS_FALLBACK:
            k = t["id"].lstrip("0")
            titik.append({**t, "status": status_dict.get(k,"Selesai")})

    if show_stats:
        cnt = {"Selesai":0,"Sedang Proses":0,"Belum Proses":0,"Menunggu":0}
        for t in titik:
            s = t["status"]
            cnt[s] = cnt.get(s, 0) + 1

        st.markdown(f"""
        <div class="map-stat-grid">
          <div class="map-stat green"><div class="msv">{cnt.get('Selesai',0)}</div><div class="msl">✅ Selesai</div></div>
          <div class="map-stat amber"><div class="msv">{cnt.get('Sedang Proses',0)}</div><div class="msl">🔄 Sedang</div></div>
          <div class="map-stat red"><div class="msv">{cnt.get('Belum Proses',0)}</div><div class="msl">🚨 Belum</div></div>
          <div class="map-stat blue"><div class="msv">{cnt.get('Menunggu',0)}</div><div class="msl">🕐 Tunggu</div></div>
        </div>
        """, unsafe_allow_html=True)

    sumber = "📡 Google Sheets" if use_sheets else "⚠️ Koordinat estimasi"
    st.markdown(f"""
    <div class="map-header">
      <span class="map-title">🗺️ Peta GIS · 32 Titik TPS Kota Soe</span>
      <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
        <span class="map-chip">{sumber}</span>
        <span class="map-chip green-chip">🔄 60s</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    m = folium.Map(location=[-9.862,124.283], zoom_start=14,
                   tiles="CartoDB Positron", prefer_canvas=True)
    Fullscreen(position="topright").add_to(m)
    MiniMap(tile_layer="CartoDB Positron", toggle_display=True,
            position="bottomright", width=100, height=80).add_to(m)

    for t in titik:
        s   = t["status"]
        col = WARNA.get(s,"#22c55e")
        bg_c, txt_c = BG_PILL.get(s,("#e6f7ea","#1a5c24"))
        num = t["id"].zfill(2)

        popup_html = f"""
        <div style="font-family:sans-serif;min-width:170px;border-radius:8px;overflow:hidden;">
          <div style="background:#071a09;color:#fff;padding:8px 12px;">
            <b style="font-size:12px;">TPS-{num} · {t['nama']}</b><br>
            <small style="color:rgba(255,255,255,.5);">Kel. {t['kel']}</small>
          </div>
          <div style="padding:8px 12px;background:#fff;">
            <span style="background:{bg_c};color:{txt_c};padding:2px 9px;border-radius:10px;
                         font-size:11px;font-weight:700;">{s}</span>
            <div style="margin-top:6px;font-size:10px;color:#888;">
              📍 {t['lat']:.4f}, {t['lng']:.4f}
            </div>
          </div>
        </div>"""

        folium.CircleMarker(
            location=[t["lat"],t["lng"]], radius=11,
            color="white", weight=2.5,
            fill=True, fill_color=col, fill_opacity=0.92,
            tooltip=folium.Tooltip(
                f"<b>TPS-{num} · {t['nama']}</b><br>"
                f"<span style='color:{col};font-weight:700;'>{s}</span>",
                sticky=True),
            popup=folium.Popup(popup_html, max_width=220),
        ).add_to(m)

        folium.Marker(
            location=[t["lat"],t["lng"]],
            icon=folium.DivIcon(
                html=f'<div style="font-size:7px;font-weight:800;color:white;'
                     f'text-align:center;line-height:1;margin-top:-1px;">{num}</div>',
                icon_size=(22,13), icon_anchor=(11,6))
        ).add_to(m)

    folium.Marker(
        location=[-9.8631,124.2691],
        icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
        tooltip=folium.Tooltip("<b>🌿 Rumah Bokashi DLH TTS</b>", sticky=True),
        popup=folium.Popup(
            "<div style='font-family:sans-serif;padding:4px;'>"
            "<b>🌿 Rumah Bokashi DLH TTS</b><br>"
            "<small style='color:#888;'>Pusat produksi pupuk bokashi</small></div>",
            max_width=180),
    ).add_to(m)

    legend = """
    <div style="position:absolute;bottom:28px;left:8px;z-index:1000;
                background:white;border-radius:8px;padding:7px 10px;
                box-shadow:0 2px 8px rgba(0,0,0,.15);font-size:10px;font-family:sans-serif;">
      <b style="color:#071a09;">Status TPS</b>
      <div style="display:flex;align-items:center;gap:4px;margin:3px 0;">
        <div style="width:9px;height:9px;border-radius:50%;background:#22c55e;"></div>Selesai
      </div>
      <div style="display:flex;align-items:center;gap:4px;margin:3px 0;">
        <div style="width:9px;height:9px;border-radius:50%;background:#f59e0b;"></div>Sedang
      </div>
      <div style="display:flex;align-items:center;gap:4px;margin:3px 0;">
        <div style="width:9px;height:9px;border-radius:50%;background:#ef4444;"></div>Belum
      </div>
      <div style="display:flex;align-items:center;gap:4px;margin:3px 0;">
        <div style="width:9px;height:9px;border-radius:50%;background:#60a5fa;"></div>Tunggu
      </div>
      <div style="display:flex;align-items:center;gap:4px;margin:4px 0 0;">
        <span style="font-size:11px;">🌿</span>Rumah Bokashi
      </div>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))

    st_folium(m, use_container_width=True, height=height,
              returned_objects=[], key=map_key)

    if not use_sheets:
        st.caption("📌 Koordinat masih estimasi. Isi kolom Latitude & Longitude di sheet HABOCK Master Data.")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --g9:#051408; --g8:#0a2210; --g7:#0f3318; --g6:#165e24;
  --g5:#1f8433; --g4:#28a641; --g3:#40c45a; --g2:#8de09d; --g1:#e0f5e4;
  --a5:#b86b00; --a4:#d4880a; --a3:#f0a820; --a1:#fef3d6;
  --n9:#101810; --n7:#253025; --n5:#485649; --n3:#8da08e; --n2:#cedad0; --n1:#eef4ef;
  --white:#ffffff; --r5:#dc2626; --r1:#fee2e2;
  --rad-sm:6px; --rad-md:12px; --rad-lg:16px;
  --sh-sm:0 1px 4px rgba(0,0,0,.07);
  --sh-md:0 4px 16px rgba(0,0,0,.09);
  --sh-lg:0 10px 36px rgba(0,0,0,.13);
}

html,body,[class*="css"]{font-family:'DM Sans',sans-serif;-webkit-font-smoothing:antialiased;}
.stApp{background:var(--n1);}
.block-container{padding:0!important;max-width:100%!important;}
section[data-testid="stSidebar"]{display:none!important;}
div[data-testid="stToolbar"]{display:none!important;}
.stDeployButton{display:none!important;}

.ticker-wrap{background:var(--g8);height:34px;overflow:hidden;display:flex;align-items:center;}
.ticker-label{background:linear-gradient(135deg,var(--a4),var(--a5));color:#fff;padding:0 14px;height:100%;display:flex;align-items:center;font-size:.68em;font-weight:800;letter-spacing:1px;text-transform:uppercase;white-space:nowrap;flex-shrink:0;clip-path:polygon(0 0,calc(100% - 8px) 0,100% 50%,calc(100% - 8px) 100%,0 100%);padding-right:20px;}
.ticker-track{display:flex;gap:40px;align-items:center;animation:ticker 32s linear infinite;white-space:nowrap;padding-left:20px;}
.ticker-track:hover{animation-play-state:paused;}
@keyframes ticker{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.t-item{font-size:.7em;color:rgba(255,255,255,.78);display:inline-flex;align-items:center;gap:5px;}
.t-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;}
.t-dot.ok{background:#40c45a;box-shadow:0 0 5px #40c45a;}
.t-dot.warn{background:#f0a820;box-shadow:0 0 5px #f0a820;}
.t-dot.busy{background:#60a5fa;box-shadow:0 0 5px #60a5fa;}

.topbar{background:linear-gradient(135deg,var(--g9),var(--g8));padding:0 20px;height:60px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.08);box-shadow:0 3px 20px rgba(0,0,0,.4);}
.topbar-l{display:flex;align-items:center;gap:12px;overflow:hidden;}
.t-sep{width:1px;height:30px;background:rgba(255,255,255,.15);flex-shrink:0;}
.t-inst .sub{font-size:.58em;color:rgba(255,255,255,.42);letter-spacing:.7px;text-transform:uppercase;}
.t-inst .main{font-family:'Syne',sans-serif;font-size:.84em;font-weight:700;color:#fff;white-space:nowrap;}
.t-brand{display:flex;align-items:center;gap:8px;flex-shrink:0;}
.t-brand .nm{font-family:'Syne',sans-serif;font-size:1.45em;font-weight:800;color:#fff;letter-spacing:2px;text-shadow:0 0 16px rgba(64,196,90,.4);}
.t-brand .tg{font-size:.55em;color:rgba(255,255,255,.35);letter-spacing:1.5px;text-transform:uppercase;}
.topbar-r{display:flex;align-items:center;gap:8px;flex-shrink:0;}
.t-clock{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.13);border-radius:16px;padding:5px 11px;font-size:.67em;color:rgba(255,255,255,.72);white-space:nowrap;}
.t-cta{background:linear-gradient(135deg,var(--a4),var(--a5));color:#fff!important;border-radius:16px;padding:7px 15px;font-size:.72em;font-weight:800;text-decoration:none!important;box-shadow:0 3px 12px rgba(212,136,10,.45);}

.status-bar{background:var(--g7);padding:8px 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.06);gap:8px;flex-wrap:wrap;}
.sb-pills{display:flex;gap:6px;flex-wrap:wrap;}
.sb-pill{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:3px 10px;font-size:.67em;color:rgba(255,255,255,.68);display:flex;align-items:center;gap:5px;white-space:nowrap;}
.sb-pill.active{background:rgba(64,196,90,.15);border-color:rgba(64,196,90,.38);color:#5ee07a;}
.sb-pill.warn{background:rgba(240,168,32,.11);border-color:rgba(240,168,32,.28);color:var(--a3);}

.hero{background:linear-gradient(135deg,var(--g9) 0%,#071a0c 40%,#0a1f0d 100%);padding:44px 24px 0;position:relative;overflow:hidden;}
.hero-bg-img{position:absolute;top:0;right:0;width:50%;height:100%;background-size:cover;background-position:center top;}
.hero-bg-overlay{position:absolute;top:0;right:0;width:50%;height:100%;background:linear-gradient(90deg,var(--g9) 0%,#0a1f0d 28%,rgba(7,26,12,.55) 70%,rgba(7,26,12,.15) 100%);}
.hero-deco{position:absolute;top:-80px;left:-80px;width:340px;height:340px;border-radius:50%;background:radial-gradient(circle,rgba(40,166,65,.16) 0%,transparent 65%);pointer-events:none;}
.hero-inner{position:relative;z-index:2;max-width:520px;}
.hero-eyebrow{display:inline-flex;align-items:center;gap:6px;background:rgba(64,196,90,.14);border:1px solid rgba(64,196,90,.42);border-radius:20px;padding:5px 14px;font-size:.68em;color:#6de08a;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:18px;box-shadow:0 0 16px rgba(64,196,90,.1);}
.hero-title{font-family:'Syne',sans-serif;font-size:3.8em;font-weight:800;line-height:.88;letter-spacing:-2px;margin:0 0 14px;}
.hero-title .line1{display:block;color:#ffffff;text-shadow:0 0 30px rgba(255,255,255,.2),0 2px 4px rgba(0,0,0,.6);}
.hero-title .line2{display:block;background:linear-gradient(90deg,#4ade80 0%,#34d399 40%,#22d3ee 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;filter:drop-shadow(0 0 18px rgba(74,222,128,.6));}
.hero-sub{font-size:.9em;color:rgba(255,255,255,.68);font-weight:400;max-width:400px;line-height:1.68;margin:0 0 26px;}
.hero-btns{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:38px;}
.btn-hero-p{display:inline-flex;align-items:center;gap:7px;background:linear-gradient(135deg,var(--a4),var(--a5));color:#fff!important;padding:12px 22px;border-radius:40px;text-decoration:none!important;font-weight:800;font-size:.86em;box-shadow:0 5px 20px rgba(212,136,10,.45);transition:all .2s;}
.btn-hero-p:hover{transform:translateY(-2px);box-shadow:0 8px 26px rgba(212,136,10,.55);}
.btn-hero-s{display:inline-flex;align-items:center;gap:7px;background:rgba(255,255,255,.1);color:#fff!important;padding:12px 22px;border-radius:40px;text-decoration:none!important;font-weight:600;font-size:.86em;border:1.5px solid rgba(255,255,255,.3);backdrop-filter:blur(6px);transition:all .2s;}
.btn-hero-s:hover{background:rgba(255,255,255,.18);transform:translateY(-2px);}

.kpi-strip{background:rgba(0,0,0,.32);border-top:1px solid rgba(255,255,255,.09);display:grid;grid-template-columns:repeat(4,1fr);backdrop-filter:blur(8px);}
.kpi{padding:16px 0;text-align:center;border-right:1px solid rgba(255,255,255,.07);}
.kpi:last-child{border-right:none;}
.kpi-val{font-family:'Syne',sans-serif;font-size:1.8em;font-weight:800;color:#fff;display:block;line-height:1;text-shadow:0 0 18px rgba(255,255,255,.25);}
.kpi-lbl{font-size:.6em;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.8px;display:block;margin-top:4px;}

.wrap{padding:20px 16px;max-width:1440px;margin:0 auto;}

.ring-section{background:var(--g8);border-radius:var(--rad-lg);padding:20px 22px;margin-bottom:16px;display:flex;align-items:center;gap:24px;box-shadow:var(--sh-lg);}
.ring-wrap{position:relative;flex-shrink:0;}
.ring-label{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;}
.ring-pct{font-family:'Syne',sans-serif;font-size:1.3em;font-weight:800;color:#fff;display:block;line-height:1;}
.ring-sub{font-size:.58em;color:rgba(255,255,255,.4);display:block;margin-top:2px;}
.ring-info{flex:1;min-width:0;}
.ring-title{font-family:'Syne',sans-serif;font-size:1em;font-weight:700;color:#fff;margin:0 0 5px;}
.ring-desc{font-size:.78em;color:rgba(255,255,255,.5);line-height:1.55;margin:0 0 12px;}
.ring-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.rs-item{background:rgba(255,255,255,.06);border-radius:6px;padding:8px 10px;}
.rs-val{font-family:'Syne',sans-serif;font-size:1em;font-weight:800;color:var(--a3);display:block;line-height:1;}
.rs-lbl{font-size:.6em;color:rgba(255,255,255,.35);text-transform:uppercase;letter-spacing:.4px;display:block;margin-top:2px;}

.stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:16px;}
.stat-card{background:var(--white);border-radius:var(--rad-lg);padding:16px 14px;box-shadow:var(--sh-md);position:relative;overflow:hidden;}
.sc-bar{position:absolute;top:0;left:0;right:0;height:3px;}
.sc-bar.g{background:linear-gradient(90deg,var(--g5),var(--g3));}
.sc-bar.a{background:linear-gradient(90deg,var(--a5),var(--a3));}
.sc-bar.r{background:linear-gradient(90deg,#b91c1c,#f87171);}
.sc-bar.n{background:linear-gradient(90deg,var(--n5),var(--n3));}
.sc-ico{font-size:1.5em;margin-bottom:6px;}
.sc-val{font-family:'Syne',sans-serif;font-size:1.6em;font-weight:800;color:var(--n9);line-height:1;margin-bottom:2px;}
.sc-lbl{font-size:.64em;font-weight:600;color:var(--n3);text-transform:uppercase;letter-spacing:.4px;}

.panel{background:var(--white);border-radius:var(--rad-lg);padding:16px 18px;box-shadow:var(--sh-md);margin-bottom:14px;}
.ph{display:flex;align-items:center;gap:7px;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--n1);}
.ph-dot{width:6px;height:6px;border-radius:50%;background:var(--g4);flex-shrink:0;}
.ph-title{margin:0;font-family:'Syne',sans-serif;font-size:.9em;font-weight:700;color:var(--n7);}
.ph-sub{font-size:.68em;color:var(--n3);margin-left:auto;}

.svc-grid{display:grid;grid-template-columns:1fr;gap:12px;margin-bottom:16px;}
.svc{border-radius:var(--rad-lg);padding:18px;transition:transform .2s,box-shadow .2s;}
.svc:hover{transform:translateY(-3px);box-shadow:var(--sh-lg);}
.svc.g{background:linear-gradient(145deg,var(--g8),var(--g6));color:#fff;}
.svc.r{background:linear-gradient(145deg,#7f1d1d,#b91c1c);color:#fff;}
.svc.a{background:linear-gradient(145deg,#3d1500,#7a4800);color:#fff;}
.svc-ico{font-size:1.9em;margin-bottom:10px;}
.svc-title{font-family:'Syne',sans-serif;font-size:.95em;font-weight:700;margin-bottom:6px;}
.svc-desc{font-size:.8em;line-height:1.55;opacity:.72;margin-bottom:10px;}
.svc-tag{font-size:.68em;font-weight:700;padding:4px 10px;border-radius:16px;background:rgba(255,255,255,.13);display:inline-block;}

.flow{display:flex;align-items:flex-start;justify-content:center;gap:2px;flex-wrap:wrap;padding:8px 0;}
.fstep{display:flex;flex-direction:column;align-items:center;padding:10px 10px;border-radius:10px;min-width:76px;text-align:center;}
.fstep-ico{font-size:1.4em;margin-bottom:4px;}
.fstep-lbl{font-size:.68em;font-weight:700;margin-bottom:1px;}
.fstep-sub{font-size:.58em;color:var(--n3);}
.farr{color:var(--n2);font-size:1em;padding:0 1px;margin-top:16px;}

.gis-panel{background:var(--white);border-radius:var(--rad-lg);padding:14px 16px;box-shadow:var(--sh-md);margin-bottom:14px;}
.map-stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-bottom:10px;}
.map-stat{border-radius:8px;padding:9px 6px;text-align:center;}
.map-stat.green{background:#d4f7dc;}.map-stat.amber{background:#fef3c7;}
.map-stat.red{background:#fee2e2;}.map-stat.blue{background:#e0f2fe;}
.msv{font-family:'Syne',sans-serif;font-size:1.4em;font-weight:800;line-height:1;}
.map-stat.green .msv{color:#1a5c24;}.map-stat.amber .msv{color:#92400e;}
.map-stat.red .msv{color:#991b1b;}.map-stat.blue .msv{color:#075985;}
.msl{font-size:.62em;font-weight:600;margin-top:2px;}
.map-stat.green .msl{color:#22873b;}.map-stat.amber .msl{color:#b45309;}
.map-stat.red .msl{color:#dc2626;}.map-stat.blue .msl{color:#0284c7;}
.map-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:6px;}
.map-title{font-family:'Syne',sans-serif;font-size:.86em;font-weight:700;color:var(--n7);}
.map-chip{background:#f0f4f0;border-radius:10px;padding:2px 8px;font-size:.63em;color:var(--n5);}
.green-chip{background:#e0f5e4;color:#1a5c24;}

.prod-card{background:var(--n1);border:1px solid var(--n2);border-radius:10px;padding:11px 13px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;transition:all .18s;}
.prod-card:hover{border-color:var(--g4);background:var(--g1);transform:translateX(4px);}
.prod-nm{font-weight:700;color:var(--n7);font-size:.87em;}
.prod-km{font-size:.66em;color:var(--n3);margin-top:1px;}
.prod-ph{font-family:'Syne',sans-serif;font-size:1em;font-weight:800;color:var(--g6);}
.b-ok{background:var(--g2);color:var(--g7);padding:1px 6px;border-radius:8px;font-size:.62em;font-weight:700;}
.b-no{background:var(--r1);color:var(--r5);padding:1px 6px;border-radius:8px;font-size:.62em;font-weight:700;}

.order-box{background:linear-gradient(140deg,var(--g8),var(--g6));border-radius:var(--rad-lg);padding:16px 18px;color:#fff;margin-top:10px;}
.order-box h4{margin:0 0 10px;font-family:'Syne',sans-serif;font-size:.88em;font-weight:700;}
.ostep{display:flex;align-items:flex-start;gap:8px;margin-bottom:7px;font-size:.76em;line-height:1.4;}
.onum{background:rgba(255,255,255,.14);border-radius:50%;width:18px;height:18px;min-width:18px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.68em;}
.oloc{background:rgba(255,255,255,.08);border-radius:6px;padding:6px 10px;margin-top:9px;font-size:.73em;}
.btn-wa{display:block;margin-top:10px;text-align:center;background:#25D366;color:#fff!important;text-decoration:none!important;padding:10px 18px;border-radius:40px;font-weight:800;font-size:.82em;box-shadow:0 4px 14px rgba(37,211,102,.38);}

.bene-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:10px;}
.bene{background:var(--g1);border:1px solid var(--g2);border-radius:7px;padding:8px 10px;display:flex;align-items:flex-start;gap:6px;font-size:.74em;color:var(--n7);line-height:1.35;}

.qr-section{background:linear-gradient(135deg,var(--g8),var(--g7));border-radius:var(--rad-lg);padding:22px 18px;margin-top:16px;margin-bottom:16px;box-shadow:var(--sh-lg);}
.qr-title{font-family:'Syne',sans-serif;font-size:1.05em;font-weight:800;color:#fff;text-align:center;margin:0 0 5px;}
.qr-sub{font-size:.76em;color:rgba(255,255,255,.48);text-align:center;margin:0 0 20px;}
.qr-grid{display:grid;grid-template-columns:1fr;gap:12px;}
.qr-item{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:16px 14px;text-align:center;}
.qr-item-label{font-size:.76em;font-weight:700;color:rgba(255,255,255,.85);margin-bottom:10px;display:block;}
.qr-box{width:76px;height:76px;background:#fff;border-radius:8px;margin:0 auto 8px;display:flex;align-items:center;justify-content:center;font-size:1.8em;}
.qr-url{font-size:.58em;color:rgba(255,255,255,.32);word-break:break-all;line-height:1.4;}
.qr-btn{display:inline-block;margin-top:8px;background:linear-gradient(135deg,var(--a4),var(--a5));color:#fff!important;text-decoration:none!important;padding:5px 13px;border-radius:16px;font-size:.68em;font-weight:800;}

.footer{background:linear-gradient(135deg,var(--g9),var(--g8));padding:24px 20px 16px;margin-top:24px;border-top:1px solid rgba(255,255,255,.07);}
.footer-brand .name{font-family:'Syne',sans-serif;font-size:1.2em;font-weight:800;color:#fff;margin-bottom:6px;}
.footer-brand .name span{color:var(--a3);}
.footer-brand p{font-size:.76em;color:rgba(255,255,255,.38);line-height:1.55;}
.footer-col{margin-top:18px;}
.footer-col h4{font-family:'Syne',sans-serif;font-size:.72em;font-weight:700;color:rgba(255,255,255,.45);letter-spacing:.8px;text-transform:uppercase;margin:0 0 8px;}
.footer-col p,.footer-col a{font-size:.76em;color:rgba(255,255,255,.4);line-height:1.8;text-decoration:none!important;display:block;}
.footer-col a:hover{color:var(--a3);}
.footer-bottom{border-top:1px solid rgba(255,255,255,.07);padding-top:14px;margin-top:18px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;}
.footer-bottom p{font-size:.66em;color:rgba(255,255,255,.22);}
.footer-badge{background:rgba(212,136,10,.14);border:1px solid rgba(212,136,10,.28);border-radius:14px;padding:3px 10px;font-size:.64em;color:var(--a3);font-weight:700;}

.stTabs [data-baseweb="tab-list"]{background:var(--white)!important;border-radius:var(--rad-md)!important;padding:3px!important;box-shadow:var(--sh-sm)!important;gap:2px!important;margin-bottom:8px!important;}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;font-weight:600!important;font-size:.78em!important;padding:7px 12px!important;color:var(--n5)!important;font-family:'DM Sans',sans-serif!important;}
.stTabs [aria-selected="true"]{background:var(--g8)!important;color:#fff!important;}

@media(min-width:640px){
  .wrap{padding:24px 28px;}
  .stats-grid{grid-template-columns:repeat(4,1fr);}
  .svc-grid{grid-template-columns:repeat(3,1fr);}
  .qr-grid{grid-template-columns:repeat(3,1fr);}
  .hero{padding:52px 44px 0;}
  .hero-title{font-size:4.6em;}
  .topbar{padding:0 28px;height:64px;}
  .status-bar{padding:9px 28px;}
  .footer{padding:32px 36px 20px;}
}

@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.topbar,.hero{animation:fadeUp .4s ease both;}
.wrap{animation:fadeUp .4s ease .1s both;}
</style>
""", unsafe_allow_html=True)

# TICKER
now_dt  = datetime.now()
now_str = now_dt.strftime("%d %b %Y · %H:%M WITA")

df_main      = load_data()
ticker_items = []
if not df_main.empty and 'Lokasi' in df_main.columns:
    for _, row in df_main.tail(8).iterrows():
        lok = row.get('Lokasi','TPS')
        s   = row.get('Status','')
        if s == 'Selesai':
            ticker_items.append(f'<span class="t-item"><span class="t-dot ok"></span>{lok} — Selesai diangkut</span>')
        elif s == 'Belum Proses':
            ticker_items.append(f'<span class="t-item"><span class="t-dot warn"></span>{lok} — Menunggu petugas</span>')
        else:
            ticker_items.append(f'<span class="t-item"><span class="t-dot busy"></span>{lok} — Sedang diproses</span>')

if not ticker_items:
    ticker_items = [
        '<span class="t-item"><span class="t-dot ok"></span>TPS-01 Pasar Inpres — Selesai 04.15 WITA</span>',
        '<span class="t-item"><span class="t-dot ok"></span>TPS-05 Km 7 — Selesai 04.42 WITA</span>',
        '<span class="t-item"><span class="t-dot warn"></span>TPS-12 Terminal Lama — Menunggu petugas</span>',
        '<span class="t-item"><span class="t-dot ok"></span>TPS-03 Perumahan — Selesai 05.10 WITA</span>',
        '<span class="t-item"><span class="t-dot busy"></span>TPS-18 Jl. Diponegoro — Sedang diangkut</span>',
        '<span class="t-item"><span class="t-dot ok"></span>TPS-07 Puskesmas — Selesai 05.30 WITA</span>',
        '<span class="t-item"><span class="t-dot warn"></span>TPS-22 Pasar Malam — Penuh, segera angkut</span>',
        '<span class="t-item"><span class="t-dot ok"></span>TPS-09 Lap. Olahraga — Selesai 05.55 WITA</span>',
    ]

ticker_html = "".join(ticker_items * 2)
st.markdown(f"""
<div class="ticker-wrap">
  <div class="ticker-label">🔴 LIVE</div>
  <div style="overflow:hidden;flex:1;">
    <div class="ticker-track">{ticker_html}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# TOPBAR
gform    = "https://docs.google.com/forms/d/e/1FAIpQLSejAQXpYJh_v9QZeAaoyqy66puWQutFnV7V6Ux9od-uMWr0UQ/viewform"
appsheet = "https://www.appsheet.com/start/YOUR_APPSHEET_ID"

st.markdown(f"""
<div class="topbar">
  <div class="topbar-l">
    {'<img src="data:image/png;base64,' + logo_pemda + '" height="34" style="border-radius:6px;flex-shrink:0;">' if logo_pemda else ''}
    <div class="t-sep"></div>
    <div class="t-inst">
      <div class="sub">Kab. Timor Tengah Selatan</div>
      <div class="main">Dinas Lingkungan Hidup</div>
    </div>
    <div class="t-sep"></div>
    <div class="t-brand">
      {'<img src="data:image/png;base64,' + logo_hb + '" height="28" style="border-radius:5px;">' if logo_hb else ''}
      <div>
        <div class="nm">HABOCK</div>
        <div class="tg">Sistem Informasi</div>
      </div>
    </div>
  </div>
  <div class="topbar-r">
    <span class="t-clock">🕐 {now_str}</span>
    <a href="{gform}" target="_blank" class="t-cta">📩 Lapor</a>
  </div>
</div>
""", unsafe_allow_html=True)

# STATUS BAR
jam = now_dt.hour
if 3 <= jam < 7:    sst="active"; slbl="Shift Subuh Aktif · 03.00–07.00"
elif 7 <= jam < 16: sst="warn";   slbl="Jam Kantor · 07.00–16.00"
else:               sst="";       slbl="Di Luar Jam Operasional"

hari     = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"][now_dt.weekday()]
is_wkday = now_dt.weekday() < 5

st.markdown(f"""
<div class="status-bar">
  <div class="sb-pills">
    <div class="sb-pill active">🟢 Online</div>
    <div class="sb-pill {sst}">⏰ {slbl}</div>
    <div class="sb-pill">📅 {hari}</div>
    {'<div class="sb-pill active">✅ Hari Operasional</div>' if is_wkday else '<div class="sb-pill">⛔ Libur</div>'}
  </div>
  <div class="sb-pills">
    <div class="sb-pill active">📡 Google Sheets</div>
    <div class="sb-pill">🔄 60 detik</div>
  </div>
</div>
""", unsafe_allow_html=True)

# HERO
st.markdown(f"""
<div class="hero">
  {'<div class="hero-bg-img" style="background-image:url(\'data:image/jpeg;base64,' + bg_kantor + '\');"></div><div class="hero-bg-overlay"></div>' if bg_kantor else ''}
  <div class="hero-deco"></div>
  <div class="hero-inner">
    <div class="hero-eyebrow">🍃 Platform Persampahan · Kota Soe, TTS</div>
    <h1 class="hero-title">
      <span class="line1">HABOCK</span>
      <span class="line2">DIGITAL</span>
    </h1>
    <p class="hero-sub">Sistem terpadu pengawasan TPS real-time, absensi petugas GPS, pengaduan publik digital, dan ekonomi sirkular pupuk bokashi Kab. TTS.</p>
    <div class="hero-btns">
      <a href="{gform}" target="_blank" class="btn-hero-p">📩 Lapor Sampah</a>
      <a href="{appsheet}" target="_blank" class="btn-hero-s">👮 Portal Petugas</a>
    </div>
  </div>
  <div class="kpi-strip">
    <div class="kpi"><span class="kpi-val">32</span><span class="kpi-lbl">Titik TPS</span></div>
    <div class="kpi"><span class="kpi-val">6</span><span class="kpi-lbl">Operator</span></div>
    <div class="kpi"><span class="kpi-val" style="color:#4ade80;text-shadow:0 0 14px rgba(74,222,128,.5);">03:00</span><span class="kpi-lbl">Jam Ops</span></div>
    <div class="kpi"><span class="kpi-val" style="color:#f0a820;text-shadow:0 0 14px rgba(240,168,32,.4);">30 Jt</span><span class="kpi-lbl">Target PAD</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# TABS
tab_home, tab_stats, tab_map, tab_logs, tab_bokashi = st.tabs([
    "🏠 Beranda","📊 Statistik","📍 Peta GIS","📜 Log","🌿 Bokashi"
])

# BERANDA
with tab_home:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    df_prod    = load_bokashi_produksi()
    total_pad  = int(df_prod["Total Pendapatan"].sum())      if not df_prod.empty and "Total Pendapatan"      in df_prod.columns else 0
    total_prod = int(df_prod["Pupuk Diproduksi (kg)"].sum()) if not df_prod.empty and "Pupuk Diproduksi (kg)" in df_prod.columns else 0
    total_jual = int(df_prod["Pupuk Terjual (kg)"].sum())    if not df_prod.empty and "Pupuk Terjual (kg)"    in df_prod.columns else 0
    pct        = min(int(total_pad / 30_000_000 * 100), 100)
    r = 50; circ = 2*3.14159*r
    dv = circ*pct/100; dg = circ-dv

    st.markdown(f"""
    <div class="ring-section">
      <div class="ring-wrap">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="{r}" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="11"/>
          <circle cx="60" cy="60" r="{r}" fill="none" stroke="#d4880a" stroke-width="11"
            stroke-dasharray="{dv:.1f} {dg:.1f}" stroke-linecap="round" transform="rotate(-90 60 60)"/>
        </svg>
        <div class="ring-label"><span class="ring-pct">{pct}%</span><span class="ring-sub">target</span></div>
      </div>
      <div class="ring-info">
        <p class="ring-title">Progress PAD Bokashi 2026</p>
        <p class="ring-desc">Realisasi PAD Rumah Bokashi DLH TTS terhadap target Rp 30 juta/tahun.</p>
        <div class="ring-stats">
          <div class="rs-item"><span class="rs-val">Rp {total_pad:,.0f}</span><span class="rs-lbl">Realisasi</span></div>
          <div class="rs-item"><span class="rs-val">{total_prod:,} kg</span><span class="rs-lbl">Produksi</span></div>
          <div class="rs-item"><span class="rs-val">{total_jual:,} kg</span><span class="rs-lbl">Terjual</span></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="svc-grid">
      <div class="svc g">
        <div class="svc-ico">🗑️</div>
        <div class="svc-title">Pengawasan TPS</div>
        <div class="svc-desc">Pemantauan 32 titik TPS di Kota Soe secara real-time via AppSheet oleh 6 operator mulai 03.00 WITA.</div>
        <span class="svc-tag">📍 32 TPS · 👷 6 Operator · ⏰ 03.00</span>
      </div>
      <div class="svc r">
        <div class="svc-ico">📢</div>
        <div class="svc-title">Pengaduan Publik</div>
        <div class="svc-desc">Laporan sampah liar, TPS penuh, atau jadwal angkut terlambat langsung ke sistem DLH via Google Form.</div>
        <span class="svc-tag">🔴 Klik Lapor Sampah di atas</span>
      </div>
      <div class="svc a">
        <div class="svc-ico">🌿</div>
        <div class="svc-title">Pupuk Bokashi</div>
        <div class="svc-desc">Sampah organik diolah jadi pupuk bokashi berkualitas untuk petani & masyarakat mulai Rp 5.000/kg.</div>
        <span class="svc-tag">🛒 Lihat katalog di tab Bokashi</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="gis-panel">', unsafe_allow_html=True)
    st.markdown('<div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Peta GIS Persebaran TPS</h3><span class="ph-sub">Klik titik untuk detail</span></div>', unsafe_allow_html=True)
    render_peta_gis(height=380, show_stats=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
      <div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Alur Sistem HABOCK</h3></div>
      <div class="flow">
        <div class="fstep" style="background:#e0f5e4;"><div class="fstep-ico">🗑️</div><div class="fstep-lbl" style="color:#1a5c24;">Sampah</div><div class="fstep-sub">TPS Kota Soe</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#e0f2fe;"><div class="fstep-ico">📱</div><div class="fstep-lbl" style="color:#075985;">AppSheet</div><div class="fstep-sub">Input Petugas</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#fef3c7;"><div class="fstep-ico">📊</div><div class="fstep-lbl" style="color:#92400e;">Sheets</div><div class="fstep-sub">Database</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#e0f5e4;"><div class="fstep-ico">🌿</div><div class="fstep-lbl" style="color:#1a5c24;">Bokashi</div><div class="fstep-sub">Sirkular</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#fef3d6;"><div class="fstep-ico">💰</div><div class="fstep-lbl" style="color:#7a4800;">PAD</div><div class="fstep-sub">Daerah</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#e0f5e4;"><div class="fstep-ico">🌐</div><div class="fstep-lbl" style="color:#1a5c24;">Web</div><div class="fstep-sub">Publik</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    wa_number = "6281326024674"
    wa_pesan  = urllib.parse.quote("Halo, saya ingin memesan pupuk bokashi DLH Kab. TTS. Terima kasih 🙏")
    wa_link   = f"https://wa.me/{wa_number}?text={wa_pesan}"

    st.markdown(f"""
    <div class="qr-section">
      <p class="qr-title">Scan QR Code — Akses Cepat</p>
      <p class="qr-sub">Tempel di titik TPS agar warga bisa lapor & akses info dari HP</p>
      <div class="qr-grid">
        <div class="qr-item">
          <span class="qr-item-label">📩 Lapor Sampah</span>
          <div class="qr-box">📋</div>
          <div class="qr-url">Google Form · Pengaduan Masyarakat</div>
          <a href="{gform}" target="_blank" class="qr-btn">Buka Form ↗</a>
        </div>
        <div class="qr-item">
          <span class="qr-item-label">🌿 Beli Pupuk Bokashi</span>
          <div class="qr-box">💬</div>
          <div class="qr-url">WhatsApp · Pemesanan Pupuk DLH TTS</div>
          <a href="{wa_link}" target="_blank" class="qr-btn">WhatsApp ↗</a>
        </div>
        <div class="qr-item">
          <span class="qr-item-label">🌐 Web HABOCK</span>
          <div class="qr-box">🌐</div>
          <div class="qr-url">habock-dlh-tts.streamlit.app</div>
          <a href="https://habock-dlh-tts.streamlit.app" target="_blank" class="qr-btn">Buka Web ↗</a>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# STATISTIK
with tab_stats:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    df = load_data()
    if not df.empty:
        total   = len(df)
        selesai = len(df[df['Status']=='Selesai'])      if 'Status' in df.columns else 0
        proses  = len(df[df['Status']=='Belum Proses']) if 'Status' in df.columns else 0
        st.markdown(f"""
        <div class="stats-grid">
          <div class="stat-card"><div class="sc-bar g"></div><div class="sc-ico">📋</div><div class="sc-val">{total}</div><div class="sc-lbl">Total Laporan</div></div>
          <div class="stat-card"><div class="sc-bar n"></div><div class="sc-ico">📍</div><div class="sc-val">32</div><div class="sc-lbl">TPS Dipantau</div></div>
          <div class="stat-card"><div class="sc-bar a"></div><div class="sc-ico">✅</div><div class="sc-val">{selesai}</div><div class="sc-lbl">Selesai</div></div>
          <div class="stat-card"><div class="sc-bar r"></div><div class="sc-ico">⏳</div><div class="sc-val">{proses}</div><div class="sc-lbl">Belum Proses</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        if 'Status' in df.columns:
            counts = df['Status'].value_counts().reset_index()
            counts.columns = ['Status','Jumlah']
            fig = px.bar(counts, x='Status', y='Jumlah', color='Status', height=300, text='Jumlah')
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', showlegend=False,
                margin=dict(t=20,b=10,l=0,r=0),
                xaxis=dict(title=''), yaxis=dict(title='Jumlah', gridcolor='#f0f0f0'))
            fig.update_traces(
                marker_color=['#1f8433','#d4880a','#dc2626'][:len(counts)],
                marker_line_width=0, textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⏳ Menghubungkan ke database...")
    st.markdown('</div>', unsafe_allow_html=True)

# PETA GIS
with tab_map:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_peta_gis(height=560, show_stats=True)
    st.markdown('</div>', unsafe_allow_html=True)

# LOG
with tab_logs:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Log Pengawasan & Pelaporan</h3><span class="ph-sub">Real-time · Google Sheets</span></div>', unsafe_allow_html=True)
    df = load_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("⏳ Memuat data...")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# BOKASHI
with tab_bokashi:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    df_prod2    = load_bokashi_produksi()
    df_katalog2 = load_bokashi_katalog()

    tp2  = int(df_prod2["Pupuk Diproduksi (kg)"].sum()) if not df_prod2.empty and "Pupuk Diproduksi (kg)" in df_prod2.columns else 0
    tj2  = int(df_prod2["Pupuk Terjual (kg)"].sum())    if not df_prod2.empty and "Pupuk Terjual (kg)"    in df_prod2.columns else 0
    pad2 = int(df_prod2["Total Pendapatan"].sum())       if not df_prod2.empty and "Total Pendapatan"      in df_prod2.columns else 0
    stk2 = int(df_prod2["Stok Tersisa"].iloc[-1])        if not df_prod2.empty and "Stok Tersisa" in df_prod2.columns and len(df_prod2)>0 else 0

    st.markdown(f"""
    <div class="stats-grid">
      <div class="stat-card"><div class="sc-bar g"></div><div class="sc-ico">🌾</div><div class="sc-val">{tp2:,}</div><div class="sc-lbl">kg Diproduksi</div></div>
      <div class="stat-card"><div class="sc-bar r"></div><div class="sc-ico">🛒</div><div class="sc-val">{tj2:,}</div><div class="sc-lbl">kg Terjual</div></div>
      <div class="stat-card"><div class="sc-bar n"></div><div class="sc-ico">📦</div><div class="sc-val">{stk2:,}</div><div class="sc-lbl">kg Stok</div></div>
      <div class="stat-card"><div class="sc-bar a"></div><div class="sc-ico">💰</div><div class="sc-val">{pad2//1000}rb</div><div class="sc-lbl">Total PAD</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Grafik Produksi & Penjualan</h3></div>', unsafe_allow_html=True)
    if not df_prod2.empty and "Tanggal" in df_prod2.columns:
        df_c = df_prod2[["Tanggal","Pupuk Diproduksi (kg)","Pupuk Terjual (kg)"]].dropna()
        df_m = df_c.melt(id_vars="Tanggal", var_name="Keterangan", value_name="kg")
        fig  = px.bar(df_m, x="Tanggal", y="kg", color="Keterangan", barmode="group",
            color_discrete_map={"Pupuk Diproduksi (kg)":"#1f8433","Pupuk Terjual (kg)":"#d4880a"},
            height=240)
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(t=10,b=10,l=0,r=0),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=10)),
            xaxis=dict(title=""), yaxis=dict(title="kg", gridcolor="#f5f5f5"))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⏳ Data belum tersedia.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Katalog Produk</h3><span class="ph-sub">Rumah Bokashi DLH TTS</span></div>', unsafe_allow_html=True)

    katalog_data = []
    if not df_katalog2.empty:
        for _, row in df_katalog2.iterrows():
            try:
                kode=str(row.iloc[0]); nama=str(row.iloc[1]); kemasan=str(row.iloc[2])
                harga=int(float(str(row.iloc[3]).replace(",","").replace(".","")))
                try: sv=int(float(str(row.iloc[4]).replace(",","")))
                except: sv=1
                katalog_data.append((kode,nama,kemasan,harga,sv))
            except: pass

    if not katalog_data:
        katalog_data=[
            ("BOK-001","Pupuk Bokashi Curah","Per kg",5000,100),
            ("BOK-002","Bokashi Kemasan 5 kg","5 kg / sak",25000,50),
            ("BOK-003","Bokashi Kemasan 10 kg","10 kg / sak",48000,30),
            ("BOK-004","Bokashi Kemasan 25 kg","25 kg / karung",115000,15),
        ]

    for kode,nama,kemasan,harga,sv in katalog_data:
        badge='<span class="b-ok">✅ Ada</span>' if sv>0 else '<span class="b-no">⚠️ Habis</span>'
        st.markdown(f"""
        <div class="prod-card">
          <div>
            <div class="prod-nm">{nama}</div>
            <div class="prod-km">📦 {kemasan} · {kode} &nbsp;{badge}</div>
          </div>
          <div class="prod-ph">Rp {harga:,}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    wa_link2 = f"https://wa.me/{wa_number}?text={wa_pesan}"
    st.markdown(f"""
    <div class="order-box">
      <h4>📞 Cara Pemesanan</h4>
      <div class="ostep"><div class="onum">1</div><div>Klik tombol WhatsApp di bawah</div></div>
      <div class="ostep"><div class="onum">2</div><div>Sebutkan nama, alamat &amp; jumlah pesanan</div></div>
      <div class="ostep"><div class="onum">3</div><div>Bayar tunai / transfer rekening DLH</div></div>
      <div class="ostep"><div class="onum">4</div><div>Ambil di Rumah Bokashi, Kota Soe</div></div>
      <div class="ostep"><div class="onum">5</div><div>Pengiriman tersedia untuk pembelian ≥ 50 kg</div></div>
      <div class="oloc">📍 Rumah Bokashi DLH Kab. TTS · Kota Soe · TTS</div>
      <a href="{wa_link2}" target="_blank" class="btn-wa">💬 Pesan via WhatsApp — 0813-2602-4674</a>
    </div>
    <div class="panel" style="margin-top:12px;">
      <div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Manfaat Pupuk Bokashi</h3></div>
      <div class="bene-grid">
        <div class="bene"><span>🌱</span>Memperbaiki struktur &amp; kesuburan tanah</div>
        <div class="bene"><span>⚡</span>Mempercepat pertumbuhan tanaman</div>
        <div class="bene"><span>♻️</span>Ramah lingkungan dari sampah organik</div>
        <div class="bene"><span>💸</span>Lebih murah dari pupuk kimia</div>
        <div class="bene"><span>🏘️</span>Mendukung kebersihan Kota Soe</div>
        <div class="bene"><span>📈</span>Mendukung PAD &amp; ekonomi sirkular</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown(f"""
<div class="footer">
  <div class="footer-brand">
    <div class="name">HA<span>BOCK</span> Digital</div>
    <p>Sistem Informasi Persampahan &amp; Ekonomi Sirkular Kabupaten Timor Tengah Selatan.<br>Proyek Aktualisasi LATSAR CPNS Gelombang 8 Angkatan 274.</p>
  </div>
  <div class="footer-col">
    <h4>Kontak DLH</h4>
    <p>📞 (0388) 21476 — Kantor DLH</p>
    <p>📱 0813-2602-4674 — Rumah Bokashi</p>
    <p>📧 kabttsdlh@gmail.com</p>
    <p>⏰ Senin–Jumat, 08.00–16.00 WITA</p>
  </div>
  <div class="footer-col">
    <h4>Tautan Cepat</h4>
    <a href="{gform}" target="_blank">📩 Lapor Sampah</a>
    <a href="{appsheet}" target="_blank">👮 Portal Petugas</a>
    <a href="https://habock-dlh-tts.streamlit.app" target="_blank">🌐 Web HABOCK</a>
    <a href="https://tts.go.id" target="_blank">🏛️ Website Kab. TTS</a>
  </div>
  <div class="footer-bottom">
    <p>© 2026 · Bidang Pengelolaan Sampah, Limbah B3 · DLH Kab. TTS</p>
    <span class="footer-badge">⭐ LATSAR CPNS 274</span>
  </div>
</div>
""", unsafe_allow_html=True)
