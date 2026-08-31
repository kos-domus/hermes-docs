#!/usr/bin/env python3
"""Regenerate docs/index.yaml from frontmatter of all docs. Cron-safe, line-based parser."""
import os

DOCS = "/home/kos/job-desk/hermes-docs/docs"
ORDER = ["getting-started", "guides", "reference", "concepts", "troubleshooting"]
entries = []

def parse_frontmatter(path):
    fields = {}
    tags = []
    with open(path) as f:
        lines = f.read().splitlines()
    if not lines or lines[0] != "---":
        return None, None
    key = None
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("- ") and key == "tags":
            tags.append(line[2:].strip().strip('"').strip("'"))
        elif line.startswith("- ") and key == "sources":
            continue
        elif ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1]
                fields[key] = [v.strip().strip('"').strip("'") for v in inner.split(",")]
            else:
                fields[key] = val.strip('"').strip("'")
    if tags or "tags" not in fields:
        fields["tags"] = tags
    return fields, None

for cat in ORDER:
    catdir = os.path.join(DOCS, cat)
    if not os.path.isdir(catdir):
        continue
    for fn in sorted(os.listdir(catdir)):
        if not fn.endswith(".md"):
            continue
        fm, _ = parse_frontmatter(os.path.join(catdir, fn))
        if fm is None:
            print("NO FRONTMATTER:", fn)
            continue
        entries.append({
            "slug": fm["slug"],
            "title": fm["title"],
            "category": cat,
            "tags": fm["tags"],
            "path": "docs/" + cat + "/" + fn,
            "last_updated": fm["last_updated"],
            "version": fm["version"],
            "hvm": fm["hermes_version_min"],
        })

slugs = [e["slug"] for e in entries]
dupes = [s for s in set(slugs) if slugs.count(s) > 1]
assert not dupes, "DUPLICATE SLUGS: %s" % dupes
for e in entries:
    for k in ("slug", "title", "last_updated", "version", "hvm"):
        assert e[k], "MISSING %s in %s" % (k, e["path"])

out = ["generated_at: '2026-08-31'", "doc_count: %d" % len(entries), "categories:"]
out += ["- " + c for c in ORDER]
out.append("docs:")
for e in entries:
    out.append("- slug: " + e["slug"])
    out.append("  title: " + e["title"])
    out.append("  category: " + e["category"])
    out.append("  tags:")
    for t in e["tags"]:
        out.append("  - " + t)
    out.append("  path: " + e["path"])
    out.append("  last_updated: '" + e["last_updated"] + "'")
    out.append("  version: " + e["version"])
    out.append("  hermes_version_min: " + e["hvm"])

with open(os.path.join(DOCS, "index.yaml"), "w") as f:
    f.write("\n".join(out) + "\n")

print("Wrote index.yaml with %d docs" % len(entries))
for e in entries:
    print("  %-42s v%s %s [%s] tags=%d" % (e["slug"], e["version"], e["last_updated"], e["category"], len(e["tags"])))
