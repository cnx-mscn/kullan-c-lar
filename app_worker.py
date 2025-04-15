import streamlit as st
import base64
from PIL import Image

# PAGE CONFIG
title = "Montaj İşçi Arayüzü"
st.set_page_config(page_title=title, layout="wide")
st.title(f"👷 {title}")

# Session Init
if "aktif_ekip" not in st.session_state:
    st.session_state.aktif_ekip = None
if "ekipler" not in st.session_state:
    st.session_state.ekipler = {}

# İşçiye Görev Atama ve Onay
st.subheader("📝 Atanmış Görevler")
if st.session_state.aktif_ekip:
    ekip = st.session_state.ekipler.get(st.session_state.aktif_ekip)
    if ekip:
        for i, sehir in enumerate(ekip["visited_cities"]):
            if sehir["foto"] is None:  # Fotoğraf yüklenmemişse görev tamamlanmamış
                st.write(f"📍 {sehir['sehir']} - Onem: {sehir['onem']} - Montaj Süresi: {sehir['is_suresi']} saat")
                photo = st.file_uploader(f"{sehir['sehir']} fotoğraf yükle", type=['jpg', 'jpeg', 'png'], key=f"photo_{i}")
                if photo:
                    # Fotoğraf yüklendikten sonra görevin tamamlandığı bildirilir
                    sehir["foto"] = photo
                    st.success("Fotoğraf yüklendi, görev tamamlandı.")
            else:
                st.write(f"📍 {sehir['sehir']} - Tamamlandı!")
    else:
        st.warning("Aktif ekip bulunamadı.")
else:
    st.warning("Aktif bir ekip seçilmedi.")
