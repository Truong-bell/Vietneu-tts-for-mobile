import streamlit as st
from gradio_client import Client, handle_file
import os

# Cấu hình giao diện mobile thân thiện
st.set_page_config(page_title="VieNeu TTS Advanced Mobile", page_icon="🎙️", layout="centered")

st.title("🎙️ VieNeu-TTS v3 Pro Max")
st.caption("Hạ tầng Cloud GPU - Đầy đủ tính năng như bản PC gốc")

# PHẦN 1: CẤU HÌNH NGÔN NGỮ & GIỌNG ĐỌC MẪU ĐA DẠNG
st.subheader("🌐 Cấu hình Ngôn ngữ & Giọng đọc")

# Lựa chọn Ngôn ngữ / Chế độ đọc
language_mode = st.selectbox(
    "Chọn ngôn ngữ / Chế độ hệ thống:",
    ["Tiếng Việt (Bản xứ)", "Bilingual (Song ngữ Anh - Việt Code-switching)"]
)

# Danh sách giọng đọc đa dạng được phân loại theo vùng miền/giọng mặc định của VieNeu real
if language_mode == "Tiếng Việt (Bản xứ)":
    speaker_options = {
        "Nữ miền Bắc (Trúc Ly - Mặc định)": "female_north_01",
        "Nam miền Bắc (Mạnh Dũng)": "male_north_01",
        "Nữ miền Nam (Mai Vy)": "female_south_01",
        "Nam miền Nam (Thành Nam)": "male_south_01",
        "Nữ miền Trung (Hương Giang)": "female_central_01",
        "Nam miền Trung (Trọng Tấn)": "male_central_01"
    }
else:
    speaker_options = {
        "Bilingual Giọng Nữ (Trúc Ly English-Mix)": "bilingual_female",
        "Bilingual Giọng Nam (Mạnh Dũng English-Mix)": "bilingual_male"
    }

selected_speaker_label = st.selectbox("Chọn giọng đọc hệ thống:", list(speaker_options.keys()))
speaker_token = speaker_options[selected_speaker_label]


# PHẦN 2: CHẾ ĐỘ VOICE CLONING (NHÂN BẢN GIỌNG NÓI)
st.subheader("👤 Tính năng Nhân bản giọng nói (Voice Cloning)")

# Cho phép chọn 1 trong 2 cách: Tải file có sẵn HOẶC Thu âm trực tiếp
clone_type = st.radio(
    "Cách cung cấp giọng mẫu:",
    ["Dùng giọng đọc mặc định đã chọn ở trên", "Tải file âm thanh mẫu (.mp3, .wav)", "Thu âm trực tiếp từ Mic điện thoại 🎤"]
)

ref_audio_path = None

if clone_type == "Tải file âm thanh mẫu (.mp3, .wav)":
    uploaded_file = st.file_uploader("Tải lên clip giọng nói mẫu (3-8 giây):", type=["wav", "mp3", "m4a"])
    if uploaded_file:
        ref_audio_path = f"uploaded_{uploaded_file.name}"
        with open(ref_audio_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

elif clone_type == "Thu âm trực tiếp từ Mic điện thoại 🎤":
    # Tính năng thu âm tích hợp sẵn của Streamlit chạy mượt trên Chrome/Safari điện thoại
    audio_value = st.audio_input("Bấm vào nút Mic để ghi âm giọng của bạn (Nói khoảng 4-7 giây):")
    if audio_value:
        ref_audio_path = "recorded_user_voice.wav"
        with open(ref_audio_path, "wb") as f:
            f.write(audio_value.read())
        st.success("🤖 Đã ghi nhận giọng thu âm thành công! Sẵn sàng bắt chước.")


# PHẦN 3: NHẬP VĂN BẢN & XỬ LÝ TỔNG HỢP
st.subheader("📝 Nội dung văn bản")
default_text = "Chào bạn! Đây là hệ thống Việt Nêu phiên bản chuẩn. Hello, welcome to our application! [cười]" if "Bilingual" in language_mode else "Chào bạn! Tôi là trí tuệ nhân tạo đang nói bằng mô hình Việt Nêu phiên bản nâng cấp [cười]."

text_input = st.text_area("Nhập văn bản cần đọc:", value=default_text, height=120)

# Nút kích hoạt co giãn toàn màn hình điện thoại
if st.button("🔥 Tiến hành tạo giọng nói", use_container_width=True):
    if not text_input.strip():
        st.warning("Vui lòng nhập văn bản!")
    elif "mẫu" in clone_type and not uploaded_file:
        st.warning("Vui lòng tải file âm thanh lên trước!")
    elif "Thu âm" in clone_type and not audio_value:
        st.warning("Vui lòng thực hiện bấm thu âm trước!")
    else:
        with st.spinner("🚀 Đang gửi gói dữ liệu lên Cloud GPU để xử lý..."):
            try:
                # Kết nối trực tiếp tới API Space của tác giả thông qua thư viện Gradio Client chính chủ
                client = Client("pnnbao-ump/VieNeu-TTS-v3-Turbo")
                
                # Cấu hình tham số gửi đi
                if ref_audio_path and os.path.exists(ref_audio_path):
                    # Chế độ bắt chước / Clone giọng (Gửi file âm thanh mẫu qua handle_file)
                    result = client.predict(
                        text=text_input,
                        ref_audio_input=handle_file(ref_audio_path),
                        api_name="/predict"
                    )
                else:
                    # Chế độ chạy giọng mặc định được chọn (Bắc - Trung - Nam hoặc Bilingual)
                    # Gửi kèm mã định danh Speaker Token của hệ thống VieNeu
                    result = client.predict(
                        text=text_input,
                        ref_audio_input=speaker_token, # Truyền token giọng đọc hệ thống
                        api_name="/predict"
                    )
                
                # Phát file kết quả nhận được
                if result and os.path.exists(result):
                    with open(result, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                    
                    st.audio(audio_bytes, format="audio/wav")
                    st.success("🎉 Đã tổng hợp giọng nói thành công!")
                else:
                    st.error("Không nhận được phản hồi âm thanh từ máy chủ Cloud.")
                    
                # Dọn dẹp tệp tin tạm thời trên server Streamlit
                if ref_audio_path and os.path.exists(ref_audio_path):
                    os.remove(ref_audio_path)
                    
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")
