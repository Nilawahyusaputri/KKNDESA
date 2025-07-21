import streamlit as st
import pandas as pd
import joblib
from streamlit_option_menu import option_menu
from io import BytesIO

model = joblib.load("stunting_classification_model.pkl")
label_encoder_gender = joblib.load("label_encoder_gender.pkl")
label_encoder_status = joblib.load("label_encoder_status.pkl")

st.set_page_config(
    page_title="Prediksi Stunting",
    page_icon="UMT.png"
)

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
            "menu-title":{
                "font-size": "18px",
                "font-weight": "bold",
            },
            "menu-icon": {
                "font-size": "18px",
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px 0",
                "--hover-color": "rgba(67, 139, 255, 0.2)"
            },
            "nav-link-selected": {
                "background-color": "#438BFF",
            },
        }
    )
    st.sidebar.markdown("<hr></hr>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<p style='font-size:14px; color:gray; text-align:center;'>© 2025 Kerja Praktik Informatika – Universitas Muhammadiyah Tangerang</p>",
        unsafe_allow_html=True
    )

if selected == "Data Individu":
    st.markdown(
        "<h2 style='font-size:32px; font-weight:bold;'>Data Individu</h2>",
        unsafe_allow_html=True
    )

    umur = st.number_input("Umur (bulan)", min_value=0, max_value=60, step=1)
    jenis_kelamin = st.selectbox("Jenis Kelamin", ["laki-laki", "perempuan"])
    tinggi = st.number_input("Tinggi Badan (cm)", min_value=30.0, max_value=150.0, step=0.1)

    if st.button("Prediksi"):
        jenis_kelamin_encoded = label_encoder_gender.transform([jenis_kelamin])[0]
        input_data = pd.DataFrame([[umur, jenis_kelamin_encoded, tinggi]],
                                  columns=["Umur (bulan)", "Jenis Kelamin", "Tinggi Badan (cm)"])
        hasil_prediksi = model.predict(input_data)[0]
        label_prediksi = label_encoder_status.inverse_transform([hasil_prediksi])[0].title()

        if hasil_prediksi == 1 or hasil_prediksi == 2:
            st.error(f"Status Gizi: **{label_prediksi}**")
        else:
            st.success(f"Status Gizi: **{label_prediksi}**")

elif selected == "Data Kelompok":
    st.markdown(
        "<h2 style='font-size:32px; font-weight:bold;'>Data Kelompok</h2>",
        unsafe_allow_html=True
    )

    def predict_status_gizi(row):
        jenis_kelamin_encoded_group = label_encoder_gender.transform([row['Jenis Kelamin']])[0]
        input_data_group = pd.DataFrame([[row['Umur (bulan)'], jenis_kelamin_encoded_group, row['Tinggi Badan (cm)']]],
                                  columns=["Umur (bulan)", "Jenis Kelamin", "Tinggi Badan (cm)"])
        hasil_prediksi_group = model.predict(input_data_group)[0]
        label_prediksi_group = label_encoder_status.inverse_transform([hasil_prediksi_group])[0].title()
        return label_prediksi_group

    uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx"])
    expected_columns = {"Umur (bulan)", "Jenis Kelamin", "Tinggi Badan (cm)", "Status Gizi"}
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.dropna(how='all', inplace=True)
        st.subheader("Data Balita")
        st.dataframe(df)

        if not expected_columns.issubset(df.columns):
            st.warning(
                "⚠️ Format file tidak sesuai. Pastikan kolom: 'Umur (bulan)', 'Jenis Kelamin', dan 'Tinggi Badan (cm)' tersedia.")
            st.stop()
        else:
            if st.button("Prediksi"):
                df['Status Gizi'] = df.apply(predict_status_gizi, axis=1)
                st.subheader("Hasil Prediksi")
                st.dataframe(df)

                def to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                    return output.getvalue()

                excel_data = to_excel(df)
                st.download_button(
                    label="Download File Hasil Prediksi",
                    data=excel_data,
                    file_name='data_status_gizi_balita.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
