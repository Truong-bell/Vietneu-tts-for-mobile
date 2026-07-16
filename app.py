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

# Tải và giữ mô hình trong bộ nhớ để không phải tải lại mỗi lần bấm nút
@st.cache_resource
def load_model():
    # Sử dụng cấu hình v3turbo (Hỗ trợ 48 kHz, siêu nhẹ, không cần PyTorch)
    return Vieneu(mode="v3turbo")

with st.spinner("Đang khởi tạo mô hình VieNeu-TTS (Vui lòng đợi trong giây lát)..."):
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

# Danh sách giọng mặc định có sẵn của kiến trúc v3 Turbo
speaker = st.selectbox(
    "Chọn giọng đọc (Speaker Token):",
    ["female_01", "male_01"]
)

# Nút xử lý co giãn vừa vặn màn hình điện thoại
if st.button("🔊 Phát giọng nói", use_container_width=True):
    if not text_input.strip():
        st.warning("Vui lòng không để trống văn bản!")
    else:
        with st.spinner("Hệ thống đang xử lý và tổng hợp âm thanh..."):
            try:
                output_file = "output_voice.wav"
                
                # Gọi hàm synthesize từ SDK gốc của tác giả
                tts.synthesize(text_input, output_path=output_file, speaker=speaker)
                
                if os.path.exists(output_file):
                    # Đọc file âm thanh vừa xuất ra và phát trực tiếp trên trình duyệt
                    with open(output_file, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/wav")
                    st.success("Tổng hợp giọng nói thành công!")
                else:
                    st.error("Không tìm thấy file âm thanh đầu ra.")
            except Exception as e:
                st.error(f"Quá trình xử lý bị lỗi: {e}")

