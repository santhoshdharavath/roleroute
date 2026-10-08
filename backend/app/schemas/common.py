from datetime import date, datetime

from pydantic import BaseModel, Field


class SkillDefinition(BaseModel):
    id: str
    name: str
    weight: float


class SkillCoverage(BaseModel):
    id: str
    name: str
    weight: float
    mastery: float
    status: str


class TopicOut(BaseModel):
    id: int
    module_id: int
    title: str
    description: str
    skill_tags: list[str]
    estimated_minutes: int
    order_index: int
    completed: bool = False
    completed_at: datetime | None = None


class ModuleOut(BaseModel):
    id: int
    role_id: int
    title: str
    description: str
    order_index: int
    topics: list[TopicOut]
    completed_count: int
    total_count: int


class RoleOut(BaseModel):
    id: int
    name: str
    description: str
    required_skills: list[SkillDefinition]
    role_goal_threshold: int


class RolePathOut(BaseModel):
    role: RoleOut
    modules: list[ModuleOut]
    next_topic: TopicOut | None = None


class OnboardingRequest(BaseModel):
    role_id: int
    target_date: date
    name: str | None = None


class OnboardingResponse(BaseModel):
    user_id: int
    name: str
    selected_role_id: int
    target_date: date


class CompleteTopicRequest(BaseModel):
    topic_id: int = Field(..., ge=1)


class SnapshotOut(BaseModel):
    readiness_score: float
    recorded_at: datetime


class ProgressSummaryOut(BaseModel):
    user_id: int
    selected_role: RoleOut | None
    target_date: date | None
    completed_count: int
    total_count: int
    readiness_score: float
    stage: str
    skill_coverage: list[SkillCoverage]
    skill_gaps: list[SkillCoverage]
    next_topic: TopicOut | None
    module_progress: list[ModuleOut]
    graph_history: list[SnapshotOut]
    demo_mode: bool


class PredictionsOut(BaseModel):
    readiness_score: float
    stage: str
    role_goal_threshold: int
    skill_coverage: list[SkillCoverage]
    skill_gaps: list[SkillCoverage]
    next_topic: TopicOut | None
    next_topic_improves: list[str]
    goal_status: str
    goal_explanation: str
    suggested_actions: list[str]
    disclaimer: str
    demo_mode: bool


class InternshipOut(BaseModel):
    id: int
    title: str
    company: str
    location: str
    work_mode: str
    description: str
    required_skills: list[str]
    application_url: str
    is_demo_data: bool
    fit_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    recommendation: str


class InternshipListOut(BaseModel):
    internships: list[InternshipOut]
    is_sample_data: bool
    disclaimer: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    reply: str
    demo_mode: bool
    assistant_name: str = "SAM — Skill Advancement Mentor"


class ResetResponse(BaseModel):
    success: bool
    message: str


class HealthOut(BaseModel):
    status: str
    app: str
    demo_mode: bool
    llm_configured: bool
