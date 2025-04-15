
import streamlit as st
from PIL import Image

# PAGE CONFIG
title = "İşçi Arayüzü"
st.set_page_config(page_title=title, layout="wide")
st.title(f"🛠️ {title}")

# Fotoğraf Yükleme
st.subheader("📸 Fotoğraf Yükleyin")
uploaded_image = st.file_uploader("Fotoğrafınızı yükleyin", type=["jpg", "jpeg", "png"])

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Yüklenen Fotoğraf", use_column_width=True)

# Şehir ve Montaj Süresi
st.subheader("📍 Şehir ve Montaj Süresi")
with st.form("sehir_form"):
    sehir_adi = st.text_input("Şehir / Bayi Adı")
    is_suresi = st.number_input("Montaj Süre (saat)", 1, 24, 2)
    tamamla_btn = st.form_submit_button("Görev Tamamla")
    if tamamla_btn:
        st.success(f"{sehir_adi} için montaj görevi tamamlandı. Süre: {is_suresi} saat.")
