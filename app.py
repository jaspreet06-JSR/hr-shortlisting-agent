import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from fpdf import FPDF

from parsers.pdf_parser import extract_text_from_pdf
from scoring.matcher import match_skills

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="HR Resume Shortlisting Agent",
    page_icon="📄",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
.main {
    background-color: #0f172a;
}

.stApp {
    background-color: #0f172a;
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.metric-card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}

.skill-box {
    background-color: #14532d;
    padding: 8px 14px;
    border-radius: 10px;
    margin: 5px;
    display: inline-block;
    color: white;
}

.missing-box {
    background-color: #7f1d1d;
    padding: 8px 14px;
    border-radius: 10px;
    margin: 5px;
    display: inline-block;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("Recruiter Settings")

min_score = st.sidebar.slider(
    "Minimum Match Score",
    0,
    100,
    50
)

# =========================
# TITLE
# =========================

st.title("📄 HR Resume Shortlisting Agent")
st.caption("AI Powered Candidate Screening Dashboard")

# =========================
# FILE UPLOADS
# =========================

jd_file = st.file_uploader(
    "Upload Job Description",
    type=["pdf"]
)

resume_files = st.file_uploader(
    "Upload Candidate Resumes",
    type=["pdf"],
    accept_multiple_files=True
)

# =========================
# SKILL DATABASE
# =========================

SKILLS_DB = [
    "Python",
    "Java",
    "C++",
    "Machine Learning",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "SQL",
    "NLP",
    "Data Analysis",
    "Communication",
    "Leadership",
    "React",
    "AWS",
    "Docker",
    "Kubernetes",
    "Flask",
    "Django",
    "Git"
]

# =========================
# PDF REPORT FUNCTION
# =========================

def generate_pdf(candidate_name, score, matched, missing):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 18)
    pdf.cell(200, 10, txt="Candidate Evaluation Report", ln=True)

    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Candidate: {candidate_name}", ln=True)
    pdf.cell(200, 10, txt=f"Match Score: {score:.2f}%", ln=True)

    pdf.ln(10)

    pdf.multi_cell(
        0,
        10,
        txt=f"Matched Skills:\n{', '.join(matched)}"
    )

    pdf.ln(5)

    pdf.multi_cell(
        0,
        10,
        txt=f"Missing Skills:\n{', '.join(missing)}"
    )

    pdf_output = BytesIO()
    pdf.output(pdf_output)

    return pdf_output.getvalue()

# =========================
# PROCESSING
# =========================

if jd_file and resume_files:

    # =========================
    # JD EXTRACTION
    # =========================

    jd_text = extract_text_from_pdf(jd_file)

    st.subheader("📌 Extracted Job Description")

    st.text_area(
        "JD Text",
        jd_text[:3000],
        height=250
    )

    # =========================
    # EXTRACT JD SKILLS
    # =========================

    jd_skills = []

    for skill in SKILLS_DB:
        if skill.lower() in jd_text.lower():
            jd_skills.append(skill)

    st.subheader("🧠 JD Skills Detected")

    for skill in jd_skills:
        st.markdown(
            f"<span class='skill-box'>{skill}</span>",
            unsafe_allow_html=True
        )

    st.divider()

    leaderboard = []

    # =========================
    # PROCESS EACH RESUME
    # =========================

    for idx, resume in enumerate(resume_files):

        st.header(f"👤 Candidate: {resume.name}")

        resume_text = extract_text_from_pdf(resume)

        with st.expander("View Extracted Resume Text"):
            st.text_area(
                f"Resume Text {idx}",
                resume_text[:3000],
                height=250
            )

        # =========================
        # SKILL MATCHING
        # =========================

        matched_skills, missing_skills, score = match_skills(
            jd_skills,
            resume_text
        )

        # =========================
        # FILTER
        # =========================

        if score < min_score:

            st.warning(
                f"Candidate filtered out. Match Score below {min_score}%"
            )

            continue

        # =========================
        # METRICS
        # =========================

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Match Score",
            f"{score:.2f}%"
        )

        col2.metric(
            "Matched Skills",
            len(matched_skills)
        )

        col3.metric(
            "Missing Skills",
            len(missing_skills)
        )

        # =========================
        # MATCHED SKILLS
        # =========================

        st.subheader("✅ Matched Skills")

        for skill in matched_skills:
            st.markdown(
                f"<span class='skill-box'>{skill}</span>",
                unsafe_allow_html=True
            )

        # =========================
        # MISSING SKILLS
        # =========================

        st.subheader("❌ Missing Skills")

        for skill in missing_skills:
            st.markdown(
                f"<span class='missing-box'>{skill}</span>",
                unsafe_allow_html=True
            )

        # =========================
        # PIE CHART
        # =========================

        pie_chart = px.pie(
            names=["Matched", "Missing"],
            values=[
                len(matched_skills),
                len(missing_skills)
            ],
            title="Skill Match Distribution"
        )

        st.plotly_chart(
            pie_chart,
            use_container_width=True,
            key=f"pie_chart_{idx}"
        )

        # =========================
        # RADAR CHART
        # =========================

        radar_categories = jd_skills

        radar_values = []

        for skill in radar_categories:
            if skill in matched_skills:
                radar_values.append(1)
            else:
                radar_values.append(0)

        radar_chart = go.Figure()

        radar_chart.add_trace(go.Scatterpolar(
            r=radar_values,
            theta=radar_categories,
            fill='toself',
            name=resume.name
        ))

        radar_chart.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=False,
            title="Candidate Skill Radar"
        )

        st.plotly_chart(
            radar_chart,
            use_container_width=True,
            key=f"radar_chart_{idx}"
        )

        # =========================
        # PDF REPORT
        # =========================

        pdf_data = generate_pdf(
            resume.name,
            score,
            matched_skills,
            missing_skills
        )

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_data,
            file_name=f"{resume.name}_report.pdf",
            mime="application/pdf",
            key=f"pdf_download_{idx}"
        )

        # =========================
        # LEADERBOARD DATA
        # =========================

        leaderboard.append({
            "Candidate": resume.name,
            "Score": round(score, 2),
            "Matched Skills": ", ".join(matched_skills),
            "Missing Skills": ", ".join(missing_skills)
        })

        st.divider()

    # =========================
    # FINAL LEADERBOARD
    # =========================

    if leaderboard:

        st.header("🏆 Candidate Leaderboard")

        leaderboard_df = pd.DataFrame(leaderboard)

        leaderboard_df = leaderboard_df.sort_values(
            by="Score",
            ascending=False
        )

        st.dataframe(
            leaderboard_df,
            use_container_width=True
        )

        # =========================
        # BAR CHART
        # =========================

        bar_chart = px.bar(
            leaderboard_df,
            x="Candidate",
            y="Score",
            title="Candidate Ranking"
        )

        st.plotly_chart(
            bar_chart,
            use_container_width=True,
            key="leaderboard_bar_chart"
        )

        # =========================
        # CSV EXPORT
        # =========================

        csv = leaderboard_df.to_csv(index=False)

        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name="candidate_rankings.csv",
            mime="text/csv",
            key="csv_download"
        )

        # =========================
        # RECRUITER ANALYTICS
        # =========================

        st.header("📊 Recruiter Analytics Dashboard")

        avg_score = leaderboard_df["Score"].mean()

        top_score = leaderboard_df["Score"].max()

        total_candidates = len(leaderboard_df)

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Average Score",
            f"{avg_score:.2f}%"
        )

        c2.metric(
            "Top Score",
            f"{top_score:.2f}%"
        )

        c3.metric(
            "Candidates",
            total_candidates
        )

        analytics_chart = px.histogram(
            leaderboard_df,
            x="Score",
            nbins=10,
            title="Candidate Score Distribution"
        )

        st.plotly_chart(
            analytics_chart,
            use_container_width=True,
            key="analytics_histogram_chart"
        )