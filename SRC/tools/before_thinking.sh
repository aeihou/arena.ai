#!/usr/bin/env bash
# Prompt capture tool.
#
# Pseudocode contract:
#   BeforeThinking.Add(new Prompt);
#
# Appends a verbatim developer prompt to the private prompt store before an agent
# starts reasoning. Source this file to use the function, or run it as a command.
#
#   source SRC/tools/before_thinking.sh
#   BeforeThinking.Add "the next developer prompt"

# Strict mode applies to the command form only; sourcing must not change the
# caller's shell options.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
	set -euo pipefail
fi

BEFORE_THINKING_DEFAULT_STORE="AGENTS/.user/MyPrompts.md"

_before_thinking_usage() {
	cat <<'USAGE'
Usage: SRC/tools/before_thinking.sh [options] PROMPT
       SRC/tools/before_thinking.sh [options] --stdin < prompt.txt
       source SRC/tools/before_thinking.sh && BeforeThinking.Add "PROMPT"

Append a verbatim developer prompt to the private prompt store.

Options:
  -r, --root DIR      repository root (default: Git top level, else the tool's ../..)
  -f, --file PATH     prompt store relative to the root (default: AGENTS/.user/MyPrompts.md)
  -S, --session LABEL session heading (default: today's ISO date)
  -s, --stdin         read the prompt from standard input
  -l, --list          print the stored prompts and exit
  -n, --dry-run       show what would be appended without writing
      --verify        run self-consistency verification after appending
  -h, --help          show this help

Repeating the most recent prompt is ignored, so re-running a session capture is safe.

Exit status: 0 success, 1 verification findings, 2 usage or environment error.
USAGE
}

_before_thinking_fail() {
	printf 'before_thinking: error: %s\n' "$1" >&2
	return 2
}

_before_thinking_root() { # $1 requested root
	local requested="$1" tool_dir
	if [ -n "$requested" ]; then
		(cd "$requested" 2>/dev/null && pwd) || return 1
		return 0
	fi
	tool_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
	git -C "$tool_dir" rev-parse --show-toplevel 2>/dev/null && return 0
	(cd "$tool_dir/../.." && pwd)
}

_before_thinking_header() {
	printf '# My prompts\n\n'
	printf 'Verbatim developer prompts kept for this workspace. Entries are appended by\n'
	printf '`SRC/tools/before_thinking.sh` before an agent starts reasoning, newest last.\n'
}

_before_thinking_last_prompt() { # $1 store
	awk '
		/^```text$/ { collecting = 1; body = ""; first = 1; next }
		/^```$/ { if (collecting) { last = body; collecting = 0 }; next }
		collecting { body = first ? $0 : body "\n" $0; first = 0 }
		END { printf "%s", last }
	' "$1"
}

# BeforeThinking.Add "prompt text" — the function form of the pseudocode.
BeforeThinking.Add() {
	local root="" store_relative="$BEFORE_THINKING_DEFAULT_STORE" session=""
	local prompt="" from_stdin="no" dry_run="no" list="no" verify="no" have_prompt="no"

	while [ "$#" -gt 0 ]; do
		case "$1" in
		-r | --root)
			[ "$#" -ge 2 ] || _before_thinking_fail "$1 requires a value" || return 2
			root="$2"
			shift 2
			;;
		-f | --file)
			[ "$#" -ge 2 ] || _before_thinking_fail "$1 requires a value" || return 2
			store_relative="$2"
			shift 2
			;;
		-S | --session)
			[ "$#" -ge 2 ] || _before_thinking_fail "$1 requires a value" || return 2
			session="$2"
			shift 2
			;;
		-s | --stdin | -)
			from_stdin="yes"
			shift
			;;
		-l | --list)
			list="yes"
			shift
			;;
		-n | --dry-run)
			dry_run="yes"
			shift
			;;
		--verify)
			verify="yes"
			shift
			;;
		-h | --help)
			_before_thinking_usage
			return 0
			;;
		--)
			shift
			if [ "$#" -gt 0 ]; then
				prompt="$1"
				have_prompt="yes"
				shift
			fi
			;;
		-*)
			_before_thinking_fail "unknown option: $1" || return 2
			;;
		*)
			if [ "$have_prompt" = "yes" ]; then
				_before_thinking_fail "only one prompt can be added at a time" || return 2
			fi
			prompt="$1"
			have_prompt="yes"
			shift
			;;
		esac
	done

	root=$(_before_thinking_root "$root") || {
		_before_thinking_fail "root is not a directory"
		return 2
	}
	local store="$root/$store_relative"

	if [ "$list" = "yes" ]; then
		if [ -f "$store" ]; then
			cat "$store"
			return 0
		fi
		_before_thinking_fail "prompt store does not exist: $store_relative"
		return 2
	fi

	if [ "$from_stdin" = "yes" ]; then
		prompt=$(cat)
		have_prompt="yes"
	fi
	if [ "$have_prompt" != "yes" ] || [ -z "${prompt//[[:space:]]/}" ]; then
		_before_thinking_usage >&2
		_before_thinking_fail "a non-empty prompt is required"
		return 2
	fi

	# Keep the text verbatim except for trailing blanks, which are a documented
	# consistency defect in this repository.
	prompt=$(printf '%s\n' "$prompt" | sed 's/[[:space:]]*$//')
	session="${session:-$(date +%F)}"

	if [ -f "$store" ] && [ "$(_before_thinking_last_prompt "$store")" = "$prompt" ]; then
		printf 'BeforeThinking.Add: prompt already recorded as the newest entry\n'
		return 0
	fi

	local number=1
	if [ -f "$store" ]; then
		number=$(($(grep -c '^### Prompt ' "$store" || true) + 1))
	fi

	if [ "$dry_run" = "yes" ]; then
		printf 'BeforeThinking.Add: would append prompt %s to %s under session %s\n' \
			"$number" "$store_relative" "$session"
		return 0
	fi

	mkdir -p "$(dirname "$store")"
	if [ ! -f "$store" ]; then
		_before_thinking_header >"$store"
	fi
	if ! grep -qxF "## Session $session" "$store"; then
		printf '\n## Session %s\n' "$session" >>"$store"
	fi
	{
		printf '\n### Prompt %s\n\n' "$number"
		printf '```text\n%s\n```\n' "$prompt"
	} >>"$store"
	printf 'BeforeThinking.Add: appended prompt %s to %s\n' "$number" "$store_relative"

	if [ "$verify" = "yes" ]; then
		local verifier="$root/SRC/tools/self_consistency.py"
		if [ -f "$verifier" ]; then
			python3 "$verifier" --root "$root" || return 1
		fi
	fi
	return 0
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
	BeforeThinking.Add "$@"
fi
