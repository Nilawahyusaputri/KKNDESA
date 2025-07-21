import streamlit as st
import pandas as pd
import joblib
from streamlit_option_menu import option_menu
from io import BytesIO
from datetime import datetime

# Load model dan encoder
model = joblib.load("stunting_classification_model.pkl")
label_encoder_gender = joblib.load("label_encoder_gender.pkl")
label_encoder_status = joblib.load("label_encoder_status.pkl")

# Konfigurasi halaman
st.set_page_config(
    page_title="Prediksi Stunting",
    page_icon="UMT.png"
)

# Saran berdasarkan status
saran_mapping = {
    "Stunting": "Perbanyak makanan bergizi, seperti telur, ikan, daging, dan sayur.",
    "Gizi Kurang": "Konsumsi makanan tinggi kalori dan protein, seperti susu, keju, dan kacang-kacangan.",
    "Normal": "Pertahankan pola makan sehat dan aktivitas fisik.",
    "Gizi Lebih": "Kurangi makanan manis dan berlemak, lebih banyak sayur dan olahraga ringan.",
    "Obesitas": "Batasi makanan cepat saji dan minuman manis, tingkatkan aktivitas fisik harian."
}

# Fungsi hitung umur
def hitung_umur_dalam_bulan(tgl_lahir):
    today = datetime.today()
    delta = today - tgl_lahir
    tahun = today.year - tgl_lahir.year
    bulan = today.month - tgl_lahir.month
    hari = today.day - tgl_lahir.day

    if hari < 0:
        bulan -= 1
        hari += 30

    if bulan < 0:
        tahun -= 1
        bulan += 12

    total_bulan = tahun * 12 + bulan
    return total_bulan, tahun, bulan, hari

# Sidebar
with st.sidebar:
    st.sidebar.markdown(
        "<h2 style='font-size:28px; font-weight:bold; color:#438BFF;'>Prediksi Stunting</h2>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        "<h2 style='font-size:16px; margin-bottom:20px;'>Prediksi lebih cepat, hasil lebih tepat.</h2>",
        unsafe_allow_html=True
    )
    selected = option_menu(
        "Menu Prediksi",
        ["Data Individu", "Data Kelompok"],
        icons=["person", "people"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"font-size": "16px"},
            "menu-title": {"font-size": "18px", "font-weight": "bold"},
            "menu-icon": {"font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px 0",
                "--hover-color": "rgba(67, 139, 255, 0.2)"
            },
            "nav-link-selected": {"background-color": "#438BFF"},
        }
    )
    st.sidebar.markdown("<hr></hr>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<p style='font-size:14px; color:gray; text-align:center;'>© 2025 Kerja Praktik Informatika – Universitas Muhammadiyah Tangerang</p>",
        unsafe_allow_html=True
    )

# Halaman Data Individu
if selected == "Data Individu":
    st.markdown("<h2 style='font-size:32px; font-weight:bold;'>Data Individu</h2>", unsafe_allow_html=True)

    nama = st.text_input("Nama Anak")
    tgl_lahir = st.date_input("Tanggal Lahir")
    jenis_kelamin = st.selectbox("Jenis Kelamin", ["laki-laki", "perempuan"])
    tinggi = st.number_input("Tinggi Badan (cm)", min_value=30.0, max_value=150.0, step=0.1)

    if st.button("Prediksi"):
        umur_bulan, th, bl, hr = hitung_umur_dalam_bulan(tgl_lahir)
        st.info(f"Umur: {th} tahun, {bl} bulan, {hr} hari ({umur_bulan} bulan)")

        jenis_kelamin_encoded = label_encoder_gender.transform([jenis_kelamin])[0]
        input_data = pd.DataFrame([[umur_bulan, jenis_kelamin_encoded, tinggi]],
                                  columns=["Umur (bulan)", "Jenis Kelamin", "Tinggi Badan (cm)"])
        hasil_prediksi = model.predict(input_data)[0]
        label_prediksi = label_encoder_status.inverse_transform([hasil_prediksi])[0].title()
        saran = saran_mapping.get(label_prediksi, "Konsultasi lebih lanjut ke tenaga medis.")

        warna_box = {
            "Stunting": "red",
            "Gizi Kurang": "orange",
            "Normal": "green",
            "Gizi Lebih": "blue",
            "Obesitas": "purple"
        }.get(label_prediksi, "gray")

        st.markdown(
            f"<div style='background-color:{warna_box};padding:20px;border-radius:10px;color:white;'>"
            f"<h4>Nama: {nama}</h4>"
            f"<b>Status Gizi:</b> {label_prediksi}<br>"
            f"<b>Saran:</b> {saran}"
            f"</div>",
            unsafe_allow_html=True
        )

        # Simpan ke Excel
        df_individu = pd.DataFrame([{
            "Nama": nama,
            "Tanggal Lahir": tgl_lahir,
            "Umur (bulan)": umur_bulan,
            "Tinggi Badan (cm)": tinggi,
            "Status Gizi": label_prediksi,
            "Saran": saran
        }])

        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Hasil Individu')
            return output.getvalue()

        st.download_button(
            label="📥 Download Hasil Individu",
            data=to_excel(df_individu),
            file_name=f'hasil_prediksi_{nama.lower().replace(" ", "_")}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

# Halaman Data Kelompok
elif selected == "Data Kelompok":
    st.markdown("<h2 style='font-size:32px; font-weight:bold;'>Data Kelompok</h2>", unsafe_allow_html=True)

    def hitung_umur_dlm_bulan(row):
        try:
            tgl_lahir = pd.to_datetime(row['Tanggal Lahir'])
            umur_bulan, _, _, _ = hitung_umur_dalam_bulan(tgl_lahir)
            return umur_bulan
        except:
            return None

    def predict_status_gizi(row):
        umur_bulan = row['Umur (bulan)']
        jenis_kelamin_encoded = label_encoder_gender.transform([row['Jenis Kelamin']])[0]
        input_data = pd.DataFrame([[umur_bulan, jenis_kelamin_encoded, row['Tinggi Badan (cm)']]],
                                  columns=["Umur (bulan)", "Jenis Kelamin", "Tinggi Badan (cm)"])
        hasil = model.predict(input_data)[0]
        return label_encoder_status.inverse_transform([hasil])[0].title()

    uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx"])
    expected_columns = {"Nama", "Tanggal Lahir", "Jenis Kelamin", "Tinggi Badan (cm)"}

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.dropna(how='all', inplace=True)
        st.subheader("Data Balita")
        st.dataframe(df)

        if not expected_columns.issubset(df.columns):
            st.warning("⚠️ Format file tidak sesuai. Pastikan ada kolom: 'Nama', 'Tanggal Lahir', 'Jenis Kelamin', dan 'Tinggi Badan (cm)'.")
            st.stop()
        else:
            if st.button("Prediksi"):
                df['Umur (bulan)'] = df.apply(hitung_umur_dlm_bulan, axis=1)
                df['Status Gizi'] = df.apply(predict_status_gizi, axis=1)
                df['Saran'] = df['Status Gizi'].map(saran_mapping).fillna("Konsultasi lebih lanjut ke tenaga medis.")

                st.subheader("Hasil Prediksi")
                st.dataframe(df[["Nama", "Tanggal Lahir", "Umur (bulan)", "Tinggi Badan (cm)", "Status Gizi", "Saran"]])

                def to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Hasil Kelompok')
                    return output.getvalue()

                excel_data = to_excel(df)
                st.download_button(
                    label="📥 Download File Hasil Kelompok",
                    data=excel_data,
                    file_name='data_status_gizi_balita.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
