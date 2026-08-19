# AGENTS-HAND-OFF.md

> Hand-off document for the next AI agent. Read [`AGENTS/README.md`](README.md) first for authoritative instructions, then read this file to continue where the previous session left off.

---

## 1. What this repo is

`aeihou/arena.ai` acts as persistent memory between AI sessions: each session reloads the repo before thinking and commits/pushes after responding. Work only on the Arena branch assigned to the current session.

## 2. Operating rules (CheckFirst → `AGENTS/README.md`)

Before anything else, **always fetch GitHub first** (`git fetch origin`):

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
├── AEIHOU/AEIHOU.md                  ← owner docs
├── DOCS/
│   ├── README.md
│   └── PLAN/
│       ├── README.md
│       └── FILE_STRUCTURE/README.md  ← file-structure optimization plans (empty)
├── PG01/README.md                    ← Playground 01 (empty)
├── SRC/README.md                     ← source / workspaces (empty)
├── GITHUB/
│   ├── README.md                     ← GitHub-related files
│   └── self-consistency.yml          ← portable Actions workflow template
└── tools/
    ├── README.md                     ← verifier usage
    ├── self_consistency.py           ← portable verifier CLI
    └── test_self_consistency.py      ← standard-library tests
```

## 4. Skills learned this session (so far)

### Git workflow (reliable sync)
- **Before thinking**: fetch the current Arena branch → check `git rev-list --count HEAD..FETCH_HEAD` → if behind, inspect `git diff HEAD FETCH_HEAD` and `git show FETCH_HEAD:<file>` → fast-forward (`git merge --ff-only FETCH_HEAD`).
- **After responding**: `git add -A && git commit` → fetch again → push; if remote advanced, `git rebase FETCH_HEAD` then push.
- **Conflict resolution**: the user's GitHub edits are **authoritative**. Use `git checkout --ours <file>` for files the user changed, keep your changes only where they don't collide. Resume with `GIT_EDITOR=true git rebase --continue`.
- **Cross-session updates**: inspect other remote Arena branches when the user asks to check broadly for updates; infer semantic intent rather than copying malformed or branch-specific text.
- **No PRs** unless explicitly asked. Push only to the current session's assigned Arena branch.

### Self-consistency verification (self.consistency.verify)
- Check for **broken links** (markdown refs to non-existent files).
- Check **naming**: preserve the canonical owner, repository, and GitHub names exactly as documented in the root README.
- Check **every folder self-describes** (README.md or `<NAME>.md` inside).
- Check **no stale `.gitkeep`** when the folder already has real files.
- Check **formatting**: no trailing whitespace, consistent casing (`GitHub`), clean file endings.
- Run `python3 tools/self_consistency.py`; use `--interactive` for a guided report prompt. A portable GitHub Actions template is available in `GITHUB/`, and the verifier is covered by `unittest` tests.

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

1. **PLAN FILE_STRUCTURE Optimization** — define an actionable structure plan in `DOCS/PLAN/FILE_STRUCTURE/` after developer approval.
2. **Activate continuous verification** — install `GITHUB/self-consistency.yml` under `.github/workflows/` when GitHub workflow permissions are available.
3. **PG01 purpose** — decide whether it becomes a project workspace (for example, `PG01/DOCS` plus `PG01/SRC`).
4. Keep `DOCS/PLAN/README.md` current as plans are proposed, approved, completed, or superseded.
5. Keep enforcing: reload before thinking, commit+push after every response, self-consistency verification on each session.

## 6. Golden rules recap

- Always fetch GitHub **before** thinking (user edits the repo between sessions — often).
- User's remote edits win conflicts.
- Ask before acting; confirm before committing structural changes.
- Keep `AGENTS/README.md` as the single source of truth for agent instructions.
- Commit and push after finishing each response.

---

*Hand-off written by the previous AI session on 2026-08-19. Continue from here.*
