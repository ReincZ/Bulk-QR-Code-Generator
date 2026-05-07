import streamlit as st
# ... (import lainnya tetap sama)

def check_file_size(file):
    # Maksimal 5MB dalam bytes (5 * 1024 * 1024)
    MAX_FILE_SIZE = 5 * 1024 * 1024 
    if file.size > MAX_FILE_SIZE:
        return False
    return True

# --- UI STREAMLIT ---
st.title("🏥 Bulk QR Code Generator Dokter")

col1, col2 = st.columns(2)

with col1:
    excel_upload = st.file_uploader("Upload Excel (.xlsx)", type=['xlsx'])
    if excel_upload:
        if not check_file_size(excel_upload):
            st.error("Ukuran file Excel terlalu besar! Maksimal 5MB.")
            excel_upload = None

with col2:
    # Penjagaan ekstensi melalui parameter 'type'
    logo_upload = st.file_uploader("Upload Logo RS", type=['png', 'jpg', 'jpeg'])
    if logo_upload:
        if not check_file_size(logo_upload):
            st.error("Ukuran file Logo terlalu besar! Maksimal 5MB.")
            logo_upload = None

# Tambahkan pengecekan sebelum tombol diproses
if excel_upload and st.button("Generate QR Codes"):
    # ... (logika proses tetap sama)
