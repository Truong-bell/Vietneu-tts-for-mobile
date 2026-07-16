import streamlit as st
import asyncio
import edge_tts
import os
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

# Cấu hình trang web (Giao diện rộng)
st.set_page_config(
    page_title="Studio Chuyển Đổi Giọng Nói AI",
    page_icon="🎙️",
    layout="centered"
)

# Khởi tạo trạng thái chuyển trang nếu chưa có (Mặc định ở trang TTS)
if "current_page" not in st.session_state:
    st.session_state.current_page = "TTS"

# Kiểm tra xem người dùng có bấm chuyển trang qua thanh điều hướng không
query_params = st.query_params
if "nav" in query_params:
    st.session_state.current_page = query_params["nav"]

# GIAO DIỆN CSS TÙY BIẾN CAO CẤP & HAMBURGER MENU 3 GẠCH
st.markdown("""
    <style>
    /* Nền tối chủ đạo phòng thu */
    .stApp { 
        background: linear-gradient(135deg, #0f0c20 0%, #15102a 50%, #060212 100%); 
    }
    
    /* Làm đẹp tiêu đề chính */
    .studio-title {
        text-align: center; font-weight: 800; letter-spacing: 2px;
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px;
    }
    
    /* Thiết kế khung kính mờ Glassmorphism */
    div[data-testid="stForm"], .stTextArea, .stSelectbox, div[data-testid="stExpander"], .stFileUploader {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    h1, h2, h3, h4, p, span, label, th, td { color: #e0e0ff !important; }
    
    /* Nút bấm chính Premium Phát Sáng */
    div.stButton > button {
        background: linear-gradient(45deg, #ff007f, #7f00ff) !important; color: white !important;
        border: none !important; font-weight: bold !important; font-size: 16px !important;
        padding: 12px 24px !important; border-radius: 12px !important; box-shadow: 0 4px 15px rgba(255, 0, 127, 0.4) !important;
    }
    div.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 25px rgba(127, 0, 255, 0.7) !important; }
    
    /* --- PHẦN THIẾT KẾ MENU 3 GẠCH Ở GÓC TRÊN PHẢI --- */
    .menu-container {
        position: fixed;
        top: 15px;
        right: 15px;
        z-index: 99999;
    }
    
    /* Nút 3 gạch ẩn/hiện */
    .menu-toggle {
        display: block;
        width: 35px;
        height: 35px;
        cursor: pointer;
        position: relative;
    }
    .menu-toggle span {
        display: block;
        width: 100%;
        height: 4px;
        background: #ff4b2b;
        margin: 6px 0;
        border-radius: 2px;
        transition: 0.3s;
    }
    
    /* Nội dung Menu thả xuống */
    .menu-dropdown {
        display: none;
        position: absolute;
        top: 40px;
        right: 0;
        background: #15102a;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        width: 220px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        padding: 10px 0;
    }
    .menu-container:hover .menu-dropdown {
        display: block;
    }
    .menu-item {
        display: block;
        padding: 12px 20px;
        color: #e0e0ff !important;
        text-decoration: none !important;
        font-weight: bold;
        font-size: 14px;
        transition: 0.2s;
    }
    .menu-item:hover {
        background: linear-gradient(45deg, #ff007f, #7f00ff);
        color: white !important;
    }
    </style>
    
    <!-- Nhúng mã HTML tạo cấu trúc Menu 3 gạch ở góc trên phải -->
    <div class="menu-container">
        <div class="menu-toggle">
            <span></span>
            <span></span>
            <span></span>
        </div>
        <div class="menu-dropdown">
            <p style='margin: 5px 20px; font-size:11px; color:#888 !important; text-transform: uppercase;'>Chức năng hệ thống</p>
            <a class="menu-item" href="?nav=TTS" target="_self">✨ Chữ thành Giọng nói (TTS)</a>
            <a class="menu-item" href="?nav=STT" target="_self">🔊 Giọng nói thành Chữ (STT)</a>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<h1 class='studio-title'>🎙️ AI VOICE ULTIMATE STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0a0d0 !important; font-size:14px; margin-bottom:25px;'>Chạm vào dấu 3 gạch ở góc trên bên phải để chuyển đổi tính năng</p>", unsafe_allow_html=True)

# ==================== ĐIỀU HƯỚNG HIỂN THỊ TRANG TRỰC QUAN ====================
if st.session_state.current_page == "TTS":
    st.markdown("## ✨ CHUYỂN VĂN BẢN THÀNH GIỌNG NÓI")
    
    if "history" not in st.session_state: st.session_state.history = []
    uploaded_file = st.file_uploader("📂 Tải lên file văn bản (.txt) nếu không muốn gõ tay:", type=["txt"])
    default_text = "Xin chào, đây là hệ thống Studio tối ưu hóa cấu trúc mã nguồn."
    if uploaded_file is not None:
        try: default_text = uploaded_file.read().decode("utf-8")
        except: st.error("Không thể đọc file. Vui lòng kiểm tra định dạng!")
        
    text_input = st.text_area("✍️ Nhập văn bản cần xử lý:", default_text, height=150, key="tts_input")
    translate_to_en = st.toggle("🔤 Tự động dịch văn bản sang Tiếng Anh trước khi đọc")
    
    char_count = len(text_input)
    max_chars = 20000
    st.progress(min(char_count / max_chars, 1.0))
    st.caption(f"Dung lượng bộ nhớ: **{char_count:,}** / **{max_chars:,}** ký tự tối đa.")
    
    st.markdown("### 🎛️ BÀN TRỘN THIẾT KẾ GIỌNG ĐỌC")
    preset = st.radio("Chọn công thức giọng mẫu nhanh:", ["Mặc định", "Em bé", "Người già", "Quái vật", "Thủ công"], horizontal=True)
    if preset == "Mặc định": s_val, p_val = 0, 0
    elif preset == "Em bé": s_val, p_val = 15, 40
    elif preset == "Người già": s_val, p_val = -15, -20
    elif preset == "Quái vật": s_val, p_val = -10, -50
    else: s_val, p_val = 0, 0
    
    col_speed, col_pitch = st.columns(2)
    with col_speed: speed = st.slider("⚡ Tốc độ đọc (Speed):", -50, 50, s_val, 5, format="%d%%")
    with col_pitch: pitch = st.slider("🎵 Cao độ / Độ trầm bổng (Pitch):", -50, 50, p_val, 5, format="%d%%")
    
    speed_str = f"{'+' if speed >= 0 else ''}{speed}%"
    pitch_str = f"{'+' if pitch >= 0 else ''}{pitch}Hz"
    
    col_lang, col_voice = st.columns(2)
    with col_lang:
        lang_option = st.selectbox("🌐 Chọn Ngôn ngữ gốc:", ["Tiếng Anh (English)"] if translate_to_en else ["Tiếng Việt (Vietnamese)", "Tiếng Anh (English)", "Tiếng Hàn (Korean)", "Tiếng Nhật (Japanese)", "Tiếng Trung (Chinese)"])
    
    voice_list = ["HoaiAn (Gốc Nữ)", "NamMinh (Gốc Nam)", "Google (Mặc định)"] if "Tiếng Việt" in lang_option or translate_to_en else ["Aria (Gốc Nữ)", "Guy (Gốc Nam)", "Google (Mặc định)"]
    with col_voice: voice_option = st.selectbox("👤 Chọn Chất giọng gốc để trộn (Base Voice):", voice_list)
    loop_audio = st.checkbox("🔄 Bật hiệu ứng phát lặp lại liên tục (Loop Audio)")
    
    if st.button("🔥 TIẾN HÀNH KHỞI TẠO VÀ XUẤT THÀNH PHẨM AI", use_container_width=True):
        if text_input.strip() == "": st.warning("Vui lòng nhập nội dung văn bản trước!")
        else:
            output_file = "output.mp3"
            if os.path.exists(output_file): os.remove(output_file)
            
            if "Google" in voice_option:
                g_lang = 'en' if translate_to_en else 'vi'
                with st.spinner("🤖 Hệ thống Google đang render file..."):
                    try: gTTS(text=text_input, lang=g_lang, slow=(speed<0)).save(output_file)
                    except Exception as e: st.error(f"Lỗi kết nối Google: {e}")
            else:
                target_voice = "vi-VN-HoaiAnNeural" if "HoaiAn" in voice_option else "vi-VN-NamMinhNeural"
                if "Tiếng Anh" in lang_option or translate_to_en: target_voice = "en-US-AriaNeural" if "Aria" in voice_option else "en-US-GuyNeural"
                
                async def generate_tts():
                    try: await edge_tts.Communicate(text_input, target_voice, rate=speed_str, pitch=pitch_str).save(output_file)
                    except: pass
                with st.spinner("⚡ Siêu máy chủ Microsoft đang xử lý..."): asyncio.run(generate_tts())
                
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                st.success("🎉 Khởi tạo file âm thanh thành công!")
                st.session_state.history.append(text_input)
                if len(st.session_state.history) > 5: st.session_state.history.pop(0)
                st.audio(output_file, format="audio/mp3", loop=loop_audio)
                with open(output_file, "rb") as f:
                    st.download_button(label="📥 TẢI XUỐNG FILE MP3 THÀNH PHẨM", data=f, file_name="ai_studio_voice.mp3", mime="audio/mp3", use_container_width=True)

    if st.session_state.history:
        with st.expander("📜 Xem lịch sử các đoạn văn bản vừa tạo (Tối đa 5 dòng gần nhất)"):
            for i, hist_text in enumerate(reversed(st.session_state.history)):
                st.text(f"{i+1}. {hist_text[:100]}..." if len(hist_text) > 100 else f"{i+1}. {hist_text}")

elif st.session_state.current_page == "STT":
    st.markdown("## 🔊 CHUYỂN GIỌNG NÓI THÀNH VĂN BẢN")
    st.caption("Tải lên file ghi âm để rã băng thành chữ có chia mốc thời gian (Timestamp) chính xác từng giây.")
    
    stt_lang = st.selectbox("🎯 Chọn ngôn ngữ nói trong file âm thanh:", ["Tiếng Việt (vi-VN)", "Tiếng Anh (en-US)", "Tiếng Hàn (ko-KR)", "Tiếng Nhật (ja-JP)"])
    lang_code = "vi-VN"
    if "Tiếng Anh" in stt_lang: lang_code = "en-US"
    elif "Tiếng Hàn" in stt_lang: lang_code = "ko-KR"
    elif "Tiếng Nhật" in stt_lang: lang_code = "ja-JP"
    
    audio_file = st.file_uploader("🎙️ Tải file ghi âm lên tại đây (.mp3, .wav, .m4a):", type=["mp3", "wav", "m4a", "ogg"])
    
    if audio_file is not None:
        st.audio(audio_file)

