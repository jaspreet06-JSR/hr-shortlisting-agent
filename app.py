import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
from datetime import datetime
from fpdf import FPDF

from scoring.rubric_scorer import evaluate_candidate
from parsers.pdf_parser import extract_text_from_pdf
from scoring.matcher import match_skills
# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="HR Resume Shortlisting Agent",
    page_icon="📄",
    layout="wide"
)

# =========================================================
# CACHE
# =========================================================

@st.cache_data
def cached_match_skills(jd_skills, resume_text):
    return match_skills(jd_skills, resume_text)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

* {
    transition:none !important;
    animation:none !important;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 95%;
}

.main {
    background: linear-gradient(
        180deg,
        #020617,
        #071028
    );
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #071028,
        #0b1735
    );
    border-right:1px solid rgba(255,255,255,0.05);
    width:260px !important;
}

h1,h2,h3,h4,h5 {
    color:white;
}

.card {
    background: rgba(15,23,42,0.85);
    border-radius:20px;
    padding:18px;
    border:1px solid rgba(255,255,255,0.05);
    margin-bottom:15px;
}

.metric-card {
    background: linear-gradient(
        135deg,
        #111827,
        #0f172a
    );

    border-radius:18px;
    padding:18px;
    text-align:center;

    border:1px solid rgba(255,255,255,0.05);
}

.skill-pill {
    display:inline-block;

    padding:8px 14px;

    margin:4px;

    border-radius:12px;

    font-size:14px;

    font-weight:600;

    color:white;

    border:1px solid rgba(255,255,255,0.08);
}

.match-pill {
    background: linear-gradient(
        135deg,
        #134e4a,
        #115e59
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

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Recruiter Settings")

min_score = st.sidebar.slider(
    "Minimum Match Score",
    0,
    100,
    50
)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<h1>📄 HR Resume Shortlisting Agent</h1>

<p style='color:#94a3b8;font-size:15px;'>
AI Powered Candidate Screening Dashboard
</p>
""", unsafe_allow_html=True)

# =========================================================
# FILE UPLOADS
# =========================================================

jd_file = st.file_uploader(
    "Upload Job Description",
    type=["pdf"]
)

resume_files = st.file_uploader(
    "Upload Candidate Resumes",
    type=["pdf"],
    accept_multiple_files=True
)

linkedin_text = st.text_area(
    "🔗 Optional LinkedIn / Portfolio Text",
    placeholder="Paste LinkedIn summary, portfolio description, GitHub bio, achievements, etc.",
    height=120
)

# =========================================================
# MAIN APP
# =========================================================

if jd_file and resume_files:

    # =====================================================
    # JD PROCESSING
    # =====================================================

    jd_text = extract_text_from_pdf(jd_file)

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

    with st.expander("📌 Extracted Job Description"):
        st.text_area(
            "JD Text",
            jd_text,
            height=180
        )

    st.subheader("🧠 JD Skills Required")

    jd_html = ""

    for skill in jd_skills:

        jd_html += f"""
        <span class="skill-pill match-pill">
        {skill}
        </span>
        """

    st.markdown(jd_html, unsafe_allow_html=True)

    st.divider()

    # =====================================================
    # PROCESS ALL RESUMES
    # =====================================================

    processed_candidates = []

    for resume_file in resume_files:

        resume_text = extract_text_from_pdf(
            resume_file
        )

        if linkedin_text:
            resume_text += f"\n{linkedin_text}"

        matched_skills, missing_skills, score = match_skills(
            jd_skills,
            resume_text,
        )
        rubric_result = evaluate_candidate(
            jd_skills,
            matched_skills,
            resume_text,
            jd_text
        )
        final_score = rubric_result["total_score"]
        profile_bonus = 0
        achievement_keywords = [
            "open source",
            "leadership",
            "hackathon",
            "research",
            "published",
            "github",
            "portfolio",
            "team lead",
            "internship",
            "certification"
        ]
        linkedin_lower = linkedin_text.lower() if linkedin_text else ""

        bonus_hits = sum(
            1 for keyword in achievement_keywords
            if keyword in linkedin_lower
        )

        profile_bonus = min(bonus_hits * 1.5, 10)

        final_score += profile_bonus

        final_score = min(final_score, 100)
        dimension_scores = rubric_result["scores"]
        justifications = rubric_result["justifications"]

        if score < min_score:
            continue

        recommendation = (
            "Strong Hire" if final_score >= 85 else
            "Hire" if final_score >= 70 else
            "Consider" if final_score >= 50 else
            "Reject"
        )

        processed_candidates.append({
            "name": resume_file.name,
            "resume_text": resume_text,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "score": score,
            "final_score": final_score,
            "recommendation": recommendation,
            "dimension_scores": dimension_scores,
            "justifications": justifications
        })

    if not processed_candidates:
        st.warning("No candidates match the selected threshold.")
        st.stop()

    # =====================================================
    # SELECT CANDIDATE
    # =====================================================

    candidate_names = [
        c["name"] for c in processed_candidates
    ]

    selected_candidate_name = st.selectbox(
        "Select Candidate",
        candidate_names
    )

    selected_candidate = next(
        c for c in processed_candidates
        if c["name"] == selected_candidate_name
    )

    matched_skills = selected_candidate["matched_skills"]
    missing_skills = selected_candidate["missing_skills"]
    score = selected_candidate["score"]
    final_score = selected_candidate["final_score"]
    recommendation = selected_candidate["recommendation"]
    dimension_scores = selected_candidate["dimension_scores"]
    justifications = selected_candidate["justifications"]
    resume_text = selected_candidate["resume_text"]

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3 = st.tabs([
        "📄 Candidate",
        "🏆 Leaderboard",
        "📊 Analytics"
    ])

    # =====================================================
    # TAB 1
    # =====================================================

    with tab1:

        st.markdown(f"""
        <div class="card">
        <h2>👤 {selected_candidate_name}</h2>
        </div>
        """, unsafe_allow_html=True)

        # =================================================
        # METRICS
        # =================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Final Score", f"{final_score:.2f}%")

        with col2:
            st.metric("Matched Skills", len(matched_skills))

        with col3:
            st.metric("Recommendation", recommendation)

        with col4:
            st.metric("Profile Bonus", f"{profile_bonus:.1f} pts")    

        st.divider()

        st.markdown("### 📊 Rubric Evaluation")

        rubric_data = {
            "Dimension": [
                "Skills Match",
                "Experience Relevance",
                "Education & Certs",
                "Projects",
                "Communication"
            ],
            "Score (/10)": [
                dimension_scores["skills"],
                dimension_scores["experience"],
                dimension_scores["education"],
                dimension_scores["projects"],
                dimension_scores["communication"]
            ],
            "Justification": [
                justifications["skills"],
                justifications["experience"],
                justifications["education"],
                justifications["projects"],
                justifications["communication"]
            ]
        }

        rubric_df = pd.DataFrame(rubric_data)

        st.dataframe(
            rubric_df,
            use_container_width=True
        )
        st.markdown("### 👨‍💼 Recruiter Override")

        override_decision = st.selectbox(
            "Recruiter Decision",
            [
                "Strong Hire",
                "Hire",
                "Consider",
                "Reject"
            ],
            index=2,
            key=f"decision_{candidate_names}"
        )

        recruiter_notes = st.text_area(
            "Recruiter Notes",
            placeholder="Add recruiter feedback or override reason...",
            key=f"notes_{candidate_names}"
        )

        if st.button(
           f"Save Recruiter Review - {candidate_names}",
           key=f"save_review_{candidate_names}"
        ):

            review_data = {
                "candidate": candidate_names,
                "ai_recommendation": recommendation,
                "recruiter_decision": override_decision,
                "score": final_score,
                "notes": recruiter_notes,
                "timestamp": str(datetime.now())
            }

            filename = f"recruiter_logs/{candidate_names.replace(' ', '_')}.json"

            with open(filename, "w") as f:
                json.dump(review_data, f, indent=4)

            st.success("Recruiter review saved successfully.")

            with open(filename, "r") as f:
                st.download_button(
                    label="⬇ Download Review JSON",
                    data=f,
                    file_name=f"{candidate_names.replace(' ', '_')}_review.json",
                    mime="application/json",
                    key=f"download_review_{candidate_names}"
                )

        # =================================================
        # SKILLS
        # =================================================

        col4, col5 = st.columns(2)

        with col4:

            st.subheader("✅ Matched Skills")

            matched_html = ""

            for skill in matched_skills:

                matched_html += f"""
                <span class="skill-pill match-pill">
                {skill}
                </span>
                """

            st.markdown(
                matched_html,
                unsafe_allow_html=True
            )

        with col5:

            st.subheader("❌ Missing Skills")

            missing_html = ""

            for skill in missing_skills:

                missing_html += f"""
                <span class="skill-pill missing-pill">
                {skill}
                </span>
                """

            st.markdown(
                missing_html,
                unsafe_allow_html=True
            )

        st.divider()

        # =================================================
        # CHARTS
        # =================================================

        col6, col7 = st.columns(2)

        # PIE CHART

        with col6:

            pie_chart = px.pie(
                names=["Matched", "Missing"],
                values=[
                    len(matched_skills),
                    len(missing_skills)
                ],
                hole=0.6
            )

            pie_chart.update_layout(
                template="plotly_dark",
                height=220,
                width=420,
                autosize=False,
                margin=dict(
                    l=10,
                    r=10,
                    t=30,
                    b=10
                )
            )

            st.plotly_chart(
                pie_chart,
                config={
                    "displayModeBar": False
                },
                key="pie_chart"
            )

        # RADAR CHART

        with col7:

            radar_labels = jd_skills.copy()

            radar_values = []

            for skill in radar_labels:

                if skill in matched_skills:
                    radar_values.append(1)
                else:
                    radar_values.append(0)

            radar_values.append(radar_values[0])
            radar_labels.append(radar_labels[0])

            radar_chart = go.Figure()

            radar_chart.add_trace(
                go.Scatterpolar(
                    r=radar_values,
                    theta=radar_labels,
                    fill='toself'
                )
            )

            radar_chart.update_layout(
                template="plotly_dark",
                showlegend=False,
                height=220,
                width=420,
                autosize=False,
                margin=dict(
                    l=10,
                    r=10,
                    t=30,
                    b=10
                ),
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0,1]
                    )
                )
            )

            st.plotly_chart(
                radar_chart,
                config={
                    "displayModeBar": False
                },
                key="radar_chart"
            )

        st.divider()

        st.markdown("### 🧑‍💼 Recruiter Review")

        review_col1, review_col2 = st.columns([1, 2])

        with review_col1:
            recruiter_decision = st.selectbox(
                "Decision",
                ["Shortlist", "Hold", "Reject"],
                key=f"decision_{selected_candidate_name}"
            )

        with review_col2:
            recruiter_notes = st.text_area(
                "Recruiter Notes",
                placeholder="Add recruiter comments here...",
                key=f"notes_{selected_candidate_name}"
            )

        save_review = st.button(
            "💾 Save Review",
            key=f"save_review_{selected_candidate_name}"
        )

        if save_review:

            review_data = {
                "candidate": selected_candidate_name,
                "score": round(final_score, 2),
                "decision": recruiter_decision,
                "notes": recruiter_notes,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            log_path = f"recruiter_logs/{selected_candidate_name}.json"

            with open(log_path, "w") as f:
                json.dump(review_data, f, indent=4)

            st.success("Recruiter review saved successfully.")

        # =================================================
        # PDF REPORT
        # =================================================

        pdf = FPDF()

        pdf.add_page()

        pdf.set_font(
            "Arial",
            size=16
        )

        pdf.cell(
            200,
            10,
            txt="Candidate Report",
            ln=True
        )

        pdf.ln(5)

        pdf.set_font(
            "Arial",
            size=12
        )

        pdf.cell(
            200,
            10,
            txt=f"Candidate: {selected_candidate_name}",
            ln=True
        )

        pdf.cell(
            200,
            10,
            txt=f"Score: {score:.1f}%",
            ln=True
        )

        pdf.ln(4)

        matched_text = ", ".join(
            matched_skills
        )

        missing_text = ", ".join(
            missing_skills
        )

        pdf.multi_cell(
            180,
            8,
            f"Matched Skills: {matched_text}"
        )

        pdf.ln(2)

        pdf.multi_cell(
            180,
            8,
            f"Missing Skills: {missing_text}"
        )

        pdf_output = bytes(
            pdf.output(dest='S')
        )

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_output,
            file_name=f"{selected_candidate_name}.pdf",
            mime="application/pdf"
        )

        # =================================================
        # RESUME TEXT
        # =================================================

        with st.expander("View Resume Text"):
            st.text_area(
                "Resume",
                resume_text,
                height=200
            )

    # =====================================================
    # TAB 2
    # =====================================================

    with tab2:

        leaderboard = []

        for candidate in processed_candidates:

            leaderboard.append({
                "Candidate": candidate["name"],
                "Score": candidate["score"],
                "Matched Skills":
                    ", ".join(candidate["matched_skills"]),
                "Missing Skills":
                    ", ".join(candidate["missing_skills"])
            })

        leaderboard_df = pd.DataFrame(
            leaderboard
        )

        leaderboard_df = leaderboard_df.sort_values(
            by="Score",
            ascending=False
        )

        st.subheader("🏆 Candidate Leaderboard")

        st.dataframe(
            leaderboard_df,
            use_container_width=True
        )

        ranking_chart = px.bar(
            leaderboard_df,
            x="Candidate",
            y="Score"
        )

        ranking_chart.update_layout(
            template="plotly_dark",
            height=300,
            autosize=False,
            margin=dict(
                l=10,
                r=10,
                t=30,
                b=10
            )
        )

        st.plotly_chart(
            ranking_chart,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
            key="ranking_chart"
        )

        csv = leaderboard_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "📥 Export CSV",
            csv,
            "leaderboard.csv",
            "text/csv"
        )

        st.divider()

        st.markdown("## 📂 Recruiter Decision Logs")

        # Ensure recruiter_logs directory exists
        if not os.path.exists("recruiter_logs"):
            os.makedirs("recruiter_logs")

        log_files = os.listdir("recruiter_logs")

        if log_files:

            for log_file in log_files:

                with open(f"recruiter_logs/{log_file}", "r") as f:
                    data = json.load(f)

                with st.expander(f"📄 {data['candidate']}"):

                   st.write(f"**Decision:** {data['decision']}")
                   st.write(f"**Score:** {data['score']}")
                   st.write(f"**Notes:** {data['notes']}")
                   st.write(f"**Timestamp:** {data['timestamp']}")

        else:
            st.info("No recruiter logs available.")

    # =====================================================
    # TAB 3
    # =====================================================

    with tab3:

        analytics_df = leaderboard_df

        col8, col9, col10 = st.columns(3)

        with col8:
            st.metric(
                "Average Score",
                f"{analytics_df['Score'].mean():.1f}%"
            )

        with col9:
            st.metric(
                "Top Score",
                f"{analytics_df['Score'].max():.1f}%"
            )

        with col10:
            st.metric(
                "Candidates",
                len(analytics_df)
            )

        analytics_chart = px.histogram(
            analytics_df,
            x="Score"
        )

        analytics_chart.update_layout(
            template="plotly_dark",
            height=300,
            autosize=False,
            margin=dict(
                l=10,
                r=10,
                t=30,
                b=10
            )
        )

        st.plotly_chart(
            analytics_chart,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
            key="analytics_chart"
        )