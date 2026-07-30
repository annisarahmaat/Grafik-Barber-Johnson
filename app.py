import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch

# 1. KONFIGURASI HALAMAN WEB
st.set_page_config(
    page_title="Aplikasi Grafik Barber Johnson",
    page_icon="📊",
    layout="wide"
)

# Judul Utama
st.title("Aplikasi Generator Grafik Barber Johnson")
st.markdown("Aplikasi interaktif untuk analisis efisiensi pelayanan rawat inap Rumah Sakit.")
st.divider()

# 2. PANEL INPUT DATA (SIDEBAR KIRI)
st.sidebar.header("⚙️ Form Input Data RS")
st.sidebar.caption("💡 *Gunakan tombol **Tab** di keyboard untuk berpindah antar input dengan cepat seperti di Excel.*")

periode     = st.sidebar.text_input("Nama Periode (misal: Januari 2026)", value="")
bor         = st.sidebar.number_input("1. BOR - Bed Occupancy Rate (%)", min_value=0.0, max_value=100.0, value=None, step=0.10, format="%.2f")
los         = st.sidebar.number_input("2. AvLOS - Length of Stay (Hari)", min_value=0.0, value=None, step=0.01, format="%.2f")
toi         = st.sidebar.number_input("3. TOI - Turn Over Interval (Hari)", min_value=0.0, value=None, step=0.01, format="%.2f")
bto         = st.sidebar.number_input("4. BTO - Bed Turnover (Kali)", min_value=0.0, value=None, step=0.01, format="%.2f")
jumlah_hari = st.sidebar.number_input("5. Jumlah Hari Periode (misal: 31 untuk Jan)", min_value=1, value=None, step=1)

# Tentukan Nama Periode
nama_periode = f"— Periode {periode.strip()}" if periode.strip() != "" else ""

# 3. LAYOUT UTAMA (Dua Kolom)
col1, col2 = st.columns([2.5, 1])

with col1:
    # Menggunakan spinner agar loading grafik terlihat rapi & transisi mulus
    with st.spinner("Memproses grafik..."):
        fig, ax = plt.subplots(figsize=(8.5, 7.5), dpi=120)
        
        max_x = 8
        max_y = 15
        
        # A. DAERAH EFISIENSI (Selalu Tampil)
        x_poly = [1.0, 1.0, 3.0, 3.0, 1.17]
        y_poly = [3.5, 14.0, 14.0, 9.35, 3.5]
        
        ax.fill(x_poly, y_poly, color='#b0a875', alpha=0.75, label='Daerah Efisiensi')
        ax.text(2.0, 10.5, 'Daerah\nEfisiensi', fontsize=12, color='#2c2810', fontweight='bold', 
                ha='center', va='center')

        x_grid = np.linspace(0, max_x, 500)

        # Warna Garis
        color_bor = '#dc2626'  # Merah
        color_bto = '#16a34a'  # Hijau
        color_toi = '#2563eb'  # Biru
        color_los = '#9333ea'  # Ungu

        # B. GARIS BOR (Merah) -> Langsung muncul begitu BOR diisi!
        if bor is not None and 0 < bor < 100:
            slope_bor = bor / (100 - bor)
            y_bor = slope_bor * x_grid
            valid_bor = (y_bor <= max_y) & (x_grid <= max_x)
            if np.any(valid_bor):
                end_x = x_grid[valid_bor][-1]
                end_y = y_bor[valid_bor][-1]
                
                ax.plot(x_grid[valid_bor], y_bor[valid_bor], color=color_bor, linewidth=2.5)
                ax.annotate('', xy=(end_x, end_y), xytext=(end_x*0.95, end_y*0.95),
                            arrowprops=dict(arrowstyle="->", color=color_bor, lw=2.5))

        # C. GARIS BTO (Hijau) -> Langsung muncul jika BTO & Jumlah Hari diisi!
        if bto is not None and jumlah_hari is not None and bto > 0:
            c_bto = jumlah_hari / bto
            y_bto = c_bto - x_grid
            valid_bto = (y_bto >= 0) & (y_bto <= max_y) & (x_grid <= max_x)
            if np.any(valid_bto):
                ax.plot(x_grid[valid_bto], y_bto[valid_bto], color=color_bto, linestyle='-', linewidth=2.0)

        # D. GARIS TOI & AvLOS + TITIK HASIL -> Langsung muncul jika TOI & AvLOS diisi!
        if toi is not None and los is not None:
            ax.plot([toi, toi], [0, los], color=color_toi, linestyle='--', linewidth=2.0, zorder=4)
            ax.plot([0, toi], [los, los], color=color_los, linestyle='--', linewidth=2.0, zorder=4)
            ax.scatter(toi, los, color='black', s=80, zorder=6)

        # E. KOTAK LEGENDA IN-GRAPH (Hanya jika SEMUA data terisi)
        if (bor is not None) and (los is not None) and (toi is not None) and (bto is not None):
            box = FancyBboxPatch((4.2, 10.5), 3.5, 4.0, boxstyle="round,pad=0.2", 
                                 facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.5, zorder=3)
            ax.add_patch(box)

            lbl_periode = periode.strip() if periode.strip() != "" else "Input Data"
            ax.text(5.95, 14.1, f"Keterangan — {lbl_periode}", fontsize=10, fontweight='bold', color='#0f172a', ha='center', va='top', zorder=4)
            
            y_start = 13.3
            ax.text(4.5, y_start,        "— BOR", color=color_bor, fontweight='bold', fontsize=9.5, va='top', zorder=4)
            ax.text(6.1, y_start,        f": {bor:.2f}%", color='#334155', fontweight='bold', fontsize=9.5, va='top', zorder=4)
            
            ax.text(4.5, y_start - 0.65, "— BTO", color=color_bto, fontweight='bold', fontsize=9.5, va='top', zorder=4)
            ax.text(6.1, y_start - 0.65, f": {bto:.2f} kali", color='#334155', fontweight='bold', fontsize=9.5, va='top', zorder=4)
            
            ax.text(4.5, y_start - 1.30, "— TOI", color=color_toi, fontweight='bold', fontsize=9.5, va='top', zorder=4)
            ax.text(6.1, y_start - 1.30, f": {toi:.2f} hari", color='#334155', fontweight='bold', fontsize=9.5, va='top', zorder=4)
            
            ax.text(4.5, y_start - 1.95, "— AvLOS", color=color_los, fontweight='bold', fontsize=9.5, va='top', zorder=4)
            ax.text(6.1, y_start - 1.95, f": {los:.2f} hari", color='#334155', fontweight='bold', fontsize=9.5, va='top', zorder=4)

        # F. STYLING SKALA SUMBU
        ax.set_xlabel('TOI ( Turn Over Interval )', fontweight='bold', fontsize=11)
        ax.set_ylabel('AvLOS ( Average Lenght Of Stay )', fontweight='bold', fontsize=11)
        ax.set_title(f'Grafik Barber Johnson {nama_periode}', fontweight='bold', fontsize=13, pad=15)
        
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)
        
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        
        ax.grid(True, which='major', color='#cbd5e1', linestyle='-', linewidth=0.6)
        ax.minorticks_on()
        ax.grid(True, which='minor', color='#e2e8f0', linestyle=':', linewidth=0.5)
        
        plt.tight_layout()
        st.pyplot(fig)

# 4. KOTAK KESIMPULAN OTOMATIS (SIDE PANEL KANAN)
with col2:
    st.subheader("📋 Status Efisiensi")
    
    # Status Efisiensi baru dihitung kalau BOR & TOI sudah diisi
    if bor is not None and toi is not None:
        is_efisien = (60.0 <= bor <= 85.0) and (1.0 <= toi <= 3.0)

        if is_efisien:
            st.success("✅ EFISIEN: Berada dalam rentang standar Depkes RI.")
        else:
            st.error("❌ BELUM EFISIEN: Berada di luar rentang standar Depkes RI.")
    else:
        st.info("Masukkan nilai **BOR** & **TOI** untuk melihat status efisiensi.")

    st.markdown("---")
    st.markdown("**Ringkasan Indikator:**")
    st.metric("BOR", f"{bor:.2f}%" if bor is not None else "-")
    st.metric("AvLOS", f"{los:.2f} hari" if los is not None else "-")
    st.metric("TOI", f"{toi:.2f} hari" if toi is not None else "-")
    st.metric("BTO", f"{bto:.2f} kali" if bto is not None else "-")
