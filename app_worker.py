# app_worker.py
import streamlit as st

st.set_page_config(page_title="İşçi Paneli", layout="wide")
st.title("👷 Montaj İşçi Paneli")

# Giriş Kontrolü
if "giris_tipi" not in st.session_state:
    st.session_state.giris_tipi = st.radio("Giriş tipi seçin:", ["Yönetici", "İşçi"])

if st.session_state.giris_tipi != "İşçi":
    st.warning("Bu sayfa sadece işçi girişi içindir.")
    st.stop()

if "aktif_ekip" not in st.session_state:
    st.session_state.aktif_ekip = None
if "ekipler" not in st.session_state:
    st.session_state.ekipler = {}

aktif_secim = st.selectbox("Ekip Seç", list(st.session_state.ekipler.keys()) if st.session_state.ekipler else [])
st.session_state.aktif_ekip = aktif_secim

# Görevler
if st.session_state.aktif_ekip:
    ekip = st.session_state.ekipler.get(st.session_state.aktif_ekip)
    if ekip:
        st.subheader(f"{aktif_secim} ekibine atanmış görevler")
        for i, sehir in enumerate(ekip["visited_cities"]):
            if not sehir["foto"]:
                st.write(f"📍 {sehir['sehir']} - {sehir['tarih']} - Süre: {sehir['is_suresi']} saat")
                foto = st.file_uploader(f"Fotoğraf yükle ({sehir['sehir']})", type=["jpg", "jpeg", "png"], key=f"foto_{i}")
                if foto:
                    sehir["foto"] = foto
                    st.success("Fotoğraf yüklendi, onay bekleniyor.")
            else:
                if sehir["onay"] == True:
                    st.success(f"{sehir['sehir']} ✅ Onaylandı")
                elif sehir["onay"] == False:
                    st.error(f"{sehir['sehir']} ❌ Reddedildi, tekrar yükleyin")
                    sehir["foto"] = None
                else:
                    st.info(f"{sehir['sehir']} ⏳ Onay bekleniyor")
    else:
        st.warning("Ekip verisi bulunamadı.")
else:
    st.warning("Lütfen bir ekip seçin.")
