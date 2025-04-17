# app_manager.py
import streamlit as st
import googlemaps
import pandas as pd
from datetime import date
from haversine import haversine
import folium
from streamlit_folium import st_folium

# Google Maps API Anahtarı
gmaps = googlemaps.Client(key="AIzaSyDwQVuPcON3rGSibcBrwhxQvz4HLTpF9Ws")  # Kendi API anahtarınızı girin

st.set_page_config(page_title="Yönetici Paneli", layout="wide")
st.title("🛠️ Montaj Yönetici Paneli")

# Kullanıcı girişi
if "giris_tipi" not in st.session_state:
    st.session_state.giris_tipi = st.radio("Giriş tipi seçin:", ["Yönetici", "İşçi"])

if "ekipler" not in st.session_state:
    st.session_state.ekipler = {}
if "aktif_ekip" not in st.session_state:
    st.session_state.aktif_ekip = None
if "baslangic_konum" not in st.session_state:
    st.session_state.baslangic_konum = None

if st.session_state.giris_tipi != "Yönetici":
    st.warning("Bu sayfa sadece yönetici girişi içindir.")
    st.stop()

# Ekip Yönetimi
st.sidebar.header("👷 Ekip Yönetimi")
ekip_adi = st.sidebar.text_input("Yeni Ekip Adı")
if st.sidebar.button("➕ Ekip Oluştur") and ekip_adi:
    if ekip_adi not in st.session_state.ekipler:
        st.session_state.ekipler[ekip_adi] = {"members": [], "visited_cities": []}
        st.session_state.aktif_ekip = ekip_adi

aktif_secim = st.sidebar.selectbox("Aktif Ekip Seç", list(st.session_state.ekipler.keys()))
st.session_state.aktif_ekip = aktif_secim

# Başlangıç Noktası
st.sidebar.header("📍 Başlangıç Konumu")
if not st.session_state.baslangic_konum:
    adres = st.sidebar.text_input("Başlangıç adresini girin")
    if st.sidebar.button("✅ Konumu Onayla") and adres:
        sonuc = gmaps.geocode(adres)
        if sonuc:
            st.session_state.baslangic_konum = sonuc[0]["geometry"]["location"]
            st.sidebar.success("Başlangıç noktası belirlendi.")
        else:
            st.sidebar.error("Konum bulunamadı.")

# Şehir Ekleme
st.subheader("📌 Görev (Şehir) Ekle")
with st.form("sehir_form"):
    sehir_adi = st.text_input("Şehir / Bayi Adı")
    onem = st.slider("Önem Derecesi", 1, 5, 3)
    is_suresi = st.number_input("Montaj Süresi (saat)", 1, 24, 2)
    tarih = st.date_input("Montaj Tarihi", value=date.today())
    ekle_btn = st.form_submit_button("➕ Görev Ekle")
    if ekle_btn:
        sonuc = gmaps.geocode(sehir_adi)
        if sonuc:
            konum = sonuc[0]["geometry"]["location"]
            st.session_state.ekipler[st.session_state.aktif_ekip]["visited_cities"].append({
                "sehir": sehir_adi,
                "konum": konum,
                "onem": onem,
                "is_suresi": is_suresi,
                "tarih": str(tarih),
                "foto": None,
                "onay": None
            })
            st.success(f"{sehir_adi} eklendi.")
        else:
            st.error("Şehir bulunamadı.")

# Harita
st.subheader("🗺️ Rota Haritası")
if st.session_state.baslangic_konum:
    baslangic = st.session_state.baslangic_konum
    harita = folium.Map(location=[baslangic["lat"], baslangic["lng"]], zoom_start=6)
    folium.Marker([baslangic["lat"], baslangic["lng"]], popup="Başlangıç", icon=folium.Icon(color="blue")).add_to(harita)

    sehirler = st.session_state.ekipler[st.session_state.aktif_ekip]["visited_cities"]
    sehirler = sorted(sehirler, key=lambda x: x["onem"], reverse=True)

    for i, sehir in enumerate(sehirler, 1):
        lat, lng = sehir["konum"]["lat"], sehir["konum"]["lng"]
        durum = sehir.get("onay")
        renk = "red"
        if durum == True:
            renk = "green"
        elif durum == None and sehir["foto"]:
            renk = "orange"
        folium.Marker(
            [lat, lng],
            popup=f"{i}. {sehir['sehir']} ({sehir['tarih']})",
            icon=folium.Icon(color=renk)
        ).add_to(harita)

    st_folium(harita, width=700)

# Onay Paneli
st.subheader("✅ Görev Onay Paneli")
for i, sehir in enumerate(sehirler):
    if sehir["foto"] and sehir["onay"] is None:
        st.info(f"{sehir['sehir']} → Fotoğraf yüklendi, onay bekliyor.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✔️ Onayla", key=f"onay_{i}"):
                sehir["onay"] = True
        with col2:
            if st.button("❌ Reddet", key=f"red_{i}"):
                sehir["onay"] = False
