import streamlit as st
import os

# Ép cấu hình chạy hoàn toàn trên CPU trước khi nạp thư viện
os.environ["VIENEU_DEVICE"] = "cpu"

try:
    from vieneu import Vieneu
except ImportError:
    st.error("Chưa cài đặt thư viện 'vieneu'. Hãy kiểm tra lại file requirements.txt!")
    st.stop()

# Thiết lập giao diện hiển thị gọn gàng trên màn hình điện thoại
st.set_page_config(page_title="VieNeu TTS Mobile", page_icon="🎙️", layout="centered")

st.title("🎙️ VieNeu-TTS v3 Turbo")
st.caption("Ứng dụng chạy trên hạ tầng Streamlit Cloud CPU")

# Tải và giữ mô hình trong bộ nhớ
@st.cache_resource
def load_model():
    return Vieneu(mode="v3turbo")

with st.spinner("Đang khởi tạo mô hình..."):
    try:
        tts = load_model()
    except Exception as e:
        st.error(f"Lỗi nạp mô hình: {e}")
        st.stop()

# Ô nhập văn bản hỗ trợ tag cảm xúc
text_input = st.text_area(
    "Nhập văn bản tiếng Việt:",
    value="Chào bạn! Tôi là trí tuệ nhân tạo đang nói bằng mô hình Việt Nêu chấm T T S [cười].",
    height=120
)

st.subheader("👤 Tùy chọn Giọng đọc")
clone_mode = st.checkbox("Bật chế độ Nhân bản giọng nói (Voice Cloning)")

uploaded_file = None
if clone_mode:
    uploaded_file = st.file_uploader("Tải lên file âm thanh mẫu (3-8 giây):", type=["wav", "mp3", "m4a"])
    st.info("Hệ thống sẽ bắt chước chính xác giọng trong file âm thanh này!")

# Nút xử lý co giãn vừa vặn màn hình điện thoại
if st.button("🔊 Phát giọng nói", use_container_width=True):
    if not text_input.strip():
        st.warning("Vui lòng không để trống văn bản!")
    elif clone_mode and not uploaded_file:
        st.warning("Vui lòng tải lên file âm thanh mẫu để clone giọng!")
    else:
        with st.spinner("Hệ thống đang xử lý và tổng hợp âm thanh..."):
            try:
                output_file = "output_voice.wav"
                
                # Gọi đúng hàm tts.infer() theo tài liệu kỹ thuật
                if clone_mode and uploaded_file:
                    # Ghi file âm thanh tạm thời
                    temp_ref_path = "temp_ref.wav"
                    with open(temp_ref_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Tiến hành clone giọng từ file âm thanh bạn tải lên
                    audio_data = tts.infer(text=text_input, prompt_audio=temp_ref_path)
                else:
                    # Chạy giọng đọc mặc định của hệ thống
                    audio_data = tts.infer(text=text_input)
                
                # Lưu file kết quả đầu ra
                tts.save(audio_data, output_file)
                
                if os.path.exists(output_file):
                    with open(output_file, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/wav")
                    st.success("Tổng hợp thành công!")
                else:
                    st.error("Không tìm thấy dữ liệu âm thanh.")
            except Exception as e:
                st.error(f"Quá trình xử lý bị lỗi: {e}")
                    
