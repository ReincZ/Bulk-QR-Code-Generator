import streamlit as st
import qrcode
import pandas as pd
from PIL import Image
import os
import shutil
import io
from pathvalidate import sanitize_filename

# Konfigurasi Halaman
st.set_page_config(page_title="Bulk QR Generator RS", layout="centered")

def check_file_size(file):
    # Maksimal 5MB dalam bytes (5 * 1024 * 1024)
    MAX_FILE_SIZE = 5 * 1024 * 1024 
    if file.size > MAX_FILE_SIZE:
        return False
    return True

def generate_doctor_qrs(df, logo_file, output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    logo = None
    if logo_file is not None:
        logo = Image.open(logo_file)

    for index, row in df.iterrows():
        nama = str(row['Nama']).strip() if pd.notna(row['Nama']) else ""
        sip = str(row['SIP']).strip() if pd.notna(row['SIP']) else ""
        
        if not nama and not sip: continue

        isi_qr = f"{nama}\n{sip}"

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=4,
        )
        qr.add_data(isi_qr)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        if logo is not None:
            qr_w, qr_h = img_qr.size
            logo_size = int(qr_w * 0.2)
            current_logo = logo.copy().resize((logo_size, logo_size), Image.Resampling.LANCZOS)
           
            buffer_size = logo_size + 6
            white_bg = Image.new("RGB", (buffer_size, buffer_size), "white")
           
            img_qr.paste(white_bg, ((qr_w - buffer_size) // 2, (qr_h - buffer_size) // 2))
            if current_logo.mode == 'RGBA':
                img_qr.paste(current_logo, ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2), current_logo)
            else:
                img_qr.paste(current_logo, ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2))

        filename = sanitize_filename(f"{nama}_{sip}")[:50]
        img_qr.save(os.path.join(output_folder, f"{filename}.png"))

    zip_path = 'Hasil_QR_Archive'
    shutil.make_archive(zip_path, 'zip', output_folder)
    return f"{zip_path}.zip"

# --- UI STREAMLIT ---
st.title("🏥 Bulk QR Code Generator Dokter")
st.write("Upload file Excel dan Logo untuk membuat QR Code secara masal.")

col1, col2 = st.columns(2)

with col1:
    excel_upload = st.file_uploader("Upload Excel (.xlsx)", type=['xlsx'])
    if excel_upload:
        if not check_file_size(excel_upload):
            st.error("Ukuran file Excel terlalu besar! Maksimal 5MB.")
            excel_upload = None

with col2:
    logo_upload = st.file_uploader("Upload Logo RS", type=['png', 'jpg', 'jpeg'])
    if logo_upload:
        if not check_file_size(logo_upload):
            st.error("Ukuran file Logo terlalu besar! Maksimal 5MB.")
            logo_upload = None

# PERBAIKAN DI SINI: Logika harus masuk ke dalam blok IF
if excel_upload and st.button("Generate QR Codes"):
    try:
        df = pd.read_excel(excel_upload, header=None)
        df = df.iloc[:, :2]
        df.columns = ['Nama', 'SIP']
        
        with st.spinner('Sedang memproses...'):
            output_dir = "temp_qr_folder"
            zip_file = generate_doctor_qrs(df, logo_upload, output_dir)
            
            with open(zip_file, "rb") as f:
                st.success(f"Berhasil memproses {len(df)} data!")
                st.download_button(
                    label="📥 Download Semua QR (ZIP)",
                    data=f,
                    file_name="QR_Codes_Dokter.zip",
                    mime="application/zip"
                )
            
            # Cleanup
            if os.path.exists(output_dir): shutil.rmtree(output_dir)
            if os.path.exists(zip_file): os.remove(zip_file)
            
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
