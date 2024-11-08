# app.py

import streamlit as st
import os
import tempfile
import zipfile
from io import BytesIO
from convert_to_yolo import convert_voc_to_yolo

st.set_page_config(page_title="XML to TXT Converter", layout="centered")

st.title("XML to TXT Format Converter")
st.write("Convert XML annotation files from Pascal XML format to YOLO format. Choose to convert a single XML file or a ZIP file containing multiple XML files.")

# Sidebar: Mode Selection
st.sidebar.header("Conversion Mode")
conversion_mode = st.sidebar.radio("Choose conversion mode:", ["Single File", "Folder (ZIP)"])

# Sidebar: Class Names Input
st.sidebar.header("Class Names")
class_names = st.sidebar.text_area("Enter class names (one per line)", "number_plate")
classes = [name.strip() for name in class_names.splitlines() if name.strip()]

if conversion_mode == "Single File":
    # Single File Mode: File Uploader
    uploaded_file = st.file_uploader("Upload an XML file", type="xml")

    if st.button("Convert Single File"):
        if not uploaded_file:
            st.warning("Please upload an XML file.")
        else:
            with st.spinner("Converting file..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    xml_path = os.path.join(temp_dir, uploaded_file.name)
                    
                    # Save uploaded file to temporary path
                    with open(xml_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Convert XML to YOLO format
                    txt_filename = os.path.join(temp_dir, uploaded_file.name.replace(".xml", ".txt"))
                    convert_voc_to_yolo([xml_path], temp_dir, classes)

                    # Download the converted file
                    with open(txt_filename, "r") as file:
                        txt_data = file.read()

                    st.success("Conversion completed!")
                    st.download_button(
                        label="Download txt File",
                        data=txt_data,
                        file_name=uploaded_file.name.replace(".xml", ".txt"),
                        mime="text/plain"
                    )

elif conversion_mode == "Folder (ZIP)":
    # Folder Mode: ZIP File Uploader
    uploaded_zip = st.file_uploader("Upload a ZIP file containing XML files", type="zip")

    if st.button("Convert ZIP Folder"):
        if not uploaded_zip:
            st.warning("Please upload a ZIP file.")
        else:
            with st.spinner("Converting files..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_path = os.path.join(temp_dir, "uploaded.zip")
                    
                    # Save uploaded ZIP file
                    with open(zip_path, "wb") as f:
                        f.write(uploaded_zip.getbuffer())

                    # Extract ZIP file
                    with zipfile.ZipFile(zip_path, "r") as zip_ref:
                        zip_ref.extractall(temp_dir)

                    # List all extracted XML files
                    extracted_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".xml")]

                    # Convert each XML file to YOLO format
                    converted_files = []
                    for xml_file in extracted_files:
                        txt_filename = xml_file.replace(".xml", ".txt")
                        convert_voc_to_yolo([xml_file], temp_dir, classes)
                        converted_files.append(txt_filename)

                    # Create a ZIP file with all YOLO files
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                        for file_path in converted_files:
                            zip_file.write(file_path, os.path.basename(file_path))
                    zip_buffer.seek(0)

                st.success("Conversion completed!")
                st.download_button(
                    label="Download All txt Files as ZIP",
                    data=zip_buffer,
                    file_name="converted_txt_files.zip",
                    mime="application/zip"
                )

# Sidebar Instructions
st.sidebar.header("Instructions")
st.sidebar.write(
    """
    1. Select conversion mode: **Single File** or **Folder (ZIP)**.
    2. Upload an XML file (Single File mode) or a ZIP containing multiple XML files (Folder mode).
    3. Enter class names (one per line).
    4. Click 'Convert' to process the files.
    5. Download the converted YOLO files.
    """
)
