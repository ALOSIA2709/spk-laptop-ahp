import streamlit as st
import pandas as pd
import numpy as np

# =============================
# KONFIGURASI TAMPILAN
# =============================
st.set_page_config(page_title="SPK Laptop AHP", layout="wide")

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
[data-testid="stMetricValue"] { color: #C71585; }
</style>
""", unsafe_allow_html=True)

# =============================
# FUNGSI KONVERSI KE SKOR (1–4)
# =============================
def convert_to_score(row):
    scores = {}

    # Harga (Cost)
    if row['Harga'] <= 7000000: scores['Harga'] = 4
    elif row['Harga'] <= 12000000: scores['Harga'] = 3
    elif row['Harga'] <= 20000000: scores['Harga'] = 2
    else: scores['Harga'] = 1

    scores['RAM'] = {"8GB": 1, "16GB": 2, "32GB": 4}[row['RAM']]
    scores['Performa'] = {
        "Intel i3 / Ryzen 3": 1,
        "Intel i5 / Ryzen 5": 2,
        "Intel i7 / Ryzen 7": 3,
        "Intel i9 / Ryzen 9": 4
    }[row['Performa']]

    scores['GPU'] = {
        "Integrated": 1,
        "GTX": 2,
        "RTX": 3,
        "Dedicated High-End": 4
    }[row['GPU']]

    scores['Portabilitas'] = {
        "> 2.5 kg": 1,
        "2 – 2.5 kg": 2,
        "1.5 – 2 kg": 3,
        "< 1.5 kg": 4
    }[row['Portabilitas']]

    scores['Baterai'] = {
        "< 4 jam": 1,
        "4 – 6 jam": 2,
        "6 – 8 jam": 3,
        "> 8 jam": 4
    }[row['Baterai']]

    scores['Merek'] = {
        "Apple": 4,
        "Asus": 3,
        "Lenovo": 3,
        "HP": 2,
        "Dell": 2,
        "Acer": 2,
        "MSI": 3
    }.get(row['Merek'], 1)

    scores['Kegiatan'] = {
        "Gaming": 4,
        "Desain": 3,
        "Coding": 3,
        "Kerja Kantoran": 2
    }[row['Kegiatan']]

    return pd.Series(scores)

# =============================
# DATA DUMMY
# =============================
if 'data_laptop' not in st.session_state:
    st.session_state.data_laptop = pd.DataFrame([
        ["Asus Zenbook 14", 15000000, "16GB", "Intel i7 / Ryzen 7", "Integrated", "< 1.5 kg", "> 8 jam", "Asus", "Kerja Kantoran"],
        ["Lenovo Legion 5", 22000000, "16GB", "Intel i7 / Ryzen 7", "RTX", "2 – 2.5 kg", "4 – 6 jam", "Lenovo", "Gaming"],
        ["MacBook Air M2", 18000000, "8GB", "Intel i7 / Ryzen 7", "Integrated", "< 1.5 kg", "> 8 jam", "Apple", "Desain"]
    ], columns=["Nama Laptop", "Harga", "RAM", "Performa", "GPU", "Portabilitas", "Baterai", "Merek", "Kegiatan"])

# =============================
# UI INPUT
# =============================
st.title("Pemilihan Laptop Terbaik (AHP)")

with st.expander("Tambahkan Laptop Baru", expanded=True):
    c1, c2, c3 = st.columns(3)

    with c1:
        nama = st.text_input("Nama Laptop")
        harga = st.number_input("Harga (Rp)", min_value=0, value=10000000, step=500000)
        merek = st.selectbox("Merek", ["Asus", "HP", "Apple", "Lenovo", "Acer", "MSI", "Dell"])

    with c2:
        ram = st.selectbox("RAM", ["8GB", "16GB", "32GB"])
        performa = st.selectbox("Processor", [
            "Intel i3 / Ryzen 3", "Intel i5 / Ryzen 5",
            "Intel i7 / Ryzen 7", "Intel i9 / Ryzen 9"
        ])
        gpu = st.selectbox("GPU", ["Integrated", "GTX", "RTX", "Dedicated High-End"])

    with c3:
        berat = st.selectbox("Portabilitas", ["> 2.5 kg", "2 – 2.5 kg", "1.5 – 2 kg", "< 1.5 kg"])
        baterai = st.selectbox("Baterai", ["< 4 jam", "4 – 6 jam", "6 – 8 jam", "> 8 jam"])
        kegiatan = st.selectbox("Kegunaan", ["Gaming", "Kerja Kantoran", "Desain", "Coding"])

    if st.button("Simpan Laptop"):
        st.session_state.data_laptop.loc[len(st.session_state.data_laptop)] = [
            nama, harga, ram, performa, gpu, berat, baterai, merek, kegiatan
        ]
        st.success("Laptop berhasil ditambahkan!")

# =============================
# TABEL DATA
# =============================
st.subheader("Daftar Laptop")
st.dataframe(st.session_state.data_laptop, use_container_width=True)

# =============================
# PROSES AHP
# =============================
if st.button("🏆 HITUNG LAPTOP TERBAIK"):
    df = st.session_state.data_laptop.copy()

    weights = {
        'Harga': 0.194,
        'Performa': 0.156,
        'RAM': 0.100,
        'GPU': 0.075,
        'Merek': 0.039,
        'Kegiatan': 0.353,
        'Baterai': 0.060,
        'Portabilitas': 0.023
    }

    scored = df.apply(convert_to_score, axis=1)
    normalized = scored / scored.max()

    for col, w in weights.items():
        normalized[col] *= w

    df['Total Skor'] = normalized.sum(axis=1)
    hasil = df.sort_values("Total Skor", ascending=False)

    st.snow()
    st.success(f"Laptop Terbaik: **{hasil.iloc[0]['Nama Laptop']}**")

    st.bar_chart(hasil.set_index("Nama Laptop")["Total Skor"])
    st.table(hasil[["Nama Laptop", "Merek", "Kegiatan", "Total Skor"]])
