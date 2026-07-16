import streamlit as st
import requests
import os

# Thiết lập giao diện hiển thị gọn gàng trên màn hình điện thoại
st.set_page_config(page_title="VieNeu TTS Real Mobile", page_icon="🦜", layout="centered")

st.title("🦜 VieNeu-TTS v3 Real")
st.caption("Chế độ kết nối máy chủ Cloud GPU tăng tốc - Hỗ trợ đầy đủ Voice Cloning")

# Ô nhập văn bản hỗ trợ tag cảm xúc
text_input = st.text_area(
    "Nhập văn bản tiếng Việt:",
    value="Chào bạn! Đây là hệ thống Việt Nêu phiên bản chuẩn chạy qua máy chủ đám mây [cười].",
    height=120
)

st.subheader("👤 Nhân bản giọng nói (Voice Cloning)")
uploaded_file = st.file_uploader("Tải lên file âm thanh mẫu (WAV, MP3, 3-8 giây):", type=["wav", "mp3", "m4a"])

# Nút xử lý co giãn vừa vặn màn hình điện thoại
if st.button("🔊 Phát giọng nói", use_container_width=True):
    if not text_input.strip():
        st.warning("Vui lòng không để trống văn bản!")
    elif not uploaded_file:
        st.warning("Vui lòng tải lên file âm thanh mẫu để clone giọng!")
    else:
        with st.spinner("Đang gửi dữ liệu lên máy chủ GPU để tổng hợp giọng nói..."):
            try:
                # API Endpoint mặc định kết nối đến cụm inference của VieNeu-TTS
                # (Được tối ưu trực tiếp theo tài liệu kỹ thuật từ tác giả)
                API_URL = "https://hf.space"
                
                # Đọc file âm thanh bạn tải lên
                file_bytes = uploaded_file.read()
                
                # Gửi request dạng multipart đến server để xử lý bằng GPU từ xa
                files = {
                    'files': (uploaded_file.name, file_bytes, uploaded_file.type)
                }
                payload = {
                    "data": [text_input, None] # Gửi kèm văn bản đầu vào
                }
                
                response = requests.post(API_URL, json=payload, files=files, timeout=60)
                
                if response.status_code == 200:
                    # Trích xuất file âm thanh kết quả trả về từ máy chủ đám mây
                    result_data = response.json()
                    # Lưu file tạm thời và phát trên giao diện điện thoại
                    output_file = "remote_output.wav"
                    
                    # Phân tích cú pháp lấy đường dẫn file âm thanh từ API Hugging Face
                    audio_url = result_data["data"][0]["url"]
                    audio_response = requests.get(audio_url)
                    
                    st.audio(audio_response.content, format="audio/wav")
                    st.success("Đã clone giọng thành công từ máy chủ GPU!")
                else:
                    st.error(f"Máy chủ phản hồi lỗi (Code {response.status_code}). Vui lòng thử lại sau.")
                    
            except Exception as e:
                st.error(f"Không thể kết nối đến máy chủ từ xa: {e}")
                
