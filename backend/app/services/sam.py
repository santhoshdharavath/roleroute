from __future__ import annotations

import httpx

from app.core.config import Settings
from app.models.learning import Role, Topic
from app.models.user import User
from app.schemas.common import InternshipOut, SkillCoverage

SAM_SYSTEM_PROMPT = (
    "You are SAM, the Skill Advancement Mentor inside RoleRoute. Your role is to help college students "
    "make structured, practical progress toward their selected career goal.\n\n"
    "You know the student’s target role, target date, current module, current topic, completed topics, "
    "role readiness score, skill coverage, missing skills, internship fit information, and recommended next topic.\n\n"
    "Explain concepts clearly using simple language and practical real-world examples. When relevant, connect "
    "every concept to the student’s chosen career role. Help the student understand why a topic matters, what "
    "they should learn next, and how completing a topic can improve their readiness.\n\n"
    "Give practical, concise guidance. Encourage consistency without making unrealistic promises. Be honest about "
    "uncertainty. Do not guarantee internships, jobs, salaries, placements, or career outcomes. Do not complete "
    "graded assignments dishonestly; instead, guide the student to understand the concepts and solve problems "
    "independently.\n\n"
    "Your goal is to help the student move from confusion to clear next actions."
)


def build_student_context(
    user: User,
    role: Role | None,
    score: float,
    stage: str,
    next_topic: Topic | None,
    coverage: list[SkillCoverage],
    internships: list[InternshipOut],
    completed_titles: list[str],
) -> str:
    if role is None:
        return (
            "The student has not selected a target role yet. Ask them to choose Data Analyst, "
            "Software Developer, or Machine Learning Engineer on the onboarding screen."
        )

    gaps = [item.name for item in coverage if item.status != "strong"]
    covered = [item.name for item in coverage if item.status == "strong"]
    next_title = next_topic.title if next_topic else "All topics in the current path are complete."
    target = user.target_date.isoformat() if user.target_date else "not set"
    top_fit = internships[0] if internships else None
    internship_line = (
        f"Top sample internship fit: {top_fit.title} at {top_fit.company} ({top_fit.fit_score:.0f}% match)."
        if top_fit
        else "No internship rows loaded."
    )
    completed = ", ".join(completed_titles[-8:]) if completed_titles else "none yet"

    return (
        f"Target role: {role.name}. Target date: {target}. Role Readiness Score: {score:.1f}/100 ({stage}). "
        f"Next recommended topic: {next_title}. Completed topics: {completed}. "
        f"Stronger skills: {', '.join(covered) or 'none yet'}. Weaker or missing skills: {', '.join(gaps) or 'none'}. "
        f"{internship_line} Internship listings are curated demo opportunities, not live job board results."
    )


def demo_reply(message: str, role: Role | None, next_topic: Topic | None, score: float) -> str:
    text = message.lower()
    role_name = role.name if role else "your selected role"
    next_title = next_topic.title if next_topic else "review weaker skills and internships"

    if "join" in text:
        return (
            "In SQL, a JOIN combines rows from two tables using a shared key. As a Data Analyst, you might join "
            "`orders` to `customers` so you can report revenue by city instead of only by order id. Start with INNER JOIN "
            "when you only want matching rows, then try LEFT JOIN when you still need customers with no orders. "
            f"Next action: complete {next_title} and write one query that answers a real business question."
        )
    if "rest" in text or "api" in text:
        return (
            "A REST API lets one program request data from another over HTTP. A Software Developer might expose "
            "`GET /internships` so the RoleRoute dashboard can show curated opportunities. You send a method and path, "
            "get JSON back, and handle status codes. Do not skip testing the unhappy path. "
            f"Next action: {next_title}."
        )
    if "statistic" in text:
        return (
            "Statistics helps a Data Analyst avoid overreacting to noise. If weekly signups jump, you check spread, "
            "sample size, and outliers before telling a manager that a campaign 'worked.' Completing statistics topics "
            f"raises your readiness because the role weights that skill. Next action: {next_title}."
        )
    if "missing" in text or "ml engineer" in text:
        return (
            f"For {role_name}, RoleRoute treats a skill as demonstrated only after you complete topics tagged with that skill. "
            "Open Predictions to see missing skills, then finish the next recommended topic instead of jumping around. "
            "Scores are learning-progress estimates, not hiring guarantees."
        )
    if "behind" in text or "this week" in text:
        return (
            f"If you are behind, pick a small recoverable plan: finish {next_title}, then one extra topic this week. "
            "Consistency beats a heroic all-nighter. Update your target date if it is no longer realistic. "
            "SAM will not promise an internship from a sprint."
        )
    if "internship" in text or "fit" in text:
        return (
            f"Internship fit is the share of that posting's required skills you have already demonstrated. "
            f"Your current Role Readiness Score is {score:.0f}. Complete {next_title} to raise coverage, then re-check "
            "Internships. Listings are curated demo opportunities."
        )
    if "next" in text or "study" in text:
        return (
            f"Study {next_title} next. It sits at the front of your unfinished sequence for {role_name}, so it is the "
            "clearest step toward higher readiness. After you mark it complete, the dashboard graph should move up if "
            "that topic covers a required skill."
        )
    if "help me reach" in text or "this topic" in text or "goal" in text:
        return (
            f"Each completed topic increases mastery for its skill tags. Those tags feed the weighted Role Readiness Score "
            f"for {role_name}. Completing {next_title} is the next measurable step. The goal status card estimates pace "
            "to your date; it is not a probability of getting hired."
        )

    return (
        f"I am SAM, your Skill Advancement Mentor. For {role_name}, your readiness is {score:.0f}/100. "
        f"The most useful next action is to complete {next_title}, then ask me about any concept that still feels fuzzy. "
        "I can explain ideas, skill gaps, and internship fit — I cannot guarantee jobs or placements."
    )


def _gemini_reply(settings: Settings, context: str, message: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    payload = {
        "system_instruction": {"parts": [{"text": SAM_SYSTEM_PROMPT}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"Student context:\n{context}\n\nStudent message:\n{message}"}],
            }
        ],
    }
    response = httpx.post(url, params={"key": settings.gemini_api_key}, json=payload, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(part.get("text", "") for part in parts).strip()


def _openai_reply(settings: Settings, context: str, message: str) -> str:
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": SAM_SYSTEM_PROMPT},
            {"role": "user", "content": f"Student context:\n{context}\n\nStudent message:\n{message}"},
        ],
    }
    response = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30.0)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def generate_sam_reply(
    settings: Settings,
    message: str,
    context: str,
    role: Role | None,
    next_topic: Topic | None,
    score: float,
) -> tuple[str, bool]:
    if not settings.llm_configured:
        return demo_reply(message, role, next_topic, score), True

    try:
        provider = settings.llm_provider.strip().lower()
        if provider == "openai":
            return _openai_reply(settings, context, message), False
        return _gemini_reply(settings, context, message), False
    except Exception:
        fallback = demo_reply(message, role, next_topic, score)
        return (
            fallback + "\n\n(SAM is using demo guidance because the hosted LLM request did not complete.)",
            True,
        )
