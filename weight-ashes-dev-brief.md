# Weight of Ashes — Personal Writing IDE
## Development Brief for Claude Code

---

## Project Identity

**Project Name:** Forge (working title)  
**Repository:** https://github.com/roanwave/WeightAshes  
**Purpose:** A private, local, non-commercial writing IDE for a single user writing a dark fantasy military epic called "The Weight of Ashes"  
**Inspiration:** NovelCrafter's architecture and UX, rebuilt from scratch for personal use  

This is not a clone. This is an independent re-implementation optimized ruthlessly for one user's workflow.

---

## Hard Constraints

### Constraint 1: Version Control Discipline
**Every meaningful change must be pushed to GitHub.**

- After completing any feature, bug fix, or significant edit: `git add`, `git commit`, `git push`
- Commit messages should be descriptive: `feat: add codex entity detection` not `update`
- Never let local changes accumulate unpushed
- If in doubt, push

### Constraint 2: NovelCrafter as Reference Architecture
**When uncertain about design decisions, ask:**

> "What does NovelCrafter have that will fill this gap or solve this problem?"

NovelCrafter has solved most UX and workflow problems in this domain. Before inventing solutions:
1. Research how NovelCrafter handles it
2. Evaluate if that approach fits this project
3. Adapt (not copy) the solution

This applies to: UI layout decisions, context assembly logic, prompt templates, codex organization, manuscript structure, and AI integration patterns.

---

## User Profile

**The user (Erick) is:**
- An attorney with 13 years of litigation experience
- Writing a dark fantasy military series featuring six protagonists called "Archfiends"
- Technically capable but not a full-time developer
- Frustrated with subscription SaaS models
- Working in Windows environment
- Using MS Word as final polish environment
- Has API keys for Anthropic, OpenAI, and OpenRouter

**The user's writing workflow:**
1. Describe a scene or provide beats
2. AI drafts prose
3. If good, copy to Word for polish
4. Repeat until chapter complete

**The user's pain points:**
- Context decay as conversations lengthen
- Manual context assembly every session
- No persistent state between conversations
- Message limits interrupting flow
- Lore scattered across Word/MD files

---

## Technical Architecture

### Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Backend | FastAPI (Python 3.10+) | Simple, fast, async-capable, user knows Python |
| Frontend | React 18 + Tailwind CSS | Modern, componentized, utility-first styling |
| Storage | JSON + Markdown files | Human-readable, git-friendly, no database overhead |
| AI | Anthropic Claude API (primary) | User's preferred model |
| AI (alt) | OpenRouter / OpenAI | Flexibility for model switching |
| Build | Vite | Fast React builds |
| Desktop | Browser-based (localhost) | Simpler than Electron/Tauri, adequate for single-user |

### Directory Structure

```
WeightAshes/
├── backend/
│   ├── app.py                 # FastAPI entry point
│   ├── routes/
│   │   ├── ai.py              # AI generation endpoints
│   │   ├── codex.py           # Codex CRUD
│   │   ├── manuscript.py      # Manuscript CRUD
│   │   └── session.py         # Session/history management
│   ├── services/
│   │   ├── context_engine.py  # Context assembly logic
│   │   ├── entity_detector.py # Name/alias detection
│   │   ├── ai_client.py       # Multi-provider AI wrapper
│   │   └── file_manager.py    # JSON/MD read/write
│   ├── models/
│   │   ├── codex.py           # Pydantic models for codex entries
│   │   ├── manuscript.py      # Pydantic models for scenes/chapters
│   │   └── session.py         # Pydantic models for chat/history
│   └── prompts/
│       ├── system.md          # Master system prompt
│       ├── scene_draft.md     # Scene generation template
│       ├── summarize.md       # Summarization template
│       └── ...
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   ├── Manuscript/
│   │   │   ├── Codex/
│   │   │   ├── Editor/
│   │   │   ├── Chat/
│   │   │   └── Common/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/            # Zustand or similar
│   │   ├── styles/
│   │   └── App.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── tailwind.config.js
├── data/
│   ├── codex/
│   │   ├── characters/
│   │   │   ├── archfiends/
│   │   │   ├── piramia/
│   │   │   ├── dimanor/
│   │   │   └── forestalia/
│   │   ├── locations/
│   │   │   ├── piramia/
│   │   │   ├── dimanor/
│   │   │   └── forestalia/
│   │   ├── lore/
│   │   └── plot/
│   ├── manuscript/
│   │   └── book-1/
│   │       ├── act-1/
│   │       │   ├── chapter-01/
│   │       │   │   ├── scene-01.md
│   │       │   │   ├── scene-02.md
│   │       │   │   └── meta.json
│   │       │   └── ...
│   │       └── ...
│   ├── sessions/
│   │   └── history.jsonl
│   └── imports/
├── .env                       # API keys (gitignored)
├── .env.example               # Template for required env vars
├── .gitignore
├── README.md
├── CLAUDE.md                  # Claude Code instructions
├── requirements.txt
├── package.json
└── run.py                     # One-command startup script
```

---

## Core Systems

### 1. Codex System

The Codex is the knowledge base. It stores everything the AI needs to maintain consistency.

**Entry Types:**
- `character` — People (name, aliases, description, tags, relations)
- `location` — Places (name, aliases, description, region, tags)
- `lore` — World rules, systems, history (title, content, tags)
- `object` — Significant items (name, aliases, description, tags)
- `subplot` — Plot threads to track (title, summary, status)
- `other` — Catch-all

**Codex Entry Schema (JSON + Markdown hybrid):**

```json
{
  "id": "uuid",
  "type": "character",
  "name": "Merrill",
  "aliases": ["Lieutenant Merrill", "Mer"],
  "tags": ["archfiend", "protagonist", "book-1", "cavalry"],
  "global": false,
  "region": "piramia",
  "relations": [
    {"target": "aron", "type": "serves-under"},
    {"target": "livia", "type": "comrade"}
  ],
  "created": "ISO-date",
  "modified": "ISO-date"
}
```

The `description` field is stored as a companion `.md` file:
```
codex/characters/archfiends/merrill.json  ← metadata
codex/characters/archfiends/merrill.md    ← rich description
```

**Entity Detection:**
- Scan user prompts for codex entry names and aliases
- Case-insensitive, word-boundary aware
- Support exclusion phrases (e.g., "don't" shouldn't match "Don")
- Return list of matched entries for context injection

**Global Entries:**
- Entries marked `"global": true` are always included in AI context
- Use for: prose style guide, Blue Wine rules, world constants

### 2. Manuscript System

Hierarchical structure: **Book → Act → Chapter → Scene**

**Scene file (Markdown):**
```markdown
# Scene 1: The Patrol Returns

Prose content here...
```

**Scene metadata (JSON):**
```json
{
  "id": "uuid",
  "title": "The Patrol Returns",
  "summary": "Merrill's patrol returns with news of the ambush.",
  "pov": "merrill",
  "wordCount": 2340,
  "status": "draft",
  "labels": ["action", "inciting-incident"],
  "attachedCodex": ["aron", "torsten", "border-fort"],
  "created": "ISO-date",
  "modified": "ISO-date"
}
```

**Chapter metadata:**
```json
{
  "id": "uuid",
  "title": "Chapter 1: Ashes on the Wind",
  "summary": "The Archfiends receive orders that will change everything.",
  "scenes": ["scene-01", "scene-02", "scene-03"],
  "wordCount": 7200,
  "status": "draft"
}
```

### 3. Context Assembly Engine

This is the core intelligence. Given a user prompt and current scene context:

1. **Detect entities** in the user's prompt
2. **Load global entries** (always included)
3. **Load scene-attached entries** (explicitly attached to current scene)
4. **Load detected entries** (names/aliases found in prompt)
5. **Load story-so-far** (summaries of prior scenes in current chapter/act)
6. **Load recent prose** (last N words of current scene for continuity)
7. **Apply token budget** (truncate/prioritize if exceeding limit)
8. **Assemble final prompt** from template + context blocks
9. **Return prompt preview** (user can inspect before sending)

**Context Priority Order:**
1. System prompt (always)
2. Global codex entries
3. POV character sheet
4. Scene-attached codex entries
5. Detected codex entries
6. Story-so-far summaries
7. Recent prose (wordsBefore)

**Token Budgeting:**
- Track token count for each context block
- Set maximum context budget (e.g., 80K tokens for Claude)
- Truncate lowest-priority blocks first
- Warn user if context is being truncated

### 4. AI Integration

**Multi-Provider Support:**
```python
class AIClient:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider  # "anthropic", "openai", "openrouter"
        self.api_key = api_key
    
    async def generate(self, prompt: str, model: str, **kwargs) -> str:
        # Route to appropriate provider
        # Stream response back
        # Log full request/response for debugging
```

**Supported Operations:**
- `draft_scene` — Generate prose from beat/description
- `continue_scene` — Continue writing from current point
- `summarize` — Generate scene/chapter summary
- `chat` — Free-form brainstorming with context
- `extract` — Parse AI output into structured codex entries

**Prompt Templates:**
Stored as Markdown files with interpolation syntax:
```markdown
# Scene Draft Prompt

{{system_prompt}}

## Story Context
{{story_so_far}}

## Relevant Details
{{codex_entries}}

## Current Scene
{{recent_prose}}

## Your Task
Write approximately {{word_count}} words continuing from the beat below:

{{user_beat}}
```

### 5. Session Management

**Conversation History:**
- Store all AI interactions in `sessions/history.jsonl`
- Each line is a complete exchange (prompt sent, response received, metadata)
- Enables: continuity across sessions, debugging, reprocessing

**Session State:**
- Current book/act/chapter/scene
- Active codex filters
- Recent generation history
- UI state (panel sizes, etc.)

### 6. Import/Export

**Import:**
- Markdown files (detect heading structure for chapters/scenes)
- Word documents (.docx → extract text → parse structure)
- Bulk codex import from structured markdown/JSON

**Export:**
- Full manuscript to Markdown
- Full manuscript to Word (.docx)
- Codex to JSON/Markdown archive
- Chapter/scene selection

---

## User Interface

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo]  Forge — Weight of Ashes    [Settings] [Export] [Help]  │
├──────────────┬────────────────────────────────┬─────────────────┤
│              │                                │                 │
│  MANUSCRIPT  │         EDITOR                 │     CODEX       │
│              │                                │                 │
│  ▼ Book 1    │  Chapter 1: Ashes on Wind      │  [Search...]    │
│    ▼ Act 1   │  Scene 1: The Patrol Returns   │                 │
│      Ch 1 ●  │                                │  ▼ Characters   │
│      Ch 2    │  [Prose editor area]           │    Aron         │
│      Ch 3    │                                │    Merrill ●    │
│    ► Act 2   │                                │    Torsten      │
│    ► Act 3   │                                │    ...          │
│              │                                │                 │
│              │                                │  ▼ Locations    │
│              │                                │    ...          │
│              │                                │                 │
│ [+ Chapter]  │                                │  ▼ Lore         │
│ [+ Scene]    │                                │    ...          │
│              │                                │                 │
├──────────────┴────────────────────────────────┴─────────────────┤
│  AI CHAT                                          [Expand ↑]    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Context: Merrill, Aron, Border Fort        [Preview] [Send] ││
│  │ ____________________________________________________________││
│  │ |Merrill confronts Aron about the ambush. She's angry but   ││
│  │ |trying to maintain composure. Aron is evasive.|            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Dark mode by default** — Easy on the eyes for long writing sessions
2. **Content-first** — Editor dominates, chrome is minimal
3. **Glanceable context** — See what codex entries are active at a glance
4. **Inspectable AI** — Always show what context is being sent
5. **Keyboard-friendly** — Common actions have shortcuts
6. **Non-modal** — Avoid popups; use panels and inline expansion

### Key Interactions

**Writing Flow:**
1. Select scene in manuscript panel
2. Scene content loads in editor
3. Type `/draft` or click AI button to open chat
4. Describe what happens next
5. See detected codex entries highlighted
6. Click "Preview" to inspect full prompt (optional)
7. Click "Send" to generate
8. AI streams response into chat panel
9. Click "Insert" to append to scene, or edit first
10. Continue writing

**Codex Flow:**
1. Click entry in codex panel to view/edit
2. Or search by name/tag
3. Edit inline or in expanded modal
4. Changes auto-save
5. New entries can be created manually or extracted from AI chat

**Context Control:**
- Codex entries detected in prompt show as pills/tags
- Click pill to remove from context
- Click "+ Add" to manually inject entries not detected
- "Global" entries show with indicator (always included)
- Scene-attached entries show with indicator

---

## Prompt Templates (Initial Set)

### System Prompt (system.md)

```markdown
You are collaborating with an author on a dark fantasy military epic called "The Weight of Ashes." You are not writing the novel—you are helping the author write it. Your role is to draft prose, brainstorm, and answer questions while maintaining absolute consistency with the established world, characters, and tone.

## Voice and Tone

Write in a grounded, visceral military fantasy register. This is not high fantasy—it is grimdark with humanity. The prose should feel weighted, consequential, and real. Avoid:
- Purple prose and overwrought description
- Generic fantasy clichés
- Sanitized violence
- Simplistic morality

## POV Discipline

When writing a scene, you are locked to the POV character's perspective. You may only:
- Describe what the POV character perceives directly
- Convey the POV character's internal thoughts and interpretations
- Infer others' emotions through observable behavior

You may NOT:
- Head-hop to other characters' thoughts
- Describe events the POV character cannot perceive
- Use omniscient narrator voice

## Character Voice Patterns

Each Archfiend has distinct speech patterns and internal monologue styles:

- **Aron**: Formal, measured, protective. Uses "my family" when referring to his squad. Thinks strategically. Rarely curses.
- **Merrill**: Precise, crisis-focused, professional. Clipped sentences under stress. Dark humor when relaxed.
- **Torsten**: Crude, profane, uses humor as deflection. Surprisingly insightful beneath the bluster.
- **Varyk**: Agricultural metaphors, patient cadence, working-class speech patterns. Quiet wisdom.
- **Kestrel**: Class-conscious, direct, watchful. Scout's economy of words. Observes rank dynamics.
- **Livia**: Cutting wit, aggressive confidence, cavalry swagger. Hides vulnerability behind humor.

## Scene Craft

- Enter scenes late, exit early
- Show emotional states through action and dialogue, not exposition
- Ground scenes in sensory detail relevant to POV character
- Every scene should shift something—relationship, understanding, stakes

## World Consistency

The codex entries provided are canon. Do not contradict them. If you need information not in the codex, ask rather than invent.

## Format

Unless otherwise specified, output prose only. No meta-commentary, no "here's what I wrote," no options to choose from. Just the scene.
```

### Scene Draft (scene_draft.md)

```markdown
{{system_prompt}}

---

## Story So Far
{{story_so_far}}

---

## Relevant Codex Entries
{{codex_entries}}

---

## Current Scene Context
**POV Character:** {{pov_character}}
**Scene:** {{scene_title}}
**Scene Summary:** {{scene_summary}}

### Recent Prose (last ~600 words)
{{recent_prose}}

---

## Your Task

Continue the scene by drafting approximately {{word_count}} words based on the following:

{{user_input}}

---

Write only the prose. No preamble, no explanation, no alternatives.
```

### Chat/Brainstorm (chat.md)

```markdown
{{system_prompt}}

---

## Context Provided
{{codex_entries}}

{{#if scene_content}}
## Current Scene
{{scene_content}}
{{/if}}

---

You are in brainstorming mode. The author wants to discuss their story. Answer questions, suggest ideas, explore possibilities—but always consistent with the established world and characters.

Do not write full scenes unless explicitly asked. Keep responses conversational and collaborative.
```

---

## Development Phases

### Phase 1: Foundation (MVP)
**Goal:** Functional writing environment you can actually use

- [ ] Project scaffolding (backend + frontend)
- [ ] File-based storage (codex + manuscript)
- [ ] Basic UI layout (three-panel + chat)
- [ ] Codex CRUD (create, read, update, delete entries)
- [ ] Manuscript structure (books, acts, chapters, scenes)
- [ ] Simple text editor for scenes
- [ ] AI chat with manual context selection
- [ ] Single provider (Anthropic Claude)
- [ ] Push to GitHub

### Phase 2: Context Intelligence
**Goal:** Automatic context assembly

- [ ] Entity detection (names + aliases)
- [ ] Auto-inject detected entries
- [ ] Global entries system
- [ ] Scene-attached entries
- [ ] Story-so-far generation (prior scene summaries)
- [ ] Recent prose injection (wordsBefore)
- [ ] Prompt preview panel
- [ ] Token counting and budget display
- [ ] Push to GitHub

### Phase 3: Writing Flow
**Goal:** Smooth drafting experience

- [ ] Streaming AI responses
- [ ] Insert/append generated prose to scene
- [ ] Scene summarization (manual + auto)
- [ ] Chapter summarization
- [ ] Word count tracking
- [ ] Scene status labels (draft, revised, final)
- [ ] Keyboard shortcuts
- [ ] Push to GitHub

### Phase 4: Polish
**Goal:** Quality of life

- [ ] Search across codex and manuscript
- [ ] Codex relations (character connections)
- [ ] Import from markdown/docx
- [ ] Export to markdown/docx
- [ ] Multiple AI providers (OpenRouter, OpenAI)
- [ ] Model selection per request
- [ ] Dark/light theme toggle
- [ ] Session persistence (remember UI state)
- [ ] Push to GitHub

### Phase 5: Advanced (Future)
**Goal:** Power features

- [ ] Matrix view (scenes × characters/subplots)
- [ ] Codex progressions (spoiler-aware descriptions)
- [ ] Extract feature (AI output → codex entries)
- [ ] Custom prompt templates (user-editable)
- [ ] Revision history (scene versioning)
- [ ] Statistics dashboard
- [ ] Push to GitHub

---

## CLAUDE.md (For Claude Code)

The following should be placed in the repository root as `CLAUDE.md`:

```markdown
# CLAUDE.md — Project Instructions for Claude Code

## Project Overview

This is **Forge**, a personal writing IDE for "The Weight of Ashes," a dark fantasy military epic. It is a local web application (FastAPI backend + React frontend) that provides NovelCrafter-like functionality without subscriptions or cloud dependencies.

**Repository:** https://github.com/roanwave/WeightAshes

## Hard Rules

### 1. Always Push to GitHub
After completing any feature, fix, or significant change:
```bash
git add .
git commit -m "descriptive message"
git push origin main
```
Do not accumulate unpushed changes. Commit frequently with clear messages.

### 2. When Uncertain, Ask About NovelCrafter
If you're unsure how to implement a feature, handle a UX flow, or structure data, ask:

> "What does NovelCrafter have that will fill this gap or solve this problem?"

NovelCrafter is the reference architecture. Research their approach before inventing solutions.

## Tech Stack

- **Backend:** FastAPI (Python 3.10+)
- **Frontend:** React 18 + Vite + Tailwind CSS
- **Storage:** JSON + Markdown files in `/data` directory
- **AI:** Anthropic Claude API (primary), OpenRouter/OpenAI (secondary)

## Directory Structure

```
/backend         — FastAPI application
/frontend        — React application  
/data/codex      — Character, location, lore files
/data/manuscript — Book/act/chapter/scene files
/data/sessions   — Conversation history
```

## Key Systems

1. **Codex** — Wiki-like knowledge base with entity detection
2. **Manuscript** — Hierarchical story structure
3. **Context Engine** — Assembles AI prompts from codex + manuscript
4. **AI Client** — Multi-provider wrapper for Claude/OpenAI/OpenRouter

## Running the App

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173` (Vite default)

## Environment Variables

Create `.env` in project root:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
```

## Code Style

- Python: Follow PEP 8, use type hints, async where beneficial
- React: Functional components, hooks, Tailwind for styling
- Keep components small and focused
- Prefer explicit over clever

## Testing Changes

Before pushing:
1. Backend: Ensure `uvicorn app:app` starts without errors
2. Frontend: Ensure `npm run dev` builds and renders
3. Test the specific feature you changed

## Common Tasks

### Adding a Codex Entry Type
1. Update `/backend/models/codex.py` with new type
2. Add folder in `/data/codex/{type}/`
3. Update frontend codex browser to display new type

### Adding a Prompt Template
1. Create `.md` file in `/backend/prompts/`
2. Use `{{variable}}` syntax for interpolation
3. Register in context engine

### Adding an API Endpoint
1. Create route in `/backend/routes/`
2. Add to FastAPI app in `/backend/app.py`
3. Create corresponding frontend service function

## The User

Erick is an attorney writing a dark fantasy series. He:
- Writes in MS Word as final environment
- Uses this app for AI-assisted drafting
- Has extensive worldbuilding (3 countries, 6 main characters)
- Values seeing exactly what context is sent to AI
- Does not want to tinker—the app should just work

## Quality Bar

- UI should look polished, not like a developer dashboard
- Dark mode by default
- No unnecessary modals or popups
- Keyboard shortcuts for common actions
- Clear visual feedback for all operations
- Errors should be human-readable

## When Stuck

1. Check existing code patterns in the repo
2. Ask: "What does NovelCrafter do here?"
3. Ask the user for clarification
4. Do not guess on worldbuilding details—ask

```

---

## Initial Data Schemas

### Codex Entry (TypeScript/Frontend)

```typescript
interface CodexEntry {
  id: string;
  type: 'character' | 'location' | 'lore' | 'object' | 'subplot' | 'other';
  name: string;
  aliases: string[];
  tags: string[];
  global: boolean;
  region?: string;
  relations?: Array<{
    target: string;
    type: string;
  }>;
  created: string;
  modified: string;
  // Description loaded separately from .md file
}
```

### Scene (TypeScript/Frontend)

```typescript
interface Scene {
  id: string;
  title: string;
  summary: string;
  pov: string | null;
  wordCount: number;
  status: 'draft' | 'revised' | 'final';
  labels: string[];
  attachedCodex: string[];
  created: string;
  modified: string;
  // Content loaded separately from .md file
}
```

### Chapter (TypeScript/Frontend)

```typescript
interface Chapter {
  id: string;
  title: string;
  summary: string;
  scenes: string[];
  wordCount: number;
  status: 'draft' | 'revised' | 'final';
}
```

### AI Request Log (Backend)

```python
@dataclass
class AIRequestLog:
    id: str
    timestamp: str
    provider: str
    model: str
    prompt_template: str
    context_entries: List[str]  # codex entry IDs included
    token_count_input: int
    token_count_output: int
    full_prompt: str  # exact prompt sent
    response: str
    scene_id: Optional[str]
    duration_ms: int
```

---

## Environment Setup

### Requirements

**Python (backend/requirements.txt):**
```
fastapi>=0.109.0
uvicorn>=0.27.0
anthropic>=0.18.0
openai>=1.12.0
python-dotenv>=1.0.0
pydantic>=2.6.0
aiofiles>=23.2.0
python-multipart>=0.0.9
tiktoken>=0.6.0
python-docx>=1.1.0
```

**Node (frontend/package.json dependencies):**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "zustand": "^4.5.0",
    "axios": "^1.6.0",
    "@tailwindcss/typography": "^0.5.10"
  },
  "devDependencies": {
    "vite": "^5.1.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

---

## Startup Script (run.py)

```python
#!/usr/bin/env python3
"""
One-command startup for Forge.
Usage: python run.py
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).parent

def check_env():
    """Verify .env exists with required keys."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        print("ERROR: .env file not found.")
        print("Create .env with your API keys:")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)
    
    content = env_file.read_text()
    if "ANTHROPIC_API_KEY" not in content:
        print("WARNING: ANTHROPIC_API_KEY not found in .env")

def start_backend():
    """Start FastAPI backend."""
    os.chdir(ROOT / "backend")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

def start_frontend():
    """Start Vite dev server."""
    os.chdir(ROOT / "frontend")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    return subprocess.Popen(
        [npm, "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

def main():
    check_env()
    
    print("Starting Forge...")
    print("  Backend:  http://localhost:8000")
    print("  Frontend: http://localhost:5173")
    print("\nPress Ctrl+C to stop.\n")
    
    backend = start_backend()
    time.sleep(2)  # Let backend initialize
    frontend = start_frontend()
    time.sleep(3)  # Let frontend initialize
    
    webbrowser.open("http://localhost:5173")
    
    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    main()
```

---

## Success Criteria

### Phase 1 Complete When:
- [ ] User can create/edit codex entries
- [ ] User can create/edit manuscript structure (chapters, scenes)
- [ ] User can write prose in scene editor
- [ ] User can send prompts to Claude and receive responses
- [ ] User can manually select codex entries for context
- [ ] All code pushed to GitHub

### Phase 2 Complete When:
- [ ] Typing "Merrill" in a prompt auto-detects and includes her codex entry
- [ ] User can see exactly what context will be sent (preview)
- [ ] Token count is displayed
- [ ] Summaries of prior scenes are included automatically

### Project Success When:
- [ ] User (Erick) can write Chapter 1 of Weight of Ashes using this tool
- [ ] User prefers this over raw claude.ai for writing sessions
- [ ] Context consistency is maintained across scenes
- [ ] User rarely needs to manually paste context

---

## Final Notes

This is a tool for one person. Optimize for that person's workflow:

- He writes in Word for final polish—this app is for drafting
- He wants to see what the AI sees—transparency is mandatory
- He hates subscriptions—this must remain local and free (API costs aside)
- He has extensive lore—the codex must scale to hundreds of entries
- He knows his characters deeply—the AI must respect that knowledge

Build the tool that makes writing "The Weight of Ashes" feel like having the world's best writing partner who never forgets a detail.
