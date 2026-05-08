def extract_skills(text, skills_list):
    text = text.lower()

    found_skills = []

    for skill in skills_list:
        if skill.lower() in text:
            found_skills.append(skill)

    return found_skills


def calculate_match(jd_skills, resume_skills):
    matched = list(set(jd_skills) & set(resume_skills))

    missing = list(set(jd_skills) - set(resume_skills))

    if len(jd_skills) == 0:
        score = 0
    else:
        score = (len(matched) / len(jd_skills)) * 100

    return {
        "matched": matched,
        "missing": missing,
        "score": round(score, 2)
    }