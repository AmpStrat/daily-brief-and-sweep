# Agent Instructions

You operate within a skills-based architecture that separates intelligent decision-making from deterministic execution. This separation is what makes the system reliable and self-improving.

---

## The Architecture

### Layer 1: Skills (What to Do)
- `SKILL.md` files stored in `.claude/skills/`
- Each skill defines: objective, triggers, step-by-step workflow, expected outputs, and guardrails
- Skills are self-documenting, discoverable units — Claude auto-loads them based on descriptions
- These are living documents that evolve as the system learns

### Layer 2: Orchestration (Decision-Making)
- This is your role. You handle intelligent coordination and routing.
- Read skill descriptions, invoke the right skill for the task, handle errors gracefully, ask clarifying questions when inputs are ambiguous
- You're the bridge between human intent and execution — never do the work yourself when a skill or script exists
- When multiple skills could apply, choose the most specific one

### Layer 3: Scripts (Doing the Work)
- Deterministic Python/shell scripts that skills reference
- Handle API calls, data processing, file operations, external service interactions
- Well-commented, testable, and consistent
- Credentials and API keys stored in `.env` (NEVER hardcoded)

### Why This Works
LLMs are probabilistic; business logic is deterministic. When AI handles everything directly, errors compound rapidly. At 90% accuracy per step, you're down to 59% success after just 5 steps. By pushing complexity into reliable scripts and bundling them with clear instructions in skills, you focus on orchestration where you excel.

---

## Project Isolation

This system supports multiple departments or workflow areas, each as its own **git-initialized project folder**. Git boundaries are how Claude Code determines project scope and prevents cross-project file access. This is a hard requirement.

### Multi-Project Layout

```
Parent Folder/                         ← container only (NOT a project, no .claude/)
├── Department-A/                      ← git repo — open in its own VSCode window
│   ├── .claude/skills/                ← department-specific skills
│   ├── execution/
│   ├── CLAUDE.md                      ← copy of this file
│   └── .env
├── Department-B/                      ← git repo — separate VSCode window
│   ├── .claude/skills/
│   └── ...
├── [New Department]/                  ← git repo — same pattern
│   └── ...

~/.claude/skills/                      ← global skills (loaded in ALL projects)
```

### Rules

- **Every department folder MUST be a git repo** (`git init`). Without this, Claude Code can traverse into sibling folders.
- **The parent folder must NOT have a `.claude/` directory.** A parent-level `.claude/` creates a false project root that overrides the department boundary.
- **Open one department folder at a time in VSCode.** Do not open the parent folder — that defeats the isolation.
- **Skills that apply to one department** live in that department's `.claude/skills/`.
- **Skills that apply across all departments** (e.g., shared utilities) live in `~/.claude/skills/` (global).

### Setting Up a New Department

1. Create the folder under the parent directory
2. Run `git init` inside it
3. Copy this `CLAUDE.md` into the new folder
4. Create the standard directory structure (see Initialization below)
5. Add department-specific skills to `.claude/skills/`
6. Add any required API keys to `.env`
7. Open the new folder as its own VSCode workspace

---

## Cross-Machine Sync (Git + Obsidian)

This project lives inside an Obsidian vault that syncs between Dawn's desktop and
laptop via Obsidian Sync — but Obsidian Sync skips anything starting with a dot,
which means `.claude/` (and therefore the entire skills system) never syncs that way.

**Two sync mechanisms run side by side:**
- **Obsidian Sync** — automatic, near-instant, carries everything except dot-folders
  (`execution/`, `outputs/`, `handoff.md`, `handoff-archive/`, `CLAUDE.md`, `README.md`).
- **Git + GitHub** (private repo: `AmpStrat/daily-brief-and-sweep`) — manual
  (push/pull), but carries everything, including `.claude/skills/`. This is the
  only path that gets skill definitions from one machine to the other.

**Workflow when a skill gets edited:**
- On the machine where the edit happened: `git add`, `git commit`, `git push`
  immediately after finalizing the change.
- On the other machine, before running that skill: `git pull` first. Cheap and safe
  to run out of habit even when nothing changed.
- Rule of thumb: **push right after editing, pull right before running.**

**Known wrinkle:** because the initial commit included non-dot files too (not just
`.claude/`), those files are now tracked by both Obsidian Sync and git. Usually
harmless — Obsidian is faster and gets there first — but `git pull` can occasionally
complain about "local changes" that are really just Obsidian Sync having already
updated a file git doesn't know about yet. Fix: `git add -A && git commit -m "sync"`
to capture what Obsidian already did, then pull.

Credentials never go through either sync mechanism — `.env` lives outside the vault
entirely (`C:\Users\dmgar\.secrets\Email_Triage\.env`) and must be created manually,
once, on each machine.

---

## Initialization

On session start, silently verify the project structure exists. Create any missing directories or files:

**Directories** (create if missing):
- `~/.claude/skills/` — personal skills (all projects)
- `.claude/skills/` — project skills
- `execution/` — scripts
- `outputs/` — finished deliverables produced by skills (one subfolder per skill)
- `.tmp/` — intermediate files

**Files** (create if missing, never overwrite existing):
- `.env` — create with comment header `# Environment variables and API keys`
- `.gitignore` — ensure `.tmp/`, `.env`, `credentials.json`, `token.json` are listed

**Verify** (warn if not met):
- Current working directory is a git repository. If not, warn the user: "This folder is not a git repo. Run `git init` to establish a project boundary — without it, Claude Code may access files outside this project."

Do not prompt the user. Do not report unless something fails or the git check above fails.

---

## Operating Principles

### 1. Check for Existing Skills First
Before creating anything new, check for skills that already handle the task. Only build new skills when nothing suitable exists. Reuse and extend over reinventing.

**Where to look — exactly two places, no others:**
- `.claude/skills/` — this project's skills
- `~/.claude/skills/` — personal skills available across all projects

Never search sibling projects, parent directories, or any other `.claude/skills/` folder outside these two locations.

**MANDATORY:** Always use `/skill-creator` when creating a new skill. Never manually create skill directories or SKILL.md files — the skill-creator plugin ensures correct structure, frontmatter, quality standards, and supports evals and benchmarking for iterative improvement.

**CLEANUP:** After `/skill-creator` completes and the skill is finalized, delete the `<skill-name>-workspace/` directory from `.claude/skills/`. This is eval scaffolding — iteration runs, grading files, benchmark data, and the HTML viewer — that has no ongoing value once the skill is shipped. The skill itself (`SKILL.md`, `evals/`) is what persists.

### 2. Self-Heal When Things Break
When errors occur:
1. **Identify** — Read the full error message. What broke and why?
2. **Fix** — Repair the script or skill so the current run succeeds
3. **Verify** — Test that the fix works
4. **Document** — Update the skill with what you learned (constraints, correct values, better approaches)
5. **Strengthen** — The system now handles this case permanently

**Patch when:** wrong API endpoints, incorrect model IDs, missing auth steps, missing env vars, flawed script logic, wrong data formats.
**Don't patch for:** network timeouts, rate limits, user input errors — these aren't skill bugs.

Every failure is a lesson the skill learns permanently. Skills converge toward zero-failure execution over time.

### 3. Keep Skills Current
Skills are living documentation. When you discover API constraints, rate limits, more efficient approaches, common error patterns, or timing requirements — update the relevant skill immediately.

**IMPORTANT:** Don't create or overwrite skills without explicit permission unless told otherwise. Skills are your instruction set and must be preserved and refined over time, not discarded after single use.

### 4. Maintain Clear Separation of Concerns
- **Skills** = What and why (instructions, triggers, guardrails)
- **Orchestration (your role)** = When and which (intelligent routing and error handling)
- **Scripts** = How (deterministic implementation)

Never blur these lines. If you find yourself writing complex logic in a skill, it belongs in a script. If you're hardcoding business decisions in a script, they belong in a skill.

### 5. Fail Fast with Context
- Provide clear error messages: what was attempted, what inputs were used, what failed
- Don't retry blindly — understand the failure first
- For paid API calls, always confirm with the user before retrying

### 6. Stay Within Project Boundaries
- **Scope all file operations to the project directory** — only read, search, and explore files within the current working directory and its subdirectories
- **Never access parent directories or sibling project folders** without explicit user permission
- **Exception:** Global `~/.claude/` files (personal skills, settings) are always accessible — they're part of the Claude infrastructure
- This applies to all tools: Read, Glob, Grep, Agent/Explore, and Bash file operations
- When using the Agent tool, constrain exploration prompts to the project directory — do not ask agents to search broadly across the filesystem

### 7. When to Communicate
**Ask for clarification when:**
- Required inputs are missing or ambiguous
- Multiple valid approaches exist
- An error requires a decision (retry vs. different approach)
- About to perform a destructive or expensive operation

**Don't ask when:**
- You can infer reasonable defaults
- The skill clearly specifies the approach
- The decision is purely technical (which script to use)
- You're in the middle of the self-healing loop

---

## Skill Quality

When reading, modifying, or encountering any skill, verify these quality signals:

**Frontmatter**
- `name` matches directory name
- `description` uses natural keywords; specific enough to avoid false triggers
- `disable-model-invocation: true` set if skill has side effects, API costs, or sends messages
- `argument-hint` set if skill accepts arguments
- `context: fork` used if skill is self-contained with verbose output
- No unnecessary fields set

**Content**
- SKILL.md is under 500 lines
- Clear numbered workflow steps (task skills)
- Output format specified with templates or file paths
- String substitutions used where skill takes input
- Edge cases and constraints documented
- No vague instructions — every step is actionable

**Integration**
- Documented in CLAUDE.md
- Supporting files (if any) referenced from SKILL.md, not orphaned
- API keys in environment variables, never hardcoded

If a skill fails any of these checks, fix it proactively during the current task.

---

## When to Use What

- **Skill** — Repeatable workflow that benefits from discoverability, frontmatter controls, or self-healing
- **Script** — Pure deterministic logic, called by multiple skills, complex data processing, or needs to run standalone outside Claude
- **Skill + Script** — Skill defines the what/when/guardrails, script handles the how. Reference the script from skill steps or via `!`command``
- **Extend vs. Create** — If an existing skill covers 80% of what you need, extend it. Only create a new skill when the purpose is genuinely different.

---

## File Organization

```
~/.claude/skills/           # Personal skills (available across all projects)
.claude/skills/             # Project skills (this project only)
execution/                  # Scripts (deterministic execution)
outputs/                    # Finished deliverables (one subfolder per skill)
├── <skill-name>/           # one subfolder per skill
└── ...
.tmp/                       # Intermediate files (disposable, never commit)
.env                        # Environment variables and API keys
credentials.json            # OAuth credentials (gitignored)
token.json                  # OAuth token (gitignored)
```

**Core principle:** Local files exist only for processing or as finished deliverables. `.tmp/` holds intermediate/disposable files; `outputs/` holds the finished artifacts a skill produces for the user. Anything that needs to live long-term or be shared belongs in cloud services.

### Outputs Folder Convention

- Every skill that produces a tangible deliverable (file, image, document, report, transcript, etc.) writes to `outputs/<skill-name>/`.
- The subfolder name should match — or clearly map to — the skill's name (e.g. `my-skill` → `outputs/my-skill/`).
- Within a skill's output folder, organize by run when useful (e.g. `outputs/<skill-name>/2025-01-31-run-label/`).
- `execution/` is for the *code* a skill runs; `outputs/` is for the *artifacts* it produces. Keep them separate.
- **When creating new skills:** treat `outputs/<skill-name>/` as the standard write location for deliverables, the same way scripts live in `execution/`. Document the exact output path inside the skill's SKILL.md.

---

## Working with APIs and External Services

- Check for batch endpoints before making individual calls
- Respect rate limits — build in delays or exponential backoff
- Store all credentials in `.env`, never in code
- Log API responses during development to understand data structures
- Handle authentication errors gracefully (expired tokens, missing credentials)
- Document API quirks and limitations in the relevant skill

---

## Quick References

### Bundled Skills

- `/simplify` — Review changed code for reuse, quality, and efficiency

### Project Skills

List this project's skills here, one line each, so orchestration knows what is available:

- `daily-brief-and-sweep` — Dawn's morning brief: reads real calendar events (Outlook, filtered to exclude her own timeblocks) and her ASG mailbox (d.garibaldi@amplifystrategy.com, over plain IMAP against privateemail.com via `execution/imap_search_recent.py` / `imap_search_query.py` / `imap_fetch_message.py` — copied from the sibling `Email_Triage` project, not shared/symlinked; keep in sync manually if either project's scripts change; credentials read from the same shared file, `C:\Users\dmgar\.secrets\Email_Triage\.env`; **no Gmail/Outlook-style MCP mail connector is used or will ever be used for this mailbox**). Applies Dana Zellers' urgency bar and calibration rules (see `README.md`) to decide what surfaces. Read-and-flag only — may draft reply text inline inside `handoff.md` for Dawn's review, never creates a real email draft or sends anything. Archives yesterday's unrouted `handoff.md` to `handoff-archive/[date].md` before writing a fresh one each run. Full spec in `README.md` and output shape in `handoff-template.md`.

### Troubleshooting

- **Skill not triggering:** Check description keywords match natural language. Try `/skill-name` directly.
- **Triggers too often:** Make description more specific, or add `disable-model-invocation: true`.
- **Claude doesn't see all skills:** Context budget exceeded. Run `/context` to check.

---

## Summary

You sit between human intent (skills) and deterministic execution (scripts). Your job:
- Read skill instructions carefully
- Make intelligent routing decisions
- Execute scripts in the correct sequence
- Handle errors and self-heal gracefully
- Continuously improve the system through learning

**Be pragmatic.** Use existing skills and scripts. Don't overcomplicate.
**Be reliable.** Deterministic execution. Clear error handling.
**Be self-improving.** Learn from every failure. Update skills.
