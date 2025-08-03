import os
import json
import io
import time
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import texttospeech
from google.cloud import speech
import pyaudio
import wave
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- Constants ---
MAX_HISTORY_MESSAGES = 10  # Messages to keep in immediate context
SUMMARY_INTERVAL = 6       # Messages between summaries
DATA_DIR = "data"
USER_DATA_DIR = os.path.join(DATA_DIR, "user_data")
VOICE_DATA_DIR = os.path.join(DATA_DIR, "user_voice_data")

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

    # Extract just role and parts for the API (ignoring "spoken" field)
    recent_history = []
    for msg in mode_data["full_history"][-MAX_HISTORY_MESSAGES:]:
        recent_history.append({"role": msg["role"], "parts": msg["parts"]})

    context.extend(recent_history)
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


def text_to_speech(text, output_file=None):
    # Check if output_file is None and set default with proper path
    if output_file is None:
        os.makedirs(VOICE_DATA_DIR, exist_ok=True)
        output_file = os.path.join(VOICE_DATA_DIR, "neva_speech.mp3")

    # Clean the text by removing any invalid characters
    text = text.encode('utf-8', errors='ignore').decode('utf-8')

    # Convert text to speech using Google Cloud TTS
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Configure voice - Turkish female voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="tr-TR",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        name="tr-TR-Standard-A"  # You can change to a specific voice if preferred
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)

    # Play audio based on platform
    import platform

    system = platform.system()
    if system == "Darwin":  # macOS
        os.system(f"afplay {output_file}")
    elif system == "Windows":
        os.system(f"start {output_file}")
    elif system == "Linux":
        os.system(f"mpg123 {output_file}")



def speech_to_text():
    """Record audio with improved silence detection"""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    SILENCE_THRESHOLD = 700  # Adjust based on environment
    INITIAL_TIMEOUT = 3  # Seconds to wait for speech to begin
    SILENCE_DURATION = 1.5  # Seconds of silence to end recording
    MAX_DURATION = 15  # Maximum recording time
    os.makedirs(VOICE_DATA_DIR, exist_ok=True)
    WAVE_OUTPUT_FILENAME = os.path.join(VOICE_DATA_DIR, "user_input.wav")

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Sizi dinliyorum... (konuşmanız bittiğinde otomatik olarak kaydedilecek)")

    frames = []
    is_speaking = False
    silence_start = None
    recording_start = time.time()

    # Track consecutive frames over threshold for better speech detection
    speech_frames_count = 0
    required_speech_frames = 3  # Require multiple frames to confirm speech

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        # Calculate audio amplitude for silence detection
        amplitude = max(abs(int.from_bytes(data[i:i + 2], byteorder='little', signed=True))
                        for i in range(0, len(data), 2))

        # Visual feedback
        elapsed = time.time() - recording_start
        print(f"\r🎙️ Dinliyorum {'●' * int(elapsed)} {amplitude:4d}", end="")

        # More robust speech detection
        if amplitude > SILENCE_THRESHOLD:
            speech_frames_count += 1
            if speech_frames_count >= required_speech_frames:
                is_speaking = True
                silence_start = None
        else:
            speech_frames_count = 0
            if is_speaking:
                # Start timing silence after speech detected
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_DURATION:
                    print("\nKonuşma sona erdi.")
                    break
            elif time.time() - recording_start > INITIAL_TIMEOUT and not is_speaking:
                print("\nKonuşma algılanmadı.")
                if len(frames) <= INITIAL_TIMEOUT * RATE / CHUNK:
                    return ""  # Return empty if no speech detected initially
                break

        # Safety timeout
        if elapsed > MAX_DURATION:
            print("\nMaksimum süre aşıldı.")
            break

    print("\nKaydı işliyorum...")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Same processing as before
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Speech recognition part remains unchanged
    client = speech.SpeechClient()
    with io.open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="tr-TR"
    )

    response = client.recognize(config=config, audio=audio)
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return transcript

def is_stop_command(text):
    """Check if the input contains the specific stop command"""
    return "neva durdur" in text.lower()

def process_chat_turn(user_id: str, mode: str, user_input: str, use_voice: bool = False):
    """Process a single chat turn and return the response"""
    # Load user data
    user_data = load_user_data(user_id)
    
    # Initialize model with selected mode
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro-latest',
        system_instruction=MODES[mode]["system_instruction"],
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )
    
    # Start chat with context
    chat = model.start_chat(history=build_context(user_data, mode))
    
    # Send message and get response
    response = chat.send_message(user_input)
    response_text = response.text
    
    # Check for Turkish language and retry if necessary
    if not any(char in "çğıöşüÇĞİÖŞÜ" for char in response_text):
        response = chat.send_message("Lütfen bu cevabı TÜRKÇE olarak ver!")
        response_text = response.text
    
    # Update conversation history
    mode_data = user_data["modes"][mode]
    mode_data["full_history"].extend([
        {"role": "user", "parts": [user_input], "spoken": use_voice},
        {"role": "model", "parts": [response_text], "spoken": use_voice}
    ])
    
    # Generate summary if needed
    if needs_summarization(user_data, mode):
        user_data = generate_summary(model, user_data, mode)
        # Update chat context after summary
        chat = model.start_chat(history=build_context(user_data, mode))
    
    # Save user data
    save_user_data(user_data)
    
    # Return response
    return response_text


# --- Main Application ---
def main():
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # Set up Google Cloud credentials properly
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CLOUD_KEY_PATH")

    user_id = input("İsminizi girin: ").strip() or "misafir"
    
    # Mod seçimi
    print("\nLütfen bir mod seçin:")
    for key, mode in MODES.items():
        print(f"{key[0]}) {mode['name']}")

    mode_choice = input("Seçiminiz (f/p): ").lower()
    selected_mode = "psych" if mode_choice == "p" else "friend"

    # Add voice interaction option
    use_voice = input("Sesli etkileşim kullanmak ister misiniz? (e/h): ").lower() == 'e'

    # Welcome message
    welcome_message = f"Merhaba {user_id}! Bugün nasılsınız?"
    print(f"\nNeva ({MODES[selected_mode]['name']}): {welcome_message}")

    # Speak welcome message if voice enabled
    if use_voice:
        text_to_speech(welcome_message)

    print("(Mod değiştirmek için '/mod', çıkmak için '/çıkış' yazın)")

    current_mode = selected_mode

    while True:
        try:
            # Get user input via voice or text
            if use_voice:
                print("\nSizi dinliyorum...")
                user_input = speech_to_text()
                print(f"\nSiz: {user_input}")

                # Check for stop command in voice input
                if is_stop_command(user_input):
                    print("\nDurdurma komutu algılandı. Program sonlandırılıyor...")
                    break
            else:
                user_input = input("\nSiz: ")

            # Özel komutları kontrol et
            if user_input.lower() == '/çıkış':
                break

            elif user_input.lower() == '/mod':
                # Mod değiştirme
                print("\nLütfen yeni mod seçin:")
                for key, mode in MODES.items():
                    print(f"{key[0]}) {mode['name']}")

                mode_choice = input("Seçiminiz (f/p): ").lower()
                new_mode = "psych" if mode_choice == "p" else "friend"

                if new_mode != current_mode:
                    current_mode = new_mode
                    mode_change_msg = f"Mod değiştirildi! Şimdi {MODES[current_mode]['name']} modundayım."
                    print(f"\nNeva: {mode_change_msg}")

                    if use_voice:
                        text_to_speech(mode_change_msg)
                continue

            # Process chat turn and get response
            response_text = process_chat_turn(user_id, current_mode, user_input, use_voice)
            
            # Output the response
            print(f"Neva: {response_text}")

            # Convert response to speech if voice enabled
            if use_voice:
                text_to_speech(response_text)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Hata: {str(e)}")

    # Çıkışta veda mesajı
    goodbye_message = f"Görüşmek üzere {user_id}! Sizinle sohbet etmek güzeldi."
    print(f"\nNeva: {goodbye_message}")

    # Speak goodbye message if voice enabled
    if use_voice:
        text_to_speech(goodbye_message)

if __name__ == "__main__":
    main()
