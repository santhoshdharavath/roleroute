from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.learning import Module, Role, Topic
from app.models.progress import ProgressSnapshot, UserProgress
from app.models.user import User
from app.schemas.common import ModuleOut, RoleOut, SkillCoverage, SkillDefinition, SnapshotOut, TopicOut

STAGE_FOUNDATION = "Foundation Stage"
STAGE_BUILDING = "Building Stage"
STAGE_INTERNSHIP_READY = "Internship-Ready Stage"
STAGE_ADVANCED = "Advanced / Job-Readiness Direction"


def stage_for_score(score: float) -> str:
    if score <= 34:
        return STAGE_FOUNDATION
    if score <= 69:
        return STAGE_BUILDING
    if score <= 84:
        return STAGE_INTERNSHIP_READY
    return STAGE_ADVANCED


def completed_topic_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(UserProgress).filter(UserProgress.user_id == user_id, UserProgress.completed.is_(True)).all()
    return {row.topic_id for row in rows}


def role_topics(db: Session, role_id: int) -> list[Topic]:
    return (
        db.query(Topic)
        .join(Module, Topic.module_id == Module.id)
        .filter(Module.role_id == role_id)
        .order_by(Module.order_index, Topic.order_index)
        .all()
    )


def skill_mastery_map(role: Role, topics: list[Topic], completed_ids: set[int]) -> dict[str, float]:
    mastery: dict[str, float] = {}
    for skill in role.required_skills:
        skill_id = skill["id"]
        covering = [topic for topic in topics if skill_id in (topic.skill_tags or [])]
        if not covering:
            mastery[skill_id] = 0.0
            continue
        done = sum(1 for topic in covering if topic.id in completed_ids)
        mastery[skill_id] = done / len(covering)
    return mastery


def readiness_score(role: Role, mastery: dict[str, float]) -> float:
    total_weight = sum(float(skill["weight"]) for skill in role.required_skills)
    if total_weight <= 0:
        return 0.0
    weighted = sum(float(skill["weight"]) * mastery.get(skill["id"], 0.0) for skill in role.required_skills)
    return round((weighted / total_weight) * 100, 1)


def coverage_list(role: Role, mastery: dict[str, float]) -> list[SkillCoverage]:
    items: list[SkillCoverage] = []
    for skill in role.required_skills:
        value = round(mastery.get(skill["id"], 0.0), 3)
        if value >= 0.7:
            status = "strong"
        elif value > 0:
            status = "building"
        else:
            status = "missing"
        items.append(
            SkillCoverage(
                id=skill["id"],
                name=skill["name"],
                weight=float(skill["weight"]),
                mastery=value,
                status=status,
            )
        )
    return items


def skill_gaps(coverage: list[SkillCoverage]) -> list[SkillCoverage]:
    return [item for item in coverage if item.status != "strong"]


def to_role_out(role: Role) -> RoleOut:
    return RoleOut(
        id=role.id,
        name=role.name,
        description=role.description,
        required_skills=[SkillDefinition(**skill) for skill in role.required_skills],
        role_goal_threshold=role.role_goal_threshold,
    )


def to_topic_out(topic: Topic, completed_ids: set[int], completed_at: datetime | None = None) -> TopicOut:
    return TopicOut(
        id=topic.id,
        module_id=topic.module_id,
        title=topic.title,
        description=topic.description,
        skill_tags=topic.skill_tags,
        estimated_minutes=topic.estimated_minutes,
        order_index=topic.order_index,
        completed=topic.id in completed_ids,
        completed_at=completed_at,
    )


def next_topic(topics: list[Topic], completed_ids: set[int]) -> Topic | None:
    for topic in topics:
        if topic.id not in completed_ids:
            return topic
    return None


def module_progress(db: Session, role_id: int, completed_ids: set[int]) -> list[ModuleOut]:
    modules = db.query(Module).filter(Module.role_id == role_id).order_by(Module.order_index).all()
    result: list[ModuleOut] = []
    for module in modules:
        topics = db.query(Topic).filter(Topic.module_id == module.id).order_by(Topic.order_index).all()
        topic_out = [to_topic_out(topic, completed_ids) for topic in topics]
        result.append(
            ModuleOut(
                id=module.id,
                role_id=module.role_id,
                title=module.title,
                description=module.description,
                order_index=module.order_index,
                topics=topic_out,
                completed_count=sum(1 for item in topic_out if item.completed),
                total_count=len(topic_out),
            )
        )
    return result


def snapshot_history(db: Session, user_id: int) -> list[SnapshotOut]:
    rows = (
        db.query(ProgressSnapshot)
        .filter(ProgressSnapshot.user_id == user_id)
        .order_by(ProgressSnapshot.recorded_at.asc())
        .all()
    )
    return [SnapshotOut(readiness_score=row.readiness_score, recorded_at=row.recorded_at) for row in rows]


def record_snapshot_if_changed(db: Session, user_id: int, score: float) -> None:
    latest = (
        db.query(ProgressSnapshot)
        .filter(ProgressSnapshot.user_id == user_id)
        .order_by(ProgressSnapshot.recorded_at.desc())
        .first()
    )
    if latest is not None and abs(latest.readiness_score - score) < 0.05:
        return
    db.add(ProgressSnapshot(user_id=user_id, readiness_score=score, recorded_at=datetime.now(timezone.utc)))


def goal_status(
    score: float,
    threshold: int,
    target: date | None,
    remaining_topics: int,
    recent_completions: int,
) -> tuple[str, str]:
    if target is None:
        return (
            "Medium",
            "Set a target date so RoleRoute can estimate whether your current pace is likely to reach internship-ready status in time. This is a goal likelihood indicator, not a guarantee.",
        )

    days_left = (target - date.today()).days
    remaining = max(remaining_topics, 0)

    if remaining == 0 or score >= threshold:
        return (
            "High",
            f"Based on current progress, your Role Readiness Score is {score:.0f} against a {threshold} internship-ready threshold. Keep reviewing weaker skills so the score stays meaningful.",
        )

    if days_left <= 0:
        return (
            "Low",
            "Your target date has already passed while remaining topics are still open. Choose a more realistic date or complete several topics this week. This is an estimated goal status, not a probability.",
        )

    weeks_left = max(days_left / 7, 0.1)
    needed_per_week = remaining / weeks_left
    recent_per_week = recent_completions  # completions in last 7 days

    if recent_per_week >= needed_per_week or (score >= threshold * 0.85 and needed_per_week <= 2):
        status = "High"
        pace_note = "you appear on track"
    elif recent_per_week >= needed_per_week * 0.5 or needed_per_week <= 3:
        status = "Medium"
        pace_note = "you need stronger consistency"
    else:
        status = "Low"
        pace_note = "you likely need a faster pace or a later date"

    needed_display = max(1, round(needed_per_week))
    return (
        status,
        (
            f"At your current pace, {pace_note} to reach a {threshold} readiness threshold by {target.isoformat()}. "
            f"You have about {days_left} days and {remaining} topics remaining — roughly {needed_display} topic"
            f"{'s' if needed_display != 1 else ''} per week. This is a readiness trajectory estimate based on current progress, not a guaranteed outcome."
        ),
    )


def recent_completion_count(db: Session, user_id: int, days: int = 7) -> int:
    start = datetime.now(timezone.utc) - timedelta(days=days)
    return (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.completed.is_(True),
            UserProgress.completed_at.is_not(None),
            UserProgress.completed_at >= start,
        )
        .count()
    )


def compute_progress(db: Session, user: User) -> dict:
    if user.selected_role_id is None:
        return {
            "role": None,
            "topics": [],
            "completed_ids": set(),
            "score": 0.0,
            "coverage": [],
            "next": None,
        }

    role = db.get(Role, user.selected_role_id)
    topics = role_topics(db, role.id)
    completed_ids = completed_topic_ids(db, user.id)
    mastery = skill_mastery_map(role, topics, completed_ids)
    score = readiness_score(role, mastery)
    coverage = coverage_list(role, mastery)
    upcoming = next_topic(topics, completed_ids)
    return {
        "role": role,
        "topics": topics,
        "completed_ids": completed_ids,
        "score": score,
        "coverage": coverage,
        "next": upcoming,
        "mastery": mastery,
    }
