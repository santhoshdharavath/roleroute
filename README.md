# RoleRoute

**AI-powered career-growth platform for college students.**

Pick a target role, follow a structured learning route, mark topics as complete, watch your Role Readiness Score climb, review skill-gap analysis, check internship fit scores, and get guidance from **SAM — Skill Advancement Mentor**.

> This is a hackathon MVP. Scores are learning-progress estimates, not scientifically validated predictions, and are not guarantees of internships, jobs, or placements.

---

## Technology Stack

| Layer       | Technology                                         |
| ----------- | -------------------------------------------------- |
| Frontend    | Next.js 16, TypeScript, React 19, Tailwind CSS 4   |
| Charts      | Recharts                                           |
| Icons       | Lucide React                                       |
| Animations  | Framer Motion                                      |
| Backend     | FastAPI, Pydantic, SQLAlchemy                      |
| Database    | SQLite (auto-created on first run)                 |
| AI (SAM)    | Gemini or OpenAI — demo-mode fallback when no key  |

---

## Project Structure

```
roleroute/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route handlers
│   │   ├── core/           # Settings & configuration
│   │   ├── db/             # Database session & bootstrap/seed
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── seed/           # JSON seed data (roles, modules, topics, internships)
│   │   ├── services/       # Business logic (scoring, SAM, internships)
│   │   └── main.py         # FastAPI application entry point
│   ├── .env.example        # Environment variable template
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── app/                # Next.js App Router pages
│   ├── components/         # Reusable React components
│   ├── lib/                # API client & utilities
│   ├── types/              # TypeScript type definitions
│   ├── public/             # Static assets
│   ├── .env.local.example  # Frontend env template
│   └── package.json        # Node.js dependencies
├── docs/
│   ├── API.md              # API documentation
│   └── DEMO.md             # Demo mode documentation
├── .gitignore
└── README.md
```

---

## Prerequisites

- **Python** 3.11 or higher
- **Node.js** 18 or higher (with npm)
- **Git** (for version control)

---

## Getting Started

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

**macOS / Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Verify the backend is running:
- Health check: [http://localhost:8000/health](http://localhost:8000/health)
- API docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

The SQLite database file `backend/roleroute.db` is automatically created and seeded on first startup with three roles, modules, topics, internships, and one demo user.

### 2. Frontend Setup

```bash
cd frontend
```

**Windows PowerShell:**

```powershell
copy .env.local.example .env.local
npm install
npm run dev
```

**macOS / Linux:**

```bash
cp .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The app should show the onboarding screen when the backend API is running.

### 3. Environment Variables

#### Backend (`backend/.env`)

| Variable          | Description                                    | Default                     |
| ----------------- | ---------------------------------------------- | --------------------------- |
| `DATABASE_URL`    | SQLite connection string                       | `sqlite:///./roleroute.db`  |
| `CORS_ORIGINS`    | Comma-separated allowed origins                | `http://localhost:3000`     |
| `DEMO_USER_ID`    | Demo student user ID                           | `1`                         |
| `DEMO_USER_NAME`  | Demo student display name                      | `Alex Rivera`               |
| `DEMO_USER_EMAIL` | Demo student email                             | `alex@roleroute.demo`       |
| `LLM_PROVIDER`    | AI provider for SAM (`gemini` / `openai` / `none`) | `gemini`                |
| `GEMINI_API_KEY`  | Google Gemini API key (leave empty for demo)   | _(empty)_                   |
| `GEMINI_MODEL`    | Gemini model name                              | `gemini-2.0-flash`          |
| `OPENAI_API_KEY`  | OpenAI API key (leave empty for demo)          | _(empty)_                   |
| `OPENAI_MODEL`    | OpenAI model name                              | `gpt-4o-mini`               |

#### Frontend (`frontend/.env.local`)

| Variable                    | Description                  | Default                    |
| --------------------------- | ---------------------------- | -------------------------- |
| `NEXT_PUBLIC_API_BASE_URL`  | Backend API URL              | `http://localhost:8000`    |

### 4. Optional: SAM with a Hosted LLM

In `backend/.env`, set either:
- `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=<your-key>`
- `LLM_PROVIDER=openai` and `OPENAI_API_KEY=<your-key>`

If both keys are empty, SAM runs in **demo mode** and still returns useful contextual replies.

---

## Available Commands

### Backend

| Command                                          | Description                      |
| ------------------------------------------------ | -------------------------------- |
| `uvicorn app.main:app --reload --port 8000`      | Start dev server with hot-reload |
| `pip install -r requirements.txt`                | Install Python dependencies      |

### Frontend

| Command           | Description                              |
| ----------------- | ---------------------------------------- |
| `npm run dev`     | Start Next.js dev server (port 3000)     |
| `npm run build`   | Create production build                  |
| `npm run start`   | Serve production build                   |
| `npm run lint`    | Run ESLint                               |

---

## Scoring (Transparent Estimates)

- **Role Readiness Score (0–100):** Weighted sum of skill mastery. Completing a topic raises mastery for its skill tags.
  - 0–34: Foundation · 35–69: Building · 70–84: Internship-Ready direction · 85–100: Advanced / job-readiness direction
  - A score of 70 does **not** guarantee an internship.
- **Internship Fit Score (0–100):** Percentage of a posting's required skills already demonstrated via completed topics.
- **Goal-Achievement Status (High / Medium / Low):** Compares current score, remaining topics, completion pace, and target date. Likelihood indicator, not a probability.

---

## MVP vs Future

**In MVP:** Three roles (Data Analyst, Software Developer, Machine Learning Engineer), structured learning paths, mark topics complete, readiness graph, skill gaps, goal status, sample internships, SAM, demo reset.

**Not in MVP:** Full authentication, live job scraping, video courses, payments, faculty dashboards, additional roles, resume builder.

---

## Deployment

- **Frontend:** Vercel — set `NEXT_PUBLIC_API_BASE_URL` to your public API URL.
- **Backend:** Render or Railway — set `DATABASE_URL`, `CORS_ORIGINS`, and optional LLM keys.

---

## Contributing

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-org>/roleroute.git
   cd roleroute
   ```
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Set up backend and frontend** following the instructions above.
4. **Make your changes** — do not commit `.env` files or API keys.
5. **Test your changes** — ensure both backend and frontend run without errors.
6. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: describe your change"
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** against `main`.

### Commit Message Convention

Use descriptive prefixes:
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `style:` — formatting, no logic change
- `refactor:` — code restructuring, no feature change
- `chore:` — build process, tooling, dependencies

---

## Documentation

- [API Reference](docs/API.md)
- [Demo Mode Guide](docs/DEMO.md)

---

## License

This project was created for a hackathon. License to be determined.
