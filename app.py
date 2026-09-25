import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone, date
import os
from PIL import Image
import streamlit.components.v1 as components

# --- 1. CONFIG HALAMAN & CSS GLOBAL ---
st.set_page_config(page_title="Portal Pasut Maritim NTT", layout="wide", page_icon="🌊")

# INJEKSI CSS MODERN: Menyembunyikan elemen bawaan & menambahkan gaya modern
st.markdown("""
<style>
    /* 1. Sembunyikan elemen bawaan Streamlit (PERBAIKAN KALENDER) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {display:none;}
    .stDeployButton {display:none !important;}

    /* 2. Kurangi jarak kosong di bagian atas aplikasi */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* 3. Memaksa menu tabs untuk menempel di atas (Sticky) */
    div[data-testid="stTabs"] > div:first-of-type {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 0rem !important;
        z-index: 99999 !important;
        background-color: var(--background-color) !important;
        padding-top: 15px;
        padding-bottom: 5px;
        border-bottom: 2px solid var(--secondary-background-color);
    }
    
    /* 4. Gaya Tab Text */
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        letter-spacing: 0.5px;
        font-weight: 600 !important;
    }

    /* 5. Efek Shadow pada Tabel DataFrame */
    [data-testid="stDataFrame"] {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE FASE BULAN 2026 ---
FASE_BULAN_2026 = {
    '2026-01-02': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-01-03': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-01-19': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-01-30': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-02-02': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-02-17': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-02-25': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-03-03': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-03-19': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-03-22': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-04-02': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-04-17': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-04-19': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-05-02': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-05-17': ('Super New Moon (Perigee + Bulan Baru)', '🔴✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
    '2026-05-31': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-06-15': ('Super New Moon (Perigee + Bulan Baru)', '🔴✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
    '2026-06-30': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-07-14': ('Super New Moon (Perigee + Bulan Baru)', '🔴✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
    '2026-07-29': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-08-10': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-08-13': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-08-28': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-09-07': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-09-11': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-09-26': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-10-10': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-10-26': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-10-29': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-11-09': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-11-24': ('Supermoon (Perigee + Bulan Purnama)', '🔵✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
    '2026-12-09': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-12-24': ('Supermoon (Perigee + Bulan Purnama)', '🔵✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
}

# --- GENERATOR DATA POTENSI ROB 2026 ---
PERIODE_ROB = [
    ("1. Januari", "2026-01-01", "2026-01-06", "1 - 6 Januari 2026"),
    ("1. Januari", "2026-01-17", "2026-01-22", "17 - 22 Januari 2026"),
    ("1. Januari", "2026-01-30", "2026-02-07", "30 Jan - 7 Feb 2026"), 
    ("2. Februari", "2026-02-15", "2026-02-20", "15 - 20 Februari 2026"),
    ("2. Februari", "2026-02-24", "2026-02-27", "24 - 27 Februari 2026"),
    ("3. Maret", "2026-03-01", "2026-03-05", "1 - 5 Maret 2026"),
    ("3. Maret", "2026-03-18", "2026-03-24", "18 - 24 Maret 2026"),
    ("3. Maret", "2026-03-31", "2026-04-05", "31 Mar - 5 Apr 2026"),
    ("4. April", "2026-04-16", "2026-04-21", "16 - 21 April 2026"),
    ("5. Mei", "2026-05-01", "2026-05-05", "1 - 5 Mei 2026"),
    ("5. Mei", "2026-05-15", "2026-05-20", "15 - 20 Mei 2026"),
    ("5. Mei", "2026-05-29", "2026-06-03", "29 Mei - 3 Jun 2026"),
    ("6. Juni", "2026-06-13", "2026-06-18", "13 - 18 Juni 2026"),
    ("6. Juni", "2026-06-28", "2026-07-03", "28 Jun - 3 Jul 2026"),
    ("7. Juli", "2026-07-12", "2026-07-17", "12 - 17 Juli 2026"),
    ("7. Juli", "2026-07-27", "2026-07-31", "27 - 31 Juli 2026"),
    ("8. Agustus", "2026-08-09", "2026-08-15", "9 - 15 Agustus 2026"),
    ("8. Agustus", "2026-08-26", "2026-08-30", "26 - 30 Agustus 2026"),
    ("9. September", "2026-09-06", "2026-09-13", "6 - 13 September 2026"),
    ("9. September", "2026-09-24", "2026-09-28", "24 - 28 September 2026"),
    ("10. Oktober", "2026-10-08", "2026-10-12", "8 - 12 Oktober 2026"),
    ("10. Oktober", "2026-10-24", "2026-10-31", "24 - 31 Oktober 2026"),
    ("11. November", "2026-11-07", "2026-11-11", "7 - 11 November 2026"),
    ("11. November", "2026-11-22", "2026-11-27", "22 - 27 November 2026"),
    ("12. Desember", "2026-12-07", "2026-12-11", "7 - 11 Desember 2026"),
    ("12. Desember", "2026-12-22", "2026-12-27", "22 - 27 Desember 2026")
]

def hitung_prediksi_buku(base_min, base_max, bulan_int):
    variasi = {1: 0.1, 2: 0.0, 3: 0.2, 4: 0.1, 5: 0.3, 6: 0.4, 7: 0.2, 8: 0.1, 9: 0.2, 10: 0.0, 11: 0.2, 12: 0.1}
    var = variasi.get(bulan_int, 0)
    return f"{base_min + var:.1f} - {base_max + var:.1f}"

LOKASI_ROB = [
    {"Lokasi": "Pesisir Pulau Sumba", "Stasiun_Acuan": ["Waingapu"], "Threshold": 1.0, "B_Min": 2.3, "B_Max": 2.7},
    {"Lokasi": "Pesisir pulau Flores - Alor", "Stasiun_Acuan": ["Maumere", "Ende", "Labuan Bajo", "Kalabahi"], "Threshold": 1.0, "B_Min": 2.0, "B_Max": 2.5},
    {"Lokasi": "Pesisir Pulau Timor - Rote", "Stasiun_Acuan": ["Kupang", "Atapupu"], "Threshold": 1.7, "B_Min": 2.1, "B_Max": 3.0},
    {"Lokasi": "Pesisir Sabu - Raijua", "Stasiun_Acuan": ["Kupang"], "Threshold": 1.5, "B_Min": 2.4, "B_Max": 2.9},
]

DATA_ROB_2026 = []
for periode in PERIODE_ROB:
    bulan_int = int(periode[0].split('.')[0])
    for lok in LOKASI_ROB:
        DATA_ROB_2026.append({
            "Bulan": periode[0],
            "Lokasi": lok["Lokasi"],
            "Stasiun_Acuan": lok["Stasiun_Acuan"],
            "Threshold": lok["Threshold"],
            "Prediksi_Pasut": hitung_prediksi_buku(lok["B_Min"], lok["B_Max"], bulan_int), 
            "Potensi": "✅ Ya",
            "Tanggal_Potensi": periode[3],
            "Start_Date": periode[1],
            "End_Date": periode[2]
        })

BULAN_MAP = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}

# Setup default kalender saat pertama dibuka
waktu_utc = datetime.now(timezone.utc).replace(tzinfo=None)
hari_ini = waktu_utc + timedelta(hours=8)
try:
    default_tgl = date(2026, hari_ini.month, hari_ini.day)
except ValueError:
    default_tgl = date(2026, 2, 28) # Pencegahan error tanggal 29 Februari

# --- 2. FUNGSI LOAD DATA (DIPERBAIKI) ---
@st.cache_data
def load_range_data(start_date, end_date, wilayah_list):
    all_data = []
    
    # Ambil list bulan yang dicakup oleh tanggal mulai hingga selesai
    bulan_dibutuhkan = list(range(start_date.month, end_date.month + 1))
    
    # Fungsi Anti-Crash untuk tanggal Excel (Misal: 30 Februari)
    def create_safe_datetime(year, month, day, hour):
        try:
            if pd.isna(day) or pd.isna(hour): return pd.NaT
            return datetime(year, month, int(day), int(hour)-1, 0)
        except ValueError:
            return pd.NaT

    for wilayah in wilayah_list:
        for bln in bulan_dibutuhkan:
            file_name = f"Pasut_{BULAN_MAP[bln]}.xlsx"
            if os.path.exists(file_name):
                try:
                    df = pd.read_excel(file_name, sheet_name=wilayah)
                    df.rename(columns={df.columns[0]: 'Tanggal'}, inplace=True)
                    df_melt = df.melt(id_vars=['Tanggal'], var_name='Jam', value_name='Ketinggian')
                    
                    df_melt['Jam'] = pd.to_numeric(df_melt['Jam'], errors='coerce')
                    df_melt['Ketinggian'] = pd.to_numeric(df_melt['Ketinggian'], errors='coerce')
                    
                    # Terapkan safe parser
                    df_melt['Waktu'] = df_melt.apply(lambda r: create_safe_datetime(2026, bln, r['Tanggal'], r['Jam']), axis=1)
                    
                    # Buang data yang tanggalnya NaT (tidak valid)
                    df_melt = df_melt.dropna(subset=['Waktu', 'Ketinggian'])
                    df_melt['Wilayah'] = wilayah
                    all_data.append(df_melt)
                except Exception as e: 
                    pass # Abaikan jika sheet tidak ditemukan
                    
    if not all_data: return pd.DataFrame()
    
    df_master = pd.concat(all_data, ignore_index=True)
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    return df_master[(df_master['Waktu'] >= start_dt) & (df_master['Waktu'] <= end_dt)].sort_values(['Wilayah', 'Waktu']).reset_index(drop=True)

# --- 3. HEADER, LOGO & LIVE CLOCK (GAYA BMKG) ---
col_logo, col_title, col_clock = st.columns([1, 8, 3])

with col_logo:
    logo_file = next((f for f in os.listdir('.') if 'bmkg' in f.lower() and f.lower().endswith(('.png', '.jpg', '.jpeg'))), None)
    if logo_file: st.image(Image.open(logo_file), width=90)

with col_title:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #0f4c81 0%, #1ea54a 100%); 
                padding: 15px 25px; 
                border-radius: 8px; 
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); 
                margin-top: 5px;'>
        <h1 style='color: white; margin:0; padding:0; line-height:1.1; font-weight:800; font-size:28px;'>
            Prakiraan Pasang Surut Air Laut NTT
        </h1>
        <h4 style='color: #e2e8f0; margin:5px 0 0 0; padding:0; font-weight:500; font-size:15px;'>
            Stasiun Meteorologi Kelas III Maritim Tenau - Kupang
        </h4>
    </div>
    """, unsafe_allow_html=True)

with col_clock:
    components.html("""
    <style>
        body { margin: 0; padding: 0; background-color: transparent; }
        .clock-container { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: right; margin-top: 5px; color: #1e293b; }
        .wita-label { color: #059669; }
        .utc-label { color: #0f4c81; }
        .title { color: #64748b; }
    </style>
    <div class="clock-container">
        <div class="title" style="font-size: 11px; margin-bottom: 2px; letter-spacing: 1px;"><b>PANEL WAKTU REAL-TIME:</b></div>
        <div class="wita-label" style="font-size: 22px; font-weight: 800; line-height: 1.1;">WITA: <span id="wita"></span></div>
        <div class="utc-label" style="font-size: 14px; font-weight: 600;">UTC: <span id="utc"></span></div>
    </div>
    <script>
        function update() {
            var d = new Date();
            var utc = d.toISOString().substr(11, 8);
            var d_wita = new Date(d.getTime() + 8*3600*1000);
            var wita = d_wita.toISOString().substr(11, 8);
            document.getElementById("utc").innerHTML = utc;
            document.getElementById("wita").innerHTML = wita;
        }
        setInterval(update, 1000);
        update();
    </script>
    """, height=80)

# --- 4. PANDUAN PENGGUNAAN ---
with st.expander("💡 Panduan Penggunaan & Cara Membaca Grafik"):
    st.markdown("""
    **A. Cara Membaca Dasbor:**
    - **Sumbu Vertikal (Y):** Menunjukkan prakiraan ketinggian air laut dalam satuan Meter di atas datum **LAT** (*Lowest Astronomical Tide*).
    - **Sumbu Horizontal (X):** Garis waktu kronologis dalam zona waktu setempat yaitu **WITA** (Waktu Indonesia Tengah).
    - **Garis Putus-Putus Hijau:** Menunjukkan penanda posisi waktu saat ini (*Real-time*).
    - **Blok Merah Transparan:** Menandakan peringatan rentang waktu potensi **Banjir Rob** pesisir. Rentang estimasi ketinggian tertera di dalam blok merah tersebut.
    - **Ikon Fenomena (🔵 / 🟤 / 🟢 / 🔴✨):** Muncul otomatis pada grafik untuk menandai fase astronomi yang memicu pasang surut ekstrem.

    **B. Karakteristik Pasut Perairan NTT:**
    - **Harian Ganda (*Semi-diurnal*):** Dalam 24 jam terjadi **2 kali pasang tertinggi** dan **2 kali surut terendah**.
    - **Spring Tide (Pasang Purnama):** Terjadi saat fase Bulan Purnama atau Bulan Baru. Arus laut menjadi lebih kencang dan pasang air sangat tinggi.
    - **Perigee:** Posisi di mana Bulan berada pada titik terdekat dengan Bumi, berpotensi meningkatkan kekuatan pasang air laut.
    """)

# --- 5. TABS INTERAKTIF ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 TREN RENTANG WAKTU", 
    "📊 KOMPARASI HARI", 
    "🌕 KALENDER FASE BULAN", 
    "💾 EKSPOR MATRIKS", 
    "🚨 LAPORAN POTENSI ROB"
])

# ==========================================
# TAB 1: TREN RENTANG WAKTU & JADWAL HARIAN
# ==========================================
with tab1:
    st.write("") 
    p_col1, p_col2, p_col3 = st.columns([2, 1, 1])
    daftar_wilayah = ["Kupang", "Atapupu", "Labuan Bajo", "Ende", "Maumere", "Waingapu", "Kalabahi"]
    
    with p_col1: 
        pilih_wilayah = st.multiselect("**📍 Pilih Lokasi Pengamatan:**", daftar_wilayah, default=["Kupang"])
    with p_col2: 
        tgl_mulai = st.date_input("**📅 Tanggal Mulai:**", value=default_tgl, min_value=date(2026,1,1), max_value=date(2026,12,31))
    with p_col3: 
        tgl_selesai = st.date_input("**📅 Tanggal Selesai:**", value=default_tgl, min_value=date(2026,1,1), max_value=date(2026,12,31))

    if tgl_selesai >= tgl_mulai and len(pilih_wilayah) > 0:
        df_tren = load_range_data(tgl_mulai, tgl_selesai, pilih_wilayah)
        if not df_tren.empty:
            idx_max, idx_min = df_tren['Ketinggian'].idxmax(), df_tren['Ketinggian'].idxmin()
            
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"""
                <div style='background-color: var(--secondary-background-color); border-left: 6px solid #ef4444; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 20px;'>
                    <p style='color: #ef4444; margin:0; font-weight: 800; font-size:14px; letter-spacing: 1px;'>🌊 PUNCAK PASANG MAKSIMUM</p>
                    <h2 style='color: var(--text-color); margin:5px 0 0 0; font-size: 36px; font-weight: 800;'>{df_tren.loc[idx_max, 'Ketinggian']:.2f} <span style='font-size:16px; font-weight:500; color: gray;'>m</span></h2>
                    <p style='color: var(--text-color); margin:5px 0 0 0; font-size:14px; font-weight: 600;'>📍 {df_tren.loc[idx_max, 'Wilayah']} | 🕒 {df_tren.loc[idx_max, 'Waktu'].strftime('%d %b %Y, %H:00 WITA')}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with m2:
                st.markdown(f"""
                <div style='background-color: var(--secondary-background-color); border-left: 6px solid #3b82f6; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 20px;'>
                    <p style='color: #3b82f6; margin:0; font-weight: 800; font-size:14px; letter-spacing: 1px;'>📉 TITIK SURUT MINIMUM</p>
                    <h2 style='color: var(--text-color); margin:5px 0 0 0; font-size: 36px; font-weight: 800;'>{df_tren.loc[idx_min, 'Ketinggian']:.2f} <span style='font-size:16px; font-weight:500; color: gray;'>m</span></h2>
                    <p style='color: var(--text-color); margin:5px 0 0 0; font-size:14px; font-weight: 600;'>📍 {df_tren.loc[idx_min, 'Wilayah']} | 🕒 {df_tren.loc[idx_min, 'Waktu'].strftime('%d %b %Y, %H:00 WITA')}</p>
                </div>
                """, unsafe_allow_html=True)

            fig = go.Figure()
            warna = ['#0ea5e9', '#0d9488', '#8b5cf6', '#f59e0b', '#ec4899', '#64748b', '#84cc16']
            
            # PERBAIKAN GRAFIK TERPOTONG (Nilai max ditambah agar atap lebih lega)
            max_y_grafik = df_tren['Ketinggian'].max() + 1.2
            
            for i, wil in enumerate(pilih_wilayah):
                df_w = df_tren[df_tren['Wilayah'] == wil].copy()
                efek_fill = 'tozeroy' if len(pilih_wilayah) == 1 else None
                fig.add_trace(go.Scatter(x=df_w['Waktu'], y=df_w['Ketinggian'], name=wil, line=dict(color=warna[i%7], width=3, shape='spline'), fill=efek_fill, fillcolor='rgba(14, 165, 233, 0.12)', hovertemplate="<b>%{x|%d %b %Y, %H:00 WITA}</b><br>Tinggi: <b>%{y:.2f} m</b><extra></extra>"))
                
                df_w['S1'], df_w['S2'] = df_w['Ketinggian'].shift(1), df_w['Ketinggian'].shift(-1)
                hi = df_w[(df_w['Ketinggian']>df_w['S1']) & (df_w['Ketinggian']>df_w['S2'])]
                lo = df_w[(df_w['Ketinggian']<df_w['S1']) & (df_w['Ketinggian']<df_w['S2'])]
                
                fig.add_trace(go.Scatter(x=hi['Waktu'], y=hi['Ketinggian'], mode='markers+text', text=hi['Ketinggian'].apply(lambda x:f"<b>{x:.2f}m</b>"), textposition="top center", textfont=dict(color="#ef4444", size=12), marker=dict(color='#ef4444', size=8), name="Titik Pasang", showlegend=(i==0)))
                fig.add_trace(go.Scatter(x=lo['Waktu'], y=lo['Ketinggian'], mode='markers+text', text=lo['Ketinggian'].apply(lambda x:f"<b>{x:.2f}m</b>"), textposition="bottom center", textfont=dict(color="#3b82f6", size=12), marker=dict(color='#3b82f6', size=8), name="Titik Surut", showlegend=(i==0)))

            rob_ditampilkan = set()
            for row in DATA_ROB_2026:
                if row['Potensi'] == "✅ Ya":
                    if any(wil in row['Stasiun_Acuan'] for wil in pilih_wilayah):
                        start_rob = datetime.strptime(row['Start_Date'], '%Y-%m-%d').date()
                        end_rob = datetime.strptime(row['End_Date'], '%Y-%m-%d').date()
                        prediksi_rentang = row.get('Prediksi_Pasut', '')
                        
                        if (start_rob <= tgl_selesai) and (end_rob >= tgl_mulai):
                            rentang_kunci = (row['Start_Date'], row['End_Date'])
                            if rentang_kunci not in rob_ditampilkan:
                                fig.add_vrect(
                                    x0=start_rob, x1=end_rob + timedelta(days=1), 
                                    fillcolor="rgba(239, 68, 68, 0.12)", layer="below", line_width=0, 
                                    annotation_text=f"<b>⚠️ POTENSI ROB</b><br><b>Estimasi: {prediksi_rentang} m</b>", 
                                    annotation_position="top left", 
                                    annotation_font=dict(color="#b91c1c", size=12)
                                )
                                rob_ditampilkan.add(rentang_kunci)

            for date_str, (name, icon, type) in FASE_BULAN_2026.items():
                dt_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                if tgl_mulai <= dt_obj <= tgl_selesai:
                    dt_with_time = datetime.combine(dt_obj, datetime.min.time()).replace(hour=12)
                    fig.add_annotation(x=dt_with_time, y=max_y_grafik - 0.2, text=icon, showarrow=False, font=dict(size=24), hovertext=f"<b>Fase BMKG: {name}</b>")

            waktu_realtime = hari_ini.replace(year=2026)
            fig.add_trace(go.Scatter(x=[waktu_realtime, waktu_realtime], y=[0, max_y_grafik], mode='lines', line=dict(color='#10b981', width=3, dash='dash'), name="Waktu Saat Ini", hoverinfo='skip'))
            fig.add_annotation(x=waktu_realtime, y=max_y_grafik - 0.05, text="<b>WAKTU SAAT INI</b>", showarrow=False, xanchor="left", yanchor="bottom", font=dict(color="#047857", size=11))

            # PERBAIKAN GRAFIK TERPOTONG (Margin Top 't' dinaikkan menjadi 85, dan Legend 'y' menjadi 1.08)
            fig.update_layout(
                title=dict(text="<b>Grafik Tren Fluktuasi Ketinggian Air Laut (LAT)</b>", font=dict(size=18)), 
                xaxis=dict(title="<b>Kronologi Waktu (WITA)</b>", tickfont=dict(weight='bold'), showgrid=True, rangeslider=dict(visible=True, thickness=0.06), type="date"), 
                yaxis=dict(title="<b>Tinggi Air (m)</b>", tickfont=dict(weight='bold'), showgrid=True, range=[0, max_y_grafik]), 
                legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="right", x=1), 
                height=600, 
                margin=dict(t=85, b=30, l=40, r=40), 
                hovermode="x unified",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True, theme="streamlit")
            
            st.markdown("### **🕒 Jadwal Pasang Surut Harian**")
            for wil in pilih_wilayah:
                if len(pilih_wilayah) > 1: st.markdown(f"**📍 Lokasi Pelabuhan: {wil}**")
                df_w = df_tren[df_tren['Wilayah'] == wil].copy()
                df_w['S1'], df_w['S2'] = df_w['Ketinggian'].shift(1), df_w['Ketinggian'].shift(-1)
                
                h = df_w[(df_w['Ketinggian']>df_w['S1']) & (df_w['Ketinggian']>df_w['S2'])][['Waktu', 'Ketinggian']].copy()
                l = df_w[(df_w['Ketinggian']<df_w['S1']) & (df_w['Ketinggian']<df_w['S2'])][['Waktu', 'Ketinggian']].copy()
                
                h['Waktu'], h['Ketinggian'] = h['Waktu'].dt.strftime('%d %b %Y | %H:00 WITA'), h['Ketinggian'].apply(lambda x: f"{x:.2f}")
                l['Waktu'], l['Ketinggian'] = l['Waktu'].dt.strftime('%d %b %Y | %H:00 WITA'), l['Ketinggian'].apply(lambda x: f"{x:.2f}")
                h.rename(columns={'Waktu':'WAKTU PASANG MAKSIMUM', 'Ketinggian':'KETINGGIAN LAT (M)'}, inplace=True)
                l.rename(columns={'Waktu':'WAKTU SURUT MINIMUM', 'Ketinggian':'KETINGGIAN LAT (M)'}, inplace=True)
                
                c1, c2 = st.columns(2)
                with c1: st.markdown("<h5 style='color: #ef4444; margin-bottom: 5px; font-weight:700;'>⬆️ Jadwal Pasang Tertinggi</h5>", unsafe_allow_html=True); st.dataframe(h.reset_index(drop=True), use_container_width=True)
                with c2: st.markdown("<h5 style='color: #3b82f6; margin-bottom: 5px; font-weight:700;'>⬇️ Jadwal Surut Terendah</h5>", unsafe_allow_html=True); st.dataframe(l.reset_index(drop=True), use_container_width=True)
        else:
            st.warning("⚠️ Berkas data tidak ditemukan untuk rentang tanggal tersebut. Pastikan file Excel tersedia di server.")

# ==========================================
# TAB 2 & 3: KOMPARASI & FASE BULAN
# ==========================================
with tab2:
    st.write("")
    col_w, col_t = st.columns([1, 2])
    with col_w: wil_cmp = st.selectbox("**📍 Pilih Lokasi/Pelabuhan:**", daftar_wilayah, key="cmp_wil")
    with col_t: tgl_cmp = st.multiselect("**📅 Pilih Tanggal Komparasi (Maksimal 6):**", [d.strftime('%Y-%m-%d') for d in pd.date_range('2026-01-01', '2026-12-31')], default=[default_tgl.strftime('%Y-%m-%d')], max_selections=6)

    if len(tgl_cmp) > 0:
        fig_cmp = go.Figure()
        data_found = False
        for idx, d_str in enumerate(tgl_cmp):
            d_obj = datetime.strptime(d_str, '%Y-%m-%d').date()
            df_day_full = load_range_data(d_obj, d_obj, [wil_cmp])
            if not df_day_full.empty:
                data_found = True
                fig_cmp.add_trace(go.Scatter(x=df_day_full['Waktu'].dt.hour + 1, y=df_day_full['Ketinggian'], mode='lines+markers', line=dict(width=3, shape='spline'), name=f"<b>Tgl {d_str}</b>", hovertemplate="<b>Jam %{x}:00 WITA</b><br>Tinggi: <b>%{y:.2f} m</b><extra></extra>"))
        if data_found:
            fig_cmp.update_layout(title=dict(text=f"<b>Analisis Komparasi Siklus Harian Pelabuhan {wil_cmp}</b>", font=dict(size=18)), xaxis=dict(title="<b>Jam Operasional (WITA)</b>", tickfont=dict(weight='bold'), tickmode='linear', tick0=1, dtick=1), yaxis=dict(title="<b>Tinggi Air - LAT (m)</b>", tickfont=dict(weight='bold')), height=500, margin=dict(t=50, b=40, l=40, r=40), hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_cmp, use_container_width=True, theme="streamlit")

with tab3:
    st.write("")
    df_fase = pd.DataFrame([{'Tanggal Puncak Fase': datetime.strptime(d, '%Y-%m-%d').strftime('%d %B %Y'), 'Ikon Visual': v[1], 'Fenomena Astronomis': v[0], 'Dampak Pada Siklus Air Laut': v[2]} for d, v in FASE_BULAN_2026.items()])
    st.dataframe(df_fase, use_container_width=True, hide_index=True)

# ==========================================
# TAB 4 & 5: EKSPOR & LAPORAN ROB PUSAT
# ==========================================
with tab4:
    st.write("")
    if 'df_tren' in locals() and not df_tren.empty:
        df_w = df_tren.copy()
        df_w['Bulan'] = df_w['Waktu'].dt.month.map(BULAN_MAP)
        df_matrix = df_w.pivot_table(index=['Wilayah', 'Bulan', 'Tanggal'], columns='Jam', values='Ketinggian').reset_index()
        kolom_jam = sorted([c for c in df_matrix.columns if str(c).isdigit()])
        df_matrix = df_matrix[['Wilayah', 'Bulan', 'Tanggal'] + kolom_jam]
        df_matrix.columns = [f"Jam {c}" if str(c).isdigit() else c for c in df_matrix.columns]
        st.download_button(label="📥 UNDUH DATA FORMAT MATRIKS (.CSV)", data=df_matrix.to_csv(index=False).encode('utf-8'), file_name=f"Pasut_{tgl_mulai}_sd_{tgl_selesai}.csv", mime='text/csv', use_container_width=True)
        st.dataframe(df_matrix, use_container_width=True)

with tab5:
    st.write("")
    st.info("💡 Modul ini secara otomatis merekap potensi rob sepanjang tahun 2026. Anda dapat menyalin tabel dan teks di bawah ini ke format Excel laporan pusat.")
    
    df_rob = pd.DataFrame(DATA_ROB_2026)
    df_rob_tampil = df_rob[['Bulan', 'Lokasi', 'Threshold', 'Prediksi_Pasut', 'Potensi', 'Tanggal_Potensi']].copy()
    df_rob_tampil.rename(columns={'Threshold': 'Threshold Rob (m)', 'Prediksi_Pasut': 'Prediksi Pasut (Buku)', 'Potensi': 'Apakah Potensi Rob?', 'Tanggal_Potensi': 'Tanggal Potensi Rob'}, inplace=True)
    
    bulan_unik = sorted(df_rob_tampil['Bulan'].unique(), key=lambda x: int(x.split('.')[0]))
    
    pilihan_bulan = ["Tampilkan Semua Bulan"] + bulan_unik
    filter_bulan = st.selectbox("**Pilih Bulan Laporan:**", pilihan_bulan)
    
    st.markdown("---")
    
    if filter_bulan == "Tampilkan Semua Bulan":
        bulan_ditampilkan = bulan_unik
    else:
        bulan_ditampilkan = [filter_bulan]
        
    for bln in bulan_ditampilkan:
        nama_bulan = bln.split(' ')[1]
        st.markdown(f"<h4 style='font-weight:700;'>📅 Laporan Bulan {nama_bulan}</h4>", unsafe_allow_html=True)
        
        df_bulan = df_rob_tampil[df_rob_tampil['Bulan'] == bln].drop(columns=['Bulan'])
        st.dataframe(df_bulan, use_container_width=True, hide_index=True)
        
        data_bulan_ini = df_rob[(df_rob['Bulan'] == bln) & (df_rob['Potensi'] == "✅ Ya")]
        if not data_bulan_ini.empty:
            tanggal_kumpulan = data_bulan_ini['Tanggal_Potensi'].unique()
            teks_tanggal = ", ".join(tanggal_kumpulan)
            st.success(f"**Ringkasan Teks Peringatan Rob {nama_bulan}:**\n\nPeringatan Tanggal Potensi Rob: **{teks_tanggal}**")
        else:
            st.success(f"**Ringkasan Teks Peringatan Rob {nama_bulan}:**\n\nPeringatan Tanggal Potensi Rob: **NIHIL**")
        
        st.write("---")

# --- 6. FOOTER CUSTOM ---
st.markdown("""
<div style='text-align: center; color: #64748b; font-size: 12px; padding: 20px; margin-top: 40px; background-color: var(--secondary-background-color); border-radius: 8px; border: 1px solid var(--border-color);'>
    <b>SUMBER PRIMER:</b> Pusat Hidro-Oseanografi TNI AL (Pushidrosal) & Badan Meteorologi Klimatologi dan Geofisika (BMKG) Pusat.<br>
    <i>DISCLAIMER: Seluruh rentang peringatan rob merupakan hasil algoritma kalender astronomis. Ketinggian muka air laut aktual di lapangan dapat berbeda akibat faktor cuaca ekstrem setempat.</i>
</div>
""", unsafe_allow_html=True)
