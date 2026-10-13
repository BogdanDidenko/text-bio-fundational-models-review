"""Model-level, role-aware input graphs and their source-to-model paths.

Agent papers: routes of one configuration converge on the receiving model; each route is a path.
Pilot papers: author-curated assemblies are DAGs; every root-to-receipt path is enumerated.
Non-computational steps (source provenance, identity) are dropped; consecutive identical tokens collapse.
Token = <role>:<operation>, role from the modalities feeding the operation:
  B = biological input only, T = text only, X = joins biological and text inputs.
Agent routes: base role from the route's source modality; join-type operations become X when the
configuration has both biological and text routes. Pilot DAGs: X when the operation's ancestors include
both biological and text roots.

  python3 scripts/build_model_graphs.py --chains <chains.json> --out <dir>
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs/input-representation-atlas/component-library/data"
BOUNDARY = {"learned_module": "LM", "fusion_unspecified": "FUSE?", "no_catalog_operation": "NOCAT",
            "external_generator": "GEN", "consensus_tie": "TIE"}
DROP = {"source_provenance", "identity"}
JOIN = {"concatenate", "add", "cross_attention", "update", "align", "FUSE?"}
AUX_PORTS = {"table", "mask", "selectors", "indices", "noise", "availability_context", "identifiers", "key_padding_mask"}
TEXTY = re.compile(r"\b(text|prompt|instruction|question|query|caption|description|summar|annotation|token ids? of text|natural language|sentence)", re.I)


def collapse(seq):
    out = []
    for x in seq:
        if not out or out[-1] != x:
            out.append(x)
    return out


def agent_paths(chains):
    by_cfg = defaultdict(list)
    for r in chains:
        by_cfg[(r["record_id"], r["configuration_id"])].append(r)
    paths = []
    for (rec, cfg), routes in by_cfg.items():
        mods = {"T" if r["source_modality"] == "text" else "B" for r in routes}
        for r in routes:
            base = "T" if r["source_modality"] == "text" else "B"
            toks = []
            for s in r["steps"]:
                if s["category"] in DROP:
                    continue
                ops = [c["operation_id"] for c in s["calls"]] if s["category"] == "library_operation" else [BOUNDARY[s["category"]]]
                for o in ops:
                    role = "X" if o in JOIN and mods == {"B", "T"} else base
                    toks.append(f"{role}:{o}")
            from scripts.build_design_taxonomy import a2 as _a2
            paths.append({"interface": _a2(r)[0], "source": "agent", "record_id": rec, "model_id": r["model_id"], "model_name": r["model_name"],
                          "configuration_id": cfg, "route_id": r["route_id"], "base": base,
                          "config_modalities": "".join(sorted(mods)), "tokens": collapse(toks)})
    return paths


def pilot_paths():
    cat = json.loads((PUBLIC / "catalog.json").read_text())
    pilot = {r for r, v in cat["records"].items() if "decomposition_status" not in v}
    paths = []
    for a in json.loads((PUBLIC / "assemblies.json").read_text()):
        if a["record_id"] not in pilot:
            continue
        nodes = {n["node_id"]: n for n in a["nodes"]}
        made_by, consumers, primary = {}, defaultdict(list), set()
        for c in a["calls"]:
            for ns in c["outputs"].values():
                for n in ns:
                    made_by[n] = c
            for port, ns in c["inputs"].items():
                for n in ns:
                    consumers[n].append(c)
                    if port not in AUX_PORTS:
                        primary.add(n)
        roots = [n for n in nodes if n not in made_by and n in primary]
        root_mod = {n: ("T" if TEXTY.search(f"{nodes[n].get('representation_type', '')} {nodes[n].get('information_content', '')}") else "B") for n in roots}
        anc = {}

        def ancestry(n, seen=()):
            if n in anc:
                return anc[n]
            if n not in made_by:
                anc[n] = {root_mod.get(n, "B")} if n in root_mod else set()
                return anc[n]
            out = set()
            for port, ns in made_by[n]["inputs"].items():
                for m in ns:
                    if m not in seen and port not in AUX_PORTS:
                        out |= ancestry(m, seen + (n,))
            anc[n] = out
            return out

        receipt = {o["node_id"] for o in a["receipt_inputs"]}

        def walk(node, toks, depth_guard):
            if node in receipt or not consumers.get(node):
                if toks:
                    yield toks
                if node in receipt:
                    return
            for c in consumers.get(node, []):
                if c["call_id"] in depth_guard:
                    continue
                ins = {m for port, ns in c["inputs"].items() if port not in AUX_PORTS for m in ns}
                mods = set().union(*(ancestry(m) for m in ins)) if ins else set()
                role = "X" if mods == {"B", "T"} else (next(iter(mods)) if mods else "B")
                tok = f"{role}:{c['operation_id'] or 'LM'}"
                for out_n in {m for ns in c["outputs"].values() for m in ns}:
                    yield from walk(out_n, toks + [tok], depth_guard | {c["call_id"]})

        seen_paths = set()
        for rt in roots:
            for toks in walk(rt, [], frozenset()):
                key = tuple(collapse(toks))
                if key in seen_paths:
                    continue
                seen_paths.add(key)
                paths.append({"interface": "graph", "source": "pilot", "record_id": a["record_id"], "model_id": a["model_variant"],
                              "model_name": a["model_variant"], "configuration_id": a["trajectory_id"],
                              "route_id": f"{a['trajectory_id']}::{rt}", "base": root_mod[rt],
                              "config_modalities": "".join(sorted(set(root_mod.values()))), "tokens": list(key)})
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chains", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    chains = json.loads((a.chains if a.chains.is_absolute() else ROOT / a.chains).read_text())
    out = a.out if a.out.is_absolute() else ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    paths = agent_paths(chains) + pilot_paths()
    graphs = defaultdict(lambda: {"paths": 0, "bio_paths": 0, "text_paths": 0, "join_ops": 0})
    for p in paths:
        g = graphs[f"{p['record_id']}|{p['configuration_id']}"]
        g.update(record_id=p["record_id"], model_name=p["model_name"], source=p["source"])
        g["paths"] += 1
        g["bio_paths" if p["base"] == "B" else "text_paths"] += 1
        g["join_ops"] += sum(t.startswith("X:") for t in p["tokens"])
    (out / "model_graphs.json").write_text(json.dumps(graphs, ensure_ascii=False, indent=1))
    (out / "model_paths.json").write_text(json.dumps(paths, ensure_ascii=False, indent=1))
    summary = defaultdict(lambda: {"paths": 0, "empty": 0, "X_ops": 0})
    for p in paths:
        s = summary[p["source"]]
        s["paths"] += 1
        s["empty"] += not p["tokens"]
        s["X_ops"] += sum(t.startswith("X:") for t in p["tokens"])
    print(json.dumps({"papers": len({p["record_id"] for p in paths}), **summary}, indent=1))


if __name__ == "__main__":
    main()
