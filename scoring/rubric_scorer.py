import re


def extract_experience_years(text):
    text = text.lower()

    patterns = [
        r"(\d+)\+?\s+years",
        r"experience\s+of\s+(\d+)",
        r"(\d+)\s+yrs"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    return 0


def score_skills(jd_skills, matched_skills):
    if not jd_skills:
        return 0, "No JD skills found"

    match_percent = (len(matched_skills) / len(jd_skills)) * 100

    if match_percent >= 85:
        score = 10
    elif match_percent >= 50:
        score = 7
    elif match_percent >= 30:
        score = 5
    else:
        score = 2

    justification = f"{len(matched_skills)} out of {len(jd_skills)} required skills matched."

    return score, justification


def score_experience(resume_text, jd_text):
    resume_exp = extract_experience_years(resume_text)
    jd_exp = extract_experience_years(jd_text)

    if resume_exp >= jd_exp and resume_exp > 0:
        score = 10
        justification = f"Candidate has {resume_exp} years experience matching JD requirement."
    elif resume_exp >= max(1, jd_exp - 1):
        score = 7
        justification = "Candidate has relevant adjacent experience."
    elif resume_exp > 0:
        score = 5
        justification = "Candidate has limited relevant experience."
    else:
        score = 2
        justification = "No clear relevant experience found."

    return score, justification


def score_education(resume_text):
    text = resume_text.lower()

    keywords = [
        "b.tech",
        "m.tech",
        "bachelor",
        "master",
        "phd",
        "certification",
        "aws",
        "google certified"
    ]

    found = sum(1 for k in keywords if k in text)

    if found >= 4:
        score = 10
        justification = "Strong educational background with certifications."
    elif found >= 2:
        score = 7
        justification = "Meets educational requirements."
    elif found >= 1:
        score = 5
        justification = "Basic education qualifications found."
    else:
        score = 2
        justification = "No strong educational qualifications detected."

    return score, justification


def score_projects(resume_text):
    text = resume_text.lower()

    project_keywords = [
        "project",
        "github",
        "portfolio",
        "developed",
        "built",
        "implemented",
        "deployed"
    ]

    found = sum(1 for k in project_keywords if k in text)

    if found >= 5:
        score = 10
        justification = "Strong portfolio/projects detected."
    elif found >= 3:
        score = 7
        justification = "Relevant projects found."
    elif found >= 1:
        score = 5
        justification = "Some project exposure found."
    else:
        score = 2
        justification = "No strong project evidence detected."

    return score, justification


def score_communication(resume_text):
    word_count = len(resume_text.split())

    grammar_score = 10

    if word_count < 150:
        grammar_score = 4
    elif word_count < 300:
        grammar_score = 6
    elif word_count < 600:
        grammar_score = 8

    if grammar_score >= 8:
        justification = "Resume is clear and well-structured."
    elif grammar_score >= 6:
        justification = "Resume communication is acceptable."
    else:
        justification = "Resume lacks proper structure or detail."

    return grammar_score, justification


def calculate_total_score(scores):
    weighted_total = (
        scores["skills"] * 0.30 +
        scores["experience"] * 0.25 +
        scores["education"] * 0.15 +
        scores["projects"] * 0.20 +
        scores["communication"] * 0.10
    )

    return round(weighted_total * 10, 2)


def evaluate_candidate(
    jd_skills,
    matched_skills,
    resume_text,
    jd_text
):

    skills_score, skills_just = score_skills(
        jd_skills,
        matched_skills
    )

    exp_score, exp_just = score_experience(
        resume_text,
        jd_text
    )

    edu_score, edu_just = score_education(
        resume_text
    )

    project_score, project_just = score_projects(
        resume_text
    )

    comm_score, comm_just = score_communication(
        resume_text
    )

    scores = {
        "skills": skills_score,
        "experience": exp_score,
        "education": edu_score,
        "projects": project_score,
        "communication": comm_score
    }

    total_score = calculate_total_score(scores)

    if total_score >= 80:
        recommendation = "Strong Hire"
    elif total_score >= 60:
        recommendation = "Consider"
    else:
        recommendation = "Reject"

    return {
        "scores": scores,
        "justifications": {
            "skills": skills_just,
            "experience": exp_just,
            "education": edu_just,
            "projects": project_just,
            "communication": comm_just
        },
        "total_score": total_score,
        "recommendation": recommendation
    }