# 🚀 HR Resume Shortlisting Agent

AI-powered recruitment assistant that automates resume screening, candidate ranking, recruiter evaluation, and analytics visualization.

---

# 📌 Features

## ✅ Job Description Parsing
- Extracts skills and requirements from JD PDFs
- Detects technical skills automatically

## ✅ Resume Parsing
- Supports multiple resume uploads
- PDF resume extraction
- Candidate skill analysis

## ✅ AI Candidate Evaluation
Uses a 5-dimension evaluation rubric:

| Dimension | Weight |
|---|---|
| Skills Match | 30% |
| Experience Relevance | 25% |
| Education & Certifications | 15% |
| Projects & Portfolio | 20% |
| Communication Quality | 10% |

---

# 📊 Dashboard Features

## Candidate Dashboard
- Match percentage
- Matched skills
- Missing skills
- AI recommendation
- Radar charts
- Pie charts

## Recruiter Analytics
- Candidate leaderboard
- Score distribution
- Recruiter override system
- Export CSV reports
- Downloadable recruiter reviews

---

# 🧠 AI Features

- Resume semantic evaluation
- Skill matching
- Rule-based scoring engine
- Recruiter override support
- AI recommendation generation

---

# 🔒 Security Measures

## API Key Protection
- API keys stored using `.env`
- No hardcoded credentials

## Prompt Injection Mitigation
- User inputs sanitized before AI processing
- Structured prompts reduce injection risks

## Hallucination Reduction
- Scores generated using deterministic rubric system
- Rule-based validation added

## PII Protection
- Resume data processed temporarily
- No permanent storage of sensitive candidate data

## Secure Recruiter Reviews
- Recruiter logs stored locally as JSON
- No external sharing of candidate information

---

# 🏗️ Architecture

## Workflow

1. Upload Job Description
2. Extract JD skills
3. Upload candidate resumes
4. Parse resume text
5. Match candidate skills
6. Run AI rubric evaluation
7. Generate recruiter analytics
8. Export reports

---

# ⚙️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| Charts | Plotly |
| AI | Gemini API |
| Data Processing | Pandas |
| PDF Reports | FPDF |
| Deployment | Streamlit Cloud |

---

# 📈 Visualizations

- Radar Charts
- Pie Charts
- Leaderboard Analytics
- Score Distribution
- Candidate Ranking

---

# 📂 Project Structure

```bash
hr-shortlisting-agent/
│
├── app.py
├── .env
├── requirements.txt
│
├── parsers/
│   ├── pdf_parser.py
│   └── llm_parser.py
│
├── scoring/
│   ├── matcher.py
│   ├── ai_scorer.py
│   └── rubric_scorer.py
│
├── recruiter_logs/
├── reports/
└── README.md
```

---

# 🚀 Local Setup

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Add Environment Variables

Create `.env`

```env
GOOGLE_API_KEY=your_api_key_here
```

## Run Application

```bash
streamlit run app.py
```

---

# ☁️ Deployment

Deployed using Streamlit Cloud.

---

# 📌 Future Improvements

- LinkedIn profile parsing
- LangChain integration
- Semantic embedding search
- Vector database integration
- Interview scheduling AI
- ATS integration

---

# 👨‍💻 Author

Developed as an AI-powered HR recruitment automation system internship project.