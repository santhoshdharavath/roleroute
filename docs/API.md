# RoleRoute API

Base URL (local): `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

The hackathon MVP uses one demo user. There is no authentication.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | API status and whether SAM is in demo mode |
| GET | `/roles` | All target roles |
| GET | `/roles/{role_id}/path` | Role, modules, topics, recommended sequence |
| POST | `/onboarding` | Save selected role and target date for the demo user |
| POST | `/progress/complete` | Mark a topic complete and return updated progress |
| GET | `/progress/summary` | Completions, readiness, graph history, next topic, skill gaps |
| GET | `/predictions` | Role-fit breakdown and goal-achievement status |
| GET | `/internships` | Curated internships with fit scores |
| POST | `/chat` | SAM reply (hosted LLM or demo fallback) |
| POST | `/demo/reset` | Reset demo progress and snapshots |

## Example bodies

### POST `/onboarding`

```json
{
  "role_id": 1,
  "target_date": "2026-12-15",
  "name": "Alex Rivera"
}
```

### POST `/progress/complete`

```json
{
  "topic_id": 7
}
```

### POST `/chat`

```json
{
  "message": "What should I study next?"
}
```

Scoring rules are documented in the root README.
