import streamlit as st
from cryptography.fernet import Fernet
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Generate key from password
def generate_key(password: str):
    return base64.urlsafe_b64encode(password.encode('utf-8').ljust(32)[:32])

# Encrypt/Decrypt functions
def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(data, key):
    f = Fernet(key)
    return f.decrypt(data)

# Watermarking image
def watermark_image(img_bytes, text):
    img = Image.open(io.BytesIO(img_bytes))
    drawable = ImageDraw.Draw(img)
    font_size = max(20, img.width // 20)
    font = ImageFont.load_default()
    drawable.text((10, 10), text, fill=(255,0,0), font=font)
    output = io.BytesIO()
    img.save(output, format='PNG')
    return output.getvalue()

# Watermarking video
def watermark_video(video_file, text):
    clip = VideoFileClip(video_file)
    txt_clip = TextClip(text, fontsize=30, color='red').set_position(('right','bottom')).set_duration(clip.duration)
    video = CompositeVideoClip([clip, txt_clip])
    output_path = "watermarked_video.mp4"
    video.write_videofile(output_path, codec="libx264", audio_codec='aac', verbose=False, logger=None)
    return output_path

st.title("🎥 Secure Multimedia Hub")
st.write("Encrypt/Decrypt and Watermark your Images/Videos in real-time!")

media_file = st.file_uploader("Upload Image or Video", type=["png","jpg","jpeg","mp4"])
password = st.text_input("Enter Password for Encryption/Decryption", type="password")
watermark_text = st.text_input("Enter Watermark Text")

action = st.radio("Choose Action", ["Encrypt", "Decrypt", "Watermark"])

if media_file and password:
    key = generate_key(password)
    data = media_file.read()

    if action == "Encrypt":
        encrypted = encrypt_data(data, key)
        st.download_button("Download Encrypted File", encrypted, file_name="encrypted_file.bin")
    
    elif action == "Decrypt":
        try:
            decrypted = decrypt_data(data, key)
            if media_file.type.startswith("image"):
                st.image(Image.open(io.BytesIO(decrypted)), caption="Decrypted Image")
            elif media_file.type.startswith("video"):
                with open("decrypted_video.mp4", "wb") as f:
                    f.write(decrypted)
                st.video("decrypted_video.mp4")
        except Exception as e:
            st.error("Decryption failed. Check password or file.")

    elif action == "Watermark":
        if media_file.type.startswith("image"):
            watermarked = watermark_image(data, watermark_text)
            st.image(Image.open(io.BytesIO(watermarked)), caption="Watermarked Image")
            st.download_button("Download Watermarked Image", watermarked, file_name="watermarked_image.png")
        elif media_file.type.startswith("video"):
            output_path = watermark_video(media_file, watermark_text)
            st.video(output_path)
            with open(output_path, "rb") as f:
                st.download_button("Download Watermarked Video", f.read(), file_name="watermarked_video.mp4")
