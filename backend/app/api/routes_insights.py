from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_settings, get_demo_user
from app.core.config import Settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ChatRequest, ChatResponse, InternshipListOut, PredictionsOut
from app.services.internships import internships_for_role
from app.services.sam import build_student_context, generate_sam_reply
from app.services.scoring import (
    compute_progress,
    goal_status,
    recent_completion_count,
    skill_gaps,
    stage_for_score,
    to_topic_out,
)

router = APIRouter(tags=["insights"])

DISCLAIMER = (
    "Role Readiness, internship fit, and goal status are estimates based on completed learning topics. "
    "They are not scientifically validated predictions and do not guarantee internships, jobs, or placements."
)


@router.get("/predictions", response_model=PredictionsOut)
def get_predictions(
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
    settings: Settings = Depends(current_settings),
) -> PredictionsOut:
    state = _require_role_state(db, user)
    role = state["role"]
    upcoming = state["next"]
    remaining = len(state["topics"]) - len(state["completed_ids"])
    status, explanation = goal_status(
        state["score"],
        role.role_goal_threshold,
        user.target_date,
        remaining,
        recent_completion_count(db, user.id),
    )
    improves = []
    if upcoming:
        names = {item["id"]: item["name"] for item in role.required_skills}
        improves = [names[tag] for tag in upcoming.skill_tags if tag in names]

    actions = []
    if upcoming:
        actions.append(f"Complete the next topic: {upcoming.title}.")
    gaps = skill_gaps(state["coverage"])
    if gaps:
        actions.append(f"Spend extra time on {gaps[0].name}, which is still weaker than the role target.")
    actions.append("Ask SAM to explain any concept before you mark the topic complete.")

    return PredictionsOut(
        readiness_score=state["score"],
        stage=stage_for_score(state["score"]),
        role_goal_threshold=role.role_goal_threshold,
        skill_coverage=state["coverage"],
        skill_gaps=gaps,
        next_topic=to_topic_out(upcoming, state["completed_ids"]) if upcoming else None,
        next_topic_improves=improves,
        goal_status=status,
        goal_explanation=explanation,
        suggested_actions=actions,
        disclaimer=DISCLAIMER,
        demo_mode=not settings.llm_configured,
    )


@router.get("/internships", response_model=InternshipListOut)
def list_internships(
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
) -> InternshipListOut:
    state = _require_role_state(db, user)
    role = state["role"]
    upcoming = state["next"]
    items = internships_for_role(db, role, state["coverage"], upcoming.title if upcoming else None)
    return InternshipListOut(
        internships=items,
        is_sample_data=True,
        disclaimer="These are curated demo opportunities, not live job-board listings. " + DISCLAIMER,
    )


@router.post("/chat", response_model=ChatResponse)
def chat_with_sam(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
    settings: Settings = Depends(current_settings),
) -> ChatResponse:
    state = compute_progress(db, user)
    role = state["role"]
    internships = internships_for_role(db, role, state["coverage"], state["next"].title if state["next"] else None) if role else []
    completed_titles = [topic.title for topic in state["topics"] if topic.id in state["completed_ids"]]
    context = build_student_context(
        user=user,
        role=role,
        score=state["score"],
        stage=stage_for_score(state["score"]),
        next_topic=state["next"],
        coverage=state["coverage"],
        internships=internships,
        completed_titles=completed_titles,
    )
    reply, demo_mode = generate_sam_reply(
        settings=settings,
        message=payload.message,
        context=context,
        role=role,
        next_topic=state["next"],
        score=state["score"],
    )
    return ChatResponse(reply=reply, demo_mode=demo_mode)


def _require_role_state(db: Session, user: User) -> dict:
    if user.selected_role_id is None:
        raise HTTPException(status_code=400, detail="Select a target role during onboarding first.")
    return compute_progress(db, user)
