#!/usr/bin/env python3
"""Build the curated Zenodo snapshot of this repository at one commit.

The snapshot leaves out third-party material that the repository holds for the review work:

* full_text                 text converted from the full texts of reviewed papers (Docling output,
                            document graphs and their provenance chunks);
* paper_sections            sections of reviewed papers that were passed to full-text screening;
* paper_figures_and_crops   figure images, crops, tiles and contact sheets taken from reviewed papers;
* llm_run_logs              raw LLM run logs (prompts, transcripts, stderr) that embed paper text;
* personal_documents        the author's conference-abstract submission packages (contact details;
                            a separate deliverable, not review data).

The structured outputs of the same runs (decisions, routes, evidence quotes, assemblies, catalogs)
are kept. In kept JSON files, fields that hold full-text sections are replaced by a marker that
records the length and SHA-256 of the omitted text. Every excluded or redacted file is listed with
its size and hashes, so the snapshot can be matched file by file against the Git commit.

Usage:
    python scripts/build_zenodo_snapshot.py --commit <sha> --out <dir> [--readme-template <md>] [--dry-run]

Outputs in <dir> (the four manifests are also written into the zip with the prefix ZENODO_):
    <name>-<commit8>.zip        curated tree under a single top-level folder
    EXCLUDED_FILES.csv          path, bytes, git blob, sha256, category, reason
    REDACTED_FILES.csv          path, original and redacted hashes, fields and characters redacted
    INCLUDED_FILES.csv          path, bytes, git blob, sha256 in the zip, redacted flag
    INCLUDED_FILES.sha256       sha256 and path of every file in the zip (shasum -a 256 -c)
    README.md                   filled from --readme-template ({placeholders} from the summary)
    snapshot_summary.json       counts and sizes per category
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
import zipfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

IMAGE = re.compile(r"\.(png|jpe?g|webp|gif|tiff?|bmp)$", re.I)
# Images made by this project: charts, flow diagrams, manuscript figures, conference figures and
# renders, screenshots of the project's own web pages, the site preview card.
OWN_IMAGE = re.compile(
    r"^(analysis/[^/]+/(v\d+/)?figures/"
    r"|analysis/(prisma_flow_2026-10-07|review_synthesis_2026-10-07|design_taxonomy_2026-10-13|motif_library_2026-10-14)/[^/]+\.png$"
    r"|manuscript/"
    r"|.*browser_qa[^/]*\.png$|.*/browser_qa/"
    r"|.*/social-preview\.png$)"
)
PERSONAL = re.compile(r"^data/health_intelligence_conference_2026_[^/]+/")
RULES: list[tuple[str, re.Pattern[str]]] = [
    ("full_text", re.compile(r"^data/docling_(include|uncertain)[^/]*/")),
    ("full_text", re.compile(r"^data/living_catalog_updates/update_2026-08-09/(05_fulltext|06_docling_screening|11_docling_vlm)[^/]*/")),
    ("full_text", re.compile(r"_docling_json_\d{8}_\d{6}/(docling|docling_graph|debug)/")),
    ("full_text", re.compile(r"\.dclg$")),
    ("paper_sections", re.compile(r"^data/fulltext_screening_context_[^/]+/")),
    ("paper_sections", re.compile(r"^data/docling_graph_screening_evidence_full_[^/]+/")),
    ("paper_sections", re.compile(r"^data/living_catalog_updates/update_2026-08-09/(07_graph_sections|08_section_input)[^/]*/")),
    ("llm_run_logs", re.compile(r"(^|/)(role_logs|subagents)/")),
    ("llm_run_logs", re.compile(r"(^|/)(prompt\.txt|stdout\.jsonl|stdout\.log|stderr\.log|llm_calls\.jsonl)$")),
    ("llm_run_logs", re.compile(r"role_logs\.tar\.gz$")),
]
# Metadata files that stay even inside excluded folders (no paper text).
KEEP_IN_EXCLUDED = re.compile(r"(^|/)(README\.md|[^/]*manifest[^/]*\.(csv|json|md)|[^/]*mapping[^/]*\.(csv|json|md)|metadata\.json)$|/manifests/")
REASON = {
    "full_text": "Text converted from the full text of a reviewed paper (Docling output, document graph or its provenance chunks); third-party copyright.",
    "paper_sections": "Sections of reviewed papers selected for full-text screening; third-party copyright.",
    "paper_figures_and_crops": "Figure image, crop, tile or contact sheet taken from a reviewed paper; third-party copyright.",
    "llm_run_logs": "Raw LLM run log (prompt, transcript or stderr) that embeds paper text; the structured outputs of the run are kept.",
    "personal_documents": "Conference-abstract submission package of the author (contact details); a separate deliverable, not review data.",
}
# Redaction inside kept JSON/JSONL files.
REDACT_KEYS = {"selected_full_text_sections", "full_text_context", "text_content"}
REDACT_TEXT_UNDER = {
    "section_evidence", "derived_full_section", "data_source_sections", "input_representation_sections",
    "data_source_chunks", "input_representation_chunks", "sections_for_screening",
    "primary_data_source_chunk", "primary_input_representation_chunk", "chunks", "pages",
}
MARKER = "[omitted from the Zenodo snapshot: third-party full-text excerpt, {n} characters, sha256 {h}]"


def classify(path: str) -> str | None:
    if PERSONAL.search(path):
        return "personal_documents"
    if IMAGE.search(path):
        return None if OWN_IMAGE.search(path) else "paper_figures_and_crops"
    for name, rx in RULES:
        if rx.search(path):
            if name in ("full_text", "paper_sections") and KEEP_IN_EXCLUDED.search(path) and not path.endswith(".dclg"):
                return None
            return name
    return None


def redact(obj, ancestors: tuple[str, ...], stats: Counter):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, str) and v and (k in REDACT_KEYS or (k == "text" and REDACT_TEXT_UNDER.intersection(ancestors))):
                stats["fields"] += 1
                stats["chars"] += len(v)
                out[k] = MARKER.format(n=len(v), h=hashlib.sha256(v.encode("utf-8")).hexdigest())
            else:
                out[k] = redact(v, ancestors + (str(k),), stats)
        return out
    if isinstance(obj, list):
        return [redact(v, ancestors, stats) for v in obj]
    return obj


def redact_bytes(path: str, data: bytes) -> tuple[bytes, Counter]:
    stats: Counter = Counter()
    text = data.decode("utf-8")
    if path.endswith(".json"):
        obj = json.loads(text)
        new = redact(obj, (), stats)
        if not stats["fields"]:
            return data, stats
        return (json.dumps(new, ensure_ascii=False, indent=2) + "\n").encode("utf-8"), stats
    lines_out = []
    for line in text.splitlines():
        if not line.strip():
            lines_out.append(line)
            continue
        new = redact(json.loads(line), (), stats)
        lines_out.append(json.dumps(new, ensure_ascii=False))
    if not stats["fields"]:
        return data, stats
    return ("\n".join(lines_out) + "\n").encode("utf-8"), stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--tag", default="", help="Optional Git tag that names the full tree on GitHub")
    ap.add_argument("--readme-template", type=Path, help="Markdown template for ZENODO_README.md")
    ap.add_argument("--extra", action="append", default=[], metavar="KEY=VALUE", help="Additional template value (repeatable)")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--name", default="text-bio-foundation-models-review")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", args.commit], capture_output=True, text=True, check=True).stdout.strip()
    blobs = {}
    for line in subprocess.run(["git", "-C", str(REPO), "ls-tree", "-r", "-l", commit], capture_output=True, text=True, check=True).stdout.splitlines():
        meta, path = line.split("\t", 1)
        blobs[path] = meta.split()[2]
    args.out.mkdir(parents=True, exist_ok=True)
    folder = f"{args.name}-{commit[:8]}"
    tar_bytes = subprocess.run(["git", "-C", str(REPO), "archive", "--format=tar", commit], capture_output=True, check=True).stdout
    excluded, redacted, included = [], [], []
    summary = Counter()
    sizes = Counter()
    zf = None if args.dry_run else zipfile.ZipFile(args.out / f"{folder}.zip", "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9)
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
        for member in tar:
            if member.issym():
                # Symbolic links are stored as zip symlink entries (target path as content).
                data = member.linkname.encode("utf-8")
                included.append((hashlib.sha256(data).hexdigest(), member.name, len(data), blobs.get(member.name, ""), "symlink"))
                summary["included"] += 1
                if zf:
                    info = zipfile.ZipInfo(f"{folder}/{member.name}", date_time=(2026, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.external_attr = 0o120777 << 16
                    zf.writestr(info, data)
                continue
            if not member.isfile():
                continue
            path = member.name
            data = tar.extractfile(member).read()
            sha = hashlib.sha256(data).hexdigest()
            cat = classify(path)
            if cat:
                excluded.append([path, len(data), blobs.get(path, ""), sha, cat, REASON[cat]])
                summary[cat] += 1
                sizes[cat] += len(data)
                continue
            if re.search(r"\.(json|jsonl)$", path):
                try:
                    new, st = redact_bytes(path, data)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    new, st = data, Counter()
                if st["fields"]:
                    redacted.append([path, len(data), blobs.get(path, ""), sha, len(new), hashlib.sha256(new).hexdigest(), st["fields"], st["chars"]])
                    summary["redacted"] += 1
                    data = new
            included.append((hashlib.sha256(data).hexdigest(), path, len(data), blobs.get(path, ""), "yes" if (redacted and redacted[-1][0] == path) else "no"))
            summary["included"] += 1
            sizes["included"] += len(data)
            if zf:
                info = zipfile.ZipInfo(f"{folder}/{path}", date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (member.mode & 0o777 | 0o100000) << 16
                zf.writestr(info, data)
    with open(args.out / "EXCLUDED_FILES.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "bytes", "git_blob_sha1", "sha256", "category", "reason"])
        w.writerows(sorted(excluded))
    with open(args.out / "REDACTED_FILES.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "original_bytes", "original_git_blob_sha1", "original_sha256", "redacted_bytes", "redacted_sha256", "fields_redacted", "characters_redacted"])
        w.writerows(sorted(redacted))
    with open(args.out / "INCLUDED_FILES.sha256", "w", encoding="utf-8") as fh:
        for sha, path, _size, _blob, kind in sorted(included, key=lambda x: x[1]):
            if kind != "symlink":
                fh.write(f"{sha}  {folder}/{path}\n")
    with open(args.out / "INCLUDED_FILES.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "bytes", "git_blob_sha1", "sha256", "redacted"])
        for sha, path, size, blob, red in sorted(included, key=lambda x: x[1]):
            w.writerow([path, size, blob, sha, red])
    result = {
        "commit": commit,
        "tag": args.tag,
        "folder": folder,
        "files_in_commit": len(blobs),
        "included_files": summary["included"],
        "included_bytes": sizes["included"],
        "redacted_files": summary["redacted"],
        "excluded": {k: {"files": summary[k], "bytes": sizes[k]} for k in REASON},
    }
    if args.readme_template:
        fill = {
            "commit": commit, "commit8": commit[:8], "tag": args.tag or "(none)", "folder": folder,
            "files_in_commit": f"{len(blobs):,}", "included_files": f"{summary['included']:,}",
            "symlinks": f"{sum(1 for x in included if x[4] == 'symlink'):,}",
            "included_mb": f"{sizes['included'] / 1e6:,.1f}", "redacted_files": f"{summary['redacted']:,}",
            "excluded_files": f"{sum(summary[k] for k in REASON):,}", "excluded_mb": f"{sum(sizes[k] for k in REASON) / 1e6:,.1f}",
        }
        for item in args.extra:
            key, _, value = item.partition("=")
            fill[key] = value
        for k in REASON:
            fill[f"{k}_files"] = f"{summary[k]:,}"
            fill[f"{k}_mb"] = f"{sizes[k] / 1e6:,.1f}"
        (args.out / "README.md").write_text(args.readme_template.read_text(encoding="utf-8").format(**fill), encoding="utf-8")
    if zf:
        if args.readme_template:
            zf.write(args.out / "README.md", f"{folder}/ZENODO_README.md")
        for extra in ("EXCLUDED_FILES.csv", "REDACTED_FILES.csv", "INCLUDED_FILES.csv", "INCLUDED_FILES.sha256"):
            zf.write(args.out / extra, f"{folder}/ZENODO_{extra}")
        zf.write(Path(__file__).resolve(), f"{folder}/ZENODO_build_zenodo_snapshot.py")
        zf.close()
        result["zip_bytes"] = (args.out / f"{folder}.zip").stat().st_size
    (args.out / "snapshot_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
