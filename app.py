import streamlit as st
from parsers.pdf_parser import extract_text_from_pdf

st.set_page_config(page_title="HR Shortlisting Agent", layout="wide")

st.title("HR Resume Shortlisting Agent")

st.write("Upload Job Description and Candidate Resumes")

# Upload JD
jd_file = st.file_uploader(
    "Upload Job Description",
    type=["pdf"]
)

# Upload Resumes
resume_files = st.file_uploader(
    "Upload Candidate Resumes",
    type=["pdf"],
    accept_multiple_files=True
)

# JD Processing
if jd_file:
    st.success(f"JD Uploaded: {jd_file.name}")

    jd_text = extract_text_from_pdf(jd_file)

    st.subheader("Extracted JD Text")
    st.text_area("JD Content", jd_text, height=200)

# Resume Processing
if resume_files:
    st.subheader("Uploaded Resumes")

    for resume in resume_files:
        st.write(f"Processing: {resume.name}")

        resume_text = extract_text_from_pdf(resume)

        st.text_area(
            f"Extracted Text - {resume.name}",
            resume_text[:3000],
            height=250
        )