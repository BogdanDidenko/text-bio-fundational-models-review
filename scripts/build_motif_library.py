"""Motif library: named, frequent sub-chains of role-aware operations (from scripts/mine_subchains.py).

Each motif is a gapped operation template; a path contains a motif when the template tokens occur in
order (other tokens may sit between them; `contiguous: true` requires adjacency). Support counts
papers. For each motif: member papers/models, archetypes of member routes, interfaces, how often each
template operation's declared parameters are unstated, and one evidence-quoted example.

  python3 scripts/build_motif_library.py
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "analysis/motif_library_2026-10-14"
REL = ROOT / "analysis/operation_decomposition_v32_2026-10-14"
CODEBOOK = ROOT / "analysis/design_taxonomy_2026-10-13/taxonomy_codebook.csv"
DROP = {"source_provenance", "identity"}
BOUNDARY = {"learned_module": "LM", "fusion_unspecified": "FUSE?", "no_catalog_operation": "NOCAT",
            "external_generator": "GEN", "consensus_tie": "TIE"}

MOTIFS = [
    # category, id, name, template, contiguous, description
    ("carrier formation", "M01", "Subset then verbalise", ["B:select", "B:serialize"], False,
     "Keep part of the biological record (top genes, fields, cells) and write it as text."),
    ("carrier formation", "M02", "Ranked gene sentence", ["B:rank", "B:serialize"], False,
     "Order features by value and write the ordered identifiers as text; magnitudes are dropped."),
    ("carrier formation", "M03", "Expression normalisation", ["B:normalize", "B:log_transform"], True,
     "Library-size or similar normalisation followed by a log transform of expression values."),
    ("carrier formation", "M04", "Sample then verbalise", ["B:sample", "B:serialize"], False,
     "Randomly draw cells, examples or negatives and write them into text."),
    ("carrier formation", "M05", "Biological alphabet embedding", ["B:tokenize", "B:lookup"], False,
     "Tokenise a sequence in its own alphabet and look the tokens up in an embedding table."),
    ("carrier formation", "M06", "Text token embedding", ["T:tokenize", "T:lookup"], False,
     "Standard text channel: tokenise text and look the tokens up in the language model's embedding table."),
    ("carrier formation", "M07", "Tile then encode", ["B:partition", "B:LM"], False,
     "Split an image, genome or sequence into patches/windows/chunks and encode them with a learned module."),
    ("encoding", "M08", "Encoder then projector", ["B:LM", "B:project"], False,
     "A learned (often pretrained, frozen) biological encoder followed by a projection into the receiving model's space."),
    ("encoding", "M09", "Projector into the model", ["B:LM", "B:project", "B:LM"], False,
     "Encoder output projected and then consumed by another learned module (typically the language model)."),
    ("encoding", "M10", "Stacked learned modules", ["B:LM", "B:LM"], False,
     "Two or more unexpanded learned modules in sequence (e.g. frozen foundation model then trainable encoder)."),
    ("encoding", "M11", "Domain computation then encoder", ["B:NOCAT", "B:LM"], False,
     "A computation outside the operation catalog (graph convolution, physics terms, clustering) before a learned encoder."),
    ("joining", "M12", "Verbalised biology read by a model", ["B:serialize", "B:LM"], False,
     "Biology written as text and consumed by a learned language model."),
    ("joining", "M13", "Encode then join", ["B:LM", "B:concatenate"], False,
     "Encoded biological representation concatenated with other inputs (text tokens, [CLS], other modalities)."),
    ("joining", "M14", "Encode then add", ["B:LM", "B:add"], False,
     "Encoded representation summed with another representation (positional, prior or other modality)."),
    ("joining", "M15", "Text tokens into the model", ["T:tokenize", "T:LM"], False,
     "Tokenised text read by a learned module."),
]


def contains(seq, template, contiguous):
    if contiguous:
        n = len(template)
        return any(seq[i:i + n] == template for i in range(len(seq) - n + 1))
    it = iter(seq)
    return all(t in it for t in template)


def agent_token_steps(chains):
    """Per agent route: collapsed role-aware tokens with the step that produced each."""
    by_cfg = defaultdict(set)
    for r in chains:
        by_cfg[(r["record_id"], r["configuration_id"])].add("T" if r["source_modality"] == "text" else "B")
    out = []
    for r in chains:
        base = "T" if r["source_modality"] == "text" else "B"
        both = by_cfg[(r["record_id"], r["configuration_id"])] == {"B", "T"}
        toks = []
        for s in r["steps"]:
            if s["category"] in DROP:
                continue
            ops = [(c["operation_id"], c.get("parameter_status", {})) for c in s["calls"]] if s["category"] == "library_operation" else [(BOUNDARY[s["category"]], {})]
            for o, ps in ops:
                role = "X" if o in {"concatenate", "add", "cross_attention", "update", "align", "FUSE?"} and both else base
                tok = f"{role}:{o}"
                if toks and toks[-1][0] == tok:
                    continue
                toks.append((tok, s["step_id"], s["chain_element"], ps))
        out.append((r, toks))
    return out


def main():
    chains = json.loads((M / "chains_1.3.0.json").read_text())
    paths = json.loads((M / "model_paths.json").read_text())
    arche = {}
    with open(CODEBOOK) as f:
        for row in csv.DictReader(f):
            arche[(row["record_id"], row["route_id"])] = row.get("archetype", "")
    agent = agent_token_steps(chains)
    evid = {}
    for rec in {r["record_id"] for r in chains}:
        for d in json.loads((REL / "records" / rec / "consensus_decisions.json").read_text())["decisions"]:
            evid[(rec, d["step_id"])] = d["evidence"]
    papers_total = len({p["record_id"] for p in paths})
    lib = []
    for cat, mid, name, tpl, contig, desc in MOTIFS:
        members = [p for p in paths if p["tokens"] and contains(p["tokens"], tpl, contig)]
        recs = sorted({p["record_id"] for p in members})
        models = sorted({p["model_name"] for p in members})
        ag = [(r, t) for r, t in agent if contains([x[0] for x in t], tpl, contig)]
        arch = Counter(arche.get((r["record_id"], r["route_id"]), "") or "n/a" for r, _ in ag)
        inter = Counter(p["interface"] for p in members if p["source"] == "agent")
        unstated = defaultdict(Counter)
        example = None
        for r, toks in ag:
            names = [x[0] for x in toks]
            for x in toks:
                if x[0] in tpl:
                    for pn, st in x[3].items():
                        unstated[f"{x[0].split(':', 1)[1]}.{pn}"][st] += 1
            if example is None:
                # first occurrence of the template: matching steps in order
                it, picked = 0, []
                for x in toks:
                    if it < len(tpl) and x[0] == tpl[it]:
                        picked.append(x)
                        it += 1
                if it == len(tpl):
                    ev = evid.get((r["record_id"], picked[0][1])) or [{}]
                    example = {"record_id": r["record_id"], "model_name": r["model_name"], "route_id": r["route_id"],
                               "steps": [{"token": x[0], "step_id": x[1], "chain_element": x[2]} for x in picked],
                               "evidence_quote": ev[0].get("quote"), "section_id": ev[0].get("section_id")}
        lib.append({"category": cat, "motif_id": mid, "name": name, "template": tpl, "contiguous": contig, "description": desc,
                    "papers": len(recs), "papers_share": round(len(recs) / papers_total, 3), "models": len(models),
                    "pilot_papers": len({p["record_id"] for p in members if p["source"] == "pilot"}),
                    "record_ids": recs, "model_names": models, "archetypes_of_agent_routes": dict(arch),
                    "interfaces_of_agent_routes": dict(inter),
                    "unstated_parameter_share": {k: round(v["unspecified"] / sum(v.values()), 2) for k, v in sorted(unstated.items()) if sum(v.values()) >= 3},
                    "example": example})
    # paper-level co-occurrence and coverage
    per_paper = defaultdict(set)
    for m in lib:
        for r in m["record_ids"]:
            per_paper[r].add(m["motif_id"])
    coverage = {"papers_total": papers_total, "papers_with_any_motif": len(per_paper),
                "motifs_per_paper": dict(Counter(len(v) for v in per_paper.values())),
                "papers_without_motif": sorted({p["record_id"] for p in paths} - set(per_paper))}
    (M / "motifs.json").write_text(json.dumps({"motifs": lib, "coverage": coverage, "paper_motifs": {k: sorted(v) for k, v in per_paper.items()}},
                                              ensure_ascii=False, indent=1))
    print(json.dumps({m["motif_id"]: m["papers"] for m in lib}), json.dumps({k: v for k, v in coverage.items() if k != "papers_without_motif"}))


if __name__ == "__main__":
    main()
