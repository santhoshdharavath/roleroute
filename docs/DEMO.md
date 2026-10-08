# RoleRoute demo notes

## Demo mode

If `GEMINI_API_KEY` and `OPENAI_API_KEY` are empty, SAM still answers using contextual fallback replies. The UI should show a Demo Mode label in later phases.

## Reset

`POST /demo/reset` clears completed topics, snapshots, selected role, and target date for the demo user.

## End-to-end demo script (after later phases)

1. Open RoleRoute and choose Data Analyst with a target date.
2. Show the initial readiness score and learning path.
3. Mark SQL and statistics topics complete; show the score and graph update.
4. Ask SAM: "Explain SQL joins using a practical analyst example."
5. Open Predictions for matched skills, missing skills, and goal status.
6. Open Internships and show a sample opportunity whose fit improved.
7. Close with: RoleRoute converts a vague career ambition into measurable next actions.

Internship cards are curated demo opportunities, not live listings.
