from fastapi import FastAPI, Header, HTTPException, status, Depends, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
import requests
import io
import tempfile
import warnings

# FFmpeg uyarılarını susturs
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub.utils")

import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
import shutil
from typing import Optional

# 🆕 FFmpeg otomatik kurulum
try:
    import imageio_ffmpeg as ffmpeg
    # pydub'u imageio-ffmpeg ile yapılandır
    AudioSegment.converter = ffmpeg.get_ffmpeg_exe()
    AudioSegment.ffmpeg = ffmpeg.get_ffmpeg_exe()
    AudioSegment.ffprobe = ffmpeg.get_ffmpeg_exe()
    print("✅ imageio-ffmpeg ile FFmpeg yapılandırıldı")
    IMAGEIO_FFMPEG_AVAILABLE = True
except ImportError:
    print("⚠️ imageio-ffmpeg bulunamadı, manuel FFmpeg aranıyor...")
    IMAGEIO_FFMPEG_AVAILABLE = False

# FFmpeg kontrolü fonksiyonu (güncellenmiş)
def check_ffmpeg_availability():
    """FFmpeg'in sistemde kurulu olup olmadığını kontrol eder"""
    
    # Önce imageio-ffmpeg'i dene
    if IMAGEIO_FFMPEG_AVAILABLE:
        try:
            ffmpeg_path = ffmpeg.get_ffmpeg_exe()
            print(f"✅ FFmpeg bulundu (imageio-ffmpeg): {ffmpeg_path}")
            return True
        except Exception as e:
            print(f"⚠️ imageio-ffmpeg hatası: {e}")
    
    # Fallback: Manuel FFmpeg
    ffmpeg_path = which("ffmpeg")
    ffprobe_path = which("ffprobe")
    
    if ffmpeg_path and ffprobe_path:
        print(f"✅ FFmpeg bulundu (manuel): {ffmpeg_path}")
        print(f"✅ FFprobe bulundu (manuel): {ffprobe_path}")
        return True
    else:
        print("❌ FFmpeg bulunamadı - ses format dönüşümü mümkün değil")
        print("💡 Çözüm: pip install imageio-ffmpeg")
        return False

# Global FFmpeg kontrol değişkeni
FFMPEG_AVAILABLE = check_ffmpeg_availability()


# app.py dosyamızdaki tüm mantığı "neva_logic" adıyla import ediyoruz
import app as neva_logic

# --- Başlangıç Ayarları ---
from dotenv import load_dotenv
load_dotenv()
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY bulunamadı.")
    neva_logic.genai.configure(api_key=api_key)
    print("Gemini API anahtarı başarıyla yapılandırıldı.")
except Exception as e:
    print(f"HATA: Gemini API anahtarı yapılandırılamadı. .env dosyanızı kontrol edin. Hata: {e}")

# --- API Uygulamasını Başlatma ---
app = FastAPI()

# Security scheme tanımlama
security = HTTPBearer()

# CORS ayarları
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Veri Modelleri ---
# DEĞİŞİKLİK: user_id'yi request body'den kaldırdık, çünkü artık token'dan gelecek.
class ChatRequest(BaseModel):
    mode: str
    message: str

class ChatResponse(BaseModel):
    reply_text: str

class TranscriptionResponse(BaseModel):
    transcript: str
    success: bool


# --- Token Doğrulama Servisi ---
async def verify_token_with_php_api(token: str) -> Optional[dict]:
    """
    PHP API'sine token'ı gönderip kullanıcı bilgilerini alır
    /api/user/profile endpoint'ini kullanır
    """
    try:
        headers = {
            "Auth": f"Bearer {token}",  # Authorization değil, Auth!
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://aiproje.guryeli.com/api/user/profile",  # HTTPS!
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                profile = data.get("profile")
                # Profile formatını user formatına çevir
                return {
                    "id": profile.get("id") if profile.get("id") else "default_id",  # ID eksikse varsayılan
                    "email": profile.get("email"), 
                    "first_name": profile.get("first_name"),
                    "last_name": profile.get("last_name")
                }
        
        return None
        
    except Exception as e:
        print(f"Token doğrulama hatası: {e}")
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Token'ı doğrulayıp kullanıcı bilgilerini döndürür
    """
    token = credentials.credentials
    
    # PHP API ile token'ı doğrula
    user_data = await verify_token_with_php_api(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya süresi dolmuş token"
        )
    
    return user_data


# --- API Endpoint'leri ---
@app.get("/")
def read_root():
    return {"Mesaj": "Neva API'si çalışıyor"}

@app.post("/chat/text", response_model=ChatResponse)
async def handle_text_chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    Frontend'den YAZILI sohbet isteğini alan ve Authorization başlığını kontrol eden endpoint.
    """
    # Artık gerçek kullanıcı bilgilerine sahibiz
    user_id = str(current_user["id"])
    print(f"DEBUG: Doğrulanmış kullanıcı ID: {user_id}")
    print(f"DEBUG: Kullanıcı: {current_user['first_name']} {current_user['last_name']}")

    response_text = neva_logic.process_chat_turn(
        user_id=user_id,
        mode=request.mode,
        user_input=request.message,
        use_voice=False
    )
    
    return ChatResponse(reply_text=response_text)


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Frontend'den gelen ses dosyasını metne çeviren endpoint.
    SpeechRecognition kütüphanesi kullanır.
    """
    user_id = str(current_user["id"])
    print(f"🎤 Transkripsiyon talebi: Kullanıcı {user_id}, Dosya: {audio.filename}")
    
    try:
        # Dosya formatını kontrol et
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            print(f"⚠️ Geçersiz dosya formatı: {audio.content_type}")
            raise HTTPException(
                status_code=400, 
                detail="Geçersiz dosya formatı. Ses dosyası gerekli."
            )
        
        # Dosya boyutunu kontrol et (max 10MB)
        file_content = await audio.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="Dosya çok büyük. Maximum 10MB."
            )
        
        if len(file_content) < 1000:  # Minimum 1KB
            print(f"⚠️ Dosya çok küçük: {len(file_content)} bytes")
            raise HTTPException(
                status_code=400,
                detail="Dosya çok küçük. Geçerli ses kaydı değil."
            )
        
        print(f"📁 Dosya boyutu: {len(file_content)} bytes ({len(file_content)/1024:.1f} KB)")
        print(f"🎵 Dosya formatı (MIME): {audio.content_type}")
        
        # Dosyanın gerçek formatını binary header'dan kontrol et
        file_header = file_content[:12] if len(file_content) >= 12 else file_content
        header_hex = file_header.hex()
        print(f"🔍 Dosya header (hex): {header_hex}")
        
        # Dosya formatını gerçek header'dan belirle
        is_real_wav = file_content.startswith(b'RIFF') and b'WAVE' in file_content[:12]
        is_webm = file_content.startswith(b'\x1a\x45\xdf\xa3')  # WebM magic number
        is_ogg = file_content.startswith(b'OggS')
        
        print(f"🔍 Format analizi: WAV={is_real_wav}, WebM={is_webm}, OGG={is_ogg}")
        
        # SpeechRecognition objesi oluştur ve optimize et
        recognizer = sr.Recognizer()
        
        # Gelişmiş recognition ayarları
        recognizer.energy_threshold = 300       # Daha hassas algılama
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8        # Daha az pause
        recognizer.phrase_threshold = 0.3       # Daha az phrase break  
        recognizer.non_speaking_duration = 0.5  # Konuşma arası süre
        
        # Dosya formatına göre işlem yap
        if is_real_wav:
            # Gerçek WAV dosyası - direkt kullan
            print("✅ Gerçek WAV formatı algılandı, direkt işleniyor...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                temp_wav.write(file_content)
                temp_wav_path = temp_wav.name
            print(f"💾 WAV temp dosya: {temp_wav_path}")
            
        else:
            # Pseudo-WAV veya diğer formatlar için conversion gerekli
            print("🔄 Dosya gerçek WAV değil, format çevirmeye çalışıyorum...")
            
            # FFmpeg kontrolü ÖNCE!
            if not FFMPEG_AVAILABLE:
                print("❌ FFmpeg yok - format dönüşümü yapılamaz")
                return TranscriptionResponse(
                    success=False,
                    transcript="Ses formatı desteklenmiyor. FFmpeg kurulu değil. Lütfen WAV formatında kayıt yapın."
                )
            
            # Temporary files
            if is_webm:
                suffix = ".webm"
                format_name = "webm"
            elif is_ogg:
                suffix = ".ogg" 
                format_name = "ogg"
            else:
                suffix = ".webm"  # Default olarak webm dene
                format_name = "webm"
                
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_original:
                # Original dosyayı geçici olarak kaydet
                temp_original.write(file_content)
                temp_original_path = temp_original.name
                
            print(f"💾 Original temp dosya ({format_name}): {temp_original_path}")
            
            # WAV formatına çevir
            try:
                print(f"🔄 {format_name.upper()} formatını WAV'ye çeviriyorum...")
                
                # pydub ile format çevirme - YÜKSEK KALİTE
                audio_segment = AudioSegment.from_file(temp_original_path, format=format_name)
                
                # WAV formatında kaydet - Yüksek kalite parametreleri
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                    temp_wav_path = temp_wav.name
                    
                # Yüksek kalite WAV export
                audio_segment.export(
                    temp_wav_path, 
                    format="wav",
                    parameters=[
                        "-acodec", "pcm_s16le",  # 16-bit PCM
                        "-ar", "44100",          # 44.1kHz sample rate  
                        "-ac", "1"               # Mono channel
                    ]
                )
                print(f"✅ WAV dosyası oluşturuldu: {temp_wav_path}")
                
                # Original temp dosyayı sil
                os.unlink(temp_original_path)
                
            except Exception as conversion_error:
                print(f"🚨 Format çevirme hatası: {conversion_error}")
                # Cleanup
                try:
                    os.unlink(temp_original_path)
                except:
                    pass
                
                # FFmpeg durumuna göre farklı mesaj
                if not FFMPEG_AVAILABLE:
                    error_msg = "FFmpeg kurulu değil. WAV formatında kayıt yapmayı deneyin."
                else:
                    error_msg = f"Ses formatı çevrilemedi: {str(conversion_error)}"
                
                return TranscriptionResponse(
                    success=False,
                    transcript=error_msg
                )
        
        try:
            # Audio dosyasını yükle
            with sr.AudioFile(temp_wav_path) as source:
                print("🎵 YÜKSEK KALİTE WAV Audio dosyası yükleniyor...")
                # Gelişmiş gürültü azaltma
                recognizer.adjust_for_ambient_noise(source, duration=1.0)  # 0.5 → 1.0 saniye
                audio_data = recognizer.record(source)
                print("✅ Audio data kaydedildi")
                
            # Google Speech Recognition ile transkript et
            print("🔄 YÜKSEK KALİTE Google Speech Recognition başlıyor...")
            try:
                # İlk deneme: Normal hassasiyet
                text = recognizer.recognize_google(audio_data, language='tr-TR')
                print(f"✅ Transcription başarılı (İlk deneme): {text}")
                
            except sr.UnknownValueError:
                print("⚠️ İlk deneme başarısız, düşük hassasiyet ile tekrar deneniyor...")
                # İkinci deneme: Düşük hassasiyet
                try:
                    recognizer.energy_threshold = 100  # Daha düşük threshold
                    with sr.AudioFile(temp_wav_path) as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio_data = recognizer.record(source)
                    
                    text = recognizer.recognize_google(audio_data, language='tr-TR')
                    print(f"✅ Transcription başarılı (İkinci deneme): {text}")
                    
                except sr.UnknownValueError:
                    print("❌ Her iki deneme de başarısız")
                    raise
            
            # Temp dosyayı sil
            os.unlink(temp_wav_path)
            
            return TranscriptionResponse(
                success=True,
                transcript=text
            )
            
        except sr.UnknownValueError:
            print("❌ Google Speech Recognition ses anlayamadı")
            # Temp dosyayı sil
            try:
                os.unlink(temp_wav_path)
            except:
                pass
            
            return TranscriptionResponse(
                success=False,
                transcript="Ses anlaşılamadı. Lütfen daha net konuşun."
            )
            
        except sr.RequestError as e:
            print(f"❌ Google Speech Recognition servis hatası: {e}")
            # Temp dosyayı sil
            try:
                os.unlink(temp_wav_path)
            except:
                pass
                
            return TranscriptionResponse(
                success=False,
                transcript=f"Speech Recognition servisi kullanılamıyor: {str(e)}"
            )
            
    except HTTPException:
        # FastAPI HTTPException'ları tekrar fırlat
        raise
        
    except Exception as e:
        print(f"🚨 Transcription genel hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Temp dosya varsa sil
        try:
            if 'temp_wav_path' in locals():
                os.unlink(temp_wav_path)
        except:
            pass
            
        raise HTTPException(
            status_code=500,
            detail=f"Transcription hatası: {str(e)}"
        )