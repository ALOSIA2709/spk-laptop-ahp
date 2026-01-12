import streamlit as st
import pandas as pd
import numpy as np

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="SPK Laptop AHP", layout="wide")

# CSS untuk tema Pink
st.markdown("""
    <style>
    .main { background-color: #FFF0F5; }
    .stButton>button { 
        background-color: #FF69B4; 
        color: white; 
        border-radius: 12px; 
        border: none;
        width: 100%;
        font-weight: bold;
        height: 3em;
    }
    .stButton>button:hover { background-color: #FF1493; border: 1px solid white; }
    h1, h2, h3 { color: #DB7093; font-family: 'Trebuchet MS', sans-serif; }
    .stSelectbox, .stNumberInput, .stTextInput { border-color: #FFB6C1; }
    [data-testid="stMetricValue"] { color: #C71585; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Konversi Nilai ke Skor (1-4)
def convert_to_score(row):
    scores = {}
    # Kriteria Harga (Cost): Semakin murah semakin tinggi skornya
    if row['Harga'] <= 7000000: scores['Harga'] = 4
    elif row['Harga'] <= 12000000: scores['Harga'] = 3
    elif row['Harga'] <= 20000000: scores['Harga'] = 2
    else: scores['Harga'] = 1
    
    # Kriteria lainnya (Benefit): Semakin tinggi spek semakin tinggi skornya
    scores['RAM'] = {"8GB": 1, "16GB": 2, "32GB": 4}.get(row['RAM'], 1)
    scores['Performa'] = {"Intel i3 / Ryzen 3": 1, "Intel i5 / Ryzen 5": 2, "Intel i7 / Ryzen 7": 3, "Intel i9 / Ryzen 9": 4}.get(row['Performa'], 1)
    scores['Penyimpanan'] = {"HDD": 1, "SSD 256GB": 2, "SSD 512GB": 3, "SSD 1TB": 4}.get(row['Penyimpanan'], 1)
    scores['GPU'] = {"Integrated": 1, "GTX": 2, "RTX": 3, "Dedicated High-End": 4}.get(row['GPU'], 1)
    scores['Portabilitas'] = {"> 2.5 kg": 1, "2 – 2.5 kg": 2, "1.5 – 2 kg": 3, "< 1.5 kg": 4}.get(row['Portabilitas'], 1)
    scores['Baterai'] = {"< 4 jam": 1, "4 – 6 jam": 2, "6 – 8 jam": 3, "> 8 jam": 4}.get(row['Baterai'], 1)
    return pd.Series(scores)

# 3. Data Dummy Awal
if 'data_laptop' not in st.session_state:
    st.session_state.data_laptop = pd.DataFrame([
        ["Asus Zenbook 14", 15000000, "16GB", "Intel i7 / Ryzen 7", "SSD 512GB", "Integrated", "< 1.5 kg", "> 8 jam", "Asus", "Kerja Kantoran"],
        ["Lenovo Legion 5", 22000000, "16GB", "Intel i7 / Ryzen 7", "SSD 512GB", "RTX", "2 – 2.5 kg", "4 – 6 jam", "Lenovo", "Gaming"],
        ["MacBook Air M2", 18000000, "8GB", "Intel i7 / Ryzen 7", "SSD 256GB", "Integrated", "< 1.5 kg", "> 8 jam", "Apple", "Desain"]
    ], columns=["Nama Laptop", "Harga", "RAM", "Performa", "Penyimpanan", "GPU", "Portabilitas", "Baterai", "Merek", "Kegiatan"])

# 4. Antarmuka Pengguna (UI)
st.title("Pemilihan Laptop Terbaik (AHP)")
st.write("Masukkan detail laptop yang sedang Anda pertimbangkan:")

# Form Input
with st.container():
    with st.expander("Tambahkan Laptop Baru ke Daftar", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            nama = st.text_input("Nama/Tipe Laptop", placeholder="Contoh: HP Pavilion 14")
            harga = st.number_input("Harga (Rp)", min_value=0, value=10000000, step=500000)
            merek = st.selectbox("Merek", ["Asus", "HP", "Apple", "Lenovo", "Acer", "MSI", "Dell"])
        with col2:
            ram = st.selectbox("Kapasitas RAM", ["8GB", "16GB", "32GB"])
            performa = st.selectbox("Processor", ["Intel i3 / Ryzen 3", "Intel i5 / Ryzen 5", "Intel i7 / Ryzen 7", "Intel i9 / Ryzen 9"])
            storage = st.selectbox("Penyimpanan", ["HDD", "SSD 256GB", "SSD 512GB", "SSD 1TB"])
        with col3:
            gpu = st.selectbox("Tipe GPU", ["Integrated", "GTX", "RTX", "Dedicated High-End"])
            berat = st.selectbox("Berat (Portabilitas)", ["> 2.5 kg", "2 – 2.5 kg", "1.5 – 2 kg", "< 1.5 kg"])
            baterai = st.selectbox("Daya Tahan Baterai", ["< 4 jam", "4 – 6 jam", "6 – 8 jam", "> 8 jam"])
            kegiatan = st.selectbox("Tujuan Penggunaan", ["Gaming", "Kerja Kantoran", "Desain", "Coding"])

        if st.button("📥 Simpan ke Daftar"):
            if nama:
                new_row = [nama, harga, ram, performa, storage, gpu, berat, baterai, merek, kegiatan]
                st.session_state.data_laptop.loc[len(st.session_state.data_laptop)] = new_row
                st.toast(f"{nama} berhasil ditambahkan!", icon="✅")
            else:
                st.error("Nama Laptop tidak boleh kosong!")

# 5. Tabel Data
st.write("---")
st.write("### Daftar Laptop yang Dibandingkan")
st.dataframe(st.session_state.data_laptop, use_container_width=True)

# 6. Kalkulasi AHP
if st.button("HITUNG SKOR TERBAIK"):
    if len(st.session_state.data_laptop) < 1:
        st.warning("Silakan tambahkan data laptop terlebih dahulu.")
    else:
        df = st.session_state.data_laptop.copy()
        
        # Bobot Kriteria (Total harus 1.0)
        weights = {
            'Harga': 0.30, 'Performa': 0.20, 'RAM': 0.15, 
            'GPU': 0.15, 'Penyimpanan': 0.10, 'Baterai': 0.05, 'Portabilitas': 0.05
        }
        
        # Proses Perhitungan
        # 1. Scoring numerik
        scored_df = df.apply(convert_to_score, axis=1)
        
        # 2. Normalisasi Max
        norm_df = scored_df / scored_df.max()
        
        # 3. Perkalian dengan Bobot
        for col, weight in weights.items():
            norm_df[col] = norm_df[col] * weight
            
        # 4. Total Skor
        df['Total Skor'] = norm_df.sum(axis=1)
        
        # Sorting
        hasil = df.sort_values(by='Total Skor', ascending=False).reset_index(drop=True)

        # Output Visual
        st.snow() # Efek salju/pita jatuh
        st.write("---")
        st.subheader("🏆 Hasil Rekomendasi Laptop")
        
        best = hasil.iloc[0]
        st.success(f"Laptop terbaik untuk Anda adalah **{best['Nama Laptop']}** ({best['Merek']}) dengan skor akhir **{best['Total Skor']:.3f}**")
        
        # Grafik
        st.write("#### 📊 Grafik Perbandingan Skor")
        st.bar_chart(hasil.set_index('Nama Laptop')['Total Skor'])
        
        # Tabel Final
        st.write("#### Tabel Peringkat")
        st.table(hasil[['Nama Laptop', 'Merek', 'Harga', 'Kegiatan', 'Total Skor']])