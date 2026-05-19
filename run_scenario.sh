#!/usr/bin/env bash
# run_scenario.sh — Build and run an oedisi scenario locally.
#
# Usage:
#   ./run_scenario.sh <scenario.json> [components.json]
#
# Defaults:
#   components.json  → <repo-root>/components.json
#

# stop any running processes that could conflict new cosim
pkill -9 helics_broker
pkill -9 python

set -euo pipefail

# ── Args ──────────────────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <scenario.json> [components.json]" >&2
    exit 1
fi

SCENARIO=$(realpath "$1")
REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
COMPONENTS_JSON="${2:-${REPO_ROOT}/components.json}"
COMPONENTS_JSON=$(realpath "$COMPONENTS_JSON")

if [[ ! -f "$SCENARIO" ]]; then
    echo "Error: scenario file not found: $SCENARIO" >&2
    exit 1
fi

# ── 1. Update submodules ──────────────────────────────────────────────────────
echo "==> Updating submodules..."
git -C "$REPO_ROOT" submodule update --init --recursive

# ── 2. Resolve component directories needed by the scenario ──────────────────
echo "==> Resolving components from scenario..."

COMPONENT_DIRS=""
while IFS= read -r comp_type; do
    comp_path=$(grep -oP "\"${comp_type}\"\s*:\s*\"\K[^\"]+" "$COMPONENTS_JSON" 2>/dev/null || true)
    if [[ -z "$comp_path" ]]; then
        echo "WARNING: type '${comp_type}' not found in components.json" >&2
        continue
    fi
    comp_dir=$(dirname "${REPO_ROOT}/${comp_path}")
    if [[ -d "$comp_dir" ]]; then
        COMPONENT_DIRS+="${comp_dir}"$'\n'
    else
        echo "WARNING: component directory not found: ${comp_dir}" >&2
    fi
done < <(grep -oP '"type"\s*:\s*"\K[^"]+' "$SCENARIO" | sort -u)

# ── 3. Install broker + all required components as editable packages ──────────
echo "==> Installing components..."

uv pip install -e "${REPO_ROOT}/Components/broker"

while IFS= read -r component_dir; do
    [[ -z "$component_dir" ]] && continue
    echo "    Installing $(basename "$component_dir")..."
    uv pip install -e "$component_dir"
done <<< "$COMPONENT_DIRS"

# ── 4. Build the scenario ─────────────────────────────────────────────────────
echo "==> Building scenario: $SCENARIO"
cd "$REPO_ROOT"
oedisi build --system "$SCENARIO"

# ── 5. Run ────────────────────────────────────────────────────────────────────
echo "==> Running..."

oedisi run
