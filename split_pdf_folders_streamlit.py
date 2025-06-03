
import streamlit as st
import os
import zipfile
import shutil
import tempfile
from pathlib import Path

st.set_page_config(page_title="📁 تقسيم ملفات PDF إلى مجلدات", layout="centered")
st.title("📂 تقسيم ملفات PDF إلى مجلدات متعددة")

uploaded_zip = st.file_uploader("📦 ارفع ملف ZIP يحتوي على ملفات PDF", type="zip")

chunk_size = st.number_input("📄 عدد الملفات في كل مجلد", min_value=10, max_value=1000, value=500, step=10)

if uploaded_zip:
    with st.spinner("🔄 جاري معالجة الملفات..."):
        temp_dir = tempfile.TemporaryDirectory()
        zip_path = os.path.join(temp_dir.name, "all_pdfs.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir.name)

        # جلب كل ملفات PDF فقط
        all_files = [f for f in os.listdir(temp_dir.name) if f.lower().endswith(".pdf")]
        all_files.sort()

        output_dir = os.path.join(temp_dir.name, "مجلدات_مقسمة")
        os.makedirs(output_dir, exist_ok=True)

        # تقسيم الملفات إلى مجلدات فرعية
        for i in range(0, len(all_files), chunk_size):
            chunk = all_files[i:i+chunk_size]
            folder_name = f"دفعة_{(i // chunk_size) + 1}"
            dest_folder = os.path.join(output_dir, folder_name)
            os.makedirs(dest_folder, exist_ok=True)

            for file in chunk:
                shutil.move(os.path.join(temp_dir.name, file), os.path.join(dest_folder, file))

        # إنشاء ملف ZIP جديد يحوي المجلدات المقسمة
        final_zip_path = os.path.join(temp_dir.name, "ملفات_مقسمة.zip")
        with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, output_dir)
                    zipf.write(full_path, arcname)

        with open(final_zip_path, "rb") as f:
            st.success("✅ تم تقسيم الملفات!")
            st.download_button(
                label="📥 تحميل الملفات المقسمة",
                data=f,
                file_name="ملفات_مقسمة.zip",
                mime="application/zip"
            )
