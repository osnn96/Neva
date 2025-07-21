import os
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS ayarı (frontend ile backend farklı portlarda çalışıyorsa şart)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Güvenlik için prod'da spesifik domain(ler)i yazın.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    mesaj: str
    user_id: str = "web_user" # Web arayüzü için varsayılan kullanıcı
    mode: str = "psych"      # Web arayüzü konuları için varsayılan mod

class ContactRequest(BaseModel):
    ad: str
    email: str
    konu: str
    mesaj: str

# --- Constants ---
MAX_HISTORY_MESSAGES = 10  # Anlık bağlamda tutulacak mesaj sayısı
SUMMARY_INTERVAL = 6       # Özetlemeler arasındaki mesaj sayısı
USER_DATA_DIR = "user_data"

# old system instructions for different modes
""" Senin adın Neva. Sen sıcakkanlı, meraklı, pozitif ve esprili bir sohbet arkadaşısın. 
            Kullanıcıyla günlük konular hakkında sohbet et, ilginç bilgiler paylaş, sorular sor ve onun anılarını dinle. 
            Asla psikolojik tavsiye verme. Amacın keyifli ve samimi bir diyalog kurmak. Cevaplarını kısa ve doğal tut.
            Ana konuşma dilin Türkçe, kullanıcı açık ve spesifik olarak söylemedikçe başka dillerde cevap verme. Gerektikçe bazı inglizce temelli keliemler kullanabilirsin.
            Basit, doğal ve sıcak bir üslup kullan. Kullanıcının geçmişte paylaştığı kişisel detayları hatırla.
            Örnek: 'Geçen konuşmamızda torunun Ayşe'den bahsetmiştin, onun sınavı nasıl geçti?
"""

MODES = {
    "friend": {
        "name": "Arkadaş Modu",
        "system_instruction": """
            Senin adın Neva. Sen sıcakkanlı, meraklı, pozitif ve esprili bir sohbet arkadaşısın. 
            Kullanıcıyla günlük konular hakkında sohbet et, ilginç bilgiler paylaş, sorular sor ve onun anılarını dinle. 
            Asla psikolojik tavsiye verme. Amacın keyifli ve samimi bir diyalog kurmak. Cevaplarını kısa ve doğal tut.
            Ana konuşma dilin Türkçe,Kullanıcı spesifik olarak istemediği sürece türkçe dışında cevap verme.
            Basit, doğal ve sıcak bir üslup kullan.
        """
    },
    "psych": {
        "name": "Psikolojik Destek Modu",
        "system_instruction": """
            Sen bir psikolojik destek asistanısın. Amacın kullanıcıyı dinlemek, duygularını anlamak ve onları yargılamadan desteklemek.
            Asla teşhis koyma ya da ilaç önerme. Kullanıcıyı profesyonel bir terapiste yönlendir.
            Kullanıcı spesifik olarak istemediği sürece türkçe dışında cevap verme. Empatik ve destekleyici bir dil kullan.
            Örnek: 'Bu konuda kendinizi yalnız hissetmeniz çok doğal. Duygularınızı paylaştığınız için teşekkür ederim.'
        """
    }
}

# --- AI Model and Safety Configuration ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

models = {
    mode_name: genai.GenerativeModel(
        model_name='gemini-1.5-pro-latest',
        # system_instruction parametresi eski kütüphane sürümleriyle uyumluluk için kaldırıldı.
        # Her istekte `generate_content` fonksiyonuna manuel olarak eklenecek.
        safety_settings=safety_settings
    ) for mode_name, details in MODES.items()
}

# --- Memory Management Functions ---
def get_user_filepath(user_id: str) -> str:
    """Get user-specific JSON file path"""
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    return os.path.join(USER_DATA_DIR, f"neva_{user_id}.json")

def load_user_data(user_id: str) -> dict:
    filepath = get_user_filepath(user_id)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            user_data = json.load(f)
            # Eski veri yapısı kontrolü ve dönüşüm
            if "modes" not in user_data:
                # Eski veriyi yeni formata dönüştür
                user_data = {
                    "user_id": user_data.get("user_id", user_id),
                    "created": user_data.get("created", datetime.now().isoformat()),
                    "modes": {
                        "friend": {
                            "full_history": user_data.get("full_history", []),
                            "summaries": user_data.get("summaries", []),
                            "critical_facts": user_data.get("critical_facts", []),
                            "last_summary_index": user_data.get("last_summary_index", 0)
                        },
                        "psych": {
                            "full_history": [],
                            "summaries": [],
                            "critical_facts": [],
                            "last_summary_index": 0
                        }
                    }
                }
            return user_data
    except FileNotFoundError:
        # Yeni kullanıcı için varsayılan veri yapısı
        return {
            "user_id": user_id,
            "created": datetime.now().isoformat(),
            "modes": {
                "friend": {
                    "full_history": [],
                    "summaries": [],
                    "critical_facts": [],
                    "last_summary_index": 0
                },
                "psych": {
                    "full_history": [],
                    "summaries": [],
                    "critical_facts": [],
                    "last_summary_index": 0
                }
            }
        }

def save_user_data(user_data: dict):
    """Save with atomic write for safety"""
    filepath = get_user_filepath(user_data["user_id"])
    temp_path = f"{filepath}.tmp"
    
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)
    
    os.replace(temp_path, filepath)
    print(f"Saved data for {user_data['user_id']}")

# --- Context Management ---
def build_context(user_data: dict, mode: str) -> list:
    mode_data = user_data["modes"][mode]
    context = []
    
    if mode_data["critical_facts"]:
        context.append({
            "role": "user", 
            "parts": [f"Önemli bilgiler: {', '.join(mode_data['critical_facts'])}"]
        })
    
    if mode_data["summaries"]:
        context.append({
            "role": "user",
            "parts": [f"Sohbet özeti: {mode_data['summaries'][-1]}"]
        })
    
    context.extend(mode_data["full_history"][-MAX_HISTORY_MESSAGES:])
    return context

def needs_summarization(user_data: dict, mode: str) -> bool:
    mode_data = user_data["modes"][mode]
    new_messages = len(mode_data["full_history"]) - mode_data["last_summary_index"]
    return new_messages >= SUMMARY_INTERVAL

def generate_summary(model, user_data: dict, mode: str):
    mode_data = user_data["modes"][mode]
    history_text = "\n".join(
        f"{msg['role']}: {msg['parts'][0]}" 
        for msg in mode_data["full_history"][mode_data["last_summary_index"]:]
    )
    
    prompt = f"""
    Aşağıdaki sohbeti {'psikolojik destek' if mode == 'psych' else 'arkadaş sohbeti'} olarak, 
    aşağıdaki odaklarla TÜRKÇE özetle:
    1. Kullanıcının duygusal durumu ve tekrarlanan endişeleri
    2. Önemli kişisel detaylar
    3. Gelecek konuşmalarda referans verilebilecek olaylar/anılar

    Sohbet:
    {history_text}

    Çıktı formatı:
    Özet: [en fazla 3 cümlelik özet]
    Önemli Bilgiler: [virgülle ayrılmış anahtar kelimeler]
    """
    
    response = model.generate_content(prompt)
    result = response.text.strip()
    
    if "Önemli Bilgiler:" in result:
        summary_part, facts_part = result.split("Önemli Bilgiler:", 1)
    else:
        summary_part = result
        facts_part = ""
    
    summary_clean = summary_part.replace("Özet:", "").strip()
    mode_data["summaries"].append(summary_clean)
    
    if facts_part:
        new_facts = [f.strip() for f in facts_part.split(",") if f.strip()]
        mode_data["critical_facts"].extend(new_facts)
    
    mode_data["last_summary_index"] = len(mode_data["full_history"])
    return user_data

# --- API Endpoints ---
@app.post("/api/sohbet")
async def sohbet(request: ChatRequest):
    user_id = request.user_id
    mode = request.mode
    user_input = request.mesaj

    if mode not in MODES:
        return {"hata": "Geçersiz mod seçimi."}, 400

    try:
        user_data = load_user_data(user_id)
        model = models[mode]
        system_instruction = MODES[mode]["system_instruction"]
        history = build_context(user_data, mode)
        
        # Mesajı işle
        response = model.generate_content(
            history,
            generation_config={"temperature": 0.9}, # Yaratıcılık için
            safety_settings=safety_settings,
            stream=False # Stream'i kapatarak tam yanıtı bekle
        )
        response_text = response.text


        # Geçmişi güncelle
        mode_data = user_data["modes"][mode]
        mode_data["full_history"].extend([
            {"role": "user", "parts": [user_input]},
            {"role": "model", "parts": [response_text]}
        ])
        
        # Gerekirse özet oluştur ve bağlamı yenile
        if needs_summarization(user_data, mode):
            # Özetleme için genel amaçlı bir model kullanalım
            summary_model = models["friend"] 
            user_data = generate_summary(summary_model, user_data, mode)
        
        save_user_data(user_data)
        
        return {"cevap": response_text}

    except Exception as e:
        print(f"API Hatası: {str(e)}")
        return {"hata": "Mesajınız işlenirken bir hata oluştu. Lütfen tekrar deneyin."}, 500

@app.post("/api/iletisim")
async def iletisim(request: ContactRequest):
    # Gelen veriyi yazdır (gerçek uygulamada veritabanına kaydedilebilir veya e-posta gönderilebilir)
    print(f"Yeni İletişim Formu Mesajı:")
    print(f"  Ad: {request.ad}")
    print(f"  Email: {request.email}")
    print(f"  Konu: {request.konu}")
    print(f"  Mesaj: {request.mesaj}")
    return {"mesaj": "Mesajınız başarıyla alındı! Teşekkür ederiz."}