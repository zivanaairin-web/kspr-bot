import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="Cek Resiko Hamil - KSPR", page_icon="🤰")
st.title("🤰 Cek Resiko Kehamilan - KSPR")
st.warning("Skrining awal Pondji Rochjati, BUKAN diagnosis. Tetap periksa ke Bidan/Dokter ya Bun..")

FAKTOR = [
    ("Hamil pertama usia <16 tahun", 4),
    ("Hamil pertama usia >35 tahun", 4),
    ("Anak terakhir umur <2 tahun / jarak hamil >10 tahun", 4),
    ("Jarak hamil lagi <2 tahun", 4),
    ("Anak sudah 4 atau lebih", 4),
    ("Usia ibu sekarang >35 tahun", 4),
    ("Tinggi badan <145 cm", 4),
    ("Pernah gagal kehamilan / keguguran", 4),
    ("Pernah melahirkan dengan vakum / tang / operasi caesar", 8),
    ("Pernah pendarahan hebat setelah melahirkan", 8),
    ("Pernah kejang / eklamsia", 8),
    ("Bayi lahir <2500 gram / prematur", 4),
    ("Pernah bayi meninggal dalam kandungan / setelah lahir", 8),
    ("Ada penyakit: TBC, jantung, ginjal, diabetes, hipertensi, HIV, malaria", 8),
    ("Bengkak di kaki / muka + tekanan darah tinggi", 4),
    ("Kehamilan lebih bulan (>42 minggu)", 4),
    ("Letak sungsang", 8),
    ("Letak lintang", 8),
    ("Ada perdarahan di kehamilan ini", 8),
    ("Preeklampsia berat / kejang-kejang", 8),
]

nama = st.text_input("Nama Ibu")
hp = st.text_input("No HP / WA")
usia = st.number_input("Usia Kehamilan (minggu)", min_value=1, max_value=45, value=12)
st.subheader("Centang jika ada:")
pilihan = []
for i, (teks, skor) in enumerate(FAKTOR):
    if st.checkbox(f"{i+1}. {teks} (skor {skor})"):
        pilihan.append((teks, skor))

if st.button("LIHAT HASIL", type="primary"):
    total = sum(s for _, s in pilihan)
    if total <= 2:
        kat = "KRR - Rendah (Hijau)"
        saran = "Bersalin di Bidan, ANC rutin"
    elif total <= 6:
        kat = "KRT - Tinggi (Kuning)"
        saran = "Wajib periksa ke Dokter/Puskesmas, rujuk terencana"
    else:
        kat = "KST - Sangat Tinggi (Merah)"
        saran = "SEGERA ke RS, harus ditangani Dokter Spesialis!"

    st.success(f"Total Skor: {total} - {kat}")
    st.info(f"Saran: {saran}")

    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("kunci.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("DATA KSPR").sheet1
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        faktor_text = "; ".join([p[0] for p in pilihan]) if pilihan else "Tidak ada faktor"
        sheet.append_row([waktu, nama, hp, usia, total, kat, faktor_text])
        st.success("Hasil sudah tersimpan & terkirim ke Bidan ✅")
    except Exception as e:
        st.error(f"Gagal simpan ke Sheets: {e}")
