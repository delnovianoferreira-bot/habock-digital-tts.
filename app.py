import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MiniMap, Fullscreen
from streamlit_folium import st_folium
import base64, os, urllib.parse
from datetime import datetime

# ─── KONFIGURASI PAGE ──────────────────────────────────────────
st.set_page_config(
    page_title="HABOCK Digital — DLH Kab. TTS",
    layout="wide",
    page_icon="🍃",
    initial_sidebar_state="collapsed"
)

# ─── URL DATA ──────────────────────────────────────────────────
URL_DATA             = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_ZOXOlq8tAN3z3zMMMbh1JFS-Sl9LecCVE7gNAoDm_IF0oFDuredZXbtO_rAPF54hlzyervBGwvuq/pub?output=csv"
URL_BOKASHI_PRODUKSI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_ZOXOlq8tAN3z3zMMMbh1JFS-Sl9LecCVE7gNAoDm_IF0oFDuredZXbtO_rAPF54hlzyervBGwvuq/pub?gid=538980514&single=true&output=csv"
URL_BOKASHI_KATALOG  = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_ZOXOlq8tAN3z3zMMMbh1JFS-Sl9LecCVE7gNAoDm_IF0oFDuredZXbtO_rAPF54hlzyervBGwvuq/pub?gid=1511411011&single=true&output=csv"
URL_MASTER           = "https://docs.google.com/spreadsheets/d/1wKycB8e3rKTaui9oJDf_6aNtngw6oK9dT-h6RuD5vos/export?format=csv&gid=1233632779"

# ─── FALLBACK TPS (berdasarkan data real dari screenshot) ──────
TPS_FALLBACK = [
    {"id":"TPS-001","nama":"Smp Sinar",                "kel":"Yusuf Missa",       "lat":-9.858904,"lng":124.282051},
    {"id":"TPS-002","nama":"Bak Belakang Kantor Lurah", "kel":"Yusuf Missa",       "lat":-9.865744,"lng":124.289227},
    {"id":"TPS-003","nama":"TPS PLN Oebesa",            "kel":"Yusuf Missa",       "lat":-9.865145,"lng":124.288217},
    {"id":"TPS-004","nama":"TPS Bak Pos 1",             "kel":"Yusuf Missa",       "lat":-9.865366,"lng":124.282691},
    {"id":"TPS-005","nama":"TPS Pak Ane Oti",           "kel":"Yusuf Missa",       "lat":-9.859317,"lng":124.273689},
    {"id":"TPS-006","nama":"TPS Tambora",               "kel":"Zet Banamtuar",     "lat":-9.860806,"lng":124.283526},
    {"id":"TPS-007","nama":"TPS Pasar Ikan Depan",      "kel":"Zet Banamtuar",     "lat":-9.857171,"lng":124.288387},
    {"id":"TPS-008","nama":"Pasa Ikan",                 "kel":"Leonard Benu",      "lat":-9.856105,"lng":124.288096},
    {"id":"TPS-009","nama":"Belakang Pasar Impres",     "kel":"Hendrik L. Tala",   "lat":-9.856412,"lng":124.287021},
    {"id":"TPS-010","nama":"Belakang Pasar 1",          "kel":"Amos Tanesit",      "lat":-9.856428,"lng":124.286855},
    {"id":"TPS-011","nama":"Belakang Pasar 2",          "kel":"Hendrik L. Tala",   "lat":-9.856637,"lng":124.286038},
    {"id":"TPS-012","nama":"TPS-012","kel":"Kota Soe","lat":-9.862,"lng":124.283},
    {"id":"TPS-013","nama":"TPS-013","kel":"Kota Soe","lat":-9.863,"lng":124.284},
    {"id":"TPS-014","nama":"TPS-014","kel":"Kota Soe","lat":-9.864,"lng":124.285},
    {"id":"TPS-015","nama":"TPS-015","kel":"Kota Soe","lat":-9.865,"lng":124.286},
    {"id":"TPS-016","nama":"TPS-016","kel":"Kota Soe","lat":-9.866,"lng":124.287},
    {"id":"TPS-017","nama":"TPS-017","kel":"Kota Soe","lat":-9.867,"lng":124.288},
    {"id":"TPS-018","nama":"TPS-018","kel":"Kota Soe","lat":-9.868,"lng":124.289},
    {"id":"TPS-019","nama":"TPS-019","kel":"Kota Soe","lat":-9.869,"lng":124.290},
    {"id":"TPS-020","nama":"TPS-020","kel":"Kota Soe","lat":-9.870,"lng":124.291},
    {"id":"TPS-021","nama":"TPS-021","kel":"Kota Soe","lat":-9.871,"lng":124.292},
    {"id":"TPS-022","nama":"TPS-022","kel":"Kota Soe","lat":-9.872,"lng":124.293},
    {"id":"TPS-023","nama":"TPS-023","kel":"Kota Soe","lat":-9.873,"lng":124.294},
    {"id":"TPS-024","nama":"TPS-024","kel":"Kota Soe","lat":-9.874,"lng":124.295},
    {"id":"TPS-025","nama":"TPS-025","kel":"Kota Soe","lat":-9.875,"lng":124.296},
    {"id":"TPS-026","nama":"TPS-026","kel":"Kota Soe","lat":-9.876,"lng":124.297},
    {"id":"TPS-027","nama":"TPS-027","kel":"Kota Soe","lat":-9.877,"lng":124.298},
    {"id":"TPS-028","nama":"TPS-028","kel":"Kota Soe","lat":-9.878,"lng":124.299},
    {"id":"TPS-029","nama":"TPS-029","kel":"Kota Soe","lat":-9.879,"lng":124.300},
    {"id":"TPS-030","nama":"TPS-030","kel":"Kota Soe","lat":-9.880,"lng":124.301},
    {"id":"TPS-031","nama":"TPS-031","kel":"Kota Soe","lat":-9.881,"lng":124.302},
    {"id":"TPS-032","nama":"TPS-032","kel":"Kota Soe","lat":-9.882,"lng":124.303},
]

# ─── HELPER ────────────────────────────────────────────────────
def parse_angka_indonesia(s):
    s = str(s).strip().replace("Rp","").replace(" ","")
    if "," in s and "." in s:
        s = s.replace(".","").replace(",",".")
    elif "." in s and "," not in s:
        if len(s.split(".")[-1]) == 3:
            s = s.replace(".","")
    elif "," in s and "." not in s:
        if len(s.split(",")[-1]) == 3:
            s = s.replace(",","")
        else:
            s = s.replace(",",".")
    try: return float(s)
    except: return 0.0

def get_img(target):
    files = os.listdir(".")
    img = next((f for f in files if target.lower() in f.lower()), None)
    if img:
        with open(img,"rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# ─── LOAD DATA ─────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    """Sheet monitoring: status pengangkutan TPS harian"""
    try:
        df = pd.read_csv(URL_DATA)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_master():
    """
    Sheet master TPS — HABOCK_Master_Data
    Struktur: Row1=judul, Row2=subtitle, Row3=header → skiprows=2
    Kolom penting: ID TPS, NAMA / LOKASI TPS, KELURAHAN / DESA, Latitude, Longitude
    """
    try:
        df = pd.read_csv(URL_MASTER, skiprows=2)
        df.columns = df.columns.str.strip()

        # Filter hanya baris yang punya ID TPS valid
        if "ID TPS" not in df.columns:
            return pd.DataFrame()

        df = df[df["ID TPS"].astype(str).str.startswith("TPS-")].copy()
        df = df.reset_index(drop=True)

        # Bersihkan koordinat (ganti koma desimal → titik)
        for col in ["Latitude", "Longitude"]:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str)
                    .str.replace(",", ".", regex=False)
                    .str.strip()
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Hanya baris dengan koordinat valid di wilayah Indonesia / NTT
        df = df.dropna(subset=["Latitude","Longitude"])
        df = df[
            (df["Latitude"].between(-12, -7)) &
            (df["Longitude"].between(120, 130))
        ]

        return df.reset_index(drop=True)

    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_bokashi_produksi():
    try:
        df = pd.read_csv(URL_BOKASHI_PRODUKSI, skiprows=2)
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=["Tanggal"])
        df = df[df["Tanggal"].astype(str).str.match(r'^\d{2}/\d{2}/\d{4}$')]
        df["Tanggal"] = pd.to_datetime(df["Tanggal"], format="%d/%m/%Y", errors="coerce")
        for col in ["Bahan Baku Masuk (kg)","Pupuk Diproduksi (kg)","Pupuk Terjual (kg)","Harga/kg","Total Pendapatan","Stok Tersisa"]:
            if col in df.columns:
                df[col] = df[col].apply(parse_angka_indonesia)
        if "Bahan Baku Masuk (kg)" in df.columns:
            df = df[df["Bahan Baku Masuk (kg)"] > 0]
        return df.reset_index(drop=True)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_bokashi_katalog():
    try:
        df = pd.read_csv(URL_BOKASHI_KATALOG, skiprows=2)
        df.columns = df.columns.str.strip()
        return df[df.iloc[:,0].astype(str).str.startswith("BOK-")].reset_index(drop=True)
    except:
        return pd.DataFrame()

# ─── LOAD ASET ─────────────────────────────────────────────────
logo_pemda = get_img("pemda")
logo_hb    = get_img("logo")
_map_counter = {"n": 0}

# ─── FUNGSI PETA GIS ──────────────────────────────────────────
def render_peta_gis(height=420, show_stats=True):
    _map_counter["n"] += 1
    map_key = f"habock_map_{_map_counter['n']}"

    WARNA   = {
        "Selesai":      "#22c55e",
        "Sedang Proses":"#f59e0b",
        "Belum Proses": "#ef4444",
        "Menunggu":     "#60a5fa"
    }
    BG_PILL = {
        "Selesai":       ("#d4f7dc","#1a5c24"),
        "Sedang Proses": ("#fef3c7","#92400e"),
        "Belum Proses":  ("#fee2e2","#991b1b"),
        "Menunggu":      ("#e0f2fe","#075985")
    }

    # 1. Ambil status dari sheet monitoring
    df_main   = load_data()
    df_master = load_master()

    status_dict = {}
    if not df_main.empty:
        # Cari kolom ID TPS di sheet monitoring (nama kolom bisa bervariasi)
        id_col = next((c for c in ["ID TPS","Kode TPS","TPS","Lokasi","ID"] if c in df_main.columns), None)
        st_col = next((c for c in ["Status","STATUS","status"] if c in df_main.columns), None)
        if id_col and st_col:
            for _, row in df_main.iterrows():
                k = str(row[id_col]).strip()
                v = str(row[st_col]).strip()
                status_dict[k] = v
                # simpan juga versi nomor saja untuk matching fleksibel
                k2 = k.replace("TPS-","").lstrip("0")
                if k2:
                    status_dict[k2] = v

    # 2. Bangun daftar titik
    titik = []
    use_sheets = (
        not df_master.empty and
        "Latitude"  in df_master.columns and
        "Longitude" in df_master.columns and
        len(df_master) > 0
    )

    if use_sheets:
        for _, row in df_master.iterrows():
            id_tps = str(row.get("ID TPS", "")).strip()
            # coba berbagai nama kolom nama TPS
            nama = str(row.get("NAMA / LOKASI TPS",
                    row.get("Nama TPS",
                    row.get("NAMA TPS", "TPS")))).strip()
            kel  = str(row.get("KELURAHAN / DESA",
                    row.get("Kelurahan", "—"))).strip()
            lat  = float(row["Latitude"])
            lng  = float(row["Longitude"])

            # Status: coba exact match → stripped number → default
            num_str = id_tps.replace("TPS-","").lstrip("0") or "0"
            status  = status_dict.get(id_tps,
                      status_dict.get(num_str,
                      str(row.get("Status","Selesai")).strip()))

            titik.append({
                "id": id_tps, "nama": nama, "kel": kel,
                "lat": lat,   "lng":  lng,  "status": status
            })
    else:
        for t in TPS_FALLBACK:
            k      = t["id"]
            k2     = k.replace("TPS-","").lstrip("0")
            status = status_dict.get(k, status_dict.get(k2, "Selesai"))
            titik.append({**t, "status": status})

    # 3. Tampilkan statistik
    if show_stats:
        cnt = {"Selesai":0,"Sedang Proses":0,"Belum Proses":0,"Menunggu":0}
        for t in titik:
            s = t["status"]
            if s in cnt:
                cnt[s] += 1
            else:
                cnt["Selesai"] += 1

        st.markdown(f'''
        <div class="map-stat-grid">
          <div class="map-stat green"><div class="msv">{cnt["Selesai"]}</div><div class="msl">✅ Selesai</div></div>
          <div class="map-stat amber"><div class="msv">{cnt["Sedang Proses"]}</div><div class="msl">🔄 Sedang</div></div>
          <div class="map-stat red"><div class="msv">{cnt["Belum Proses"]}</div><div class="msl">🚨 Belum</div></div>
          <div class="map-stat blue"><div class="msv">{cnt["Menunggu"]}</div><div class="msl">🕐 Tunggu</div></div>
        </div>''', unsafe_allow_html=True)

    # 4. Header
    sumber = f"📡 Google Sheets ({len(titik)} TPS)" if use_sheets else f"⚠️ Data fallback ({len(titik)} TPS)"
    st.markdown(
        f'<div class="map-header">'
        f'<span class="map-title">🗺️ Peta GIS · Titik TPS Kota Soe</span>'
        f'<div style="display:flex;gap:6px;align-items:center;">'
        f'<span class="map-chip">{sumber}</span>'
        f'<span class="map-chip green-chip">🔄 60s</span>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    # 5. Buat peta Folium
    # Hitung center dari titik yang ada
    if titik:
        avg_lat = sum(t["lat"] for t in titik) / len(titik)
        avg_lng = sum(t["lng"] for t in titik) / len(titik)
    else:
        avg_lat, avg_lng = -9.862, 124.283

    m = folium.Map(
        location=[avg_lat, avg_lng],
        zoom_start=14,
        tiles="CartoDB Positron",
        prefer_canvas=True
    )
    Fullscreen(position="topright").add_to(m)
    MiniMap(tile_layer="CartoDB Positron", toggle_display=True,
            position="bottomright", width=100, height=80).add_to(m)

    for t in titik:
        s       = t["status"]
        col     = WARNA.get(s, "#22c55e")
        bg_c, txt_c = BG_PILL.get(s, ("#e6f7ea","#1a5c24"))
        num     = t["id"].replace("TPS-","")  # "001", "002", dst

        popup_html = (
            f'<div style="font-family:sans-serif;min-width:170px;border-radius:8px;overflow:hidden;">'
            f'<div style="background:#0f3a1e;color:#fff;padding:8px 12px;">'
            f'<b>{t["id"]} · {t["nama"]}</b>'
            f'<br><small style="color:rgba(255,255,255,.5);">Kel. {t["kel"]}</small></div>'
            f'<div style="padding:8px 12px;background:#fff;">'
            f'<span style="background:{bg_c};color:{txt_c};padding:2px 9px;'
            f'border-radius:10px;font-size:11px;font-weight:700;">{s}</span>'
            f'<div style="margin-top:6px;font-size:10px;color:#888;">'
            f'📍 {t["lat"]:.5f}, {t["lng"]:.5f}</div></div></div>'
        )

        folium.CircleMarker(
            location=[t["lat"], t["lng"]],
            radius=11,
            color="white", weight=2.5,
            fill=True, fill_color=col, fill_opacity=0.92,
            tooltip=folium.Tooltip(
                f"<b>{t['id']} · {t['nama']}</b><br>"
                f"<span style='color:{col};font-weight:700;'>{s}</span>",
                sticky=True
            ),
            popup=folium.Popup(popup_html, max_width=220)
        ).add_to(m)

        folium.Marker(
            location=[t["lat"], t["lng"]],
            icon=folium.DivIcon(
                html=(f'<div style="font-size:7px;font-weight:800;color:white;'
                      f'text-align:center;line-height:1;margin-top:-1px;">{num}</div>'),
                icon_size=(22,13), icon_anchor=(11,6)
            )
        ).add_to(m)

    # Marker Rumah Bokashi
    folium.Marker(
        location=[-9.8631, 124.2691],
        icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
        tooltip=folium.Tooltip("<b>🌿 Rumah Bokashi DLH TTS</b>", sticky=True),
        popup=folium.Popup(
            "<div style='font-family:sans-serif;padding:4px;'>"
            "<b>🌿 Rumah Bokashi DLH TTS</b><br>"
            "<small>Pusat produksi pupuk bokashi</small></div>",
            max_width=180
        )
    ).add_to(m)

    # Legend
    legend = (
        '<div style="position:absolute;bottom:28px;left:8px;z-index:1000;background:white;'
        'border-radius:8px;padding:7px 10px;box-shadow:0 2px 8px rgba(0,0,0,.15);'
        'font-size:10px;font-family:sans-serif;">'
        '<b>Status TPS</b>'
        '<div style="display:flex;align-items:center;gap:4px;margin:3px 0;">'
        '<div style="width:9px;height:9px;border-radius:50%;background:#22c55e;"></div>Selesai</div>'
        '<div style="display:flex;align-items:center;gap:4px;margin:3px 0;">'
        '<div style="width:9px;height:9px;border-radius:50%;background:#f59e0b;"></div>Sedang</div>'
        '<div style="display:flex;align-items:center;gap:4px;margin:3px 0;">'
        '<div style="width:9px;height:9px;border-radius:50%;background:#ef4444;"></div>Belum</div>'
        '<div style="display:flex;align-items:center;gap:4px;margin:3px 0;">'
        '<div style="width:9px;height:9px;border-radius:50%;background:#60a5fa;"></div>Tunggu</div>'
        '<div style="display:flex;align-items:center;gap:4px;margin:4px 0 0;">'
        '<span>🌿</span>Rumah Bokashi</div></div>'
    )
    m.get_root().html.add_child(folium.Element(legend))

    st_folium(m, use_container_width=True, height=height,
              returned_objects=[], key=map_key)

    if not use_sheets:
        st.caption(
            "📌 Koordinat menggunakan data fallback. "
            "Pastikan kolom **Latitude** & **Longitude** sudah terisi "
            "di sheet *Daftar TPS* HABOCK_Master_Data."
        )

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
:root{
  --h-dark:#0b2e14;--h-mid:#145a24;--h-main:#1a7a30;--h-light:#2ea84a;--h-pale:#e8f5ec;
  --g-dark:#7a5200;--g-mid:#a86e00;--g-main:#c8960a;--g-light:#e2b830;--g-pale:#fdf6e3;
  --n9:#0d1a10;--n7:#1e3320;--n5:#4a6452;--n3:#8aa890;--n2:#d0e0d4;--n1:#f2f7f3;
  --white:#ffffff;--r5:#c0392b;--r1:#fdecea;
  --rad-sm:4px;--rad-md:10px;--rad-lg:16px;--rad-xl:24px;
  --sh-sm:0 1px 4px rgba(0,0,0,.07);--sh-md:0 4px 16px rgba(0,0,0,.09);--sh-lg:0 8px 32px rgba(0,0,0,.12);
}
html,body,[class*="css"]{font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased;}
.stApp{background:#f0f4f1;}
.block-container{padding:0!important;max-width:100%!important;}
section[data-testid="stSidebar"]{display:none!important;}
div[data-testid="stToolbar"]{display:none!important;}
.stDeployButton{display:none!important;}

/* TICKER */
.ticker-wrap{background:var(--h-dark);height:32px;overflow:hidden;display:flex;align-items:center;}
.ticker-label{background:linear-gradient(135deg,var(--g-main),var(--g-dark));color:#fff;padding:0 20px 0 12px;height:100%;display:flex;align-items:center;font-size:.66em;font-weight:700;letter-spacing:1px;text-transform:uppercase;white-space:nowrap;flex-shrink:0;clip-path:polygon(0 0,calc(100% - 8px) 0,100% 50%,calc(100% - 8px) 100%,0 100%);}
.ticker-track{display:flex;gap:40px;align-items:center;animation:ticker 32s linear infinite;white-space:nowrap;padding-left:20px;}
.ticker-track:hover{animation-play-state:paused;}
@keyframes ticker{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.t-item{font-size:.68em;color:rgba(255,255,255,.75);display:inline-flex;align-items:center;gap:5px;}
.t-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;}
.t-dot.ok{background:#2ea84a;}.t-dot.warn{background:#e2b830;}.t-dot.busy{background:#60a5fa;}

/* NAVBAR */
.navbar{background:var(--h-dark);padding:0 28px;height:68px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid var(--g-main);box-shadow:0 4px 24px rgba(0,0,0,.4);}
.nb-left{display:flex;align-items:center;gap:14px;overflow:hidden;}
.nb-sep{width:1px;height:36px;background:rgba(255,255,255,.15);flex-shrink:0;}
.nb-inst .sub{font-size:.56em;color:var(--g-light);letter-spacing:1px;text-transform:uppercase;font-weight:600;}
.nb-inst .main{font-size:.88em;font-weight:600;color:#fff;white-space:nowrap;letter-spacing:.3px;}
.nb-brand{display:flex;align-items:center;gap:10px;}
.nb-brand .nm{font-family:'Playfair Display',serif;font-size:1.5em;font-weight:700;color:var(--g-light);letter-spacing:1px;}
.nb-brand .tg{font-size:.52em;color:rgba(255,255,255,.35);letter-spacing:1.5px;text-transform:uppercase;}
.nb-right{display:flex;align-items:center;gap:10px;flex-shrink:0;}
.nb-clock{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:5px 13px;font-size:.65em;color:rgba(255,255,255,.7);white-space:nowrap;}
.nb-cta{background:linear-gradient(135deg,var(--g-main),var(--g-dark));color:#fff!important;border-radius:20px;padding:8px 16px;font-size:.72em;font-weight:700;text-decoration:none!important;box-shadow:0 3px 12px rgba(200,150,10,.4);letter-spacing:.3px;}

/* STATUS BAR */
.status-bar{background:var(--h-mid);padding:7px 28px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.08);gap:8px;flex-wrap:wrap;}
.sb-pills{display:flex;gap:6px;flex-wrap:wrap;}
.sb-pill{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:16px;padding:3px 10px;font-size:.65em;color:rgba(255,255,255,.68);display:flex;align-items:center;gap:5px;white-space:nowrap;}
.sb-pill.active{background:rgba(46,168,74,.2);border-color:rgba(46,168,74,.5);color:#6de87e;}
.sb-pill.warn{background:rgba(226,184,48,.12);border-color:rgba(226,184,48,.3);color:var(--g-light);}

/* HERO */
.hero{background:linear-gradient(145deg,var(--h-dark) 0%,#0e3b1a 50%,#11451f 100%);padding:52px 44px 0;position:relative;overflow:hidden;min-height:420px;display:flex;flex-direction:column;}
.hero-deco-ring{position:absolute;top:-120px;right:-80px;width:480px;height:480px;border-radius:50%;border:60px solid rgba(200,150,10,.07);pointer-events:none;}
.hero-inner{position:relative;z-index:2;max-width:560px;}
.hero-eyebrow{display:inline-flex;align-items:center;gap:7px;background:rgba(200,150,10,.15);border:1px solid rgba(200,150,10,.4);border-radius:20px;padding:5px 14px;font-size:.67em;color:var(--g-light);font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:20px;}
.hero-title{font-family:'Playfair Display',serif;font-size:4em;font-weight:700;line-height:.92;letter-spacing:-1px;margin:0 0 16px;}
.hero-title .line1{display:block;color:#ffffff;}
.hero-title .line2{display:block;color:var(--g-light);}
.hero-sub{font-size:.88em;color:rgba(255,255,255,.65);max-width:440px;line-height:1.7;margin:0 0 28px;}
.hero-btns{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:40px;}
.btn-p{display:inline-flex;align-items:center;gap:7px;background:linear-gradient(135deg,var(--g-main),var(--g-dark));color:#fff!important;padding:12px 24px;border-radius:40px;text-decoration:none!important;font-weight:700;font-size:.85em;box-shadow:0 5px 20px rgba(200,150,10,.4);}
.kpi-strip{background:rgba(0,0,0,.35);border-top:2px solid rgba(200,150,10,.3);display:grid;grid-template-columns:repeat(4,1fr);margin-top:auto;}
.kpi{padding:16px 0;text-align:center;border-right:1px solid rgba(255,255,255,.07);}
.kpi:last-child{border-right:none;}
.kpi-val{font-family:'Playfair Display',serif;font-size:1.9em;font-weight:700;color:#fff;display:block;line-height:1;}
.kpi-lbl{font-size:.58em;color:rgba(255,255,255,.38);text-transform:uppercase;letter-spacing:.8px;display:block;margin-top:4px;}

.wrap{padding:24px 20px;max-width:1440px;margin:0 auto;}

/* SAMBUTAN */
.sambutan-wrap{background:#fff;border-radius:var(--rad-xl);overflow:hidden;box-shadow:var(--sh-lg);margin-bottom:20px;border:1px solid var(--n2);}
.sambutan-header{background:linear-gradient(135deg,var(--h-dark),var(--h-mid));padding:18px 24px;display:flex;align-items:center;gap:10px;}
.sambutan-header-icon{width:6px;height:40px;background:var(--g-main);border-radius:3px;}
.sambutan-header-text .ttl{font-family:'Playfair Display',serif;font-size:1em;font-weight:700;color:#fff;}
.sambutan-header-text .sub{font-size:.7em;color:rgba(255,255,255,.45);margin-top:2px;}
.sambutan-body{display:flex;}
.sambutan-foto-col{width:200px;flex-shrink:0;background:linear-gradient(180deg,var(--h-pale),var(--n1));display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding:28px 16px 24px;border-right:1px solid var(--n2);}
.sambutan-foto-frame{width:120px;height:120px;border-radius:50%;overflow:hidden;border:4px solid var(--g-main);box-shadow:0 4px 20px rgba(200,150,10,.25);background:var(--n2);display:flex;align-items:center;justify-content:center;margin-bottom:14px;}
.sambutan-foto-frame img{width:100%;height:100%;object-fit:cover;}
.sambutan-foto-frame .no-foto{font-size:2.5em;}
.sambutan-nama{font-weight:700;color:var(--h-dark);font-size:.82em;text-align:center;line-height:1.35;margin-bottom:4px;}
.sambutan-jabatan{font-size:.68em;color:var(--h-main);text-align:center;font-weight:600;margin-bottom:2px;}
.sambutan-pangkat{font-size:.64em;color:var(--n5);text-align:center;}
.sambutan-text-col{flex:1;padding:28px 32px;}
.sambutan-openquote{font-family:'Playfair Display',serif;font-size:3em;color:var(--g-light);line-height:.5;margin-bottom:8px;}
.sambutan-teks{font-size:.85em;color:var(--n7);line-height:1.8;}
.sambutan-teks p{margin-bottom:14px;}
.sambutan-footer{padding:14px 32px 18px;border-top:1px solid var(--n2);display:flex;align-items:center;justify-content:flex-end;gap:10px;}
.sambutan-ttd .nm{font-weight:700;color:var(--h-dark);font-size:.82em;}
.sambutan-ttd .jbt{font-size:.68em;color:var(--n5);}
.sambutan-seal{width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,var(--h-pale),var(--n1));border:2px dashed var(--g-main);display:flex;align-items:center;justify-content:center;font-size:.55em;font-weight:700;color:var(--h-main);text-align:center;line-height:1.2;}

/* TIM */
.tim-section{background:#fff;border-radius:var(--rad-xl);overflow:hidden;box-shadow:var(--sh-md);margin-bottom:20px;border:1px solid var(--n2);}
.tim-header{background:linear-gradient(135deg,var(--h-dark),var(--h-mid));padding:16px 24px;display:flex;align-items:center;gap:10px;}
.tim-header-icon{width:5px;height:32px;background:var(--g-main);border-radius:3px;}
.tim-header-text .ttl{font-family:'Playfair Display',serif;font-size:.95em;font-weight:700;color:#fff;}
.tim-header-text .sub{font-size:.65em;color:rgba(255,255,255,.4);margin-top:2px;}
.tim-body{padding:24px;display:flex;justify-content:center;}
.tim-card{background:var(--n1);border:1px solid var(--n2);border-radius:var(--rad-lg);padding:24px 20px;text-align:center;max-width:240px;width:100%;}
.tim-foto-frame{width:110px;height:110px;border-radius:50%;overflow:hidden;border:3px solid var(--g-main);box-shadow:0 3px 16px rgba(200,150,10,.2);background:var(--n2);margin:0 auto 14px;display:flex;align-items:center;justify-content:center;}
.tim-foto-frame img{width:100%;height:100%;object-fit:cover;object-position:top;}
.tim-nama{font-weight:700;color:var(--h-dark);font-size:.84em;line-height:1.35;margin-bottom:4px;}
.tim-jabatan{font-size:.7em;color:var(--h-main);font-weight:600;margin-bottom:3px;}
.tim-instansi{font-size:.65em;color:var(--n5);margin-bottom:10px;}
.tim-badge{display:inline-block;background:linear-gradient(135deg,var(--h-pale),#d0edda);border:1px solid rgba(26,122,48,.25);border-radius:12px;padding:3px 10px;font-size:.62em;font-weight:700;color:var(--h-main);}

/* RING */
.ring-section{background:linear-gradient(135deg,var(--h-dark),var(--h-mid));border-radius:var(--rad-lg);padding:20px 22px;margin-bottom:16px;display:flex;align-items:center;gap:24px;box-shadow:var(--sh-lg);}
.ring-info{flex:1;min-width:0;}
.ring-title{font-family:'Playfair Display',serif;font-size:1em;font-weight:700;color:#fff;margin:0 0 5px;}
.ring-desc{font-size:.77em;color:rgba(255,255,255,.5);line-height:1.55;margin:0 0 12px;}
.ring-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.rs-item{background:rgba(255,255,255,.07);border-radius:6px;padding:8px 10px;}
.rs-val{font-family:'Playfair Display',serif;font-size:1em;font-weight:700;color:var(--g-light);display:block;line-height:1;}
.rs-lbl{font-size:.58em;color:rgba(255,255,255,.35);text-transform:uppercase;letter-spacing:.4px;display:block;margin-top:2px;}

/* STATS GRID */
.stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:16px;}
.stat-card{background:#fff;border-radius:var(--rad-lg);padding:16px 14px;box-shadow:var(--sh-md);position:relative;overflow:hidden;border:1px solid var(--n2);}
.sc-bar{position:absolute;top:0;left:0;right:0;height:3px;}
.sc-bar.g{background:linear-gradient(90deg,var(--h-main),var(--h-light));}
.sc-bar.a{background:linear-gradient(90deg,var(--g-dark),var(--g-main));}
.sc-bar.r{background:linear-gradient(90deg,#c0392b,#e74c3c);}
.sc-bar.n{background:linear-gradient(90deg,var(--n5),var(--n3));}
.sc-ico{font-size:1.5em;margin-bottom:6px;}
.sc-val{font-family:'Playfair Display',serif;font-size:1.6em;font-weight:700;color:var(--n9);line-height:1;margin-bottom:2px;}
.sc-lbl{font-size:.63em;font-weight:600;color:var(--n3);text-transform:uppercase;letter-spacing:.4px;}

/* PANEL */
.panel{background:#fff;border-radius:var(--rad-lg);padding:16px 18px;box-shadow:var(--sh-md);margin-bottom:14px;border:1px solid var(--n2);}
.ph{display:flex;align-items:center;gap:7px;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--n1);}
.ph-dot{width:5px;height:20px;border-radius:3px;background:linear-gradient(180deg,var(--g-main),var(--h-main));flex-shrink:0;}
.ph-title{margin:0;font-family:'Playfair Display',serif;font-size:.92em;font-weight:700;color:var(--n7);}
.ph-sub{font-size:.67em;color:var(--n3);margin-left:auto;}

/* SERVICES */
.svc-grid{display:grid;grid-template-columns:1fr;gap:12px;margin-bottom:16px;}
.svc{border-radius:var(--rad-lg);padding:20px;transition:transform .2s,box-shadow .2s;}
.svc:hover{transform:translateY(-3px);box-shadow:var(--sh-lg);}
.svc.g{background:linear-gradient(145deg,var(--h-dark),var(--h-mid));color:#fff;}
.svc.r{background:linear-gradient(145deg,#7f1d1d,#b91c1c);color:#fff;}
.svc.a{background:linear-gradient(145deg,#3d2200,var(--g-dark));color:#fff;}
.svc-ico{font-size:1.9em;margin-bottom:10px;}
.svc-title{font-family:'Playfair Display',serif;font-size:.95em;font-weight:700;margin-bottom:6px;}
.svc-desc{font-size:.8em;line-height:1.6;opacity:.72;margin-bottom:10px;}
.svc-tag{font-size:.67em;font-weight:700;padding:4px 10px;border-radius:16px;background:rgba(255,255,255,.12);display:inline-block;}

/* FLOW */
.flow{display:flex;align-items:flex-start;justify-content:center;gap:2px;flex-wrap:wrap;padding:8px 0;}
.fstep{display:flex;flex-direction:column;align-items:center;padding:10px;border-radius:10px;min-width:72px;text-align:center;}
.fstep-ico{font-size:1.4em;margin-bottom:4px;}
.fstep-lbl{font-size:.67em;font-weight:700;margin-bottom:1px;}
.fstep-sub{font-size:.57em;color:var(--n3);}
.farr{color:var(--n3);font-size:1em;padding:0 1px;margin-top:16px;}

/* GIS PANEL */
.gis-panel{background:#fff;border-radius:var(--rad-lg);padding:14px 16px;box-shadow:var(--sh-md);margin-bottom:14px;border:1px solid var(--n2);}
.map-stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-bottom:10px;}
.map-stat{border-radius:8px;padding:9px 6px;text-align:center;}
.map-stat.green{background:#d4f7dc;}.map-stat.amber{background:#fef3c7;}.map-stat.red{background:#fee2e2;}.map-stat.blue{background:#e0f2fe;}
.msv{font-family:'Playfair Display',serif;font-size:1.4em;font-weight:700;line-height:1;}
.map-stat.green .msv{color:#1a5c24;}.map-stat.amber .msv{color:#92400e;}.map-stat.red .msv{color:#991b1b;}.map-stat.blue .msv{color:#075985;}
.msl{font-size:.61em;font-weight:600;margin-top:2px;}
.map-stat.green .msl{color:#22873b;}.map-stat.amber .msl{color:#b45309;}.map-stat.red .msl{color:#dc2626;}.map-stat.blue .msl{color:#0284c7;}
.map-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:6px;}
.map-title{font-family:'Playfair Display',serif;font-size:.88em;font-weight:700;color:var(--n7);}
.map-chip{background:var(--n1);border:1px solid var(--n2);border-radius:10px;padding:2px 8px;font-size:.62em;color:var(--n5);}
.green-chip{background:#e0f5e4;border-color:#b0d8b8;color:var(--h-main);}

/* PRODUK */
.prod-card{background:var(--n1);border:1px solid var(--n2);border-radius:10px;padding:11px 13px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;transition:all .18s;}
.prod-card:hover{border-color:var(--g-main);background:var(--g-pale);transform:translateX(4px);}
.prod-nm{font-weight:700;color:var(--n7);font-size:.87em;}
.prod-km{font-size:.65em;color:var(--n5);margin-top:1px;}
.prod-ph{font-family:'Playfair Display',serif;font-size:1em;font-weight:700;color:var(--h-mid);}
.b-ok{background:#d4f7dc;color:#1a5c24;padding:1px 7px;border-radius:8px;font-size:.62em;font-weight:700;}
.b-no{background:var(--r1);color:var(--r5);padding:1px 7px;border-radius:8px;font-size:.62em;font-weight:700;}

/* ORDER BOX */
.order-box{background:linear-gradient(140deg,var(--h-dark),var(--h-mid));border-radius:var(--rad-lg);padding:18px 20px;color:#fff;margin-top:10px;}
.order-box h4{margin:0 0 10px;font-family:'Playfair Display',serif;font-size:.9em;font-weight:700;}
.ostep{display:flex;align-items:flex-start;gap:9px;margin-bottom:8px;font-size:.77em;line-height:1.4;}
.onum{background:rgba(255,255,255,.14);border-radius:50%;width:19px;height:19px;min-width:19px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.68em;}
.oloc{background:rgba(255,255,255,.08);border-radius:6px;padding:6px 10px;margin-top:9px;font-size:.73em;}
.btn-wa{display:block;margin-top:12px;text-align:center;background:#25D366;color:#fff!important;text-decoration:none!important;padding:11px 18px;border-radius:40px;font-weight:700;font-size:.82em;box-shadow:0 4px 14px rgba(37,211,102,.35);}
.bene-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:10px;}
.bene{background:var(--h-pale);border:1px solid rgba(26,122,48,.2);border-radius:7px;padding:8px 10px;display:flex;align-items:flex-start;gap:6px;font-size:.74em;color:var(--n7);line-height:1.35;}

/* QR */
.qr-section{background:linear-gradient(135deg,var(--h-dark),var(--h-mid));border-radius:var(--rad-xl);padding:24px 20px;margin-top:16px;margin-bottom:16px;box-shadow:var(--sh-lg);}
.qr-title{font-family:'Playfair Display',serif;font-size:1.1em;font-weight:700;color:#fff;text-align:center;margin:0 0 5px;}
.qr-sub{font-size:.75em;color:rgba(255,255,255,.45);text-align:center;margin:0 0 20px;}
.qr-grid{display:grid;grid-template-columns:1fr;gap:12px;}
.qr-item{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);border-radius:10px;padding:16px 14px;text-align:center;}
.qr-item-label{font-size:.75em;font-weight:700;color:rgba(255,255,255,.85);margin-bottom:10px;display:block;}
.qr-box{width:76px;height:76px;background:#fff;border-radius:8px;margin:0 auto 8px;display:flex;align-items:center;justify-content:center;font-size:1.8em;}
.qr-url{font-size:.57em;color:rgba(255,255,255,.3);word-break:break-all;line-height:1.4;}
.qr-btn{display:inline-block;margin-top:8px;background:linear-gradient(135deg,var(--g-main),var(--g-dark));color:#fff!important;text-decoration:none!important;padding:5px 13px;border-radius:16px;font-size:.68em;font-weight:700;}

/* FOOTER */
.footer{background:linear-gradient(135deg,var(--h-dark),#0a2811);padding:28px 28px 18px;margin-top:24px;border-top:3px solid var(--g-main);}
.footer-brand .name{font-family:'Playfair Display',serif;font-size:1.25em;font-weight:700;color:#fff;margin-bottom:6px;}
.footer-brand .name span{color:var(--g-light);}
.footer-brand p{font-size:.76em;color:rgba(255,255,255,.35);line-height:1.6;}
.footer-col{margin-top:18px;}
.footer-col h4{font-size:.7em;font-weight:700;color:rgba(255,255,255,.42);letter-spacing:.8px;text-transform:uppercase;margin:0 0 8px;}
.footer-col p,.footer-col a{font-size:.76em;color:rgba(255,255,255,.38);line-height:1.8;text-decoration:none!important;display:block;}
.footer-col a:hover{color:var(--g-light);}
.footer-bottom{border-top:1px solid rgba(255,255,255,.08);padding-top:14px;margin-top:18px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;}
.footer-bottom p{font-size:.65em;color:rgba(255,255,255,.2);}
.footer-badge{background:rgba(200,150,10,.15);border:1px solid rgba(200,150,10,.3);border-radius:14px;padding:3px 10px;font-size:.63em;color:var(--g-light);font-weight:700;}

/* TABS */
.stTabs [data-baseweb="tab-list"]{background:#fff!important;border-radius:var(--rad-md)!important;padding:4px!important;box-shadow:var(--sh-sm)!important;gap:2px!important;margin-bottom:10px!important;border:1px solid var(--n2)!important;}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;font-weight:600!important;font-size:.77em!important;padding:7px 13px!important;color:var(--n5)!important;font-family:'Inter',sans-serif!important;}
.stTabs [aria-selected="true"]{background:var(--h-dark)!important;color:#fff!important;}

@media(min-width:640px){
  .wrap{padding:28px 36px;}
  .stats-grid{grid-template-columns:repeat(4,1fr);}
  .svc-grid{grid-template-columns:repeat(3,1fr);}
  .qr-grid{grid-template-columns:repeat(3,1fr);}
}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.navbar,.hero{animation:fadeUp .4s ease both;}
.wrap{animation:fadeUp .4s ease .1s both;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PRELOAD DATA
# ══════════════════════════════════════════════════════════════
df_main = load_data()

# ── TICKER ──────────────────────────────────────────────────
now_dt  = datetime.now()
now_str = now_dt.strftime("%d %b %Y · %H:%M WITA")

# Buat isi ticker dari data real jika ada
ticker_items = []
if not df_main.empty:
    # Cari kolom nama/lokasi TPS
    lok_col = next((c for c in ["Lokasi","ID TPS","Nama TPS","TPS","Nama"] if c in df_main.columns), None)
    st_col  = next((c for c in ["Status","STATUS","status"] if c in df_main.columns), None)
    if lok_col and st_col:
        for _, row in df_main.tail(10).iterrows():
            lok = str(row.get(lok_col,"TPS")).strip()
            s   = str(row.get(st_col,"")).strip()
            if s == "Selesai":
                ticker_items.append(f'<span class="t-item"><span class="t-dot ok"></span>{lok} — Selesai diangkut</span>')
            elif s == "Belum Proses":
                ticker_items.append(f'<span class="t-item"><span class="t-dot warn"></span>{lok} — Menunggu petugas</span>')
            elif s == "Sedang Proses":
                ticker_items.append(f'<span class="t-item"><span class="t-dot busy"></span>{lok} — Sedang diproses</span>')
            elif lok and lok != "nan":
                ticker_items.append(f'<span class="t-item"><span class="t-dot ok"></span>{lok} — {s}</span>')

if not ticker_items:
    ticker_items = [
        '<span class="t-item"><span class="t-dot ok"></span>TPS-001 Smp Sinar — Selesai 04.15 WITA</span>',
        '<span class="t-item"><span class="t-dot ok"></span>TPS-003 PLN Oebesa — Selesai 04.42 WITA</span>',
        '<span class="t-item"><span class="t-dot warn"></span>TPS-009 Belakang Pasar Impres — Menunggu petugas</span>',
        '<span class="t-item"><span class="t-dot ok"></span>TPS-006 Tambora — Selesai 05.10 WITA</span>',
        '<span class="t-item"><span class="t-dot busy"></span>TPS-011 Belakang Pasar 2 — Sedang diangkut</span>',
        '<span class="t-item"><span class="t-dot ok"></span>TPS-007 Pasar Ikan — Selesai 05.30 WITA</span>',
        '<span class="t-item"><span class="t-dot warn"></span>TPS-004 Bak Pos 1 — Penuh, segera angkut</span>',
        '<span class="t-item"><span class="t-dot ok"></span>TPS-008 Pasa Ikan — Selesai 05.55 WITA</span>',
    ]

ticker_html = "".join(ticker_items * 2)
st.markdown(
    f'<div class="ticker-wrap">'
    f'<div class="ticker-label">🔴 LIVE</div>'
    f'<div style="overflow:hidden;flex:1;">'
    f'<div class="ticker-track">{ticker_html}</div>'
    f'</div></div>',
    unsafe_allow_html=True
)

# ── NAVBAR ──────────────────────────────────────────────────
gform = "https://docs.google.com/forms/d/e/1FAIpQLSejAQXpYJh_v9QZeAaoyqy66puWQutFnV7V6Ux9od-uMWr0UQ/viewform"

logo_img = (
    f'<img src="data:image/png;base64,{logo_pemda}" height="40" style="border-radius:6px;flex-shrink:0;">'
    if logo_pemda else
    '<div style="width:40px;height:40px;border-radius:50%;background:rgba(200,150,10,.2);border:2px solid var(--g-main);display:flex;align-items:center;justify-content:center;font-size:1.2em;">🍃</div>'
)
hb_logo = (
    f'<img src="data:image/png;base64,{logo_hb}" height="34" style="border-radius:5px;">'
    if logo_hb else ''
)

st.markdown(f'''
<div class="navbar">
  <div class="nb-left">
    {logo_img}
    <div class="nb-sep"></div>
    <div class="nb-inst">
      <div class="sub">Kabupaten Timor Tengah Selatan</div>
      <div class="main">Dinas Lingkungan Hidup</div>
    </div>
    <div class="nb-sep"></div>
    <div class="nb-brand">
      {hb_logo}
      <div>
        <div class="nm">HABOCK</div>
        <div class="tg">Sistem Informasi Digital</div>
      </div>
    </div>
  </div>
  <div class="nb-right">
    <span class="nb-clock">🕐 {now_str}</span>
    <a href="{gform}" target="_blank" class="nb-cta">📩 Lapor Sampah</a>
  </div>
</div>
''', unsafe_allow_html=True)

# ── STATUS BAR ───────────────────────────────────────────────
jam     = now_dt.hour
is_wkday = now_dt.weekday() < 5
if 3 <= jam < 7:
    sst  = "active"
    slbl = "Shift Subuh Aktif · 03.00–07.00"
elif 7 <= jam < 16:
    sst  = "warn"
    slbl = "Jam Kantor · 07.00–16.00"
else:
    sst  = ""
    slbl = "Di Luar Jam Operasional"
hari = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"][now_dt.weekday()]

st.markdown(f'''
<div class="status-bar">
  <div class="sb-pills">
    <div class="sb-pill active">🟢 Sistem Online</div>
    <div class="sb-pill {sst}">⏰ {slbl}</div>
    <div class="sb-pill">📅 {hari}</div>
    {'<div class="sb-pill active">✅ Hari Operasional</div>' if is_wkday else '<div class="sb-pill">⛔ Hari Libur</div>'}
  </div>
  <div class="sb-pills">
    <div class="sb-pill active">📡 Google Sheets Terhubung</div>
    <div class="sb-pill">🔄 Auto-refresh 60 detik</div>
  </div>
</div>
''', unsafe_allow_html=True)

# ── HERO ────────────────────────────────────────────────────
st.markdown(f'''
<div class="hero">
  <div class="hero-deco-ring"></div>
  <div class="hero-inner">
    <div class="hero-eyebrow">🍃 Platform Persampahan · Kota Soe, TTS</div>
    <h1 class="hero-title">
      <span class="line1">HABOCK</span>
      <span class="line2">DIGITAL</span>
    </h1>
    <p class="hero-sub">Sistem terpadu pengawasan TPS real-time, absensi petugas GPS, pengaduan publik digital, dan ekonomi sirkular pupuk bokashi Kabupaten Timor Tengah Selatan.</p>
    <div class="hero-btns">
      <a href="{gform}" target="_blank" class="btn-p">📩 Lapor Sampah</a>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────
wa_number = "6281326024674"
wa_pesan  = urllib.parse.quote("Halo, saya ingin memesan pupuk bokashi DLH Kab. TTS. Terima kasih 🙏")

tab_home, tab_stats, tab_map, tab_logs, tab_bokashi = st.tabs([
    "🏠 Beranda","📊 Statistik","📍 Peta GIS","📜 Log","🌿 Bokashi"
])

# ╔══════════════════════════════╗
# ║         TAB BERANDA          ║
# ╚══════════════════════════════╝
with tab_home:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    df_prod   = load_bokashi_produksi()
    total_pad  = int(df_prod["Total Pendapatan"].sum())      if not df_prod.empty and "Total Pendapatan"      in df_prod.columns else 0
    total_prod = int(df_prod["Pupuk Diproduksi (kg)"].sum()) if not df_prod.empty and "Pupuk Diproduksi (kg)" in df_prod.columns else 0
    total_jual = int(df_prod["Pupuk Terjual (kg)"].sum())    if not df_prod.empty and "Pupuk Terjual (kg)"    in df_prod.columns else 0

    wa_link = f"https://wa.me/{wa_number}?text={wa_pesan}"
    st.markdown(f'''
    <div class="ring-section">
      <div style="font-size:3.5em;line-height:1;flex-shrink:0;">🌿</div>
      <div class="ring-info">
        <p class="ring-title">Pupuk Bokashi DLH TTS</p>
        <p class="ring-desc">Pupuk organik hasil olahan sampah Kota Soe — tersedia untuk dibeli masyarakat & petani Kab. TTS.</p>
        <div class="ring-stats">
          <div class="rs-item"><span class="rs-val">Rp {total_pad:,.0f}</span><span class="rs-lbl">Total Penjualan</span></div>
          <div class="rs-item"><span class="rs-val">{total_prod:,} kg</span><span class="rs-lbl">Produksi</span></div>
          <div class="rs-item"><span class="rs-val">{total_jual:,} kg</span><span class="rs-lbl">Terjual</span></div>
        </div>
        <a href="{wa_link}" target="_blank"
           style="display:inline-flex;align-items:center;gap:6px;margin-top:12px;background:#25D366;
           color:#fff;text-decoration:none;padding:8px 16px;border-radius:30px;font-weight:700;font-size:.78em;">
           💬 Pesan Pupuk Sekarang
        </a>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    # SAMBUTAN
    st.markdown('''
    <div class="sambutan-wrap">
      <div class="sambutan-header">
        <div class="sambutan-header-icon"></div>
        <div class="sambutan-header-text">
          <div class="ttl">Sambutan Kepala Dinas</div>
          <div class="sub">Dinas Lingkungan Hidup Kabupaten Timor Tengah Selatan</div>
        </div>
      </div>
      <div class="sambutan-body">
        <div class="sambutan-foto-col">
          <div class="sambutan-foto-frame"><span class="no-foto">👤</span></div>
          <div class="sambutan-nama">Johny Eben Haezer Payon, SH</div>
          <div class="sambutan-jabatan">Kepala Dinas Lingkungan Hidup</div>
          <div class="sambutan-pangkat">Pembina Utama Muda · IV/c</div>
          <div class="sambutan-pangkat">Kab. Timor Tengah Selatan</div>
        </div>
        <div class="sambutan-text-col">
          <div class="sambutan-openquote">"</div>
          <div class="sambutan-teks">
            <p>Shalom, Assalamu'alaikum warahmatullahi wabarakatuh, Salam sejahtera bagi kita semua.</p>
            <p>Puji syukur kehadirat Tuhan Yang Maha Esa atas berkat dan rahmat-Nya, sehingga kami dapat meluncurkan <strong>HABOCK Digital</strong> — sistem informasi persampahan dan ekonomi sirkular berbasis teknologi digital untuk Kabupaten Timor Tengah Selatan.</p>
            <p>Melalui platform ini, kami berkomitmen mewujudkan pengelolaan sampah yang transparan, akuntabel, dan berkelanjutan. Dengan pemantauan real-time Tempat Penampungan Sampah di Kota Soe, pelaporan publik yang mudah diakses, serta program Rumah Bokashi yang mengubah sampah organik menjadi pupuk bernilai ekonomi, kami yakin dapat memberikan kontribusi nyata bagi kebersihan lingkungan dan peningkatan Pendapatan Asli Daerah.</p>
            <p>Saya mengajak seluruh masyarakat, petugas, dan pemangku kepentingan untuk bersama-sama memanfaatkan sistem ini demi terwujudnya Kab. TTS yang bersih, sehat, dan berkelanjutan.</p>
          </div>
        </div>
      </div>
      <div class="sambutan-footer">
        <div class="sambutan-ttd">
          <div class="nm">Johny Eben Haezer Payon, SH</div>
          <div class="jbt">Kepala Dinas Lingkungan Hidup Kab. TTS</div>
        </div>
        <div class="sambutan-seal">DLH<br>TTS</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    # TIM PENGEMBANG
    st.markdown('''
    <div class="tim-section">
      <div class="tim-header">
        <div class="tim-header-icon"></div>
        <div class="tim-header-text">
          <div class="ttl">Tim Pengembang</div>
          <div class="sub">Proyek Aktualisasi LATSAR CPNS Gel. 8 Angkatan 274</div>
        </div>
      </div>
      <div class="tim-body">
        <div class="tim-card">
          <div class="tim-foto-frame"><span style="font-size:2.5em;">👤</span></div>
          <div class="tim-nama">Delnoviano Ferreira Fatima</div>
          <div class="tim-jabatan">Pengawas Lingkungan Hidup Ahli Pertama</div>
          <div class="tim-instansi">DLH Kab. Timor Tengah Selatan</div>
          <span class="tim-badge">⭐ LATSAR CPNS Angk. 274</span>
        </div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    # LAYANAN
    st.markdown('''
    <div class="svc-grid">
      <div class="svc g">
        <div class="svc-ico">🗑️</div>
        <div class="svc-title">Pengawasan TPS</div>
        <div class="svc-desc">Pemantauan titik TPS di Kota Soe secara real-time via AppSheet oleh operator mulai 03.00 WITA.</div>
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
    ''', unsafe_allow_html=True)

    # PETA MINI
    st.markdown('<div class="gis-panel">', unsafe_allow_html=True)
    st.markdown('<div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Peta GIS Persebaran TPS</h3><span class="ph-sub">Klik titik untuk detail · auto-refresh 60s</span></div>', unsafe_allow_html=True)
    render_peta_gis(height=380, show_stats=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ALUR
    st.markdown('''
    <div class="panel">
      <div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Alur Sistem HABOCK</h3></div>
      <div class="flow">
        <div class="fstep" style="background:#e8f5ec;"><div class="fstep-ico">🗑️</div><div class="fstep-lbl" style="color:#145a24;">Sampah</div><div class="fstep-sub">TPS Kota Soe</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#e0f2fe;"><div class="fstep-ico">📱</div><div class="fstep-lbl" style="color:#075985;">AppSheet</div><div class="fstep-sub">Input Petugas</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#fdf6e3;"><div class="fstep-ico">📊</div><div class="fstep-lbl" style="color:#7a5200;">Sheets</div><div class="fstep-sub">Database</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#e8f5ec;"><div class="fstep-ico">🌿</div><div class="fstep-lbl" style="color:#145a24;">Bokashi</div><div class="fstep-sub">Sirkular</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#fdf6e3;"><div class="fstep-ico">💰</div><div class="fstep-lbl" style="color:#7a5200;">PAD</div><div class="fstep-sub">Daerah</div></div>
        <div class="farr">→</div>
        <div class="fstep" style="background:#e8f5ec;"><div class="fstep-ico">🌐</div><div class="fstep-lbl" style="color:#145a24;">Web</div><div class="fstep-sub">Publik</div></div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    # QR
    st.markdown(f'''
    <div class="qr-section">
      <p class="qr-title">Akses Cepat — Scan atau Klik</p>
      <p class="qr-sub">Tempel di titik TPS agar warga bisa lapor & akses info dari HP</p>
      <div class="qr-grid">
        <div class="qr-item"><span class="qr-item-label">📩 Lapor Sampah</span><div class="qr-box">📋</div><div class="qr-url">Google Form · Pengaduan Masyarakat DLH TTS</div><a href="{gform}" target="_blank" class="qr-btn">Buka Form ↗</a></div>
        <div class="qr-item"><span class="qr-item-label">🌿 Beli Pupuk Bokashi</span><div class="qr-box">💬</div><div class="qr-url">WhatsApp · Pemesanan Pupuk DLH TTS</div><a href="https://wa.me/{wa_number}?text={wa_pesan}" target="_blank" class="qr-btn">WhatsApp ↗</a></div>
        <div class="qr-item"><span class="qr-item-label">🌐 Web HABOCK</span><div class="qr-box">🌐</div><div class="qr-url">habock-dlh-tts.streamlit.app</div><a href="https://habock-dlh-tts.streamlit.app" target="_blank" class="qr-btn">Buka Web ↗</a></div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ╔══════════════════════════════╗
# ║        TAB STATISTIK         ║
# ╚══════════════════════════════╝
with tab_stats:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    if not df_main.empty:
        total   = len(df_main)
        st_col  = next((c for c in ["Status","STATUS","status"] if c in df_main.columns), None)
        selesai = len(df_main[df_main[st_col]=="Selesai"])      if st_col else 0
        belum   = len(df_main[df_main[st_col]=="Belum Proses"]) if st_col else 0

        st.markdown(f'''
        <div class="stats-grid">
          <div class="stat-card"><div class="sc-bar g"></div><div class="sc-ico">📋</div><div class="sc-val">{total}</div><div class="sc-lbl">Total Laporan</div></div>
          <div class="stat-card"><div class="sc-bar n"></div><div class="sc-ico">📍</div><div class="sc-val">32</div><div class="sc-lbl">TPS Dipantau</div></div>
          <div class="stat-card"><div class="sc-bar a"></div><div class="sc-ico">✅</div><div class="sc-val">{selesai}</div><div class="sc-lbl">Selesai</div></div>
          <div class="stat-card"><div class="sc-bar r"></div><div class="sc-ico">⏳</div><div class="sc-val">{belum}</div><div class="sc-lbl">Belum Proses</div></div>
        </div>
        ''', unsafe_allow_html=True)

        if st_col:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Distribusi Status TPS</h3></div>', unsafe_allow_html=True)
            counts = df_main[st_col].value_counts().reset_index()
            counts.columns = ["Status","Jumlah"]
            warna_map = {
                "Selesai":"#22c55e",
                "Sedang Proses":"#f59e0b",
                "Belum Proses":"#ef4444",
                "Menunggu":"#60a5fa"
            }
            colors = [warna_map.get(s,"#888") for s in counts["Status"]]
            fig = px.bar(counts, x="Status", y="Jumlah", text="Jumlah", height=300)
            fig.update_traces(marker_color=colors, marker_line_width=0, textposition="outside")
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                showlegend=False,
                margin=dict(t=20,b=10,l=0,r=0),
                xaxis=dict(title=""),
                yaxis=dict(title="Jumlah", gridcolor="#f0f0f0")
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⏳ Menghubungkan ke database Google Sheets...")

    st.markdown('</div>', unsafe_allow_html=True)

# ╔══════════════════════════════╗
# ║         TAB PETA GIS         ║
# ╚══════════════════════════════╝
with tab_map:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    render_peta_gis(height=580, show_stats=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ╔══════════════════════════════╗
# ║          TAB LOG             ║
# ╚══════════════════════════════╝
with tab_logs:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(
        '<div class="ph"><div class="ph-dot"></div>'
        '<h3 class="ph-title">Log Pengawasan & Pelaporan</h3>'
        '<span class="ph-sub">Real-time · Google Sheets · auto-refresh 60s</span></div>',
        unsafe_allow_html=True
    )
    if not df_main.empty:
        st.dataframe(df_main, use_container_width=True, hide_index=True)
    else:
        st.info("⏳ Memuat data dari Google Sheets...")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ╔══════════════════════════════╗
# ║        TAB BOKASHI           ║
# ╚══════════════════════════════╝
with tab_bokashi:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    df_prod2    = load_bokashi_produksi()
    df_katalog2 = load_bokashi_katalog()

    tp2  = int(df_prod2["Pupuk Diproduksi (kg)"].sum()) if not df_prod2.empty and "Pupuk Diproduksi (kg)" in df_prod2.columns else 0
    tj2  = int(df_prod2["Pupuk Terjual (kg)"].sum())    if not df_prod2.empty and "Pupuk Terjual (kg)"    in df_prod2.columns else 0
    pad2 = int(df_prod2["Total Pendapatan"].sum())       if not df_prod2.empty and "Total Pendapatan"      in df_prod2.columns else 0
    stk2 = 0
    if not df_prod2.empty and "Stok Tersisa" in df_prod2.columns:
        sv = df_prod2[df_prod2["Stok Tersisa"]>0]["Stok Tersisa"]
        stk2 = int(sv.iloc[-1]) if not sv.empty else 0

    st.markdown(f'''
    <div class="stats-grid" style="grid-template-columns:repeat(3,1fr);">
      <div class="stat-card"><div class="sc-bar g"></div><div class="sc-ico">🌾</div><div class="sc-val">{tp2:,}</div><div class="sc-lbl">kg Diproduksi</div></div>
      <div class="stat-card"><div class="sc-bar r"></div><div class="sc-ico">🛒</div><div class="sc-val">{tj2:,}</div><div class="sc-lbl">kg Terjual</div></div>
      <div class="stat-card"><div class="sc-bar n"></div><div class="sc-ico">📦</div><div class="sc-val">{stk2:,}</div><div class="sc-lbl">kg Stok</div></div>
    </div>
    ''', unsafe_allow_html=True)

    # Grafik produksi
    if not df_prod2.empty and "Tanggal" in df_prod2.columns:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Grafik Produksi & Penjualan</h3></div>', unsafe_allow_html=True)
        df_c = df_prod2[["Tanggal","Pupuk Diproduksi (kg)","Pupuk Terjual (kg)"]].dropna()
        df_c = df_c[df_c["Pupuk Diproduksi (kg)"] > 0]
        if not df_c.empty:
            df_m = df_c.melt(id_vars="Tanggal", var_name="Keterangan", value_name="kg")
            fig = px.bar(df_m, x="Tanggal", y="kg", color="Keterangan", barmode="group",
                color_discrete_map={"Pupuk Diproduksi (kg)":"#1a7a30","Pupuk Terjual (kg)":"#c8960a"},
                height=240)
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=10,b=10,l=0,r=0),
                legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=10)),
                xaxis=dict(title=""),
                yaxis=dict(title="kg", gridcolor="#f5f5f5")
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Katalog
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Katalog Produk</h3><span class="ph-sub">Rumah Bokashi DLH TTS</span></div>', unsafe_allow_html=True)

    katalog_data = []
    if not df_katalog2.empty:
        for _, row in df_katalog2.iterrows():
            try:
                kode    = str(row.iloc[0]).strip()
                nama    = str(row.iloc[1]).strip()
                kemasan = str(row.iloc[2]).strip()
                harga   = int(parse_angka_indonesia(row.iloc[3]))
                try: sv = int(parse_angka_indonesia(row.iloc[4]))
                except: sv = 1
                if kode.startswith("BOK-") and harga > 0:
                    katalog_data.append((kode,nama,kemasan,harga,sv))
            except:
                pass

    if not katalog_data:
        katalog_data = [
            ("BOK-001","Pupuk Bokashi Curah",       "Per kg",        5000, 100),
            ("BOK-002","Bokashi Kemasan 5 kg",       "5 kg / sak",   25000,  50),
            ("BOK-003","Bokashi Kemasan 10 kg",      "10 kg / sak",  48000,  30),
            ("BOK-004","Bokashi Kemasan 25 kg",      "25 kg / karung",115000,15),
        ]

    for kode, nama, kemasan, harga, sv in katalog_data:
        badge = '<span class="b-ok">✅ Tersedia</span>' if sv > 0 else '<span class="b-no">⚠️ Habis</span>'
        st.markdown(
            f'<div class="prod-card">'
            f'<div><div class="prod-nm">{nama}</div>'
            f'<div class="prod-km">📦 {kemasan} · {kode} &nbsp;{badge}</div></div>'
            f'<div class="prod-ph">Rp {harga:,}</div></div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Order box
    wa_link2 = f"https://wa.me/{wa_number}?text={wa_pesan}"
    st.markdown(f'''
    <div class="order-box">
      <h4>📞 Cara Pemesanan Pupuk Bokashi</h4>
      <div class="ostep"><div class="onum">1</div><div>Klik tombol WhatsApp di bawah</div></div>
      <div class="ostep"><div class="onum">2</div><div>Sebutkan nama, alamat & jumlah pesanan</div></div>
      <div class="ostep"><div class="onum">3</div><div>Pembayaran tunai / transfer rekening DLH TTS</div></div>
      <div class="ostep"><div class="onum">4</div><div>Ambil langsung di Rumah Bokashi, Kota Soe</div></div>
      <div class="ostep"><div class="onum">5</div><div>Pengiriman tersedia untuk pembelian ≥ 50 kg</div></div>
      <div class="oloc">📍 Rumah Bokashi DLH Kab. TTS · Kota Soe · Timor Tengah Selatan</div>
      <a href="{wa_link2}" target="_blank" class="btn-wa">💬 Pesan via WhatsApp — 0813-2602-4674</a>
    </div>
    <div class="panel" style="margin-top:12px;">
      <div class="ph"><div class="ph-dot"></div><h3 class="ph-title">Manfaat Pupuk Bokashi</h3></div>
      <div class="bene-grid">
        <div class="bene"><span>🌱</span>Memperbaiki struktur & kesuburan tanah</div>
        <div class="bene"><span>⚡</span>Mempercepat pertumbuhan tanaman</div>
        <div class="bene"><span>♻️</span>Ramah lingkungan dari sampah organik</div>
        <div class="bene"><span>💸</span>Lebih murah dari pupuk kimia</div>
        <div class="bene"><span>🏘️</span>Mendukung kebersihan Kota Soe</div>
        <div class="bene"><span>📈</span>Mendukung PAD & ekonomi sirkular TTS</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ──────────────────────────────────────────────────
st.markdown(f'''
<div class="footer">
  <div class="footer-brand">
    <div class="name">HA<span>BOCK</span> Digital</div>
    <p>Sistem Informasi Persampahan & Ekonomi Sirkular Kabupaten Timor Tengah Selatan.<br>Proyek Aktualisasi LATSAR CPNS Gelombang 8 Angkatan 274 · DLH Kab. TTS.</p>
  </div>
  <div class="footer-col">
    <h4>Kontak DLH TTS</h4>
    <p>📞 (0388) 21476 — Kantor DLH</p>
    <p>📱 0813-2602-4674 — Rumah Bokashi</p>
    <p>📧 kabttsdlh@gmail.com</p>
    <p>⏰ Senin–Jumat, 08.00–16.00 WITA</p>
  </div>
  <div class="footer-col">
    <h4>Tautan Cepat</h4>
    <a href="{gform}" target="_blank">📩 Lapor Sampah</a>
    <a href="https://habock-dlh-tts.streamlit.app" target="_blank">🌐 Web HABOCK Digital</a>
    <a href="https://tts.go.id" target="_blank">🏛️ Website Kab. TTS</a>
  </div>
  <div class="footer-bottom">
    <p>© 2026 · Bidang Pengelolaan Sampah, Limbah B3 & RTH · Dinas Lingkungan Hidup Kab. TTS</p>
    <span class="footer-badge">⭐ LATSAR CPNS Angkatan 274</span>
  </div>
</div>
''', unsafe_allow_html=True)
