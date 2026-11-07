import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

st.set_page_config(page_title="Cek Resiko Hamil - KSPR", page_icon="🤰")
st.title("🤰 Cek Resiko Kehamilan - KSPR")
st.warning("Skrining awal Poedji Rochjati. BUKAN diagnosis. Tetap periksa ke Bidan/Dokter ya Bun.")

# ===== 20 FAKTOR KSPR =====
FAKTOR = [
    (1, "Hamil pertama usia <=16 tahun?", 4),
    (2, "Hamil pertama usia >=35 tahun?", 4),
    (3, "Kawin >=4 tahun baru hamil / jarak hamil >=10 tahun?", 4),
    (4, "Jarak hamil lagi <2 tahun?", 4),
    (5, "Anak sudah 4 atau lebih?", 4),
    (6, "Usia ibu sekarang >=35 tahun?", 4),
    (7, "Tinggi badan <=145 cm?", 4),
    (8, "Pernah gagal kehamilan / keguguran?", 4),
    (9, "Pernah lahiran vakum / uri dirogoh / transfusi?", 4),
    (10, "Pernah operasi Caesar?", 8),
    (11, "Punya penyakit: anemia, malaria, TBC, jantung, diabetes, IMS?", 4),
    (12, "Bengkak muka/tungkai + darah tinggi?", 4),
    (13, "Hamil kembar 2 atau lebih?", 4),
    (14, "Air ketuban banyak / perut besar sekali?", 4),
    (15, "Riwayat bayi mati dalam kandungan?", 4),
    (16, "Kehamilan lebih bulan (>42 minggu)?", 4),
    (17, "Letak sungsang?", 8),
    (18, "Letak lintang?", 8),
    (19, "Ada perdarahan di kehamilan ini?", 8),
    (20, "Preeklampsia berat / kejang-kejang?", 8),
]

# ===== FORM PASIEN =====
nama = st.text_input("Nama Ibu")
no_hp = st.text_input("No HP / WA")
usia_hamil = st.number_input("Usia Kehamilan (minggu)", 1, 45, 20)

st.subheader("Jawab dengan centang jika YA (Skor awal Bunda = 2)")
jawaban_ya = []
for id, tanya, skor in FAKTOR:
    if st.checkbox(f"{id}. {tanya} (skor {skor})", key=id):
        jawaban_ya.append((id, skor))

def simpan_ke_sheets(nama, no_hp, usia_hamil, total, kategori):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Di Streamlit Cloud pakai secrets, di laptop pakai kunci.json
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("kunci.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("DATA KSPR").sheet1
        sheet.append_row([str(datetime.now()), nama, no_hp, str(usia_hamil), str(total), kategori, str(jawaban_ya)])
        return True
    except Exception as e:
        st.error(f"Gagal simpan ke Sheets: {e}")
        return False

if st.button("LIHAT HASIL", type="primary"):
    total = 2 + sum(s for _, s in jawaban_ya)
    if total == 2:
        kategori = "KRR - Rendah (Hijau)"
        st.success(f"Total Skor: {total} - {kategori}")
        st.info("Saran: Bersalin di Bidan, ANC rutin")
    elif total <= 10:
        kategori = "KRT - Tinggi (Kuning)"
        st.warning(f"Total Skor: {total} - {kategori}")
        st.info("Saran: Periksa ke Puskesmas, bersalin dengan tenaga kesehatan")
    else:
        kategori = "KRST - Sangat Tinggi (Merah)"
        st.error(f"Total Skor: {total} - {kategori}")
        st.info("Saran: WAJIB ke RS / SpOG, segera hubungi bidan!")

    if simpan_ke_sheets(nama, no_hp, usia_hamil, total, kategori):
        st.success("Hasil sudah tersimpan & terkirim ke Bidan.")
