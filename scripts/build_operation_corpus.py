"""Collect agent-decomposed records into one corpus file consumed by build_representation_library.py.

Only records whose status is `accepted` (and, with --include-open-findings, also
`accepted_with_open_findings`) are collected. Every assembly is re-validated against the
current catalog and its evidence is re-checked against the stored section packet.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.docling_graph_templates.representation_library import (  # noqa: E402
    OperationAssembly, validate_operation_ports,
)
from scripts.operation_decomposition import ATLAS, CATALOG, PILOT_RECORDS, encoded, sha  # noqa: E402

RUN = ROOT / "analysis/operation_decomposition_2026-10-07"
CORPUS = RUN / "corpus_assemblies.json"
WITHDRAWN = {"full_2026-07-06__rec_001277"}


def collect(run, include_open, include_withdrawn=False):
    catalog = json.loads(CATALOG.read_text())
    library_sha256 = sha(encoded(catalog))
    atlas = json.loads(ATLAS.read_text())
    names = {}
    for m in atlas["architectures"]:
        names.setdefault(m["record_id"], []).append(m["model_name"])
    allowed = {"accepted"} | ({"accepted_with_open_findings"} if include_open else set())
    assemblies, evidence, records, skipped = [], {}, {}, []
    for status_path in sorted((run / "records").glob("*/status.json")):
        status = json.loads(status_path.read_text())
        record = status["record_id"]
        if record in PILOT_RECORDS or status["status"] not in allowed or (record in WITHDRAWN and not include_withdrawn):
            skipped.append({"record_id": record, "status": status["status"]})
            continue
        folder = status_path.parent
        manifest = json.loads((folder / "packet_manifest.json").read_text())
        items = json.loads((folder / "assemblies.json").read_text())
        for item in json.loads((folder / "evidence.json").read_text()):
            text = (folder / "sections" / f"{item['section_id']}.md").read_text(encoding="utf-8")
            if sha(text) != item["section_sha256"] or text.find(item["quote"]) != item["quote_start_char_in_section"]:
                raise ValueError(f"{record}: evidence no longer matches its section packet")
            evidence[item["evidence_id"]] = item
        for assembly in items:
            assembly = {**assembly, "library_release": catalog["release"], "library_sha256": library_sha256}
            OperationAssembly.model_validate(assembly)
            validate_operation_ports(assembly, catalog)
            assemblies.append(assembly)
        label = ", ".join(dict.fromkeys(names.get(record, [record])))
        records[record] = {"paper": label + (" (WITHDRAWN source)" if record in WITHDRAWN else ""),
                           "source_sha256": manifest["source_sha256"], "input_packet_sha256": manifest["packet_sha256"],
                           "decomposition_status": status["status"],
                           "open_blocking_findings": status.get("open_blocking_findings", 0)}
    return {"contract_version": "operation-corpus-v1", "records": records, "assemblies": assemblies,
            "evidence": sorted(evidence.values(), key=lambda e: e["evidence_id"]), "skipped": skipped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument("--include-open-findings", action="store_true")
    parser.add_argument("--include-withdrawn", action="store_true",
                        help="Also publish the withdrawn OKR-Cell record (author decision pending)")
    args = parser.parse_args()
    corpus = collect(args.run, args.include_open_findings, args.include_withdrawn)
    CORPUS.write_bytes(encoded(corpus))
    print(json.dumps({"records": len(corpus["records"]), "assemblies": len(corpus["assemblies"]),
                      "evidence": len(corpus["evidence"]), "skipped": len(corpus["skipped"])}, indent=2))


if __name__ == "__main__":
    main()
