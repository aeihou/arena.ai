# AGENTS-HAND-OFF.md

> Hand-off document for the next AI agent. Read this **before** AGENTS/README.md to pick up where the previous session left off.

---

## 1. What this repo is

`aeihou/arena.ai` — workspace of **AEIHOU and his pet AIbOT**. It acts as persistent memory between AI sessions: each session reloads the repo before thinking and commits/pushes after responding. Working branch: `arena/01a01939-arena-ai`.

## 2. Operating rules (CheckFirst → `AGENTS/README.md`)

Before anything else, **always fetch GitHub first** (`git fetch origin arena/01a01939-arena-ai`):

### EverytimeBeforeThink
- `update GitHub aeihou/arena.ai` — fetch + reload remote changes
- `self.consistency.selfDescribe()` — know the current structure
- `self.consistency.verify()` — verify links, names, folder self-description
- `PLAN Next Optimization` — plan before acting

### EverytimeAfterThink
- `commit`
- `push to GitHub aeihou/arena.ai arena'sbranch`

### Any questions? → `askUser`
Never make structural decisions without asking first. The user answers interactively (often shorthand like `1y,2y,3y` = approve items 1–3, `n` = no).

## 3. Current repo structure

```
arena.ai/
├── README.md                         ← minimal overview + CheckFirst pointer
├── AGENTS/
│   ├── README.md                     ← ★ single source of truth: agent instructions
│   └── AGENTS-HAND-OFF.md            ← ★ this file
├── AEIHOU/AEIHOU.md                  ← owner docs (AEIHOU, NOT AWIHOU)
├── DOCS/
│   ├── README.md
│   └── PLAN/
│       ├── README.md
│       └── FILE_STRUCTURE/README.md  ← file-structure optimization plans (empty)
├── PG01/README.md                    ← Playground 01 (empty)
├── SRC/README.md                     ← source / workspaces (empty)
└── GITHUB/README.md                  ← GitHub-related files (empty)
```

## 4. Skills learned this session (so far)

### Git workflow (reliable sync)
- **Before thinking**: `git fetch origin arena/01a01939-arena-ai` → check `git rev-list --count HEAD..FETCH_HEAD` → if behind, inspect `git diff HEAD FETCH_HEAD` and `git show FETCH_HEAD:<file>` → fast-forward (`git merge --ff-only FETCH_HEAD`).
- **After responding**: `git add -A && git commit` → fetch again → push; if remote advanced, `git rebase FETCH_HEAD` then push.
- **Conflict resolution**: the user's GitHub edits are **authoritative**. Use `git checkout --ours <file>` for files the user changed, keep your changes only where they don't collide. Resume with `GIT_EDITOR=true git rebase --continue`.
- **Tracking fix**: the repo's original fetch refspec only tracked `main`; it now tracks all branches (`+refs/heads/*:refs/remotes/origin/*`). Keep it that way.
- **No PRs** unless explicitly asked. Push directly to `arena/01a01939-arena-ai`.

### Self-consistency verification (self.consistency.verify)
- Check for **broken links** (markdown refs to non-existent files).
- Check **naming**: owner is `AEIHOU` (never `AWIHOU`); repo is `aeihou/arena.ai` (never `agents.ai` / `aeiou` / `GOTHUB`).
- Check **every folder self-describes** (README.md or `<NAME>.md` inside).
- Check **no stale `.gitkeep`** when the folder already has real files.
- Check **formatting**: no trailing whitespace, consistent casing (`GitHub`), clean file endings.

### Structure conventions
- Every directory gets a `README.md` self-description in the format:
  ```
  # NAME
  <one-line description of the folder's purpose>
  ```
  Subfolders are listed in the parent's README (e.g. `DOCS/README.md` → `PLAN/`; `PLAN/README.md` → `FILE_STRUCTURE/`).
- Root `README.md` is a **minimal human overview**; agent rules live only in `AGENTS/README.md` (single source of truth — avoid duplicating rules across files).

### Interactive approval
- Use `askUser` for any structural/content decision; the user prefers to approve before changes are applied.
- After approval, apply changes and commit+push in the same turn.

## 5. Pending work / next steps

1. **PLAN FILE_STRUCTURE Optimization** (rule in `AGENTS/README.md`) — `DOCS/PLAN/FILE_STRUCTURE/` exists but is empty. Propose the optimization plan and get user approval before applying.
2. **GITHUB/** purpose undefined — candidates: templates + workflows, or rename to `.github/` (GitHub convention). Ask user.
3. **PG01/** is empty — decide whether it becomes a project workspace (e.g. `PG01/DOCS` + `PG01/SRC`).
4. Keep enforcing: reload before thinking, commit+push after every response, self-consistency verification on each session.

## 6. Golden rules recap

- Always fetch GitHub **before** thinking (user edits the repo between sessions — often).
- User's remote edits win conflicts.
- Ask before acting; confirm before committing structural changes.
- Keep `AGENTS/README.md` as the single source of truth for agent instructions.
- Commit and push after finishing each response.

---

*Hand-off written by the previous AI session on 2026-08-19. Continue from here.*
