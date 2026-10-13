"""Frequent sub-chains over role-aware operation paths (model_paths.json).

Two pattern types, both with paper-level support (a paper counts once):
- contiguous: consecutive tokens on a path;
- gapped: tokens in order with any other tokens between them (PrefixSpan).
Two token levels: operation (`B:serialize`) and role-aware family (`B:symbolise`).
No limit on pattern length; a pattern is reported when at least --min-papers papers contain it.
Closed patterns only (no super-pattern with the same paper support).

  python3 scripts/mine_subchains.py --paths <model_paths.json> --out <dir> --min-papers 4
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAMILY = {"select": "curate", "sample": "curate", "partition": "curate", "align": "curate",
          "normalize": "value", "log_transform": "value", "bin": "value", "rank": "value", "clamp": "value",
          "impute": "value", "augment": "value",
          "serialize": "symbolise", "tokenize": "symbolise",
          "lookup": "embed", "project": "embed", "self_attention": "embed", "reshape": "embed", "LM": "encoder",
          "cross_attention": "join", "concatenate": "join", "add": "join", "update": "join", "pad": "join", "FUSE?": "join",
          "GEN": "generate", "NOCAT": "other", "TIE": "other"}


def to_family(tok):
    role, op = tok.split(":", 1)
    return f"{role}:{FAMILY[op]}"


def collapse(seq):
    out = []
    for x in seq:
        if not out or out[-1] != x:
            out.append(x)
    return out


def contiguous(paths, min_papers):
    sup = defaultdict(set)
    for rec, seq in paths:
        seen = set()
        for i in range(len(seq)):
            for j in range(i + 1, len(seq) + 1):
                seen.add(tuple(seq[i:j]))
        for p in seen:
            sup[p].add(rec)
    return {p: s for p, s in sup.items() if len(s) >= min_papers}


def prefixspan(paths, min_papers):
    """Gapped sequential patterns; projected database of (path index, start position)."""
    out = {}

    def grow(prefix, proj):
        counts = defaultdict(set)
        firsts = defaultdict(list)
        for idx, start in proj:
            rec, seq = paths[idx]
            seen = set()
            for k in range(start, len(seq)):
                t = seq[k]
                if t not in seen:
                    seen.add(t)
                    counts[t].add(rec)
                    firsts[t].append((idx, k + 1))
        for t, recs in counts.items():
            if len(recs) >= min_papers:
                pat = prefix + (t,)
                out[pat] = recs
                grow(pat, firsts[t])

    grow((), [(i, 0) for i in range(len(paths))])
    return out


def closed(patterns):
    def is_sub(a, b):  # a gapped-subsequence of b
        it = iter(b)
        return all(x in it for x in a)
    keep = {}
    by_support = defaultdict(list)
    for p, s in patterns.items():
        by_support[frozenset(s)].append(p)
    for recs, pats in by_support.items():
        for p in pats:
            if not any(q != p and len(q) > len(p) and is_sub(p, q) for q in pats):
                keep[p] = recs
    return keep


def run(paths_file, min_papers):
    raw = json.loads(paths_file.read_text())
    res = {}
    for level in ("operation", "family"):
        seqs = []
        for p in raw:
            toks = p["tokens"] if level == "operation" else collapse([to_family(t) for t in p["tokens"]])
            if toks:
                seqs.append((p["record_id"], toks))
        for kind, fn in (("contiguous", contiguous), ("gapped", prefixspan)):
            pats = closed(fn(seqs, min_papers))
            res[(level, kind)] = {p: s for p, s in pats.items() if len(p) >= 2}
    return raw, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--min-papers", type=int, default=4)
    a = ap.parse_args()
    raw, res = run(a.paths if a.paths.is_absolute() else ROOT / a.paths, a.min_papers)
    out = a.out if a.out.is_absolute() else ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for (level, kind), pats in res.items():
        for p, s in sorted(pats.items(), key=lambda x: (-len(x[1]), -len(x[0]))):
            rows.append({"level": level, "kind": kind, "pattern": list(p), "papers": len(s), "record_ids": sorted(s)})
    (out / "subchains.json").write_text(json.dumps({"min_papers": a.min_papers, "papers_total": len({p["record_id"] for p in raw}),
                                                    "patterns": rows}, ensure_ascii=False, indent=1))
    print(json.dumps({f"{lv}/{k}": len(v) for (lv, k), v in res.items()}))


if __name__ == "__main__":
    main()
