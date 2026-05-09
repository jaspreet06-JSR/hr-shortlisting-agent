def match_skills(text, skills_db):

    detected_skills = []

    text = text.lower()

    for skill in skills_db:

        if skill.lower() in text:
            detected_skills.append(skill)

    return detected_skills