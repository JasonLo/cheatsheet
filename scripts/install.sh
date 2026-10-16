#!/bin/sh
# cheatsheet installer. This script clones this repo locally. It imports the
# index into your user-level ~/.claude/CLAUDE.md. Then coding agents know the
# cheatsheets. To get the latest cheatsheets, run the script again.
#
#   curl -fsSL https://raw.githubusercontent.com/JasonLo/cheatsheet/main/scripts/install.sh | sh
#
# To change the locations, set these env vars:
#   CHEATSHEET_DIR  install location   (default: ~/.cheatsheet)
#   CLAUDE_MD       target memory file (default: ~/.claude/CLAUDE.md)
set -eu

REPO_URL="${CHEATSHEET_REPO:-https://github.com/JasonLo/cheatsheet.git}"
INSTALL_DIR="${CHEATSHEET_DIR:-$HOME/.cheatsheet}"
CLAUDE_MD="${CLAUDE_MD:-$HOME/.claude/CLAUDE.md}"
INDEX_PATH="$INSTALL_DIR/index.md"
BEGIN="<!-- cheatsheet:begin (managed by install.sh) -->"
END="<!-- cheatsheet:end -->"

info() { printf '\033[1;34m==>\033[0m %s\n' "$1"; }
err()  { printf '\033[1;31merror:\033[0m %s\n' "$1" >&2; exit 1; }

command -v git >/dev/null 2>&1 || err "git is required but was not found on PATH."

# 1. Clone the cheatsheet repo. If the clone exists, fast-forward it.
if [ -d "$INSTALL_DIR/.git" ]; then
  info "Updating existing cheatsheet in $INSTALL_DIR"
  git -C "$INSTALL_DIR" pull --ff-only --quiet
else
  info "Cloning cheatsheet into $INSTALL_DIR"
  git clone --depth 1 --quiet "$REPO_URL" "$INSTALL_DIR"
fi

[ -f "$INDEX_PATH" ] || err "index.md not found at $INDEX_PATH after install."

# 2. Add or update the @import block in CLAUDE.md. The markers make this step idempotent.
mkdir -p "$(dirname "$CLAUDE_MD")"
touch "$CLAUDE_MD"

block="$BEGIN
## Cheatsheets

@$INDEX_PATH

If the index lists a cheatsheet that is related to the task, read that cheatsheet before you act.
$END"

if grep -qF "$BEGIN" "$CLAUDE_MD"; then
  info "Refreshing cheatsheet block in $CLAUDE_MD"
  tmp="$(mktemp)"
  awk -v b="$BEGIN" -v e="$END" '
    $0==b {skip=1}
    skip {if ($0==e) skip=0; next}
    {print}
  ' "$CLAUDE_MD" > "$tmp"
  printf '%s\n' "$block" >> "$tmp"
  mv "$tmp" "$CLAUDE_MD"
else
  info "Adding cheatsheet block to $CLAUDE_MD"
  printf '\n%s\n' "$block" >> "$CLAUDE_MD"
fi

info "Done. The cheatsheet index is imported into $CLAUDE_MD."
printf '    Re-run this installer any time to pull the latest cheatsheets.\n'
printf '    Uninstall with: %s/scripts/uninstall.sh\n' "$INSTALL_DIR"
