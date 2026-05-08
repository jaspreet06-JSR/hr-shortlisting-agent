import streamlit as st

st.set_page_config(page_title="HR Shortlisting Agent", layout="wide")

st.title("HR Resume Shortlisting Agent")

st.write("Upload Job Description and Candidate Resumes")

# Upload JD
jd_file = st.file_uploader(
    "Upload Job Description",
    type=["pdf", "docx", "txt"]
)

# Upload Resumes
resume_files = st.file_uploader(
    "Upload Candidate Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# Display Uploaded Files
if jd_file:
    st.success(f"JD Uploaded: {jd_file.name}")

if resume_files:
    st.subheader("Uploaded Resumes")

    for resume in resume_files:
        st.write(resume.name)