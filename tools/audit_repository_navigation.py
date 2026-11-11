"""Audit selected navigation links without fetching sparse Git objects.

Checks inline Markdown links and reference definitions, local path targets,
and materialized Markdown heading/explicit HTML anchors. This is not a full
CommonMark renderer, external URL check, or scientific-status audit.
"""

from __future__ import annotations

import argparse
from collections import Counter
import html
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
NAVIGATION_FILES = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/README.md",
    "ARTIFACT_INDEX.md",
    "STATUS.md",
    "docs/current_bhsm_status.md",
    "docs/REPOSITORY_GUIDE.md",
    "docs/RESEARCH_TOPICS.md",
    "docs/BHSM_ENVELOPE_CLARIFICATION_20261110.md",
    "docs/OPEN_RESEARCH.md",
    "docs/REPOSITORY_CLEANUP_PLAN.md",
    "artifacts/README.md",
    "theory/README.md",
    "museum/README.md",
)


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def paths_from_bytes(value: bytes) -> set[str]:
    return {p.decode("utf-8", errors="surrogateescape") for p in value.split(b"\0") if p}


def prose_lines(text: str):
    """Exclude fenced code while retaining source line numbers."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            run = marker.group(1)
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield number, line


def link_targets(text: str):
    """Yield line and target; balanced parentheses in destinations are kept."""
    for number, original in prose_lines(text):
        line = re.sub(r"(`+).*?\1", "", original)
        definition = re.match(r"^\s{0,3}\[[^\]]+\]:\s*(.*)", line)
        starts = [m.end() for m in re.finditer(r"\]\(", line)]
        if definition:
            starts.append(definition.start(1))
        for start in starts:
            rest = line[start:].lstrip()
            if rest.startswith("<"):
                end = rest.find(">")
                if end > 0:
                    yield number, rest[1:end]
                continue
            chars = []
            depth = 0
            escaped = False
            for char in rest:
                if escaped:
                    chars.append(char)
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char.isspace() or (char == ")" and depth == 0):
                    break
                else:
                    depth += (char == "(") - (char == ")")
                    chars.append(char)
            if chars:
                yield number, "".join(chars)


def anchors(text: str) -> set[str]:
    """GitHub-style heading slugs, duplicate suffixes and explicit HTML IDs."""
    result = set()
    seen: Counter[str] = Counter()
    previous = ""
    for _, line in prose_lines(text):
        result.update(re.findall(r"\b(?:id|name)=[\"']([^\"']+)[\"']", line))
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        heading = match.group(1) if match else None
        if heading is None and previous and re.fullmatch(r"\s{0,3}(?:=+|-+)\s*", line):
            heading = previous
        previous = line.strip()
        if heading is None:
            continue
        heading = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
        heading = html.unescape(re.sub(r"<[^>]+>", "", heading)).lower()
        slug = re.sub(r"[^\w\-\s]", "", heading).replace(" ", "-")
        suffix = seen[slug]
        seen[slug] += 1
        result.add(f"{slug}-{suffix}" if suffix else slug)
    return result


def audit(root: Path = ROOT, selected: tuple[str, ...] = NAVIGATION_FILES) -> dict:
    tracked = paths_from_bytes(git(root, "ls-files", "--cached", "-z"))
    # Only reviewed navigation additions are admitted before staging. An
    # arbitrary untracked file must not hide a broken repository reference.
    known = tracked | {p for p in selected if (root / p).is_file()}
    directories = {"."}
    for path in known:
        parent = PurePosixPath(path).parent
        while str(parent) != ".":
            directories.add(str(parent))
            parent = parent.parent
    failures = []
    unavailable = []
    skipped_external = 0
    checked_links = 0
    checked_fragments = 0
    anchor_cache = {}
    for source in selected:
        file = root / source
        if not file.is_file():
            item = {"source": source, "reason": "navigation_source_not_materialized"}
            (unavailable if source in tracked else failures).append(item)
            continue
        for line, raw_target in link_targets(file.read_text(encoding="utf-8")):
            target = html.unescape(raw_target)
            try:
                url = urlsplit(target)
            except ValueError:
                failures.append({"source": source, "line": line, "target": target, "reason": "invalid_url"})
                continue
            if url.scheme or url.netloc or url.path.startswith("/"):
                skipped_external += 1
                continue
            relative = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(url.path))) if url.path else source
            item = {"source": source, "line": line, "target": target, "resolved_path": relative}
            checked_links += 1
            if relative not in known and relative not in directories:
                failures.append({**item, "reason": "missing_local_target"})
                continue
            if not url.fragment:
                continue
            if relative in directories:
                relative = posixpath.join(relative, "README.md")
            if not relative.lower().endswith(".md"):
                unavailable.append({**item, "reason": "fragment_target_not_markdown"})
                continue
            content = root / relative
            if not content.is_file():
                unavailable.append({**item, "reason": "fragment_content_not_materialized"})
                continue
            if relative not in anchor_cache:
                anchor_cache[relative] = anchors(content.read_text(encoding="utf-8"))
            checked_fragments += 1
            if unquote(url.fragment) not in anchor_cache[relative]:
                failures.append({**item, "reason": "missing_markdown_fragment"})
    return {
        "audit": "repository_navigation",
        "passed": not failures,
        "validation_complete": not unavailable,
        "scope": "Selected inline/reference Markdown links; Git-index paths and materialized heading anchors only. External URLs are not validated.",
        "selected_files": list(selected),
        "local_links_checked": checked_links,
        "markdown_fragments_checked": checked_fragments,
        "external_links_skipped": skipped_external,
        "failures": failures,
        "unavailable_checks": unavailable,
    }


def inventory(root: Path, ref: str) -> dict:
    commit = git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    tree = git(root, "rev-parse", "--verify", f"{commit}^{{tree}}").decode().strip()
    paths = paths_from_bytes(git(root, "ls-tree", "-r", "--name-only", "-z", commit))
    top = Counter(p.split("/", 1)[0] if "/" in p else "[root]" for p in paths)
    extensions = Counter(PurePosixPath(p).suffix.lower() or "[none]" for p in paths)
    return {
        "schema_version": 1,
        "source_commit": commit,
        "source_tree": tree,
        "scope": "Tracked Git-tree paths only; no blob-size reads, artifact generation, or scientific-authority classification.",
        "total_tracked_paths": len(paths),
        "top_level_counts": dict(sorted(top.items())),
        "extension_counts": dict(sorted(extensions.items())),
        "root_files": sorted(p for p in paths if "/" not in p),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD", help="Commit/ref for inventory mode only")
    parser.add_argument("--inventory", type=Path, help="Write deterministic Git-tree inventory JSON instead of auditing links")
    parser.add_argument("--allow-incomplete", action="store_true", help="Allow explicitly reported sparse content omissions; CI requires complete validation by default")
    args = parser.parse_args()
    result = inventory(ROOT, args.ref) if args.inventory else audit()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.inventory:
        args.inventory.parent.mkdir(parents=True, exist_ok=True)
        args.inventory.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if result.get("passed", True) and (
        args.inventory or result["validation_complete"] or args.allow_incomplete
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
