import streamlit as st
from cryptography.fernet import Fernet
from PIL import Image, ImageDraw, ImageFont
import io
import base64

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

st.title("🎨 Secure Image Hub")
st.write("Encrypt/Decrypt and Watermark your Images in real-time!")

media_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])
password = st.text_input("Enter Password for Encryption/Decryption", type="password")
watermark_text = st.text_input("Enter Watermark Text")

action = st.radio("Choose Action", ["Encrypt", "Decrypt", "Watermark"])

if media_file and password:
    key = generate_key(password)
    data = media_file.read()

    if action == "Encrypt":
        encrypted = encrypt_data(data, key)
        st.download_button("Download Encrypted Image", encrypted, file_name="encrypted_file.bin")
    
    elif action == "Decrypt":
        try:
            decrypted = decrypt_data(data, key)
            st.image(Image.open(io.BytesIO(decrypted)), caption="Decrypted Image")
        except Exception as e:
            st.error("Decryption failed. Check password or file.")

    elif action == "Watermark":
        watermarked = watermark_image(data, watermark_text)
        st.image(Image.open(io.BytesIO(watermarked)), caption="Watermarked Image")
        st.download_button("Download Watermarked Image", watermarked, file_name="watermarked_image.png")
