#!/usr/bin/env bash
# Self-constructing folder tool.
#
# Pseudocode contract:
#   selfConstructor(nameOfFolder().newFile("nameOfFolder.md")); newSession.Reload();
#
# Creates one or more folders, gives each one its canonical descriptor, keeps the
# parent descriptor's subfolder index truthful, and then reloads session state by
# re-deriving Git and repository consistency.

set -euo pipefail

SCRIPT_NAME=$(basename "$0")

usage() {
	cat <<'USAGE'
Usage: SRC/tools/script.sh [options] NAME [NAME...]

Self-construct folders with their canonical descriptor, then reload session state.

Options:
  -r, --root DIR         repository root (default: Git top level, else the tool's ../..)
  -p, --parent DIR       parent folder, relative to the root (default: the root)
  -d, --descriptor MODE  'self' for NAME/NAME.md, 'readme' for NAME/README.md (default: self)
  -t, --title TEXT       descriptor heading (default: NAME)
  -s, --summary TEXT     descriptor first paragraph (default: "NAME folder.")
  -m, --metadata "K: V"  add a '- **K:** V' bullet; repeatable
  -i, --index MODE       'auto' updates the parent descriptor index, 'skip' leaves it (default: auto)
  -f, --force            rewrite an existing descriptor
  -n, --dry-run          print planned actions without touching the working copy
      --describe         include repository self-description in the reload
      --no-reload        skip the session reload
  -h, --help             show this help

Exit status: 0 success, 1 reload verification findings, 2 usage or environment error.
USAGE
}

fail() {
	printf '%s: error: %s\n' "$SCRIPT_NAME" "$1" >&2
	exit 2
}

note() {
	printf '%s\n' "$1"
}

root=""
parent="."
descriptor_mode="self"
title=""
summary=""
index_mode="auto"
force="no"
dry_run="no"
describe="no"
reload="yes"
metadata=()
names=()

while [ "$#" -gt 0 ]; do
	case "$1" in
	-r | --root)
		[ "$#" -ge 2 ] || fail "$1 requires a value"
		root="$2"
		shift 2
		;;
	-p | --parent)
		[ "$#" -ge 2 ] || fail "$1 requires a value"
		parent="$2"
		shift 2
		;;
	-d | --descriptor)
		[ "$#" -ge 2 ] || fail "$1 requires a value"
		descriptor_mode="$2"
		shift 2
		;;
	-t | --title)
		[ "$#" -ge 2 ] || fail "$1 requires a value"
		title="$2"
		shift 2
		;;
	-s | --summary)
		[ "$#" -ge 2 ] || fail "$1 requires a value"
		summary="$2"
		shift 2
		;;
	-m | --metadata)
		[ "$#" -ge 2 ] || fail "$1 requires a value"
		metadata+=("$2")
		shift 2
		;;
	-i | --index)
		[ "$#" -ge 2 ] || fail "$1 requires a value"
		index_mode="$2"
		shift 2
		;;
	-f | --force)
		force="yes"
		shift
		;;
	-n | --dry-run)
		dry_run="yes"
		shift
		;;
	--describe)
		describe="yes"
		shift
		;;
	--no-reload)
		reload="no"
		shift
		;;
	-h | --help)
		usage
		exit 0
		;;
	--)
		shift
		while [ "$#" -gt 0 ]; do
			names+=("$1")
			shift
		done
		;;
	-*)
		fail "unknown option: $1"
		;;
	*)
		names+=("$1")
		shift
		;;
	esac
done

[ "${#names[@]}" -gt 0 ] || {
	usage >&2
	fail "at least one folder name is required"
}

case "$descriptor_mode" in
self | readme) ;;
*) fail "--descriptor must be 'self' or 'readme'" ;;
esac

case "$index_mode" in
auto | skip) ;;
*) fail "--index must be 'auto' or 'skip'" ;;
esac

if [ -z "$root" ]; then
	tool_dir=$(cd "$(dirname "$0")" && pwd)
	root=$(git -C "$tool_dir" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$tool_dir/../..")
fi
root=$(cd "$root" 2>/dev/null && pwd) || fail "root is not a directory: $root"

parent_dir="$root/$parent"
parent_dir=$(cd "$parent_dir" 2>/dev/null && pwd) || fail "parent folder does not exist: $parent"
case "$parent_dir" in
"$root" | "$root"/*) ;;
*) fail "parent folder is outside the root: $parent" ;;
esac

relative_to_root() { # absolute path -> repository-relative POSIX path ("." for the root)
	local path="$1"
	if [ "$path" = "$root" ]; then
		printf '.'
	else
		printf '%s' "${path#"$root"/}"
	fi
}

parent_relative=$(relative_to_root "$parent_dir")

parent_descriptor() { # echo the parent's canonical descriptor, or nothing
	local base
	base=$(basename "$parent_dir")
	if [ -f "$parent_dir/README.md" ]; then
		printf '%s' "$parent_dir/README.md"
	elif [ "$parent_dir" != "$root" ] && [ -f "$parent_dir/$base.md" ]; then
		printf '%s' "$parent_dir/$base.md"
	fi
}

descriptor_body() { # $1 title, $2 summary, $3 optional first line
	local heading="$1" text="$2" first="$3" item
	if [ -n "$first" ]; then
		printf '%s\n\n' "$first"
	fi
	printf '# %s\n\n' "$heading"
	if [ "${#metadata[@]}" -gt 0 ]; then
		for item in "${metadata[@]}"; do
			printf -- '- **%s:** %s\n' "${item%%:*}" "$(printf '%s' "${item#*:}" | sed 's/^[[:space:]]*//')"
		done
		printf '\n'
	fi
	printf '%s\n' "$text"
}

index_bullet() { # $1 descriptor path relative to the root, $2 href, $3 summary
	printf -- '- [`%s`](%s) — %s\n' "$1" "$2" "$3"
}

append_index_entry() { # $1 parent descriptor, $2 bullet
	local file="$1" bullet="$2"
	if grep -q '^Subfolders:$' "$file"; then
		awk -v bullet="$bullet" '
			{ lines[NR] = $0 }
			/^Subfolders:$/ { section = NR }
			END {
				insert = section
				if (section > 0) {
					i = section + 1
					while (i <= NR && (lines[i] ~ /^[-*] / || lines[i] ~ /^[[:space:]]+[^[:space:]]/)) {
						insert = i
						i++
					}
				}
				for (n = 1; n <= NR; n++) {
					print lines[n]
					if (n == insert) print bullet
				}
			}
		' "$file" >"$file.tmp" && mv "$file.tmp" "$file"
	else
		if [ -s "$file" ] && [ "$(tail -c 1 "$file")" != "" ]; then
			printf '\n' >>"$file"
		fi
		printf '\nSubfolders:\n%s\n' "$bullet" >>"$file"
	fi
}

created=0
skipped=0

for name in "${names[@]}"; do
	case "$name" in
	"" | "." | ".." | */* | .*)
		fail "invalid folder name: $name"
		;;
	esac

	folder="$parent_dir/$name"
	if [ "$descriptor_mode" = "readme" ]; then
		descriptor="$folder/README.md"
	else
		descriptor="$folder/$name.md"
	fi
	folder_relative=$(relative_to_root "$folder")
	descriptor_relative=$(relative_to_root "$descriptor")
	entry_title="${title:-$name}"
	entry_summary="${summary:-$name folder.}"
	first_line=""
	if [ "$(basename "$descriptor")" = "README.md" ]; then
		first_line="/$descriptor_relative"
	fi

	note "selfConstructor: $folder_relative/ -> $descriptor_relative"
	if [ -e "$descriptor" ] && [ "$force" != "yes" ]; then
		note "  descriptor already exists; use --force to rewrite"
		skipped=$((skipped + 1))
	elif [ "$dry_run" = "yes" ]; then
		note "  dry run: would create the folder and write the descriptor"
	else
		mkdir -p "$folder"
		descriptor_body "$entry_title" "$entry_summary" "$first_line" >"$descriptor"
		note "  wrote $descriptor_relative"
		created=$((created + 1))
	fi

	if [ "$index_mode" = "skip" ]; then
		continue
	fi
	index_file=$(parent_descriptor)
	if [ -z "$index_file" ]; then
		note "  parent has no descriptor; index not updated: $parent_relative"
		continue
	fi
	index_relative=$(relative_to_root "$index_file")
	if grep -qF "$name/" "$index_file"; then
		note "  index already names $name/ in $index_relative"
		continue
	fi
	href="$name/$(basename "$descriptor")"
	bullet=$(index_bullet "$descriptor_relative" "$href" "$entry_summary")
	if [ "$dry_run" = "yes" ]; then
		note "  dry run: would index $name/ in $index_relative"
	else
		append_index_entry "$index_file" "$bullet"
		note "  indexed $name/ in $index_relative"
	fi
done

note "selfConstructor: $created created, $skipped skipped"

if [ "$reload" != "yes" ]; then
	exit 0
fi

note ""
note "newSession.Reload()"
branch=$(git -C "$root" branch --show-current 2>/dev/null || true)
note "- branch: ${branch:-not detected}"
if git -C "$root" rev-parse --git-dir >/dev/null 2>&1; then
	git -C "$root" status --short --branch | sed 's/^/  /'
fi
for context in AGENTS/README.md AGENTS/HAND-OFF/SESSION_CONTEXT.md DOCS/PLAN/README.md; do
	if [ -f "$root/$context" ]; then
		note "- re-read: $context"
	fi
done

verifier="$root/SRC/tools/self_consistency.py"
if [ ! -f "$verifier" ]; then
	note "- verifier not found; reload is incomplete"
	exit 0
fi

if [ "$describe" = "yes" ]; then
	python3 "$verifier" --root "$root" --describe && status=0 || status=$?
else
	python3 "$verifier" --root "$root" && status=0 || status=$?
fi
exit "$status"
