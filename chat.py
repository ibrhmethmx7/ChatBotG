from dotenv import load_dotenv
import streamlit as st
import os
import speech_recognition as sr
import google.generativeai as genai

# Ortam değişkenlerini yükle
load_dotenv()

# Streamlit sayfasını yapılandır
st.set_page_config(page_title="Bitirme Projesi")

# GenerativeAI'ı yapılandır
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Generative Modeli başlat
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Gemini'den cevap almak için fonksiyon
def gemini_cevap_al(soru):
    cevap = chat.send_message(soru, stream=True)
    return cevap

# Konuşmayı tanımlama fonksiyonu
def konusmayi_tani():
    r = sr.Recognizer()
    with sr.Microphone() as kaynak:
        st.write("Dinleniyor...")
        ses = r.listen(kaynak)
    try:
        st.write("İşleniyor...")
        kullanici_girdisi = r.recognize_google(ses, language="tr-TR")
        return kullanici_girdisi
    except sr.UnknownValueError:
        st.write("Üzgünüm, ne söylediğinizi anlayamadım.")
        return ""
    except sr.RequestError as e:
        st.write(f"Google Konuşma Tanıma servisinden sonuç alınamadı; {e}")
        return ""

# Ana Streamlit uygulaması
st.header("Bitirme Projesi Chatbot")
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

girdi_tipi = st.radio("Giriş Türü:", ("Metin", "Ses"))

if girdi_tipi == "Metin":
    metin_girdisi = st.text_input("Giriş: ", key="metin_girdisi")
    soru_sor = st.button("Sor")
    if soru_sor and metin_girdisi:
        cevap = gemini_cevap_al(metin_girdisi)
        st.session_state['chat_history'].append(("Siz", metin_girdisi))
        st.subheader("Cevap:")
        for parca in cevap:
            st.write(parca.text)
            st.session_state['chat_history'].append(("Bot", parca.text))
elif girdi_tipi == "Ses":
    st.write("Aşağıdaki düğmeye tıklayarak sorunuzu söyleyin.")
    if st.button("Kayıt"):
        metin_girdisi = konusmayi_tani()
        if metin_girdisi:
            cevap = gemini_cevap_al(metin_girdisi)
            st.session_state['chat_history'].append(("Siz", metin_girdisi))
            st.subheader("Cevap:")
            for parca in cevap:
                st.write(parca.text)
                st.session_state['chat_history'].append(("Bot", parca.text))

st.subheader("Sohbet Geçmişi")
for rol, metin in st.session_state['chat_history']:
    st.write(f"{rol}: {metin}")
