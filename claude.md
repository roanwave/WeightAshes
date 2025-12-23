# CLAUDE.md — Project Instructions for Claude Code

## Project Overview

**WeightAshes** is a personal writing IDE for "The Weight of Ashes," a dark fantasy military epic. It is a local web application (FastAPI backend + React frontend) that provides NovelCrafter-like functionality without subscriptions or cloud dependencies.

This is a single-user tool. Optimize ruthlessly for that user's workflow.

**Repository:** https://github.com/roanwave/WeightAshes

---

## Hard Rules

### 1. Git Discipline

**Always push to GitHub** after completing any feature, fix, or significant change:
```bash
git add .
git commit -m "feat: descriptive message here"
git push origin main
```

Commit frequently. Use descriptive messages. Never accumulate unpushed changes.

**Commit message format:**
- `feat: add codex entity detection`
- `fix: resolve scene loading error`
- `refactor: simplify context assembly logic`
- `docs: update README with setup instructions`

**Protect secrets with .gitignore.** The repository must have a `.gitignore` that includes:
```gitignore
# Environment and secrets
.env
.env.local
.env.*.local
*.env

# API keys and credentials
**/secrets/
*.pem
*.key

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
env/
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Build outputs
frontend/dist/
*.log
```

Before your first commit, verify `.env` is gitignored:
```bash
git check-ignore .env
```

If this returns nothing, stop and fix `.gitignore` before proceeding.

Never commit API keys. If you accidentally commit secrets, alert the user immediately — the keys must be rotated.

### 2. When Uncertain, Reference NovelCrafter

If you're unsure how to implement a feature, handle a UX flow, or structure data, ask:

> "What does NovelCrafter do here?"

NovelCrafter is the reference architecture. Research their approach before inventing solutions. This applies to: UI layout, context assembly logic, prompt templates, codex organization, manuscript structure, and AI integration patterns.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.10+) |
| Frontend | React 18 + Vite + Tailwind CSS |
| Storage | JSON + Markdown files in `/data` |
| AI | Anthropic Claude API (primary), OpenRouter/OpenAI (secondary) |

---

## Directory Structure
```
WeightAshes/
├── backend/
│   ├── app.py                 # FastAPI entry point
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic
│   ├── models/                # Pydantic schemas
│   └── prompts/               # Markdown prompt templates
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API client functions
│   │   └── stores/            # Zustand state management
│   └── index.html
├── data/
│   ├── codex/                 # Character, location, lore files
│   │   ├── characters/
│   │   ├── locations/
│   │   ├── lore/
│   │   └── ...
│   ├── manuscript/            # Book/act/chapter/scene files
│   └── sessions/              # Conversation history
├── .env                       # API keys (gitignored)
├── .env.example               # Template for required keys
└── run.py                     # One-command startup
```

---

## Running the Application

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`

---

## Environment Variables

Create `.env` in project root:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
```

Never commit `.env`. The `.env.example` file should list required variables without values:
```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
OPENROUTER_API_KEY=
```

---

## Core Systems

### 1. Codex

Wiki-like knowledge base. Each entry has:
- JSON file for metadata (id, name, aliases, tags, type, relations, global flag)
- Markdown file for rich description

**Entry types:** character, location, lore, object, subplot, other

**Entity detection** scans user prompts for codex names/aliases (case-insensitive, word-boundary aware) and auto-injects matching entries into AI context.

**Global entries** (marked `"global": true`) are always included in AI context regardless of detection.

### 2. Manuscript

Hierarchical structure: **Book → Act → Chapter → Scene**

- Scenes are Markdown files with companion JSON metadata
- Metadata includes: POV character, status (draft/revised/final), summary, attached codex entries, word count
- Chapter metadata aggregates its scenes

### 3. Context Assembly Engine

Given a user prompt and current scene, assemble AI context in this priority order:

1. System prompt (always)
2. Global codex entries
3. POV character sheet
4. Scene-attached codex entries
5. Detected codex entries (from user prompt)
6. Story-so-far (prior scene summaries)
7. Recent prose from current scene

**Token budgeting:** Track token count per block. If exceeding limit, truncate lowest-priority blocks first. Warn user when truncation occurs.

**Prompt preview:** User must be able to inspect the fully assembled prompt before sending to AI.

### 4. AI Client

Multi-provider wrapper supporting:
- Anthropic Claude (primary)
- OpenAI
- OpenRouter

Stream responses back to frontend. Log all requests/responses for debugging.

---

## Code Style

**Python:**
- Follow PEP 8
- Use type hints on all functions
- Async where beneficial
- Pydantic for all data models

**React:**
- Functional components only
- Hooks for state and effects
- Tailwind for all styling (no separate CSS files)
- Small, focused components (< 150 lines)

**General:**
- Prefer explicit over clever
- No premature abstraction
- Comments explain "why," not "what"
- Descriptive variable names over abbreviations

---

## Testing Changes

Before pushing:

1. Backend starts without errors: `uvicorn app:app`
2. Frontend builds and renders: `npm run dev`
3. Test the specific feature you changed
4. Check browser console for JavaScript errors
5. Verify no `.env` or secrets in staged files: `git status`

---

## The User

Erick is an attorney writing a dark fantasy series. He:

- Uses MS Word for final polish; this app is for AI-assisted drafting
- Has extensive worldbuilding (3 countries, 6 protagonists called Archfiends)
- Values transparency — must see exactly what context is sent to AI
- Hates subscriptions — this must remain local and free (API costs aside)
- Wants the app to just work — minimal tinkering required

**His workflow:**
1. Describe a scene or provide beats
2. AI drafts prose
3. If good, copy to Word for polish
4. Repeat until chapter complete

**His pain points this app solves:**
- Context decay as conversations lengthen
- Manual context assembly every session
- No persistent state between conversations
- Lore scattered across files

---

## UI Standards

- **Dark mode by default** — easy on eyes for long writing sessions
- **Content-first** — editor dominates, chrome is minimal
- **No unnecessary modals** — use panels and inline expansion
- **Keyboard shortcuts** — common actions must have them
- **Glanceable context** — show active codex entries at a glance
- **Inspectable AI** — always show what context is being sent
- **Clear feedback** — every action should have visible response
- **Human-readable errors** — no stack traces in UI

---

## Common Tasks

### Adding a Codex Entry Type

1. Update `/backend/models/codex.py` with new type in enum
2. Create folder in `/data/codex/{type}/`
3. Update frontend codex browser to display new type
4. Commit and push

### Adding a Prompt Template

1. Create `.md` file in `/backend/prompts/`
2. Use `{{variable}}` syntax for interpolation
3. Register in context assembly service
4. Commit and push

### Adding an API Endpoint

1. Create route in `/backend/routes/`
2. Register router in `/backend/app.py`
3. Add corresponding frontend service function in `/frontend/src/services/`
4. Commit and push

---

## When Stuck

1. Check existing code patterns in the repo
2. Ask: "What does NovelCrafter do here?"
3. Ask the user for clarification
4. Do not invent worldbuilding details — ask
5. Do not guess on UX patterns — research NovelCrafter first

---

## Quality Bar

This is not a prototype or developer tool. It should feel like software, not a hackathon project.

- UI should look polished and intentional
- Interactions should feel responsive
- Errors should guide the user toward resolution
- The app should "just work" after initial setup

Build the tool that makes writing "The Weight of Ashes" feel like having the world's best writing partner who never forgets a detail.