#!/bin/sh
# cheatsheet uninstaller — removes the @import block from CLAUDE.md and deletes
# the local clone. Mirrors install.sh.
#
#   ~/.cheatsheet/uninstall.sh
#
# Override locations with the same env vars as install.sh:
#   CHEATSHEET_DIR  install location   (default: ~/.cheatsheet)
#   CLAUDE_MD       target memory file (default: ~/.claude/CLAUDE.md)
set -eu

INSTALL_DIR="${CHEATSHEET_DIR:-$HOME/.cheatsheet}"
CLAUDE_MD="${CLAUDE_MD:-$HOME/.claude/CLAUDE.md}"
BEGIN="<!-- cheatsheet:begin (managed by install.sh) -->"
END="<!-- cheatsheet:end -->"

info() { printf '\033[1;34m==>\033[0m %s\n' "$1"; }

# 1. Strip the managed block from CLAUDE.md, if present.
if [ -f "$CLAUDE_MD" ] && grep -qF "$BEGIN" "$CLAUDE_MD"; then
  info "Removing cheatsheet block from $CLAUDE_MD"
  tmp="$(mktemp)"
  awk -v b="$BEGIN" -v e="$END" '
    $0==b {skip=1}
    skip {if ($0==e) skip=0; next}
    {print}
  ' "$CLAUDE_MD" > "$tmp"
  mv "$tmp" "$CLAUDE_MD"
else
  info "No cheatsheet block found in $CLAUDE_MD"
fi

# 2. Remove the local clone.
if [ -d "$INSTALL_DIR" ]; then
  info "Removing $INSTALL_DIR"
  rm -rf "$INSTALL_DIR"
else
  info "No install directory at $INSTALL_DIR"
fi

info "Done. cheatsheet uninstalled."
