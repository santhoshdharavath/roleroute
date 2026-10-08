from sqlalchemy.orm import Session

from app.models.internship import Internship
from app.models.learning import Role
from app.schemas.common import InternshipOut, SkillCoverage


def _skill_name(role: Role, skill_id: str) -> str:
    for skill in role.required_skills:
        if skill["id"] == skill_id:
            return skill["name"]
    return skill_id.replace("-", " ").title()


def internship_fit(
    internship: Internship,
    role: Role,
    coverage: list[SkillCoverage],
    next_topic_title: str | None,
) -> InternshipOut:
    mastery = {item.id: item.mastery for item in coverage}
    required = list(internship.required_skills)
    matched = [skill_id for skill_id in required if mastery.get(skill_id, 0) > 0]
    missing = [skill_id for skill_id in required if mastery.get(skill_id, 0) <= 0]
    fit_score = round((len(matched) / len(required)) * 100, 1) if required else 0.0

    missing_names = [_skill_name(role, skill_id) for skill_id in missing]
    if missing:
        if next_topic_title:
            recommendation = (
                f"You currently match {fit_score:.0f}% of this internship. "
                f"Complete {next_topic_title} next, then close gaps in {', '.join(missing_names)}."
            )
        else:
            recommendation = (
                f"You currently match {fit_score:.0f}% of this internship. "
                f"Strengthen {', '.join(missing_names)} to improve your fit."
            )
    else:
        recommendation = (
            f"You currently match {fit_score:.0f}% of the listed skills for this internship. "
            "Review the posting details and keep practicing weaker topics so the match stays honest."
        )

    return InternshipOut(
        id=internship.id,
        title=internship.title,
        company=internship.company,
        location=internship.location,
        work_mode=internship.work_mode,
        description=internship.description,
        required_skills=required,
        application_url=internship.application_url,
        is_demo_data=internship.is_demo_data,
        fit_score=fit_score,
        matched_skills=matched,
        missing_skills=missing,
        recommendation=recommendation,
    )


def internships_for_role(
    db: Session,
    role: Role,
    coverage: list[SkillCoverage],
    next_topic_title: str | None,
) -> list[InternshipOut]:
    rows = db.query(Internship).filter(Internship.role_id == role.id).order_by(Internship.id).all()
    ranked = [internship_fit(row, role, coverage, next_topic_title) for row in rows]
    return sorted(ranked, key=lambda item: item.fit_score, reverse=True)
