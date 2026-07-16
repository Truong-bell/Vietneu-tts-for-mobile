import streamlit as st
import asyncio
import edge_tts
import os
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

# Cấu hình trang web
st.set_page_config(
    page_title="Phòng Thu Giọng Nói & Xử Lý AI",
    page_icon="🎙️",
    layout="centered"
)

# Giao diện CSS phòng thu chuyên nghiệp
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c20 0%, #15102a 50%, #060212 100%); }
    .studio-title {
        text-align: center; font-weight: 800; letter-spacing: 2px;
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px;
    }
    div[data-testid="stForm"], .stTextArea, .stSelectbox, div[data-testid="stExpander"], .stFileUploader, div[data-testid="stTabs"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    h1, h2, h3, h4, p, span, label, th, td { color: #e0e0ff !important; }
    div.stButton > button {
        background: linear-gradient(45deg, #ff007f, #7f00ff) !important; color: white !important;
        border: none !important; font-weight: bold !important; font-size: 16px !important;
        padding: 12px 24px !important; border-radius: 12px !important; box-shadow: 0 4px 15px rgba(255, 0, 127, 0.4) !important;
    }
    div.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 25px rgba(127, 0, 255, 0.7) !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='studio-title'>🎙️ AI VOICE ULTIMATE STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0a0d0 !important; font-size:14px; margin-bottom:25px;'>Hệ thống chuyển đổi Chữ thành Giọng & rã băng Giọng nói thành Chữ có mốc thời gian</p>", unsafe_allow_html=True)

# Chia giao diện thành 2 Tab lớn chuyên nghiệp
tab1, tab2 = st.tabs(["✨ CHỮ THÀNH GIỌNG NÓI (TTS)", "🔊 GIỌNG NÓI THÀNH CHỮ (STT)"])

# ==================== TAB 1: TEXT TO SPEECH ====================
with tab1:
    if "history" not in st.session_state: st.session_state.history = []
    uploaded_file = st.file_uploader("📂 Tải lên file văn bản (.txt):", type=["txt"])
    default_text = "Xin chào, đây là hệ thống Studio tối ưu hóa cấu trúc mã nguồn."
    if uploaded_file is not None:
        try: default_text = uploaded_file.read().decode("utf-8")
        except: st.error("Không thể đọc file. Vui lòng kiểm tra định dạng!")
        
    text_input = st.text_area("✍️ Nhập văn bản cần đọc:", default_text, height=150, key="tts_input")
    translate_to_en = st.toggle("🔤 Tự động dịch sang Tiếng Anh trước khi đọc")
    
    char_count = len(text_input)
    max_chars = 20000
    st.progress(min(char_count / max_chars, 1.0))
    st.caption(f"Dung lượng: **{char_count:,}** / **{max_chars:,}** ký tự.")
    
    st.markdown("### 🎛️ BÀN TRỘN ÂM THANH")
    preset = st.radio("Mẫu nhanh:", ["Mặc định", "Em bé", "Người già", "Quái vật", "Thủ công"], horizontal=True)
    if preset == "Mặc định": s_val, p_val = 0, 0
    elif preset == "Em bé": s_val, p_val = 15, 40
    elif preset == "Người già": s_val, p_val = -15, -20
    elif preset == "Quái vật": s_val, p_val = -10, -50
    else: s_val, p_val = 0, 0
    
    col_speed, col_pitch = st.columns(2)
    with col_speed: speed = st.slider("⚡ Tốc độ (Speed):", -50, 50, s_val, 5, format="%d%%")
    with col_pitch: pitch = st.slider("🎵 Cao độ (Pitch):", -50, 50, p_val, 5, format="%d%%")
    
    speed_str = f"{'+' if speed >= 0 else ''}{speed}%"
    pitch_str = f"{'+' if pitch >= 0 else ''}{pitch}Hz"
    
    col_lang, col_voice = st.columns(2)
    with col_lang:
        lang_option = st.selectbox("🌐 Ngôn ngữ:", ["Tiếng Anh (English)"] if translate_to_en else ["Tiếng Việt (Vietnamese)", "Tiếng Anh (English)", "Tiếng Hàn (Korean)", "Tiếng Nhật (Japanese)", "Tiếng Trung (Chinese)"])
    
    voice_list = ["HoaiAn (Nữ)", "NamMinh (Nam)", "Google (Mặc định)"] if "Tiếng Việt" in lang_option or translate_to_en else ["Aria (Nữ)", "Guy (Nam)", "Google (Mặc định)"]
    with col_voice: voice_option = st.selectbox("👤 Giọng đọc:", voice_list)
    loop_audio = st.checkbox("🔄 Bật phát lặp lại (Loop)")
    
    if st.button("🔥 KHỞI TẠO GIỌNG NÓI AI", use_container_width=True):
        if text_input.strip() == "": st.warning("Vui lòng nhập văn bản!")
        else:
            output_file = "output.mp3"
            if os.path.exists(output_file): os.remove(output_file)
            
            if "Google" in voice_option:
                g_lang = 'en' if translate_to_en else 'vi'
                with st.spinner("🤖 Google đang render..."):
                    try: gTTS(text=text_input, lang=g_lang, slow=(speed<0)).save(output_file)
                    except Exception as e: st.error(f"Lỗi: {e}")
            else:
                target_voice = "vi-VN-HoaiAnNeural" if "HoaiAn" in voice_option else "vi-VN-NamMinhNeural"
                if "Tiếng Anh" in lang_option or translate_to_en: target_voice = "en-US-AriaNeural" if "Aria" in voice_option else "en-US-GuyNeural"
                
                async def generate_tts():
                    try: await edge_tts.Communicate(text_input, target_voice, rate=speed_str, pitch=pitch_str).save(output_file)
                    except: pass
                with st.spinner("⚡ Microsoft đang khởi tạo..."): asyncio.run(generate_tts())
                
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                st.success("🎉 Thành công!")
                st.audio(output_file, format="audio/mp3", loop=loop_audio)
                with open(output_file, "rb") as f:
                    st.download_button(label="📥 TẢI MP3", data=f, file_name="ai_voice.mp3", mime="audio/mp3", use_container_width=True)

# ==================== TAB 2: VOICE TO TEXT (STT) ====================
with tab2:
    st.markdown("### 🔊 RÃ BĂNG GIỌNG NÓI THEO MỐC THỜI GIAN")
    st.caption("Hỗ trợ tải lên file âm thanh (.mp3, .wav, .m4a) để chuyển đổi thành chữ có Timestamp chính xác từng giây.")
    
    # Cho phép người dùng chọn ngôn ngữ nói trong file để nhận diện chính xác
    stt_lang = st.selectbox("🎯 Chọn ngôn ngữ trong file âm thanh:", ["Tiếng Việt (vi-VN)", "Tiếng Anh (en-US)", "Tiếng Hàn (ko-KR)", "Tiếng Nhật (ja-JP)"])
    lang_code = "vi-VN"
    if "Tiếng Anh" in stt_lang: lang_code = "en-US"
    elif "Tiếng Hàn" in stt_lang: lang_code = "ko-KR"
    elif "Tiếng Nhật" in stt_lang: lang_code = "ja-JP"
    
    audio_file = st.file_uploader("🎙️ Tải file ghi âm lên tại đây:", type=["mp3", "wav", "m4a", "ogg"])
    
    if audio_file is not None:
        st.audio(audio_file)
        
        if st.button("🚀 BẮT ĐẦU CHUYỂN GIỌNG NÓI THÀNH VĂN BẢN", use_container_width=True):
            with st.spinner("🤖 Đang phân tích và xử lý dòng thời gian âm thanh..."):
                try:
                    # Lưu file tạm gọn nhẹ
                    temp_audio_path = "temp_input_audio"
                    with open(temp_audio_path, "wb") as f:
                        f.write(audio_file.getbuffer())
                    
                    # Dùng pydub chuyển đổi định dạng và cắt lát (Không tốn CPU giải nén nặng)
                    sound = AudioSegment.from_file(temp_audio_path)
                    sound = sound.set_channels(1).set_frame_rate(16000) # Chuẩn hóa tần số siêu nhẹ
                    
                    # Chia nhỏ file âm thanh thành từng đoạn 10 giây để tránh nghẽn băng thông và tràn RAM
                    chunk_length_ms = 10000 
                    chunks = [sound[i:i + chunk_length_ms] for i in range(0, len(sound), chunk_length_ms)]
                    
                    recognizer = sr.Recognizer()
                    final_result = ""
                    
                    # Khung hiển thị kết quả thời gian thực
                    st.markdown("#### 📝 Kết quả phân tích dòng thời gian:")
                    
                    for index, chunk in enumerate(chunks):
                        chunk_file = f"chunk_{index}.wav"
                        chunk.export(chunk_file, format="wav")
                        
                        # Tính mốc thời gian bắt đầu (phút:giây)
                        start_sec = (index * chunk_length_ms) // 1000
                        mins = start_sec // 60
                        secs = start_sec % 60
                        timestamp = f"[{mins:02d}:{secs:02d}]"
                        
                        with sr.AudioFile(chunk_file) as source:
                            audio_data = recognizer.record(source)
                            try:
                                # Gửi dữ liệu nhẹ lên Cloud Google dịch chữ, giải phóng 100% CPU server
                                text = recognizer.recognize_google(audio_data, language=lang_code)
                                if text.strip():
                                    st.markdown(f"<span style='color:#00ffcc;'>{timestamp}</span> {text}", unsafe_allow_html=True)
                                    final_result += f"{timestamp} {text}\n"
                            except sr.UnknownValueError:
                                # Đoạn âm thanh không có tiếng người hoặc im lặng
                                pass
                            except sr.RequestError:
                                st.error("Mất kết nối máy chủ nhận diện dữ liệu đám mây!")
                                break
                                
                        # Xóa file chunk tạm ngay lập tức để tiết kiệm bộ nhớ
                        if os.path.exists(chunk_file): os.remove(chunk_file)
                        
                    if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
                    
                    if final_result:
