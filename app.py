import streamlit as st
import asyncio
import edge_tts
import os
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

# Cấu hình trang web (Chế độ giao diện rộng)
st.set_page_config(
    page_title="Studio Chuyển Đổi Giọng Nói AI",
    page_icon="🎙️",
    layout="centered"
)

# Giao diện CSS tùy biến cao cấp (Dark Mode Premium Studio)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c20 0%, #15102a 50%, #060212 100%);
    }
    .studio-title {
        text-align: center; 
        font-weight: 800; 
        letter-spacing: 2px;
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    div[data-testid="stForm"], .stTextArea, .stSelectbox, div[data-testid="stExpander"], .stFileUploader {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    h1, h2, h3, h4, p, span, label, th, td {
        color: #e0e0ff !important;
    }
    div.stButton > button {
        background: linear-gradient(45deg, #ff007f, #7f00ff) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 16px !important;
        letter-spacing: 1px !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 15px rgba(255, 0, 127, 0.4) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(127, 0, 255, 0.7) !important;
    }
    /* Làm đẹp thanh Sidebar trượt */
    section[data-testid="stSidebar"] {
        background-color: #110c24 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- THANH MENU TRƯỢT SIDEBAR (TỰ ĐỘNG TẠO DẤU 3 GẠCH GÓC TRÊN TRÁI ĐIỆN THOẠI) ---
with st.sidebar:
    st.markdown("<h3 style='color:#ff4b2b !important; text-align:center;'>🎛️ MENU STUDIO</h3>", unsafe_allow_html=True)
    st.caption("Chạm vào đây để đổi tính năng:")
    
    # Tạo menu chọn trang bằng nút Radio cao cấp trong thanh trượt
    current_page = st.radio(
        "Lựa chọn chức năng:",
        ["✨ Chữ thành Giọng nói (TTS)", "🔊 Giọng nói thành Chữ (STT)"]
    )
    st.divider()
    st.markdown("<p style='font-size:11px; text-align:center; color:#666 !important;'>AI Voice Studio v2.0</p>", unsafe_allow_html=True)

# Tiêu đề chính trên trang
st.markdown("<h1 class='studio-title'>🎙️ AI VOICE PRO STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0a0d0 !important; font-size:14px; margin-bottom:25px;'>Hệ thống render âm thanh trí tuệ nhân tạo đa năng</p>", unsafe_allow_html=True)

# ==================== TRANG 1: CHỮ THÀNH GIỌNG NÓI (TTS) ====================
if "✨ Chữ thành Giọng nói" in current_page:
    if "history" not in st.session_state: 
        st.session_state.history = []
        
    uploaded_file = st.file_uploader("📂 Tải lên file văn bản (.txt) nếu không muốn gõ tay:", type=["txt"])
    default_text = "Xin chào, chào mừng bạn đến với Studio chuyển đổi giọng nói trí tuệ nhân tạo chuyên nghiệp."
    
    if uploaded_file is not None:
        try: 
            default_text = uploaded_file.read().decode("utf-8")
        except: 
            st.error("Không thể đọc file. Vui lòng kiểm tra định dạng!")
        
    text_input = st.text_area("✍️ Nhập văn bản cần xử lý:", default_text, height=180, key="tts_input")
    
    # Bộ đếm ký tự
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
        lang_option = st.selectbox("🌐 Chọn Ngôn ngữ gốc:", ["Tiếng Việt (Vietnamese)", "Tiếng Anh (English)", "Tiếng Hàn (Korean)", "Tiếng Nhật (Japanese)", "Tiếng Trung (Chinese)"])
    
    voice_list = []
    if "Tiếng Việt" in lang_option: voice_list = ["HoaiAn (Nữ)", "NamMinh (Nam)", "Google (Mặc định)"]
    elif "Tiếng Anh" in lang_option: voice_list = ["Aria (Nữ Mỹ)", "Guy (Nam Mỹ)", "Ava (Nữ Mỹ)", "Andrew (Nam Mỹ)", "Sonia (Nữ Anh)", "Google (Mặc định)"]
    elif "Tiếng Hàn" in lang_option: voice_list = ["SunHi (Nữ)", "InGook (Nam)", "Hyunsu (Nam trầm)", "Google (Mặc định)"]
    elif "Tiếng Nhật" in lang_option: voice_list = ["Nanami (Nữ)", "Keita (Nam)", "Aoi (Nữ)", "Google (Mặc định)"]
    elif "Tiếng Trung" in lang_option: voice_list = ["Xiaoxiao (Nữ)", "Yunxi (Nam)", "Yunjian (Nam trầm)", "Google (Mặc định)"]

    with col_voice: voice_option = st.selectbox("👤 Chọn Giọng đọc (Voice Artist):", voice_list)
    loop_audio = st.checkbox("🔄 Bật hiệu ứng phát lặp lại liên tục (Loop Audio)")
    
    if st.button("🔥 TIẾN HÀNH KHỞI TẠO GIỌNG NÓI AI", use_container_width=True):
        if text_input.strip() == "": 
            st.warning("Vui lòng nhập nội dung văn bản trước!")
        else:
            output_file = "output.mp3"
            if os.path.exists(output_file): os.remove(output_file)
            
            if "Google" in voice_option:
                g_lang = 'vi'
                if "Tiếng Anh" in lang_option: g_lang = 'en'
                elif "Tiếng Hàn" in lang_option: g_lang = 'ko'
                elif "Tiếng Nhật" in lang_option: g_lang = 'ja'
                elif "Tiếng Trung" in lang_option: g_lang = 'zh'
                
                with st.spinner("🤖 Hệ thống Google đang render file..."):
                    try: gTTS(text=text_input, lang=g_lang, slow=(speed<0)).save(output_file)
                    except Exception as e: st.error(f"Lỗi kết nối Google: {e}")
            else:
                target_voice = "vi-VN-HoaiAnNeural"
                if "Tiếng Việt" in lang_option:
                    target_voice = "vi-VN-HoaiAnNeural" if "HoaiAn" in voice_option else "vi-VN-NamMinhNeural"
                elif "Tiếng Anh" in lang_option:
                    if "Aria" in voice_option: target_voice = "en-US-AriaNeural"
                    elif "Guy" in voice_option: target_voice = "en-US-GuyNeural"
                    elif "Ava" in voice_option: target_voice = "en-US-AvaNeural"
                    elif "Andrew" in voice_option: target_voice = "en-US-AndrewNeural"
                    elif "Sonia" in voice_option: target_voice = "en-GB-SoniaNeural"
                elif "Tiếng Hàn" in lang_option:
                    if "SunHi" in voice_option: target_voice = "ko-KR-SunHiNeural"
                    elif "InGook" in voice_option: target_voice = "ko-KR-InGookNeural"
                    elif "Hyunsu" in voice_option: target_voice = "ko-KR-HyunsuNeural"
                elif "Tiếng Nhật" in lang_option:
                    if "Nanami" in voice_option: target_voice = "ja-JP-NanamiNeural"
                    elif "Keita" in voice_option: target_voice = "ja-JP-KeitaNeural"
                    elif "Aoi" in voice_option: target_voice = "ja-JP-AoiNeural"
                elif "Tiếng Trung" in lang_option:
                    if "Xiaoxiao" in voice_option: target_voice = "zh-CN-XiaoxiaoNeural"
                    elif "Yunxi" in voice_option: target_voice = "zh-CN-YunxiNeural"
                    elif "Yunjian" in voice_option: target_voice = "zh-CN-YunjianNeural"
                
                async def generate_tts():
                    try: await edge_tts.Communicate(text_input, target_voice, rate=speed_str, pitch=pitch_str).save(output_file)
                    except: pass
                with st.spinner("⚡ Siêu máy chủ Microsoft đang xử lý..."): 
                    asyncio.run(generate_tts())
                
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                st.success("🎉 Khởi tạo file âm thanh thành công!")
                st.session_state.history.append(text_input)
                if len(st.session_state.history) > 5: st.session_state.history.pop(0)
                st.audio(output_file, format="audio/mp3", loop=loop_audio)
                with open(output_file, "rb") as f:
                    st.download_button(label="📥 TẢI XUỐNG FILE MP3 THÀNH PHẨM", data=f, file_name="ai_studio_voice.mp3", mime="audio/mp3", use_container_width=True)
            else:
                st.error("Không thể tạo giọng đọc cho cấu hình này. Bạn hãy thử đổi sang giọng đọc khác nhé!")

    if st.session_state.history:
        with st.expander("📜 Xem lịch sử các đoạn văn bản vừa tạo"):
            for i, hist_text in enumerate(reversed(st.session_state.history)):
                st.text(f"{i+1}. {hist_text[:100]}..." if len(hist_text) > 100 else f"{i+1}. {hist_text}")

# ==================== TRANG 2: GIỌNG NÓI THÀNH CHỮ (STT) ====================
elif "🔊 Giọng nói thành Chữ" in current_page:
    st.markdown("## 🔊 CHUYỂN GIỌNG NÓI THÀNH VĂN BẢN")
        
