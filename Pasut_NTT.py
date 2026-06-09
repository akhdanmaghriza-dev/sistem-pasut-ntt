import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
from PIL import Image

# --- 1. CONFIG HALAMAN ---
st.set_page_config(page_title="Portal Pasut Maritim Tenau Kupang", layout="wide", page_icon="🌊")

# --- DATABASE FASE BULAN 2026 (Sesuai Legenda Kalender BMKG) ---
FASE_BULAN_2026 = {
    # JANUARI
    '2026-01-02': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-01-03': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-01-19': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-01-30': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    
    # FEBRUARI
    '2026-02-02': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-02-17': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-02-25': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    
    # MARET
    '2026-03-03': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-03-19': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-03-22': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    
    # APRIL
    '2026-04-02': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-04-17': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-04-19': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    
    # MEI
    '2026-05-02': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-05-17': ('Super New Moon (Perigee + Bulan Baru)', '🔴✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
    '2026-05-31': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    
    # JUNI
    '2026-06-15': ('Super New Moon (Perigee + Bulan Baru)', '🔴✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
    '2026-06-30': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    
    # JULI
    '2026-07-14': ('Super New Moon (Perigee + Bulan Baru)', '🔴✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
    '2026-07-29': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    
    # AGUSTUS
    '2026-08-10': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-08-13': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-08-28': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    
    # SEPTEMBER
    '2026-09-07': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    '2026-09-11': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-09-26': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    
    # OKTOBER
    '2026-10-10': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-10-26': ('Bulan Purnama', '🔵', 'Spring Tide (Pasang Purnama)'),
    '2026-10-29': ('Perigee (Jarak terdekat Bumi - Bulan)', '🟢', 'Potensi Pasang Tinggi'),
    
    # NOVEMBER
    '2026-11-09': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-11-24': ('Supermoon (Perigee + Bulan Purnama)', '🔵✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
    
    # DESEMBER
    '2026-12-09': ('Bulan Baru', '🟤', 'Spring Tide (Pasang Purnama)'),
    '2026-12-24': ('Supermoon (Perigee + Bulan Purnama)', '🔵✨', 'Spring Tide Maksimum (Sangat Tinggi)'),
}

BULAN_MAP = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

hari_ini = datetime.now()
# Mengunci default penanggalan dinamis mengikuti hari ini pada tahun data (2026)
default_tgl = datetime(2026, hari_ini.month, hari_ini.day)

# --- 2. FUNGSI LOAD DATA ---
@st.cache_data
def load_range_data(start_date, end_date, wilayah_list):
    all_data = []
    
    if start_date.year == end_date.year:
        bulan_dibutuhkan = list(range(start_date.month, end_date.month + 1))
    else:
        bulan_dibutuhkan = [start_date.month, end_date.month]
        
    for wilayah in wilayah_list:
        for bln in bulan_dibutuhkan:
            file_name = f"Pasut_{BULAN_MAP[bln]}.xlsx"
            if os.path.exists(file_name):
                try:
                    df = pd.read_excel(file_name, sheet_name=wilayah)
                    df.rename(columns={df.columns[0]: 'Tanggal'}, inplace=True)
                    df_melt = df.melt(id_vars=['Tanggal'], var_name='Jam', value_name='Ketinggian')
                    df_melt['Jam'] = pd.to_numeric(df_melt['Jam'])
                    df_melt['Ketinggian'] = pd.to_numeric(df_melt['Ketinggian'], errors='coerce')
                    df_melt['Waktu'] = df_melt.apply(lambda r: datetime(2026, bln, int(r['Tanggal']), int(r['Jam'])-1, 0), axis=1)
                    df_melt['Wilayah'] = wilayah
                    all_data.append(df_melt)
                except Exception:
                    pass
                    
    if not all_data: 
        return pd.DataFrame()
        
    df_master = pd.concat(all_data, ignore_index=True)
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    return df_master[(df_master['Waktu'] >= start_dt) & (df_master['Waktu'] <= end_dt)].sort_values(['Wilayah', 'Waktu']).reset_index(drop=True)

# --- 3. HEADER & LOGO ---
st.write("")
col_logo, col_title = st.columns([1, 10])

with col_logo:
    logo_file = None
    try:
        for f in os.listdir('.'):
            if 'bmkg' in f.lower() and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                logo_file = f
                break
        if logo_file:
            st.image(Image.open(logo_file), width=90)
    except Exception:
        pass

with col_title:
    st.markdown("<h1 style='color: var(--text-color); margin:0; padding:0; line-height:1.1;'>Prakiraan Pasang Surut Air Laut NTT</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: gray; margin:0; padding:0; font-weight:normal;'>Stasiun Meteorologi Kelas III Maritim Tenau - Kupang</h3>", unsafe_allow_html=True)

# --- 4. PANDUAN PENGGUNAAN (EDUKASI UTAMA) ---
st.write("")
with st.expander("💡 Panduan Penggunaan & Cara Membaca Grafik"):
    st.markdown("""
    **Cara Membaca Dasbor:**
    - **Sumbu Vertikal (Y):** Menunjukkan prakiraan ketinggian air laut dalam satuan Meter di atas datum **LAT** (*Lowest Astronomical Tide*).
    - **Sumbu Horizontal (X):** Garis waktu kronologis dalam zona waktu setempat yaitu **WITA** (Waktu Indonesia Tengah).
    - **Garis Putus-Putus Hijau:** Menunjukkan penanda posisi waktu saat ini (*Real-time*).
    - **Ikon Fenomena (🔵 / 🟤 / 🟢 / 🔴✨):** Muncul otomatis pada grafik untuk menandai fase astronomi yang memicu pasang surut ekstrem.
    
    **Karakteristik Pasut NTT:**
    - **Harian Ganda (*Semi-diurnal*):** Karakteristik khas perairan NTT di mana dalam 24 jam terjadi **2 kali pasang tertinggi** dan **2 kali surut terendah**.
    - **Spring Tide (Pasang Purnama):** Terjadi saat fase Bulan Purnama atau Bulan Baru. Arus laut menjadi lebih kencang dan pasang air sangat tinggi.
    - **Perigee:** Posisi di mana Bulan berada pada titik terdekat dengan Bumi, berpotensi meningkatkan kekuatan pasang air laut.
    - **Neap Tide (Pasang Perbani):** Terjadi saat posisi bulan separuh, selisih pasang-surut harian bernilai paling minimum (kondisi air tenang).
    """)

st.write("---")

# --- 5. TABS INTERAKTIF ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 TREN RENTANG WAKTU", "📊 PERBANDINGAN MULTI-TANGGAL", "🌕 KALENDER FASE BULAN", "💾 EKSPOR MATRIKS DATA"])

# ==========================================
# TAB 1: TREN RENTANG WAKTU & JADWAL HARIAN
# ==========================================
with tab1:
    st.markdown("### ⚙️ Parameter Analisis Rentang Waktu")
    p_col1, p_col2, p_col3 = st.columns([2, 1, 1])
    
    daftar_wilayah = ["Kupang", "Atapupu", "Labuan Bajo", "Ende", "Maumere", "Waingapu", "Kalabahi"]
    with p_col1: 
        pilih_wilayah = st.multiselect("📍 Pilih Lokasi Pengamatan (Bisa >1 untuk komparasi):", daftar_wilayah, default=["Kupang"])
    with p_col2: 
        tgl_mulai = st.date_input("Tanggal Mulai:", value=default_tgl, min_value=datetime(2026,1,1), max_value=datetime(2026,12,31))
    with p_col3: 
        tgl_selesai = st.date_input("Tanggal Selesai:", value=default_tgl, min_value=datetime(2026,1,1), max_value=datetime(2026,12,31))

    if tgl_selesai >= tgl_mulai and len(pilih_wilayah) > 0:
        df_tren = load_range_data(tgl_mulai, tgl_selesai, pilih_wilayah)
        
        if not df_tren.empty:
            # METRIK HIGHLIGHT EKSTREM GLOBAL (Mendukung Dark Mode)
            idx_max, idx_min = df_tren['Ketinggian'].idxmax(), df_tren['Ketinggian'].idxmin()
            m1, m2 = st.columns(2)
            
            with m1:
                st.markdown(f"""
                <div style='background-color: rgba(239,68,68,0.15); border-left: 5px solid #ef4444; padding: 10px; border-radius: 5px;'>
                    <p style='color: #ef4444; margin:0; font-weight: bold; font-size:13px;'>🔴 REKOR PASANG TERTINGGI (Acuan Datum: LAT)</p>
                    <h3 style='color: var(--text-color); margin:2px 0;'>{df_tren.loc[idx_max, 'Ketinggian']:.2f} m <span style='font-size:14px; font-weight:normal;'>({df_tren.loc[idx_max, 'Wilayah']})</span></h3>
                    <p style='color: gray; margin:0; font-size:12px;'>Waktu: {df_tren.loc[idx_max, 'Waktu'].strftime('%d %b %Y | %H:00 WITA')}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with m2:
                st.markdown(f"""
                <div style='background-color: rgba(59,130,246,0.15); border-left: 5px solid #3b82f6; padding: 10px; border-radius: 5px;'>
                    <p style='color: #3b82f6; margin:0; font-weight: bold; font-size:13px;'>🔵 REKOR SURUT TERENDAH (Acuan Datum: LAT)</p>
                    <h3 style='color: var(--text-color); margin:2px 0;'>{df_tren.loc[idx_min, 'Ketinggian']:.2f} m <span style='font-size:14px; font-weight:normal;'>({df_tren.loc[idx_min, 'Wilayah']})</span></h3>
                    <p style='color: gray; margin:0; font-size:12px;'>Waktu: {df_tren.loc[idx_min, 'Waktu'].strftime('%d %b %Y | %H:00 WITA')}</p>
                </div>
                """, unsafe_allow_html=True)

            # PEMBUATAN GRAFIK PLOTLY
            fig = go.Figure()
            warna = ['#0ea5e9', '#0d9488', '#8b5cf6', '#f59e0b', '#ec4899', '#64748b', '#84cc16']
            max_y_grafik = df_tren['Ketinggian'].max() + 0.8
            
            for i, wil in enumerate(pilih_wilayah):
                df_w = df_tren[df_tren['Wilayah'] == wil].copy()
                efek_fill = 'tozeroy' if len(pilih_wilayah) == 1 else None
                
                # Kurva Utama Pasut
                fig.add_trace(go.Scatter(
                    x=df_w['Waktu'], y=df_w['Ketinggian'], name=wil, 
                    line=dict(color=warna[i%7], width=3), fill=efek_fill, fillcolor='rgba(14, 165, 233, 0.12)',
                    hovertemplate="<b>%{x|%d %b %Y, %H:00 WITA}</b><br>Tinggi: %{y:.2f} m<extra></extra>"
                ))
                
                # Detektor Puncak Harian Ganda
                df_w['S1'], df_w['S2'] = df_w['Ketinggian'].shift(1), df_w['Ketinggian'].shift(-1)
                hi = df_w[(df_w['Ketinggian']>df_w['S1']) & (df_w['Ketinggian']>df_w['S2'])]
                lo = df_w[(df_w['Ketinggian']<df_w['S1']) & (df_w['Ketinggian']<df_w['S2'])]
                
                # Marker Pasang
                fig.add_trace(go.Scatter(
                    x=hi['Waktu'], y=hi['Ketinggian'], mode='markers+text', 
                    text=hi['Ketinggian'].apply(lambda x:f"<b>{x:.2f}m</b>"), textposition="top center", 
                    textfont=dict(color="#ef4444", size=11), marker=dict(color='#ef4444', size=8), 
                    name="Titik Pasang", showlegend=(i==0)
                ))
                
                # Marker Surut
                fig.add_trace(go.Scatter(
                    x=lo['Waktu'], y=lo['Ketinggian'], mode='markers+text', 
                    text=lo['Ketinggian'].apply(lambda x:f"<b>{x:.2f}m</b>"), textposition="bottom center", 
                    textfont=dict(color="#3b82f6", size=11), marker=dict(color='#3b82f6', size=8), 
                    name="Titik Surut", showlegend=(i==0)
                ))

            # Integrasi Tanda Ikon Astronomi dari Kalender
            for date_str, (name, icon, p_type) in FASE_BULAN_2026.items():
                dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
                if tgl_mulai <= dt_obj.date() <= tgl_selesai:
                    posisi_x = dt_obj.replace(hour=12)
                    fig.add_annotation(
                        x=posisi_x, y=max_y_grafik - 0.2, text=icon, showarrow=False, 
                        font=dict(size=24), hovertext=f"Fase BMKG: {name}"
                    )

            # Garis Vertikal Penunjuk Waktu Real-Time
            waktu_realtime = hari_ini.replace(year=2026)
            fig.add_trace(go.Scatter(
                x=[waktu_realtime, waktu_realtime], y=[0, max_y_grafik],
                mode='lines', line=dict(color='#10b981', width=2, dash='dash'),
                name="Waktu Saat Ini", hoverinfo='skip'
            ))
            
            fig.add_annotation(
                x=waktu_realtime, y=max_y_grafik - 0.05, text="WAKTU SAAT INI", showarrow=False,
                xanchor="left", yanchor="bottom", font=dict(color="#10b981", size=10, weight="bold")
            )

            # Tema "streamlit" agar mengikuti Light/Dark mode
            fig.update_layout(
                title=dict(text="<b>Grafik Tren Fluktuasi Ketinggian Air Laut Pasut NTT (WITA)</b>", font=dict(size=15)),
                xaxis=dict(title="Sumbu Waktu Kronologis", showgrid=True, rangeslider=dict(visible=True, thickness=0.06), type="date"),
                yaxis=dict(title="Tinggi Air Gelombang - Datum LAT (m)", showgrid=True, range=[0, max_y_grafik]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=600, margin=dict(t=50, b=30, l=40, r=40), hovermode="x unified"
            )
            
            fig.add_annotation(text="Referensi Ketinggian: Lowest Astronomical Tide (LAT)", xref="paper", yref="paper", x=0, y=-0.25, showarrow=False, font=dict(size=11, color="gray", style="italic"))
            st.plotly_chart(fig, use_container_width=True, theme="streamlit")
            
            # --- TABEL RINCIAN JADWAL HARIAN ---
            st.markdown("---")
            st.markdown("### 🕒 Jadwal Waktu Kejadian Pasang dan Surut Harian")
            for wil in pilih_wilayah:
                if len(pilih_wilayah) > 1:
                    st.markdown(f"**📍 Lokasi Pelabuhan: {wil}**")
                    
                df_w = df_tren[df_tren['Wilayah'] == wil].copy()
                df_w['S1'], df_w['S2'] = df_w['Ketinggian'].shift(1), df_w['Ketinggian'].shift(-1)
                
                h = df_w[(df_w['Ketinggian']>df_w['S1']) & (df_w['Ketinggian']>df_w['S2'])][['Waktu', 'Ketinggian']].copy()
                l = df_w[(df_w['Ketinggian']<df_w['S1']) & (df_w['Ketinggian']<df_w['S2'])][['Waktu', 'Ketinggian']].copy()
                
                h['Waktu'] = h['Waktu'].dt.strftime('%d %b %Y | %H:00 WITA')
                h['Ketinggian'] = h['Ketinggian'].apply(lambda x: f"{x:.2f}")
                h.rename(columns={'Waktu':'WAKTU PASANG MAKSIMUM', 'Ketinggian':'KETINGGIAN DATUM LAT (M)'}, inplace=True)
                
                l['Waktu'] = l['Waktu'].dt.strftime('%d %b %Y | %H:00 WITA')
                l['Ketinggian'] = l['Ketinggian'].apply(lambda x: f"{x:.2f}")
                l.rename(columns={'Waktu':'WAKTU SURUT MINIMUM', 'Ketinggian':'KETINGGIAN DATUM LAT (M)'}, inplace=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<h5 style='color: #ef4444; margin-bottom: 5px;'>⬆️ Jadwal Pasang Tertinggi (High Tide)</h5>", unsafe_allow_html=True)
                    st.dataframe(h.reset_index(drop=True), use_container_width=True)
                with c2:
                    st.markdown("<h5 style='color: #3b82f6; margin-bottom: 5px;'>⬇️ Jadwal Surut Terendah (Low Tide)</h5>", unsafe_allow_html=True)
                    st.dataframe(l.reset_index(drop=True), use_container_width=True)

        else:
            st.warning("⚠️ Berkas data tidak ditemukan. Pastikan file Excel bulanan diletakkan di folder aplikasi dengan format nama yang benar.")


# ==========================================
# TAB 2: PERBANDINGAN MULTI-TANGGAL (OVERLAP)
# ==========================================
with tab2:
    st.markdown("### 📊 Perbandingan Pasut Multi-Tanggal (Sumbu 24-Jam)")
    st.caption("Pilih beberapa tanggal berbeda untuk membandingkan tumpang tindih siklus pasang surut dalam bingkai sumbu waktu 24 jam tunggal.")
    
    col_w, col_t = st.columns([1, 2])
    with col_w:
        wil_cmp = st.selectbox("📍 Pilih Lokasi/Pelabuhan:", daftar_wilayah, key="cmp_wil")
    with col_t:
        semua_tanggal_2026 = [d.strftime('%Y-%m-%d') for d in pd.date_range('2026-01-01', '2026-12-31')]
        tgl_cmp = st.multiselect("📅 Pilih Tanggal Komparasi (Maksimal 6):", semua_tanggal_2026, default=[default_tgl.strftime('%Y-%m-%d')], max_selections=6)

    if len(tgl_cmp) > 0:
        fig_cmp = go.Figure()
        warna_cmp = ['#0ea5e9', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#334155']
        data_ditemukan = False
        
        for idx, d_str in enumerate(tgl_cmp):
            d_obj = datetime.strptime(d_str, '%Y-%m-%d')
            df_day_full = load_range_data(d_obj.date(), d_obj.date(), [wil_cmp])
            
            if not df_day_full.empty:
                data_ditemukan = True
                fig_cmp.add_trace(go.Scatter(
                    x=df_day_full['Waktu'].dt.hour + 1, y=df_day_full['Ketinggian'],
                    mode='lines+markers', line=dict(color=warna_cmp[idx], width=3), marker=dict(size=6),
                    name=f"Tanggal {d_str}", hovertemplate="Jam %{x}:00 WITA<br>Tinggi: %{y:.2f} m<extra></extra>"
                ))
        
        if data_ditemukan:
            fig_cmp.update_layout(
                title=dict(text=f"<b>Analisis Komparasi Siklus Harian Pelabuhan {wil_cmp}</b>", font=dict(size=15)),
                xaxis=dict(title="Jam Operasional (WITA)", tickmode='linear', tick0=1, dtick=1, showgrid=True),
                yaxis=dict(title="Tinggi Air Gelombang - LAT (Meter)", showgrid=True),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=500, margin=dict(t=50, b=40, l=40, r=40), hovermode="x unified"
            )
            st.plotly_chart(fig_cmp, use_container_width=True, theme="streamlit")
        else:
            st.warning("Data untuk penanggalan tersebut tidak ditemukan.")
    else:
        st.info("Silakan tentukan minimal 1 opsi tanggal pada parameter komparasi di atas.")


# ==========================================
# TAB 3: PORTAL KALENDER FASE BULAN
# ==========================================
with tab3:
    st.markdown("### 🌕 Kalender Astronomi Fase Bulan BMKG 2026")
    st.info("Informasi data astronomi di bawah ini digunakan sebagai referensi deteksi dini potensi lonjakan air pasang ekstrem (Spring Tide / Pasang Purnama) di wilayah perairan NTT.")
    
    cal_data = []
    for d_str, (name, icon, p_type) in FASE_BULAN_2026.items():
        dt_obj = datetime.strptime(d_str, '%Y-%m-%d')
        cal_data.append({
            'Tanggal Puncak Fase': dt_obj.strftime('%d %B %Y'),
            'Ikon Visual': icon,
            'Fenomena Astronomis': name,
            'Dampak Pada Siklus Air Laut': p_type
        })
    
    df_fase = pd.DataFrame(cal_data)
    st.dataframe(df_fase, use_container_width=True, hide_index=True)


# ==========================================
# TAB 4: PANEL EKSPOR DATA MATRIKS ASLI
# ==========================================
with tab4:
    st.markdown("### 💾 Ekspor Hasil Ekstraksi Data Tabular")
    st.write("Silakan unduh database tabular dalam bentuk susunan matriks asli menyamping (Jam 1 - Jam 24) sesuai dengan filter wilayah dan tanggal yang aktif pada Tab 1.")
    
    if 'df_tren' in locals() and not df_tren.empty:
        df_wide = df_tren.copy()
        df_wide['Bulan'] = df_wide['Waktu'].dt.month.map(BULAN_MAP)
        
        df_matrix = df_wide.pivot_table(
            index=['Wilayah', 'Bulan', 'Tanggal'], columns='Jam', values='Ketinggian'
        ).reset_index()
        
        kolom_jam = sorted([c for c in df_matrix.columns if str(c).isdigit()])
        kolom_final = ['Wilayah', 'Bulan', 'Tanggal'] + kolom_jam
        df_matrix = df_matrix[kolom_final]
        df_matrix.columns = [f"Jam {c}" if str(c).isdigit() else c for c in df_matrix.columns]

        csv_buffer = df_matrix.to_csv(index=False).encode('utf-8')
        nama_berkas = f"Database_Matriks_Pasut_BMKG_Tenau_{tgl_mulai}_sd_{tgl_selesai}.csv"
        
        st.download_button(
            label="📥 UNDUH DATA FORMAT MATRIKS ASLI (.CSV / EXCEL)",
            data=csv_buffer, file_name=nama_berkas, mime='text/csv', use_container_width=True
        )
        st.dataframe(df_matrix, use_container_width=True)
    else:
        st.info("Atur parameter wilayah dan waktu pada Tab 1 terlebih dahulu untuk mengekspor database matriks.")

# --- 6. FOOTER & PENYANGKALAN HUKUM (DISCLAIMER RESMI) ---
st.write("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 11px; padding: 12px; background-color: var(--secondary-background-color); border-radius: 5px; border: 1px solid var(--border-color);'>
    <b>SUMBER PRIMER:</b> Pusat Hidro-Oseanografi TNI Angkatan Laut (Pushidrosal) & Bidang Tanda Waktu Astronomi BMKG Pusat 2026.<br>
    <b>DISCLAIMER OPERASIONAL:</b> Seluruh data numerik dan grafik yang disajikan dalam portal ini merupakan hasil prakiraan pasang surut astronomis murni (berdasarkan pengaruh perhitungan posisi Bulan dan Matahari). Ketinggian muka air laut aktual di lapangan dapat bergeser atau berbeda dari nilai prediksi akibat intervensi faktor cuaca dan meteorologis dinamik setempat, seperti kecepatan embusan angin, tekanan udara rendah, dan rambatan gelombang alun (<i>swell</i>). Gunakan informasi portal ini secara bijak sebagai instrumen pendukung keselamatan navigasi maritim pelabuhan.
</div>
""", unsafe_allow_html=True)