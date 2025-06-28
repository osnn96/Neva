import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json

# Geçmişi kaydetme ve yükleme fonksiyonları aynı kalıyor
def save_history_to_json(history, filename="sohbet_gecmisi.json"):
    print("Geçmiş kaydediliyor...")
    serializable_history = []
    for item in history:
        serializable_history.append({
            "role": item.role,
            "parts": [part.text for part in item.parts]
        })
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(serializable_history, f, ensure_ascii=False, indent=2)
    print("Geçmiş kaydedildi.")

def load_history_from_json(filename="sohbet_gecmisi.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            print("Eski konuşmalar yükleniyor...")
            return json.load(f)
    except FileNotFoundError:
        print("Geçmiş dosyası bulunamadı, yeni bir sohbet başlıyor.")
        return []

def main():
    # --- Mod Seçim Menüsü ---
    print("Neva'ya hoş geldin! Bugün hangi modda sohbet etmek istersin?")
    print("1: Sohbet Arkadaşı (Günlük, keyifli bir sohbet için)")
    print("2: Destek Asistanı (Bir konuyu konuşmak veya içini dökmek için)")
    
    selected_prompt = ""
    # --- DEĞİŞİKLİK 1: Hangi dosyayı kullanacağımızı tutacak bir değişken ekledik ---
    history_filename = "" 

    while True:
        mode_choice = input("Lütfen seçiminizi yapın (1 veya 2): ")
        if mode_choice == '1':
            # --- DEĞİŞİKLİK 2: Mod 1 seçilirse, kullanılacak dosya adını belirliyoruz ---
            history_filename = "sohbet_arkadasi_gecmisi.json"
            selected_prompt = """
            Senin adın Neva. Sen sıcakkanlı, meraklı, pozitif ve esprili bir sohbet arkadaşısın. 
            Kullanıcıyla günlük konular hakkında sohbet et, ilginç bilgiler paylaş, sorular sor ve onun anılarını dinle. 
            Asla psikolojik tavsiye verme. Amacın keyifli ve samimi bir diyalog kurmak. Cevaplarını kısa ve doğal tut.
            """
            break
        elif mode_choice == '2':
            # --- DEĞİŞİKLİK 2: Mod 2 seçilirse, kullanılacak dosya adını belirliyoruz ---
            history_filename = "destek_asistani_gecmisi.json"
            selected_prompt = """
            Senin adın Neva. Sen son derece empatik, sabırlı ve yargılamayan bir dinleyicisin. 
            Kullanıcının duygularını ve düşüncelerini anlamaya odaklan. Ona tavsiye vermek yerine, 'Bu durum sana ne hissettirdi?' 
            veya 'Bunun altında yatan başka bir sebep olabilir mi?' gibi yansıtıcı sorular sorarak kendi cevaplarını bulmasına yardımcı ol. 
            Unutma, sen bir terapist değilsin. Kullanıcı kendine zarar verme veya ciddi bir krizden bahsederse, diyaloğu hemen durdur 
            ve şu mesajı göster: 'Anlattıkların çok önemli ve bu konuda profesyonel bir destek alman en doğrusu. 
            Lütfen 112 Acil Çağrı Merkezi'ni veya güvendiğin bir sağlık kuruluşunu ara.'
            """
            break
        else:
            print("Geçersiz seçim. Lütfen sadece 1 veya 2 girin.")
    
    # --- API ve Model Kurulumu ---
    print("\nNeva başlatılıyor... API Anahtarı kontrol ediliyor.")
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("HATA: GEMINI_API_KEY bulunamadı. Lütfen .env dosyanızı kontrol edin.")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro-latest',
        system_instruction=selected_prompt,
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

    # --- DEĞİŞİKLİK 3: Geçmişi, seçilen moda ait dosyadan yüklüyoruz ---
    loaded_history = load_history_from_json(history_filename)
    chat = model.start_chat(history=loaded_history)

    print("\n------------------------------------")
    print("Harika! Sohbetimiz başlıyor. (Çıkmak için 'çıkış' yazabilirsin)")

    # --- Sohbet Döngüsü ---
    while True:
        user_input = input("Siz: ")
        if user_input.lower() == 'çıkış':
            # --- DEĞİŞİKLİK 4: Geçmişi, seçilen moda ait dosyaya kaydediyoruz ---
            save_history_to_json(chat.history, history_filename)
            print("Neva: Görüşmek üzere! Kendine iyi bak.")
            break
        response = chat.send_message(user_input)
        print(f"Neva: {response.text}")

if __name__ == "__main__":
    main()