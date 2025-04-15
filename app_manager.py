import streamlit as st
import googlemaps
from datetime import timedelta
import pandas as pd
from haversine import haversine
import folium
from streamlit_folium import st_folium

# Google Maps API Anahtarınızı girin
gmaps = googlemaps.Client(key="AIzaSyDwQVuPcON3rGSibcBrwhxQvz4HLTpF9Ws")

# PAGE CONFIG
title = "Montaj Rota Planlayıcı"
st.set_page_config(page_title=title, layout="wide")
st.title(f"🛠️ {title}")

# GLOBAL Sabitler
SAATLIK_ISCILIK = 500
benzin_fiyati = 10.0
km_basi_tuketim = 0.1
siralama_tipi = "Önem Derecesi"  # Varsayılan sıralama tipi

# Session Init
if "ekipler" not in st.session_state:
    st.session_state.ekipler = {}
if "aktif_ekip" not in st.session_state:
    st.session_state.aktif_ekip = None
if "baslangic_konum" not in st.session_state:
    st.session_state.baslangic_konum = None

# Ekip Yönetimi
st.sidebar.subheader("👷 Ekip Yönetimi")
ekip_adi = st.sidebar.text_input("Yeni Ekip Adı")
if st.sidebar.button("➕ Ekip Oluştur") and ekip_adi:
    if ekip_adi not in st.session_state.ekipler:
        st.session_state.ekipler[ekip_adi] = {"members": [], "visited_cities": []}
        st.session_state.aktif_ekip = ekip_adi

aktif_secim = st.sidebar.selectbox("Aktif Ekip Seç", list(st.session_state.ekipler.keys()))
st.session_state.aktif_ekip = aktif_secim

# Ekip Üyeleri
st.sidebar.subheader("Ekip Üyeleri")
for ekip, details in st.session_state.ekipler.items():
    if ekip == st.session_state.aktif_ekip:
        new_member = st.sidebar.text_input(f"{ekip} için yeni üye ekleyin", key=f"new_member_{ekip}")
        if st.sidebar.button(f"➕ {ekip} Üyesi Ekle"):
            if new_member:
                details["members"].append(new_member)
                st.sidebar.success(f"{new_member} {ekip} ekibine eklendi.")
        for i, uye in enumerate(details["members"]):
            col1, col2 = st.sidebar.columns([4, 1])
            col1.write(uye)
            if col2.button("❌", key=f"remove_{uye}_{i}") :
                details["members"].remove(uye)
                st.experimental_rerun()

# Başlangıç Noktası
st.sidebar.subheader("📍 Başlangıç Noktası")
if not st.session_state.baslangic_konum:
    adres_input = st.sidebar.text_input("Manuel Adres Girin (1 kez girilir)")
    if st.sidebar.button("✅ Adres Onayla") and adres_input:
        sonuc = gmaps.geocode(adres_input)
        if sonuc:
            st.session_state.baslangic_konum = sonuc[0]["geometry"]["location"]
            st.sidebar.success("Başlangıç noktası belirlendi.")
        else:
            st.sidebar.error("Adres bulunamadı.")

# Şehir Ekleme
st.subheader("📌 Şehir Ekle")
with st.form("sehir_form"):
    sehir_adi = st.text_input("Şehir / Bayi Adı")
    onem = st.slider("Önem Derecesi", 1, 5, 3)
    is_suresi = st.number_input("Montaj Süre (saat)", 1, 24, 2)
    tarih = st.date_input("Montaj Tarihi")
    ekle_btn = st.form_submit_button("➕ Şehir Ekle")
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
                "foto": None  # Fotoğraf ekleme alanı
            })
            st.success(f"{sehir_adi} eklendi.")
        else:
            st.error("Konum bulunamadı.")

# Harita Oluşturma
st.subheader("🗺️ Aktif Ekiplerin Haritası")
if st.session_state.baslangic_konum:
    baslangic = st.session_state.baslangic_konum
    harita = folium.Map(location=[baslangic["lat"], baslangic["lng"]], zoom_start=6)
    folium.Marker([baslangic["lat"], baslangic["lng"]], popup="Başlangıç", icon=folium.Icon(color="blue")).add_to(harita)

    ekip = st.session_state.ekipler[st.session_state.aktif_ekip]
    sehirler = ekip["visited_cities"]
    if siralama_tipi == "Önem Derecesi":
        sehirler = sorted(sehirler, key=lambda x: x["onem"], reverse=True)
    else:
        sehirler = sorted(sehirler, key=lambda x: haversine(
            (baslangic["lat"], baslangic["lng"]),
            (x["konum"]["lat"], x["konum"]["lng"])
        ))

    for i, sehir in enumerate(sehirler, 1):
        lat, lng = sehir["konum"]["lat"], sehir["konum"]["lng"]
        folium.Marker(
            [lat, lng],
            popup=f"{i}. {sehir['sehir']} (Onem: {sehir['onem']})\nTarih: {sehir['tarih']}",
            icon=folium.DivIcon(html=f"<div style='font-size: 12pt; color: red'>{i}</div>")
        ).add_to(harita)
        folium.PolyLine([(baslangic["lat"], baslangic["lng"]), (lat, lng)], color="green").add_to(harita)
        baslangic = sehir["konum"]

    st_folium(harita, width=700)

# İşçiye Görev Atama ve Onay
st.subheader("📝 Atanmış Görevler")
for ekip, details in st.session_state.ekipler.items():
    if ekip == st.session_state.aktif_ekip:
        for i, sehir in enumerate(details["visited_cities"]):
            if sehir["foto"] is None:  # Fotoğraf yüklenmemişse görev tamamlanmamış
                st.write(f"📍 {sehir['sehir']} - Onem: {sehir['onem']} - Montaj Süresi: {sehir['is_suresi']} saat")
                photo = st.file_uploader(f"{sehir['sehir']} fotoğraf yükle", type=['jpg', 'jpeg', 'png'], key=f"photo_{i}")
                if photo:
                    sehir["foto"] = photo
                    st.success("Fotoğraf yüklendi, görev tamamlandı.")
            else:
                st.write(f"📍 {sehir['sehir']} - Tamamlandı!")
