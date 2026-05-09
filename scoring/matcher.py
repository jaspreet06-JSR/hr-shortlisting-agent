def match_skills(jd_skills, resume_text):

    if resume_text is None:
        resume_text = ""

    resume_text = str(resume_text).lower()

    matched_skills = []
    missing_skills = []

    for skill in jd_skills:

        if skill.lower() in resume_text:
            matched_skills.append(skill)

        else:
            missing_skills.append(skill)

    total_skills = len(jd_skills)

    if total_skills == 0:
        score = 0

    else:
        score = (len(matched_skills) / total_skills) * 100

    return matched_skills, missing_skills, score