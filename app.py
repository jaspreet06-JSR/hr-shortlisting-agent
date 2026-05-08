import streamlit as st
from parsers.pdf_parser import extract_text_from_pdf
from scoring.matcher import extract_skills, calculate_match

# Page Config
st.set_page_config(
    page_title="HR Shortlisting Agent",
    layout="wide"
)

# App Title
st.title("HR Resume Shortlisting Agent")

st.write("Upload Job Description and Candidate Resumes")

# Skills Database
SKILLS = [
    "Python",
    "SQL",
    "Machine Learning",
    "Deep Learning",
    "TensorFlow",
    "Java",
    "C++",
    "Data Analysis",
    "Communication",
    "Leadership"
]

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

# Process JD
if jd_file:

    st.success(f"JD Uploaded: {jd_file.name}")

    # Extract JD text
    jd_text = extract_text_from_pdf(jd_file)

    # Display JD text
    st.subheader("Extracted JD Text")

    st.text_area(
        "JD Content",
        jd_text,
        height=200
    )

    # Extract JD skills
    jd_skills = extract_skills(jd_text, SKILLS)

    st.subheader("JD Skills Detected")

    st.write(jd_skills)

    # Process Resumes
    if resume_files:

        st.subheader("Uploaded Resumes")

        for resume in resume_files:

            st.divider()

            st.write(f"Processing: {resume.name}")

            # Extract resume text
            resume_text = extract_text_from_pdf(resume)

            # Display resume text
            st.text_area(
                f"Extracted Text - {resume.name}",
                resume_text[:3000],
                height=250
            )

            # Extract resume skills
            resume_skills = extract_skills(
                resume_text,
                SKILLS
            )

            # Calculate matching
            result = calculate_match(
                jd_skills,
                resume_skills
            )

            # Display results
            st.subheader("Matching Results")

            st.write("Matched Skills:")
            st.success(result["matched"])

            st.write("Missing Skills:")
            st.error(result["missing"])

            st.write(f"Match Score: {result['score']}%")