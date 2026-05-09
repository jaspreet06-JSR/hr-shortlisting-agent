import streamlit as st
import pandas as pd
import plotly.express as px

from fpdf import FPDF

from parsers.pdf_parser import extract_text_from_pdf
from scoring.matcher import match_skills

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="HR Resume Shortlisting Agent",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------

st.markdown(
    """
    <style>

    .main {
        background-color: #0E1117;
    }

    .title {
        font-size: 48px;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
    }

    .subtitle {
        color: #BBBBBB;
        margin-bottom: 30px;
    }

    .card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        border: 1px solid #333333;
    }

    .score-box {
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        color: white;
        background: linear-gradient(90deg, #00C853, #009624);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# HEADER
# -----------------------------

st.markdown(
    '<div class="title">HR Resume Shortlisting Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI Powered Resume Ranking & Candidate Evaluation System</div>',
    unsafe_allow_html=True
)

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("Recruiter Settings")

minimum_score = st.sidebar.slider(
    "Minimum Match Score",
    0,
    100,
    50
)

# -----------------------------
# PDF REPORT GENERATOR
# -----------------------------

def generate_pdf_report(
    candidate_name,
    score,
    matched_skills,
    missing_skills,
    recommendation
):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(200, 10, "Candidate Evaluation Report", ln=True)

    pdf.ln(10)

    pdf.set_font("Helvetica", size=12)

    pdf.cell(200, 10, f"Candidate: {candidate_name}", ln=True)
    pdf.cell(200, 10, f"Score: {score}%", ln=True)
    pdf.cell(200, 10, f"Recommendation: {recommendation}", ln=True)

    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(200, 10, "Matched Skills", ln=True)

    pdf.set_font("Helvetica", size=12)

    for skill in matched_skills:
        pdf.cell(200, 10, f"- {skill}", ln=True)

    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(200, 10, "Missing Skills", ln=True)

    pdf.set_font("Helvetica", size=12)

    for skill in missing_skills:
        pdf.cell(200, 10, f"- {skill}", ln=True)

    pdf_output = pdf.output(dest="S")

    return bytes(pdf_output)

# -----------------------------
# FILE UPLOADS
# -----------------------------

col1, col2 = st.columns(2)

with col1:

    jd_file = st.file_uploader(
        "Upload Job Description (PDF)",
        type=["pdf"]
    )

with col2:

    resume_files = st.file_uploader(
        "Upload Candidate Resumes",
        type=["pdf"],
        accept_multiple_files=True
    )

# -----------------------------
# SKILLS DATABASE
# -----------------------------

SKILLS_DB = [
    "Python",
    "Machine Learning",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "NLP",
    "SQL",
    "Data Analysis",
    "Communication",
    "Leadership",
    "Java",
    "C++",
    "React",
    "AWS",
    "Docker",
    "Flask",
    "Django",
    "Kubernetes",
    "Git",
    "Linux"
]

# -----------------------------
# PROCESS JOB DESCRIPTION
# -----------------------------

if jd_file:

    jd_text = extract_text_from_pdf(jd_file)

    jd_skills = match_skills(
        jd_text,
        SKILLS_DB
    )

    st.success("Job Description Uploaded Successfully")

    with st.expander("View Extracted JD Text"):
        st.write(jd_text)

    st.subheader("JD Skills Detected")

    skill_cols = st.columns(4)

    for idx, skill in enumerate(jd_skills):
        skill_cols[idx % 4].success(skill)

    # -----------------------------
    # PROCESS RESUMES
    # -----------------------------

    if resume_files:

        leaderboard = []

        st.divider()

        st.header("Candidate Analysis")

        for resume in resume_files:

            resume_text = extract_text_from_pdf(resume)

            candidate_skills = match_skills(
                resume_text,
                SKILLS_DB
            )

            matched_skills = list(
                set(jd_skills).intersection(candidate_skills)
            )

            missing_skills = list(
                set(jd_skills) - set(candidate_skills)
            )

            # -----------------------------
            # SCORING ENGINE
            # -----------------------------

            if len(jd_skills) > 0:

                skills_score = (
                    len(matched_skills) / len(jd_skills)
                ) * 100

                experience_score = max(skills_score - 10, 0)
                projects_score = max(skills_score - 15, 0)
                education_score = max(skills_score - 5, 0)

                final_score = round(
                    (
                        skills_score * 0.5 +
                        experience_score * 0.2 +
                        projects_score * 0.2 +
                        education_score * 0.1
                    ),
                    2
                )

            else:
                final_score = 0

            # -----------------------------
            # FILTER
            # -----------------------------

            if final_score < minimum_score:
                continue

            # -----------------------------
            # RECOMMENDATION
            # -----------------------------

            if final_score >= 85:
                recommendation = "Highly Recommended"

            elif final_score >= 70:
                recommendation = "Recommended"

            elif final_score >= 50:
                recommendation = "Moderate Match"

            else:
                recommendation = "Weak Match"

            # -----------------------------
            # SAVE FOR LEADERBOARD
            # -----------------------------

            leaderboard.append({
                "Candidate": resume.name,
                "Score": final_score,
                "Matched Skills": len(matched_skills),
                "Recommendation": recommendation
            })

            # -----------------------------
            # CANDIDATE CARD
            # -----------------------------

            st.markdown(
                '<div class="card">',
                unsafe_allow_html=True
            )

            colA, colB = st.columns([3, 1])

            with colA:
                st.subheader(f"Candidate: {resume.name}")

            with colB:
                st.markdown(
                    f'<div class="score-box">{final_score}%</div>',
                    unsafe_allow_html=True
                )

            st.progress(final_score / 100)

            tabs = st.tabs([
                "Matched Skills",
                "Missing Skills",
                "Recommendation",
                "Resume Text"
            ])

            # -----------------------------
            # MATCHED SKILLS
            # -----------------------------

            with tabs[0]:

                if matched_skills:

                    for skill in matched_skills:
                        st.success(skill)

                else:
                    st.warning("No matched skills")

            # -----------------------------
            # MISSING SKILLS
            # -----------------------------

            with tabs[1]:

                if missing_skills:

                    for skill in missing_skills:
                        st.error(skill)

                else:
                    st.success("No missing skills")

            # -----------------------------
            # RECOMMENDATION TAB
            # -----------------------------

            with tabs[2]:

                st.info(recommendation)

                st.write(
                    f"This candidate matched "
                    f"{len(matched_skills)} "
                    f"out of {len(jd_skills)} required skills."
                )

            # -----------------------------
            # RESUME TEXT
            # -----------------------------

            with tabs[3]:

                with st.expander("View Full Resume Text"):
                    st.write(resume_text)

            # -----------------------------
            # PIE CHART
            # -----------------------------

            pie_df = pd.DataFrame({
                "Category": ["Matched", "Missing"],
                "Count": [
                    len(matched_skills),
                    len(missing_skills)
                ]
            })

            pie_chart = px.pie(
                pie_df,
                names="Category",
                values="Count",
                title="Skill Match Distribution"
            )

            st.plotly_chart(
                pie_chart,
                use_container_width=True,
                key="pie_chart_1"
            )

            # -----------------------------
            # RADAR CHART
            # -----------------------------

            radar_df = pd.DataFrame(dict(
                r=[
                    final_score,
                    max(final_score - 10, 0),
                    max(final_score - 15, 0),
                    max(final_score - 5, 0),
                    max(final_score - 12, 0)
                ],
                theta=[
                    "Skills",
                    "Experience",
                    "Projects",
                    "Education",
                    "Communication"
                ]
            ))

            radar_chart = px.line_polar(
                radar_df,
                r='r',
                theta='theta',
                line_close=True,
                title='Candidate Competency Radar'
            )

            radar_chart.update_traces(fill='toself')

            st.plotly_chart(
                radar_chart,
                use_container_width=True,
                key="radar_1"
            )

            # -----------------------------
            # DOWNLOAD REPORT
            # -----------------------------

            pdf_data = generate_pdf_report(
                resume.name,
                final_score,
                matched_skills,
                missing_skills,
                recommendation
            )

            st.download_button(
                label="Download PDF Report",
                data=pdf_data,
                file_name=f"{resume.name}_report.pdf",
                mime="application/pdf"
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

        # -----------------------------
        # LEADERBOARD
        # -----------------------------

        if leaderboard:

            st.divider()

            st.header("Candidate Leaderboard")

            leaderboard_df = pd.DataFrame(leaderboard)

            leaderboard_df = leaderboard_df.sort_values(
                by="Score",
                ascending=False
            )

            leaderboard_df.index = range(
                1,
                len(leaderboard_df) + 1
            )

            st.dataframe(
                leaderboard_df,
                use_container_width=True
            )

            # -----------------------------
            # EXPORT CSV
            # -----------------------------

            csv_data = leaderboard_df.to_csv(index=False)

            st.download_button(
                label="Export Leaderboard CSV",
                data=csv_data,
                file_name="candidate_leaderboard.csv",
                mime="text/csv"
            )

            # -----------------------------
            # BAR CHART
            # -----------------------------

            st.subheader("Candidate Score Comparison")

            bar_chart = px.bar(
                leaderboard_df,
                x="Candidate",
                y="Score",
                text="Score",
                title="Resume Ranking Scores"
            )

            st.plotly_chart(
                bar_chart,
                use_container_width=True,
                key="bar_1"
            )

            # -----------------------------
            # RECRUITER ANALYTICS
            # -----------------------------

            st.divider()

            st.header("Recruiter Analytics Dashboard")

            analytics_col1, analytics_col2, analytics_col3 = st.columns(3)

            average_score = round(
                leaderboard_df["Score"].mean(),
                2
            )

            highest_score = leaderboard_df["Score"].max()

            selected_candidates = len(
                leaderboard_df[
                    leaderboard_df["Score"] >= 70
                ]
            )

            with analytics_col1:

                st.metric(
                    "Average Candidate Score",
                    f"{average_score}%"
                )

            with analytics_col2:

                st.metric(
                    "Highest Candidate Score",
                    f"{highest_score}%"
                )

            with analytics_col3:

                st.metric(
                    "Recommended Candidates",
                    selected_candidates
                )

            # -----------------------------
            # TOP CANDIDATE
            # -----------------------------

            top_candidate = leaderboard_df.iloc[0]

            st.success(
                f"🏆 Top Candidate: "
                f"{top_candidate['Candidate']} "
                f"| Score: {top_candidate['Score']}%"
            )

else:

    st.info(
        "Upload Job Description and Candidate Resumes to Begin"
    )