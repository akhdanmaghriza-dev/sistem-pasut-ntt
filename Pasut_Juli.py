import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from PIL import Image

# --- 1. CONFIG HALAMAN (Set Luas/Wide) ---
st.set_page_config(page_title="Prakiraan Pasut Maritim Kupang", layout="wide", page_icon="🌊")

# Kamus Nama Bulan
BULAN_MAP = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

# --- DETEKSI TANGGAL DAN WAKTU HARI INI SECARA OTOMATIS ---
hari_ini = datetime.now()
tanggal_sekarang = hari_ini.day
bulan_sekarang = hari_ini.month

# Dikunci ke tahun 2026 sesuai database Anda
default_mulai = datetime(2026, bulan_sekarang, tanggal_sekarang)
default_selesai = datetime(2026, bulan_sekarang, tanggal_sekarang)

# --- 2. FUNGSI INTI: LOADING DATA MULTI-WILAYAH ---
@st.cache_data
def load_range_data(start_date, end_date, wilayah_list):
    all_data = []
    
    if start_date.year == end_date.year:
        bulan_dibutuhkan = list(range(start_date.month, end_date.month + 1))
    else:
        bulan_dibutuhkan = [start_date.month, end_date.month]
    
    for wilayah in wilayah_list:
        for bln in bulan_dibutuhkan:
            nama_bulan_file = f"Pasut_{BULAN_MAP[bln]}.xlsx"
            
            if os.path.exists(nama_bulan_file):
                try:
                    df = pd.read_excel(nama_bulan_file, sheet_name=wilayah)
                    df.rename(columns={df.columns[0]: 'Tanggal'}, inplace=True)
                    
                    df_melt = df.melt(id_vars=['Tanggal'], var_name='Jam', value_name='Ketinggian')
                    df_melt['Jam'] = pd.to_numeric(df_melt['Jam'])
                    df_melt['Ketinggian'] = pd.to_numeric(df_melt['Ketinggian'], errors='coerce')
                    
                    df_melt['Waktu'] = df_melt.apply(
                        lambda r: datetime(2026, bln, int(r['Tanggal']), int(r['Jam'])-1, 0), axis=1
                    )
                    df_melt['Wilayah'] = wilayah
                    
                    all_data.append(df_melt)
                except Exception:
                    pass 
            
    if not all_data:
        return pd.DataFrame()
        
    df_master = pd.concat(all_data, ignore_index=True)
    
    start_dt = datetime(start_date.year, start_date.month, start_date.day, 0, 0)
    end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59)
    
    df_filtered = df_master[(df_master['Waktu'] >= start_dt) & (df_master['Waktu'] <= end_dt)]
    return df_filtered.sort_values(['Wilayah', 'Waktu']).reset_index(drop=True)

# --- 3. TAMPILAN ATAS: LOGO & JUDUL UTAMA ---
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
            img = Image.open(logo_file)
            st.image(img, width=90)
        else:
            st.warning("⚠️ Logo BMKG tidak ditemukan.")
    except Exception:
        pass

with col_title:
    st.markdown("<h1 style='color: #1e3a8a; font-family:Arial; margin:0; padding:0; line-height:1.1;'>Prakiraan Pasang Surut Air Laut NTT</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #475569; font-family:Sans-Serif; margin:0; padding:0; font-weight:normal;'>Stasiun Meteorologi Kelas III Maritim Tenau - Kupang</h3>", unsafe_allow_html=True)

st.write("---")

# --- 4. SISTEM TABS (MENU DASHBOARD) ---
tab1, tab2, tab3 = st.tabs(["📈 TREN RENTANG WAKTU", "📊 PERBANDINGAN MULTI-TANGGAL", "💾 EKSPOR MATRIKS DATA"])

# ==========================================
# TAB 1: TREN RENTANG WAKTU (GRAFIK UTAMA)
# ==========================================
with tab1:
    st.markdown("### ⚙️ Parameter Analisis Rentang Waktu")
    p_col1, p_col2, p_col3 = st.columns([2, 1, 1])

    with p_col1:
        daftar_wilayah = ["Kupang", "Atapupu", "Labuan Bajo", "Ende", "Maumere", "Waingapu", "Kalabahi"]
        pilih_wilayah = st.multiselect("📍 Pilih Lokasi/Pelabuhan (Bisa pilih >1 untuk komparasi):", daftar_wilayah, default=["Kupang"])

    with p_col2:
        tgl_mulai = st.date_input("Tanggal Mulai:", value=default_mulai, min_value=datetime(2026, 1, 1), max_value=datetime(2026, 12, 31))

    with p_col3:
        tgl_selesai = st.date_input("Tanggal Selesai:", value=default_selesai, min_value=datetime(2026, 1, 1), max_value=datetime(2026, 12, 31))

    if tgl_selesai >= tgl_mulai and len(pilih_wilayah) > 0:
        df_tren = load_range_data(tgl_mulai, tgl_selesai, pilih_wilayah)
        
        if not df_tren.empty:
            idx_maks = df_tren['Ketinggian'].idxmax()
            idx_mins = df_tren['Ketinggian'].idxmin()
            row_maks = df_tren.loc[idx_maks]
            row_mins = df_tren.loc[idx_mins]
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"""
                <div style='background-color: #fef2f2; border-left: 5px solid #ef4444; padding: 10px; border-radius: 5px;'>
                    <p style='color: #991b1b; margin:0; font-weight: bold; font-size:13px;'>🔴 PASANG TERTINGGI GLOBAL (Datum: LAT)</p>
                    <h3 style='color: #b91c1c; margin:2px 0;'>{row_maks['Ketinggian']:.2f} m <span style='font-size:14px; font-weight:normal;'>({row_maks['Wilayah']})</span></h3>
                    <p style='color: #7f1d1d; margin:0; font-size:12px;'>Waktu: {row_maks['Waktu'].strftime('%d %b %Y | %H:00 WITA')}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_m2:
                st.markdown(f"""
                <div style='background-color: #eff6ff; border-left: 5px solid #2563eb; padding: 10px; border-radius: 5px;'>
                    <p style='color: #1e40af; margin:0; font-weight: bold; font-size:13px;'>🔵 SURUT TERENDAH GLOBAL (Datum: LAT)</p>
                    <h3 style='color: #1d4ed8; margin:2px 0;'>{row_mins['Ketinggian']:.2f} m <span style='font-size:14px; font-weight:normal;'>({row_mins['Wilayah']})</span></h3>
                    <p style='color: #1e3a8a; margin:0; font-size:12px;'>Waktu: {row_mins['Waktu'].strftime('%d %b %Y | %H:00 WITA')}</p>
                </div>
                """, unsafe_allow_html=True)

            fig = go.Figure()
            warna_garis = ['#0ea5e9', '#0d9488', '#8b5cf6', '#f59e0b', '#ec4899', '#64748b', '#84cc16']

            for i, wil in enumerate(pilih_wilayah):
                df_wil = df_tren[df_tren['Wilayah'] == wil].copy()
                if not df_wil.empty:
                    efek_fill = 'tozeroy' if len(pilih_wilayah) == 1 else None
                    
                    df_wil['Shift_P'] = df_wil['Ketinggian'].shift(1)
                    df_wil['Shift_N'] = df_wil['Ketinggian'].shift(-1)
                    
                    highs = df_wil[(df_wil['Ketinggian'] > df_wil['Shift_P']) & (df_wil['Ketinggian'] > df_wil['Shift_N'])]
                    lows = df_wil[(df_wil['Ketinggian'] < df_wil['Shift_P']) & (df_wil['Ketinggian'] < df_wil['Shift_N'])]

                    fig.add_trace(go.Scatter(
                        x=df_wil['Waktu'], y=df_wil['Ketinggian'],
                        mode='lines', line=dict(color=warna_garis[i % len(warna_garis)], width=3),
                        fill=efek_fill, fillcolor='rgba(14, 165, 233, 0.12)',
                        name=f"Pelabuhan {wil}", hovertemplate="<b>%{x|%d %b %Y, %H:00 WITA}</b><br>Tinggi: %{y:.2f} m<extra></extra>"
                    ))

                    fig.add_trace(go.Scatter(
                        x=highs['Waktu'], y=highs['Ketinggian'],
                        mode='markers+text',
                        marker=dict(color='#ef4444', size=10, symbol='circle', line=dict(color='white', width=2)),
                        text=[f"<b>{y:.2f}m</b>" for y in highs['Ketinggian']], textposition="top center",
                        textfont=dict(color="#dc2626", size=11),
                        name="Titik Pasang", showlegend=(i==0)
                    ))

                    fig.add_trace(go.Scatter(
                        x=lows['Waktu'], y=lows['Ketinggian'],
                        mode='markers+text',
                        marker=dict(color='#2563eb', size=10, symbol='circle', line=dict(color='white', width=2)),
                        text=[f"<b>{y:.2f}m</b>" for y in lows['Ketinggian']], textposition="bottom center",
                        textfont=dict(color="#1d4ed8", size=11),
                        name="Titik Surut", showlegend=(i==0)
                    ))

            max_y_grafik = df_tren['Ketinggian'].max() + 0.8
            
            fig.add_trace(go.Scatter(
                x=[hari_ini, hari_ini], y=[0, max_y_grafik],
                mode='lines', line=dict(color='#10b981', width=2, dash='dash'),
                name="Waktu Saat Ini (Real-time)", hoverinfo='skip'
            ))
            
            fig.add_annotation(
                x=hari_ini, y=max_y_grafik - 0.1, text="WAKTU SAAT INI", showarrow=False,
                xanchor="left", yanchor="bottom", font=dict(color="#047857", size=10, weight="bold")
            )

            fig.update_layout(
                title=dict(text="<b>Grafik Tren Fluktuasi Ketinggian Air Laut (WITA)</b>", font=dict(size=15, color='#1e293b')),
                xaxis=dict(title="Sumbu Waktu Kronologis", showgrid=True, gridcolor='rgba(226, 232, 240, 0.8)', rangeslider=dict(visible=True, thickness=0.06), type="date"),
                yaxis=dict(title="Tinggi Air Gelombang - Datum LAT (m)", showgrid=True, gridcolor='rgba(226, 232, 240, 0.8)', range=[0, max_y_grafik]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                template="plotly_white", height=580, margin=dict(t=50, b=40, l=40, r=40), hovermode="x unified"
            )
            
            fig.add_annotation(text="Referensi Ketinggian: Lowest Astronomical Tide (LAT)", xref="paper", yref="paper", x=0, y=-0.28, showarrow=False, font=dict(size=11, color="grey", style="italic"))
            fig.add_annotation(text="Sumber Data: Pusat Hidro-Oseanografi Angkatan Laut (Pushidrosal)", xref="paper", yref="paper", x=1, y=-0.28, showarrow=False, font=dict(size=11, color="grey", style="italic"))

            st.plotly_chart(fig, use_container_width=True)

            # ==========================================
            # TABEL JADWAL PASANG SURUT (FITUR BARU)
            # ==========================================
            st.markdown("---")
            st.markdown("### 🕒 Jadwal Waktu Pasang dan Surut Harian")
            
            for wil in pilih_wilayah:
                if len(pilih_wilayah) > 1:
                    st.markdown(f"**📍 Lokasi: Pelabuhan {wil}**")
                    
                df_wil = df_tren[df_tren['Wilayah'] == wil].copy()
                df_wil['Shift_P'] = df_wil['Ketinggian'].shift(1)
                df_wil['Shift_N'] = df_wil['Ketinggian'].shift(-1)
                
                # Mengambil data titik puncak dan lembah
                highs = df_wil[(df_wil['Ketinggian'] > df_wil['Shift_P']) & (df_wil['Ketinggian'] > df_wil['Shift_N'])].copy()
                lows = df_wil[(df_wil['Ketinggian'] < df_wil['Shift_P']) & (df_wil['Ketinggian'] < df_wil['Shift_N'])].copy()
                
                # Memformat Data untuk Tabel Pasang (High)
                highs_tabel = highs[['Waktu', 'Ketinggian']].copy()
                highs_tabel['Waktu'] = highs_tabel['Waktu'].dt.strftime('%d %b %Y | %H:00 WITA')
                highs_tabel['Ketinggian'] = highs_tabel['Ketinggian'].apply(lambda x: f"{x:.2f}")
                highs_tabel.rename(columns={'Waktu': 'WAKTU', 'Ketinggian': 'KETINGGIAN (M)'}, inplace=True)
                
                # Memformat Data untuk Tabel Surut (Low)
                lows_tabel = lows[['Waktu', 'Ketinggian']].copy()
                lows_tabel['Waktu'] = lows_tabel['Waktu'].dt.strftime('%d %b %Y | %H:00 WITA')
                lows_tabel['Ketinggian'] = lows_tabel['Ketinggian'].apply(lambda x: f"{x:.2f}")
                lows_tabel.rename(columns={'Waktu': 'WAKTU', 'Ketinggian': 'KETINGGIAN (M)'}, inplace=True)
                
                # Menampilkan berdampingan
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown("<h5 style='color: #b91c1c; margin-bottom: 0;'>⬆️ Pasang Tertinggi (High)</h5>", unsafe_allow_html=True)
                    st.dataframe(highs_tabel.reset_index(drop=True), use_container_width=True)
                with col_t2:
                    st.markdown("<h5 style='color: #1d4ed8; margin-bottom: 0;'>⬇️ Surut Terendah (Low)</h5>", unsafe_allow_html=True)
                    st.dataframe(lows_tabel.reset_index(drop=True), use_container_width=True)
                st.write("")

        else:
            st.warning("⚠️ Data untuk rentang waktu ini belum tersedia.")


# ==========================================
# TAB 2: PERBANDINGAN MULTI-TANGGAL
# ==========================================
with tab2:
    st.markdown("### 📊 Perbandingan Pasut Multi-Tanggal")
    st.caption("Pilih beberapa tanggal (maksimal 6) untuk membandingkan tumpang tindih siklus pasang surut dalam 24 Jam.")
    
    col_w, col_t = st.columns([1, 2])
    with col_w:
        wil_cmp = st.selectbox("📍 Pilih Lokasi/Pelabuhan:", daftar_wilayah, key="cmp_wil")
    with col_t:
        semua_tanggal_2026 = [d.strftime('%Y-%m-%d') for d in pd.date_range('2026-01-01', '2026-12-31')]
        tgl_cmp = st.multiselect("📅 Pilih Tanggal (Maksimal 6):", semua_tanggal_2026, default=[default_mulai.strftime('%Y-%m-%d')], max_selections=6)

    if len(tgl_cmp) > 0:
        fig_cmp = go.Figure()
        warna_cmp = ['#0ea5e9', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#334155']
        
        data_ditemukan = False
        for idx, d_str in enumerate(tgl_cmp):
            d_obj = datetime.strptime(d_str, '%Y-%m-%d')
            df_day_full = load_range_data(d_obj, d_obj, [wil_cmp])
            
            if not df_day_full.empty:
                data_ditemukan = True
                
                fig_cmp.add_trace(go.Scatter(
                    x=df_day_full['Jam'], y=df_day_full['Ketinggian'],
                    mode='lines+markers', line=dict(color=warna_cmp[idx], width=3),
                    marker=dict(size=6),
                    name=f"Tanggal {d_str}", hovertemplate="Jam %{x}:00<br>Tinggi: %{y:.2f} m<extra></extra>"
                ))
        
        if data_ditemukan:
            fig_cmp.update_layout(
                title=dict(text=f"<b>Komparasi 24-Jam Pelabuhan {wil_cmp}</b>", font=dict(size=15, color='#1e293b')),
                xaxis=dict(title="Jam Operasional (WITA)", tickmode='linear', tick0=1, dtick=1, showgrid=True, gridcolor='rgba(226, 232, 240, 0.8)'),
                yaxis=dict(title="Tinggi Air Gelombang - LAT (Meter)", showgrid=True, gridcolor='rgba(226, 232, 240, 0.8)'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                template="plotly_white", height=500, margin=dict(t=50, b=40, l=40, r=40), hovermode="x unified"
            )
            st.plotly_chart(fig_cmp, use_container_width=True)
        else:
            st.warning("Data untuk tanggal yang dipilih belum tersedia di database Excel.")
    else:
        st.info("Silakan pilih minimal 1 tanggal pada kotak di atas.")


# ==========================================
# TAB 3: EKSPOR DATA MATRIKS
# ==========================================
with tab3:
    st.markdown("### 💾 Fitur Ekspor Data Pasut")
    st.write("Unduh data tabular (Matriks 24 Jam) berdasarkan rentang waktu yang telah diatur di Tab 1.")
    
    if tgl_selesai >= tgl_mulai and len(pilih_wilayah) > 0 and 'df_tren' in locals() and not df_tren.empty:
        df_wide = df_tren.copy()
        df_wide['Bulan'] = df_wide['Waktu'].dt.month.map(BULAN_MAP)
        
        df_matrix = df_wide.pivot_table(
            index=['Wilayah', 'Bulan', 'Tanggal'], 
            columns='Jam', 
            values='Ketinggian'
        ).reset_index()
        
        kolom_jam = sorted([c for c in df_matrix.columns if str(c).isdigit()])
        kolom_final = ['Wilayah', 'Bulan', 'Tanggal'] + kolom_jam
        df_matrix = df_matrix[kolom_final]
        df_matrix.columns = [f"Jam {c}" if str(c).isdigit() else c for c in df_matrix.columns]

        csv_buffer = df_matrix.to_csv(index=False).encode('utf-8')
        nama_berkas = f"Data_Matriks_Pasut_BMKG_{tgl_mulai}_sd_{tgl_selesai}.csv"
        
        st.download_button(
            label="📥 UNDUH TABEL DATA FORMAT MATRIKS ASLI (.CSV)",
            data=csv_buffer, file_name=nama_berkas, mime='text/csv', use_container_width=True
        )
        st.dataframe(df_matrix, use_container_width=True)
    else:
        st.info("Pilih rentang data pada Tab 1 (Tren Rentang Waktu) terlebih dahulu untuk mengaktifkan fitur unduhan.")