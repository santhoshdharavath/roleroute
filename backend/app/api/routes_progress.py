from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_settings, get_demo_user
from app.core.config import Settings
from app.db.session import get_db
from app.models.learning import Topic
from app.models.progress import ProgressSnapshot, UserProgress
from app.models.user import User
from app.schemas.common import (
    CompleteTopicRequest,
    OnboardingRequest,
    OnboardingResponse,
    ProgressSummaryOut,
    ResetResponse,
)
from app.services.scoring import (
    compute_progress,
    module_progress,
    record_snapshot_if_changed,
    skill_gaps,
    snapshot_history,
    stage_for_score,
    to_role_out,
    to_topic_out,
)

router = APIRouter(tags=["progress"])


@router.post("/onboarding", response_model=OnboardingResponse)
def save_onboarding(
    payload: OnboardingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
) -> OnboardingResponse:
    from app.models.learning import Role

    role = db.get(Role, payload.role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found.")
    if payload.target_date < date.today():
        raise HTTPException(status_code=400, detail="Target date should be today or later.")

    role_changed = user.selected_role_id != payload.role_id
    user.selected_role_id = payload.role_id
    user.target_date = payload.target_date
    if payload.name:
        user.name = payload.name

    if role_changed:
        db.query(UserProgress).filter(UserProgress.user_id == user.id).delete()
        db.query(ProgressSnapshot).filter(ProgressSnapshot.user_id == user.id).delete()
        record_snapshot_if_changed(db, user.id, 0.0)

    db.commit()
    db.refresh(user)
    return OnboardingResponse(
        user_id=user.id,
        name=user.name,
        selected_role_id=user.selected_role_id,
        target_date=user.target_date,
    )


@router.post("/progress/complete")
def complete_topic(
    payload: CompleteTopicRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
) -> dict:
    if user.selected_role_id is None:
        raise HTTPException(status_code=400, detail="Select a role before tracking progress.")

    topic = db.get(Topic, payload.topic_id)
    if topic is None or topic.module.role_id != user.selected_role_id:
        raise HTTPException(status_code=404, detail="Topic not found in the selected role path.")

    existing = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user.id, UserProgress.topic_id == topic.id)
        .first()
    )
    if existing is None:
        db.add(
            UserProgress(
                user_id=user.id,
                topic_id=topic.id,
                completed=True,
                completed_at=datetime.now(timezone.utc),
            )
        )
    else:
        existing.completed = True
        existing.completed_at = existing.completed_at or datetime.now(timezone.utc)

    state = compute_progress(db, user)
    record_snapshot_if_changed(db, user.id, state["score"])
    db.commit()
    return _summary_payload(db, user, current_settings())


@router.get("/progress/summary", response_model=ProgressSummaryOut)
def progress_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
    settings: Settings = Depends(current_settings),
) -> ProgressSummaryOut:
    return _summary_payload(db, user, settings)


@router.post("/demo/reset", response_model=ResetResponse)
def reset_demo(
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
    settings: Settings = Depends(current_settings),
) -> ResetResponse:
    db.query(UserProgress).filter(UserProgress.user_id == user.id).delete()
    db.query(ProgressSnapshot).filter(ProgressSnapshot.user_id == user.id).delete()
    user.selected_role_id = None
    user.target_date = None
    user.name = settings.demo_user_name
    db.commit()
    return ResetResponse(success=True, message="Demo progress was reset. Choose a role to start again.")


def _summary_payload(db: Session, user: User, settings: Settings) -> ProgressSummaryOut:
    state = compute_progress(db, user)
    role = state["role"]
    completed_ids = state["completed_ids"]
    modules = module_progress(db, role.id, completed_ids) if role else []
    upcoming = state["next"]
    history = snapshot_history(db, user.id)
    if not history and role:
        history = []

    return ProgressSummaryOut(
        user_id=user.id,
        selected_role=to_role_out(role) if role else None,
        target_date=user.target_date,
        completed_count=len(completed_ids),
        total_count=len(state["topics"]),
        readiness_score=state["score"],
        stage=stage_for_score(state["score"]),
        skill_coverage=state["coverage"],
        skill_gaps=skill_gaps(state["coverage"]),
        next_topic=to_topic_out(upcoming, completed_ids) if upcoming else None,
        module_progress=modules,
        graph_history=history,
        demo_mode=not settings.llm_configured,
    )
