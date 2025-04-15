import streamlit as st
from PIL import Image
import io
import googlemaps
import folium
from streamlit_folium import st_folium

# Google Maps API
gmaps = googlemaps.Client(key="AIzaSyDwQVuPcON3rGSibcBrwhxQvz4HLTpF9Ws")  # 🔒 Buraya kendi API anahtarınızı yazın

st.set_page_config("İşçi Arayüzü", layout="wide")
st.title("👷 İşçi Paneli")

# SESSION INIT
if "gorevler" not in st.session_state:
    st.session_state.gorevler = {}

# GÖREV SEÇİMİ
if st.session_state.gorevler:
    gorev_id = st.selectbox("📋 Atanmış Görevler", list(st.session_state.gorevler.keys()))

    gorev = st.session_state.gorevler[gorev_id]
    st.markdown(f"""
    **📍 Şehir:** {gorev['sehir']}  
    **🛠️ İş Tanımı:** {gorev['is_tanimi']}  
    **📅 Tarih:** {gorev['tarih']}  
    **⏱️ Montaj Süresi:** {gorev['montaj_suresi']} saat  
    """)

    # HARİTA GÖSTER
    if "rota" in gorev:
        st.subheader("🗺️ Harita")
        harita = folium.Map(location=gorev["rota"]["start"], zoom_start=6)
        folium.Marker(gorev["rota"]["start"], tooltip="Başlangıç", icon=folium.Icon(color="blue")).add_to(harita)
        for i, stop in enumerate(gorev["rota"]["path"], 1):
            folium.Marker(stop, tooltip=f"{i}. Nokta", icon=folium.DivIcon(
                html=f"<div style='font-size: 12pt;color:red'><b>{i}</b></div>")
            ).add_to(harita)
        folium.PolyLine(gorev["rota"]["path"], color="green", weight=3).add_to(harita)
        st_folium(harita, height=500)

    # FOTO YÜKLEME
    st.subheader("📤 Görevi Tamamla ve Fotoğraf Yükle")
    fotograf = st.file_uploader("Montaj tamamlandıysa fotoğraf yükleyin", type=["jpg", "jpeg", "png"])
    yeni_is_tanimi = st.text_area("İş Tanımını Detaylandır")

    if fotograf and yeni_is_tanimi:
        if st.button("✅ Görevi Tamamla"):
            img = Image.open(fotograf)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            gorev["fotograf"] = buffer.read()
            gorev["is_tanimi"] = yeni_is_tanimi
            gorev["tamamlandi"] = True
            gorev["onay"] = False
            st.session_state.gorevler[gorev_id] = gorev
            st.success("Görev başarıyla tamamlandı. Yönetici onayı bekleniyor.")

else:
    st.info("📭 Henüz size atanmış bir görev bulunmamaktadır.")
