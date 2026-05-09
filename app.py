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
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.skill-pill {
    display:inline-block;
    padding:10px 20px;
    margin:8px 8px 8px 0;
    border-radius:18px;

    background: linear-gradient(
        135deg,
        #134e4a,
        #115e59
    );

    color:white;
    font-weight:600;
    font-size:15px;

    border:1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 4px 12px rgba(0,0,0,0.25);

    transition:0.3s ease;
}

.skill-pill:hover {
    transform:translateY(-2px);
    background: linear-gradient(
        135deg,
        #0f766e,
        #115e59
    );
}

.match-pill {
    background: linear-gradient(
        135deg,
        #14532d,
        #166534
    );
}

.missing-pill {
    background: linear-gradient(
        135deg,
        #7f1d1d,
        #991b1b
    );
}

</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("Recruiter Settings")

threshold = st.sidebar.slider(
    "Minimum Match Score",
    0,
    100,
    50
)

# =========================
# HERO SECTION
# =========================

st.markdown("""
<div style="
padding:30px;
border-radius:25px;
background: linear-gradient(135deg,#1e3a8a,#312e81);
margin-bottom:30px;
box-shadow:0 10px 40px rgba(0,0,0,0.4);
">
<h1 style="font-size:52px;">📄 HR Resume Shortlisting Agent</h1>
<p style="font-size:20px;color:#d1d5db;">
AI Powered Smart Candidate Screening Platform
</p>
</div>
""", unsafe_allow_html=True)

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

leaderboard = []

# =========================
# PROCESS FILES
# =========================

if jd_file and resume_files:

    # =========================
    # EXTRACT JD
    # =========================

    jd_text = extract_text_from_pdf(jd_file)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📌 Extracted Job Description")

    st.text_area(
        "JD Text",
        jd_text,
        height=250
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # SKILLS
    # =========================

    jd_skills = [
        "Python",
        "C++",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "NLP",
        "Communication"
    ]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🧠 JD Skills Detected")

    for skill in jd_skills:
        st.markdown(
            f'<span class="skill-pill skill-match">{skill}</span>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # PROCESS EACH RESUME
    # =========================

    for index, resume_file in enumerate(resume_files):

        resume_text = extract_text_from_pdf(resume_file)

        matched_skills, missing_skills, score = match_skills(
            jd_skills,
            resume_text
        )

        leaderboard.append({
            "Candidate": resume_file.name,
            "Score": score,
            "Matched Skills": ", ".join(matched_skills),
            "Missing Skills": ", ".join(missing_skills)
        })

        # =========================
        # CANDIDATE CARD
        # =========================

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown(f"# 👤 Candidate: {resume_file.name}")

        with st.expander("View Extracted Resume Text"):
            st.write(resume_text)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Match Score",
                f"{score:.2f}%"
            )

        with col2:
            st.metric(
                "Matched Skills",
                len(matched_skills)
            )

        with col3:
            st.metric(
                "Missing Skills",
                len(missing_skills)
            )

        # =========================
        # MATCHED SKILLS
        # =========================

        st.subheader("✅ Matched Skills")

        for skill in matched_skills:
            st.markdown(
                f'<span class="skill-pill skill-match">{skill}</span>',
                unsafe_allow_html=True
            )

        # =========================
        # MISSING SKILLS
        # =========================

        st.subheader("❌ Missing Skills")

        for skill in missing_skills:
            st.markdown(
                f'<span class="skill-pill skill-missing">{skill}</span>',
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

        pie_chart.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            height=450
        )

        st.plotly_chart(
            pie_chart,
            use_container_width=True,
            key=f"pie_chart_{index}"
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

        radar_values.append(radar_values[0])
        radar_categories.append(radar_categories[0])

        radar_chart = go.Figure()

        radar_chart.add_trace(go.Scatterpolar(
            r=radar_values,
            theta=radar_categories,
            fill='toself',
            name='Skills'
        ))

        radar_chart.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            title="Candidate Skill Radar"
        )

        st.plotly_chart(
            radar_chart,
            use_container_width=True,
            key=f"radar_chart_{index}"
        )

        # =========================
        # PDF REPORT
        # =========================

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", size=14)

        pdf.cell(200, 10, txt="HR Resume Screening Report", ln=True)

        pdf.ln(10)

        pdf.cell(200, 10, txt=f"Candidate: {resume_file.name}", ln=True)
        pdf.cell(200, 10, txt=f"Match Score: {score:.2f}%", ln=True)

        pdf.ln(10)

        pdf.multi_cell(
            0,
            10,
            txt=f"Matched Skills: {', '.join(matched_skills)}"
        )

        pdf.ln(5)

        pdf.multi_cell(
            0,
            10,
            txt=f"Missing Skills: {', '.join(missing_skills)}"
        )

        pdf_output = bytes(pdf.output(dest='S'))

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_output,
            file_name=f"{resume_file.name}_report.pdf",
            mime="application/pdf",
            key=f"pdf_download_{index}"
        )

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # LEADERBOARD
    # =========================

    if leaderboard:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("# 🏆 Candidate Leaderboard")

        leaderboard_df = pd.DataFrame(leaderboard)

        leaderboard_df = leaderboard_df.sort_values(
            by="Score",
            ascending=False
        )

        st.dataframe(
            leaderboard_df,
            use_container_width=True,
            height=300
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

        bar_chart.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            height=450
        )

        st.plotly_chart(
            bar_chart,
            use_container_width=True,
            key="leaderboard_bar_chart"
        )

        # =========================
        # EXPORT CSV
        # =========================

        csv = leaderboard_df.to_csv(index=False)

        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name="candidate_rankings.csv",
            mime="text/csv",
            key="csv_download"
        )

        st.markdown('</div>', unsafe_allow_html=True)

        # =========================
        # ANALYTICS DASHBOARD
        # =========================

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("# 📊 Recruiter Analytics Dashboard")

        avg_score = leaderboard_df["Score"].mean()
        top_score = leaderboard_df["Score"].max()
        total_candidates = len(leaderboard_df)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Average Score",
                f"{avg_score:.2f}%"
            )

        with col2:
            st.metric(
                "Top Score",
                f"{top_score:.2f}%"
            )

        with col3:
            st.metric(
                "Candidates",
                total_candidates
            )

        analytics_chart = px.histogram(
            leaderboard_df,
            x="Score",
            nbins=10,
            title="Candidate Score Distribution"
        )

        analytics_chart.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            height=450
        )

        st.plotly_chart(
            analytics_chart,
            use_container_width=True,
            key="analytics_chart"
        )

        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FOOTER
# =========================

st.markdown("""
<hr>
<center>
<p style='color:gray'>
Built with ❤️ using Streamlit + Gemini AI
</p>
</center>
""", unsafe_allow_html=True)