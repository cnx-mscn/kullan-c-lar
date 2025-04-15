import streamlit as st
import json
import io
from PIL import Image
import folium
from streamlit_folium import st_folium
from pathlib import Path

GOREV_DOSYA = "gorevler.json"

def gorevleri_yukle():
    if Path(GOREV_DOSYA).exists():
        with open(GOREV_DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def gorevleri_kaydet(gorevler):
    with open(GOREV_DOSYA, "w", encoding="utf-8") as f:
        json.dump(gorevler, f, ensure_ascii=False, indent=2)

st.title("🛠️ İşçi Arayüzü")

gorevler = gorevleri_yukle()

if not gorevler:
    st.info("Atanmış bir görev bulunmamaktadır.")
else:
    gorev_id = st.selectbox("📍 Görev Seçin", list(gorevler.keys()))
    gorev = gorevler[gorev_id]

    st.write(f"Şehir: {gorev['sehir']}")
    st.write(f"İş Tanımı: {gorev.get('is_tanimi', '-')}")
    st.write(f"Montaj Süresi: {gorev.get('montaj_suresi', '-')} saat")

    # Harita Gösterimi
    if "konum" in gorev:
        lat, lon = gorev["konum"]
        st.subheader("🗺️ Görev Haritası")
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], popup=gorev["sehir"]).add_to(m)
        st_folium(m, width=700, height=400)

    st.subheader("📤 Görevi Tamamla")
    is_tanimi = st.text_area("İş Tanımı (Gerçekleşen)")
    fotograf = st.file_uploader("Fotoğraf Yükle", type=["png", "jpg", "jpeg"])

    if st.button("✅ Görev Tamamlandı"):
        if not is_tanimi or not fotograf:
            st.warning("Lütfen iş tanımı girin ve fotoğraf yükleyin.")
        else:
            img = Image.open(fotograf)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            gorev["is_tanimi"] = is_tanimi
            gorev["fotograf"] = buffer.getvalue().hex()  # JSON’a uygun hale getiriyoruz
            gorev["tamamlandi"] = True
            gorev["onay"] = False
            gorev["bildirim"] = True  # Yönetici için yeni bildirim

            gorevler[gorev_id] = gorev
            gorevleri_kaydet(gorevler)
            st.success("Görev tamamlandı. Yönetici onayı bekleniyor.")
