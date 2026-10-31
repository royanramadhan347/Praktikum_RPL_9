import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import layer-layer yang telah dibuat
from models.model import Base
from repositories.repository import MahasiswaRepository
from services.service import PrediksiService

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Prediksi Kelulusan", page_icon="🎓")


@st.cache_resource
def inisialisasi_database():
  load_dotenv()
  # Mengambil URL dari .env, dengan fallback ke sqlite lokal jika tidak terbaca
  db_url = os.getenv("DATABASE_URL") or "sqlite:///data_prediksi.db"
  engine = create_engine(db_url)
  Base.metadata.create_all(bind=engine)
  Session = sessionmaker(bind=engine)
  return Session()


# Inisialisasi Database, Repository, dan Service
db_session = inisialisasi_database()
repo = MahasiswaRepository(db_session)
service = PrediksiService()

# 2. Membangun UI (View)
st.title("🎓 Sistem Prediksi Kelulusan")

with st.form("form_input"):
  nama = st.text_input("Nama Mahasiswa")
  ipk = st.number_input(
      "IPK (0.0 - 4.0)", min_value=0.0, max_value=4.0, step=0.01
  )
  sks = st.number_input("Total SKS", min_value=0, step=1)
  tombol_proses = st.form_submit_button("Prediksi & Simpan")

# 3. Logika saat tombol ditekan
if tombol_proses:
  if nama.strip() == "":
    st.warning("⚠️ Nama tidak boleh kosong!")
  else:
    hasil_status = service.tentukan_kelulusan(ipk, sks)
    repo.simpan_data(nama, ipk, sks, hasil_status)

    if hasil_status == "Lulus Tepat Waktu":
      st.success(f"🎉 **{nama}** dinyatakan **{hasil_status}**!")
    else:
      st.error(f"❌ **{nama}** dinyatakan **{hasil_status}**.")
    st.toast("Data berhasil disimpan!")

# 4. Menampilkan Riwayat Data (Tabel)
st.divider()
st.subheader("📜 Riwayat Prediksi")
data_db = repo.ambil_semua_data()
if data_db:
  list_data = [{
      "Nama": d.nama,
      "IPK": d.ipk,
      "SKS": d.sks,
      "Status": d.status_kelulusan,
  } for d in data_db]
  df = pd.DataFrame(list_data)
  st.dataframe(df, use_container_width=True)