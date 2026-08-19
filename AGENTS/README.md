# AI instructions

Authoritative operating instructions for Arena agents.

Subfolders:
- [`HAND-OFF/`](HAND-OFF/) — concise state and learned constraints for the next
  agent.

## EverytimeBeforeThink

### Update GitHub `GitHub_User/repo`

### Reload hand-off
Read [`HAND-OFF/README.md`](HAND-OFF/README.md), infer semantic intent, and
continue from current repository reality.

### `self.consistency.selfDescribe()`
Run `python3 SRC/tools/self_consistency.py --describe` to derive the current
branch, inventory, and top-level purposes from the working copy.

### `self.consistency.verify()`
Run `python3 SRC/tools/self_consistency.py` and resolve every finding. Use
`--interactive` when working with a developer or `--report PATH` when a durable
Markdown report is needed.

### Plan next optimization
Maintain the pending-plan section in `DOCS/PLAN/README.md`. Ask the developer
before applying structural decisions.

## EverytimeAfterThink

- Commit.
- Push to GitHub `GitHub_User/repo` on Arena's branch.

Any questions? `askDev`.
